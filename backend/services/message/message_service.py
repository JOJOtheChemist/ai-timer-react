from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.schemas.message import (
    MessageListResponse, MessageResponse, MessageTypeEnum, 
    MessageCreate, MessageUpdate
)
from crud.message.crud_message import crud_message
from crud.message.crud_message_stat import crud_message_stat

class MessageService:
    """消息服务层"""
    
    def get_message_list(
        self,
        db: Session,
        user_id: int,
        message_type: Optional[MessageTypeEnum] = None,
        page: int = 1,
        page_size: int = 20
    ) -> MessageListResponse:
        """按类型查询用户消息列表，包含未读标记"""
        # 获取消息列表和总数
        messages, total = crud_message.get_multi_by_type(
            db, user_id, message_type, page, page_size
        )
        
        # 获取未读消息数
        unread_count = crud_message.count_unread_by_type(db, user_id, message_type)
        
        # 转换为响应模型
        message_responses = []
        for message in messages:
            message_response = MessageResponse.from_orm(message)
            
            # 补充扩展字段（数据库中1=未读，0=已读）
            message_response.is_unread = message.is_unread == 1
            message_response.sender_name = self._get_sender_name(db, message.sender_id)
            message_response.sender_avatar = self._get_sender_avatar(db, message.sender_id)
            message_response.reply_count = self._get_reply_count(db, message.id)
            
            # 为不同类型消息补充关联信息
            if message_type == MessageTypeEnum.TUTOR:
                message_response = self._enrich_tutor_message(db, message_response)
            
            message_responses.append(message_response)
        
        return MessageListResponse(
            messages=message_responses,
            total=total,
            unread_count=unread_count,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def _get_sender_name(self, db: Session, sender_id: int) -> Optional[str]:
        """获取发送方姓名"""
        from sqlalchemy import text
        
        if sender_id is None or sender_id == 0:  # 系统消息
            return "系统"
        
        # 从数据库查询用户名
        query = text('SELECT username FROM "user" WHERE id = :user_id')
        result = db.execute(query, {"user_id": sender_id}).fetchone()
        
        if result:
            return result[0]
        return f"用户{sender_id}"
    
    def _get_sender_avatar(self, db: Session, sender_id: int) -> Optional[str]:
        """获取发送方头像"""
        from sqlalchemy import text
        
        if sender_id is None or sender_id == 0:  # 系统消息
            return "🔔"
        
        # 从数据库查询用户头像
        query = text('SELECT avatar FROM "user" WHERE id = :user_id')
        result = db.execute(query, {"user_id": sender_id}).fetchone()
        
        if result and result[0]:
            return result[0]
        
        # 返回默认头像（循环使用5个头像）
        avatar_files = [
            "/avatars/avatar1.png",
            "/avatars/avatar2.png",
            "/avatars/avatar3.png",
            "/avatars/avatar4.jpg",
            "/avatars/avatar5.png"
        ]
        return avatar_files[(sender_id - 1) % 5]
    
    def _get_reply_count(self, db: Session, message_id: int) -> int:
        """获取消息回复数量"""
        replies = crud_message.get_message_replies(db, message_id, 0)  # 临时用0作为user_id
        return len(replies)
    
    def _enrich_tutor_message(self, db: Session, message: MessageResponse) -> MessageResponse:
        """为导师反馈消息补充关联信息"""
        if message.related_id and message.related_type == 0:
            # 这里应该调用导师服务获取导师认证状态等信息
            # 目前添加模拟数据
            message.sender_name = f"导师{message.related_id}"
            # 可以添加导师认证状态、专业领域等信息
        return message
    
    def create_message(
        self,
        db: Session,
        sender_id: int,
        message_data: MessageCreate
    ) -> MessageResponse:
        """创建新消息"""
        # 创建消息
        db_message = crud_message.create(db, sender_id, message_data)
        
        # 转换为响应模型
        message_response = MessageResponse.from_orm(db_message)
        message_response.sender_name = self._get_sender_name(db, sender_id)
        message_response.sender_avatar = self._get_sender_avatar(db, sender_id)
        message_response.is_unread = True
        message_response.reply_count = 0
        
        return message_response
    
    def update_message(
        self,
        db: Session,
        message_id: int,
        user_id: int,
        message_data: MessageUpdate
    ) -> Optional[MessageResponse]:
        """更新消息"""
        db_message = crud_message.update(db, message_id, user_id, message_data)
        if not db_message:
            return None
        
        message_response = MessageResponse.from_orm(db_message)
        message_response.sender_name = self._get_sender_name(db, db_message.sender_id)
        message_response.sender_avatar = self._get_sender_avatar(db, db_message.sender_id)
        message_response.is_unread = db_message.is_unread == 0
        message_response.reply_count = self._get_reply_count(db, message_id)
        
        return message_response
    
    def delete_message(self, db: Session, message_id: int, user_id: int) -> bool:
        """删除消息"""
        return crud_message.delete(db, message_id, user_id)
    
    def get_conversation_history(
        self,
        db: Session,
        user_id: int,
        other_user_id: int,
        limit: int = 10
    ) -> List[MessageResponse]:
        """获取与特定用户的对话历史"""
        messages = crud_message.get_conversation_history(db, user_id, other_user_id, limit)
        
        message_responses = []
        for message in messages:
            message_response = MessageResponse.from_orm(message)
            message_response.sender_name = self._get_sender_name(db, message.sender_id)
            message_response.sender_avatar = self._get_sender_avatar(db, message.sender_id)
            message_response.is_unread = message.is_unread == 0
            message_response.reply_count = self._get_reply_count(db, message.id)
            message_responses.append(message_response)
        
        return message_responses
    
    def batch_mark_as_read(
        self,
        db: Session,
        message_ids: List[int],
        user_id: int
    ) -> int:
        """批量标记消息为已读"""
        return crud_message.batch_mark_as_read(db, message_ids, user_id)
    
    def batch_delete_messages(
        self,
        db: Session,
        message_ids: List[int],
        user_id: int
    ) -> int:
        """批量删除消息"""
        return crud_message.batch_delete(db, message_ids, user_id)
    
    def cleanup_old_messages(self, db: Session, days: int = 30) -> int:
        """清理过期消息"""
        return crud_message.cleanup_old_messages(db, days)

# 创建服务实例
message_service = MessageService() 