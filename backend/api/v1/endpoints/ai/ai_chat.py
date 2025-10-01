from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime, timedelta
import json

from core.database import get_db
from services.ai.ai_chat_service import ai_chat_service
from models.schemas.ai import (
    ChatMessageCreate, ChatResponse, ChatHistoryResponse,
    StreamChatResponse, BaseResponse
)

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def send_chat_message(
    message: ChatMessageCreate,
    stream: bool = Query(False, description="是否使用流式响应"),
    user_id: int = Query(..., description="用户ID"),  # 实际项目中应该从JWT token获取
    db: Session = Depends(get_db)
):
    """
    发送聊天消息并获取AI回复
    
    - **message**: 用户消息内容
    - **stream**: 是否使用流式响应
    - **user_id**: 用户ID
    """
    try:
        if stream:
            # 流式响应
            async def generate_stream():
                async for chunk in ai_chat_service.send_chat_message_stream(
                    db=db,
                    user_id=user_id,
                    message=message
                ):
                    yield f"data: {json.dumps(chunk.dict(), ensure_ascii=False, default=str)}\n\n"
                yield "data: [DONE]\n\n"
            
            return StreamingResponse(
                generate_stream(),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        else:
            # 同步响应
            response = await ai_chat_service.send_chat_message(
                db=db,
                user_id=user_id,
                message=message,
                stream=False
            )
            return response
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI服务错误: {str(e)}")

@router.get("/chat/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user_id: int = Query(..., description="用户ID"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    session_id: Optional[str] = Query(None, description="会话ID，不传则获取所有会话"),
    db: Session = Depends(get_db)
):
    """
    获取用户聊天历史记录
    
    - **user_id**: 用户ID
    - **page**: 页码
    - **page_size**: 每页大小
    - **session_id**: 会话ID（可选）
    """
    try:
        history = ai_chat_service.get_chat_history(
            db=db,
            user_id=user_id,
            page=page,
            page_size=page_size,
            session_id=session_id
        )
        return history
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取聊天历史失败: {str(e)}")

@router.get("/chat/history/recent", response_model=ChatHistoryResponse)
async def get_recent_chat_history(
    user_id: int = Query(..., description="用户ID"),
    days: int = Query(7, ge=1, le=30, description="最近天数"),
    session_id: Optional[str] = Query(None, description="会话ID"),
    db: Session = Depends(get_db)
):
    """
    获取最近几天的聊天历史
    
    - **user_id**: 用户ID
    - **days**: 最近天数
    - **session_id**: 会话ID（可选）
    """
    try:
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        
        messages = ai_chat_service.get_chat_history_by_time(
            db=db,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
            session_id=session_id
        )
        
        return ChatHistoryResponse(
            messages=messages,
            total=len(messages),
            page=1,
            page_size=len(messages),
            has_next=False
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取最近聊天历史失败: {str(e)}")

@router.get("/chat/sessions")
async def get_user_chat_sessions(
    user_id: int = Query(..., description="用户ID"),
    days: int = Query(7, ge=1, le=30, description="最近天数"),
    db: Session = Depends(get_db)
):
    """
    获取用户的聊天会话列表
    
    - **user_id**: 用户ID
    - **days**: 最近天数
    """
    try:
        from crud.ai.crud_ai_chat import crud_ai_chat
        
        sessions = crud_ai_chat.get_user_sessions(
            db=db,
            user_id=user_id,
            days=days
        )
        
        return BaseResponse(
            success=True,
            message="获取会话列表成功",
            data=sessions
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取会话列表失败: {str(e)}")

@router.delete("/chat/history")
async def clear_chat_history(
    user_id: int = Query(..., description="用户ID"),
    session_id: Optional[str] = Query(None, description="会话ID，不传则清空所有历史"),
    days: Optional[int] = Query(None, ge=1, description="清空多少天前的历史"),
    db: Session = Depends(get_db)
):
    """
    清空聊天历史
    
    - **user_id**: 用户ID
    - **session_id**: 会话ID（可选）
    - **days**: 清空多少天前的历史（可选）
    """
    try:
        from crud.ai.crud_ai_chat import crud_ai_chat
        from sqlalchemy import and_
        from models.ai import AIChatRecord
        
        query = db.query(AIChatRecord).filter(AIChatRecord.user_id == user_id)
        
        if session_id:
            query = query.filter(AIChatRecord.session_id == session_id)
        
        if days:
            cutoff_time = datetime.now() - timedelta(days=days)
            query = query.filter(AIChatRecord.create_time < cutoff_time)
        
        deleted_count = query.delete()
        db.commit()
        
        return BaseResponse(
            success=True,
            message=f"成功清空 {deleted_count} 条聊天记录",
            data={"deleted_count": deleted_count}
        )
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"清空聊天历史失败: {str(e)}")

# 健康检查
@router.get("/chat/health")
async def chat_health_check():
    """AI聊天服务健康检查"""
    return BaseResponse(
        success=True,
        message="AI聊天服务正常运行",
        data={
            "service": "ai_chat",
            "status": "healthy",
            "timestamp": datetime.now()
        }
    ) 