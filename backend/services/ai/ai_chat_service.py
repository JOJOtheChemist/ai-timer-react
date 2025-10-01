from sqlalchemy.orm import Session
from typing import List, Optional, AsyncGenerator
from datetime import datetime, timedelta
import httpx
import json
import uuid

from core.config import settings
from crud.ai.crud_ai_chat import crud_ai_chat
from models.schemas.ai import (
    ChatMessageCreate, ChatResponse, ChatHistoryResponse, 
    MessageRole, StreamChatResponse, ChatMessage
)

class AIChatService:
    """AI聊天服务"""
    
    def __init__(self):
        self.api_key = settings.AI_MODEL_API_KEY
        self.base_url = settings.AI_MODEL_BASE_URL
        self.model_name = settings.AI_MODEL_NAME
    
    async def send_chat_message(
        self,
        db: Session,
        user_id: int,
        message: ChatMessageCreate,
        stream: bool = False
    ) -> ChatResponse:
        """发送聊天消息并获取AI回复"""
        
        # 生成或使用现有session_id
        session_id = message.session_id or crud_ai_chat.generate_session_id()
        
        # 保存用户消息
        crud_ai_chat.create_chat_record(
            db=db,
            user_id=user_id,
            role=MessageRole.USER,
            content=message.content,
            session_id=session_id
        )
        
        # 获取对话历史（最近10条）
        chat_history = crud_ai_chat.get_recent_chat_by_session(
            db=db,
            user_id=user_id,
            session_id=session_id,
            limit=10
        )
        
        # 构建对话上下文
        messages = self._build_chat_context(chat_history, message.content)
        
        # 调用AI模型
        if stream:
            # 流式响应处理
            ai_response = await self._call_ai_model_stream(messages)
        else:
            # 同步响应
            ai_response = await self._call_ai_model(messages)
        
        # 分析是否为分析型回复
        is_analysis, analysis_tags = self._analyze_response(ai_response)
        
        # 保存AI回复
        crud_ai_chat.create_chat_record(
            db=db,
            user_id=user_id,
            role=MessageRole.AI,
            content=ai_response,
            session_id=session_id,
            is_analysis=is_analysis,
            analysis_tags=analysis_tags,
            token_count=self._estimate_tokens(ai_response)
        )
        
        return ChatResponse(
            content=ai_response,
            is_analysis=is_analysis,
            analysis_tags=analysis_tags,
            session_id=session_id,
            token_count=self._estimate_tokens(ai_response)
        )
    
    async def send_chat_message_stream(
        self,
        db: Session,
        user_id: int,
        message: ChatMessageCreate
    ) -> AsyncGenerator[StreamChatResponse, None]:
        """流式发送聊天消息"""
        
        session_id = message.session_id or crud_ai_chat.generate_session_id()
        
        # 保存用户消息
        crud_ai_chat.create_chat_record(
            db=db,
            user_id=user_id,
            role=MessageRole.USER,
            content=message.content,
            session_id=session_id
        )
        
        # 获取对话历史
        chat_history = crud_ai_chat.get_recent_chat_by_session(
            db=db,
            user_id=user_id,
            session_id=session_id,
            limit=10
        )
        
        # 构建对话上下文
        messages = self._build_chat_context(chat_history, message.content)
        
        # 流式调用AI模型
        full_response = ""
        token_count = 0
        
        async for chunk in self._call_ai_model_stream(messages):
            full_response += chunk
            token_count += 1
            
            yield StreamChatResponse(
                delta=chunk,
                is_complete=False,
                session_id=session_id,
                token_count=token_count
            )
        
        # 分析完整回复
        is_analysis, analysis_tags = self._analyze_response(full_response)
        
        # 保存完整的AI回复
        crud_ai_chat.create_chat_record(
            db=db,
            user_id=user_id,
            role=MessageRole.AI,
            content=full_response,
            session_id=session_id,
            is_analysis=is_analysis,
            analysis_tags=analysis_tags,
            token_count=token_count
        )
        
        # 发送完成信号
        yield StreamChatResponse(
            delta="",
            is_complete=True,
            session_id=session_id,
            token_count=token_count
        )
    
    def get_chat_history(
        self,
        db: Session,
        user_id: int,
        page: int = 1,
        page_size: int = 20,
        session_id: Optional[str] = None
    ) -> ChatHistoryResponse:
        """获取聊天历史"""
        
        records, total = crud_ai_chat.get_multi_by_user(
            db=db,
            user_id=user_id,
            page=page,
            page_size=page_size,
            session_id=session_id
        )
        
        # 转换为响应模型
        messages = [
            ChatMessage(
                id=record.id,
                role=MessageRole(record.role),
                content=record.content,
                is_analysis=bool(record.is_analysis),
                analysis_tags=record.analysis_tags,
                create_time=record.create_time
            )
            for record in records
        ]
        
        return ChatHistoryResponse(
            messages=messages,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def get_chat_history_by_time(
        self,
        db: Session,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        session_id: Optional[str] = None
    ) -> List[ChatMessage]:
        """按时间范围获取聊天历史"""
        
        records = crud_ai_chat.get_chat_history_by_time(
            db=db,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            session_id=session_id
        )
        
        return [
            ChatMessage(
                id=record.id,
                role=MessageRole(record.role),
                content=record.content,
                is_analysis=bool(record.is_analysis),
                analysis_tags=record.analysis_tags,
                create_time=record.create_time
            )
            for record in records
        ]
    
    def _build_chat_context(
        self, 
        chat_history: List, 
        current_message: str
    ) -> List[dict]:
        """构建对话上下文"""
        messages = [
            {
                "role": "system",
                "content": "你是一个专业的AI学习助手，专门帮助用户进行时间管理和学习规划。请用友好、专业的语气回答用户问题。"
            }
        ]
        
        # 添加历史对话（倒序，最新的在前）
        for record in reversed(chat_history[:-1]):  # 排除当前消息
            messages.append({
                "role": record.role,
                "content": record.content
            })
        
        # 添加当前消息
        messages.append({
            "role": "user",
            "content": current_message
        })
        
        return messages
    
    async def _call_ai_model(self, messages: List[dict]) -> str:
        """调用AI模型（同步）"""
        if not self.api_key:
            # 如果没有配置API密钥，返回模拟回复
            return self._get_mock_response(messages[-1]["content"])
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000
                    },
                    timeout=30.0
                )
                response.raise_for_status()
                
                result = response.json()
                return result["choices"][0]["message"]["content"]
                
        except Exception as e:
            # 如果API调用失败，返回错误提示
            return f"抱歉，AI服务暂时不可用。错误信息：{str(e)}"
    
    async def _call_ai_model_stream(self, messages: List[dict]) -> AsyncGenerator[str, None]:
        """调用AI模型（流式）"""
        if not self.api_key:
            # 模拟流式响应
            mock_response = self._get_mock_response(messages[-1]["content"])
            for char in mock_response:
                yield char
            return
        
        try:
            async with httpx.AsyncClient() as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model_name,
                        "messages": messages,
                        "temperature": 0.7,
                        "max_tokens": 1000,
                        "stream": True
                    },
                    timeout=30.0
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            
                            try:
                                chunk = json.loads(data)
                                if "choices" in chunk and len(chunk["choices"]) > 0:
                                    delta = chunk["choices"][0].get("delta", {})
                                    if "content" in delta:
                                        yield delta["content"]
                            except json.JSONDecodeError:
                                continue
                                
        except Exception as e:
            yield f"抱歉，AI服务暂时不可用。错误信息：{str(e)}"
    
    def _analyze_response(self, response: str) -> tuple[bool, Optional[List[str]]]:
        """分析回复是否为分析型回复"""
        analysis_keywords = [
            "分析", "建议", "优化", "改进", "问题", "效率", 
            "时间管理", "学习方法", "计划", "总结"
        ]
        
        is_analysis = any(keyword in response for keyword in analysis_keywords)
        
        if is_analysis:
            # 提取分析标签（简单实现）
            tags = []
            if "时间" in response and ("碎片" in response or "分散" in response):
                tags.append("时间碎片化")
            if "复习" in response and ("不足" in response or "缺乏" in response):
                tags.append("复习不足")
            if "效率" in response:
                tags.append("效率问题")
            if "计划" in response:
                tags.append("计划优化")
            
            return True, tags if tags else ["学习分析"]
        
        return False, None
    
    def _estimate_tokens(self, text: str) -> int:
        """估算token数量（简单实现）"""
        # 中文字符按1.5个token计算，英文单词按1个token计算
        chinese_chars = len([c for c in text if '\u4e00' <= c <= '\u9fff'])
        english_words = len(text.replace(' ', '').replace('\n', '')) - chinese_chars
        
        return int(chinese_chars * 1.5 + english_words * 0.5)
    
    def _get_mock_response(self, user_message: str) -> str:
        """获取模拟回复（用于测试）"""
        mock_responses = {
            "时间": "关于时间管理，我建议你可以尝试番茄工作法，将学习时间分成25分钟的专注时段。",
            "学习": "学习效率的提升需要找到适合自己的方法，建议你先分析自己的学习习惯。",
            "计划": "制定学习计划时，要考虑你的目标、可用时间和个人能力，建议采用SMART原则。",
            "复习": "复习是学习的重要环节，推荐使用艾宾浩斯遗忘曲线来安排复习时间。"
        }
        
        for keyword, response in mock_responses.items():
            if keyword in user_message:
                return response
        
        return "我理解你的问题，让我为你提供一些建议和分析。作为你的AI学习助手，我会帮助你优化学习方法和时间管理。"

# 创建服务实例
ai_chat_service = AIChatService() 