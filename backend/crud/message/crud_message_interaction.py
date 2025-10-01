from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional
from datetime import datetime

from models.message import Message
from models.schemas.message import MessageTypeEnum
from crud.message.crud_message import crud_message

class CRUDMessageInteraction:
    """消息互动CRUD操作"""
    
    def create_reply(
        self, 
        db: Session, 
        user_id: int, 
        message_id: int, 
        content: str
    ) -> Optional[Message]:
        """创建回复消息"""
        # 获取原消息
        original_message = crud_message.get_by_id(db, message_id, user_id)
        if not original_message:
            return None
        
        # 检查是否可以回复
        if original_message.message_type == 2:
            return None
        
        if original_message.receiver_id != user_id:
            return None
        
        # 创建回复消息
        reply_message = Message(
            sender_id=user_id,
            receiver_id=original_message.sender_id,  # 回复给原发送方
            type=original_message.message_type,
            title=f"Re: {original_message.title}",
            content=content,
            related_id=original_message.related_id,
            related_type=original_message.related_type,
            parent_message_id=message_id
        )
        
        db.add(reply_message)
        db.commit()
        db.refresh(reply_message)
        return reply_message
    
    def update_read_status(
        self, 
        db: Session, 
        user_id: int, 
        message_id: int
    ) -> Optional[Message]:
        """更新消息的已读状态"""
        return crud_message.mark_as_read(db, message_id, user_id)
    
    def batch_update_read_status(
        self, 
        db: Session, 
        user_id: int, 
        message_ids: list[int]
    ) -> int:
        """批量更新消息已读状态"""
        return crud_message.batch_mark_as_read(db, message_ids, user_id)
    
    def auto_mark_system_messages_read(
        self, 
        db: Session, 
        user_id: int
    ) -> int:
        """自动标记系统消息为已读"""
        updated_count = db.query(Message).filter(
            and_(
                Message.receiver_id == user_id,
                Message.type == 2,
                Message.is_unread == 0
            )
        ).update({
            "is_read": 1,
            "read_time": datetime.now()
        }, synchronize_session=False)
        
        db.commit()
        return updated_count
    
    def get_reply_chain(
        self, 
        db: Session, 
        message_id: int, 
        user_id: int
    ) -> list[Message]:
        """获取消息的完整回复链"""
        # 获取原消息
        original_message = crud_message.get_by_id(db, message_id, user_id)
        if not original_message:
            return []
        
        # 如果当前消息是回复，先找到根消息
        root_message_id = original_message.parent_message_id or message_id
        
        # 获取所有相关的消息（包括根消息和所有回复）
        all_messages = db.query(Message).filter(
            and_(
                Message.id.in_([root_message_id]),
                Message.parent_message_id == root_message_id
            )
        ).order_by(Message.create_time).all()
        
        return all_messages
    
    def check_message_permission(
        self, 
        db: Session, 
        message_id: int, 
        user_id: int, 
        action: str = "read"
    ) -> bool:
        """检查用户对消息的操作权限"""
        message = crud_message.get_by_id(db, message_id, user_id)
        if not message:
            return False
        
        if action == "read":
            # 发送方和接收方都可以查看
            return message.sender_id == user_id or message.receiver_id == user_id
        elif action == "reply":
            # 只有接收方可以回复，且系统消息不能回复
            return (message.receiver_id == user_id and 
                   message.message_type != 2)
        elif action == "delete":
            # 只有接收方可以删除
            return message.receiver_id == user_id
        elif action == "mark_read":
            # 只有接收方可以标记已读
            return message.receiver_id == user_id
        
        return False

# 创建CRUD实例
crud_message_interaction = CRUDMessageInteraction() 