from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, or_
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.message import Message
from models.schemas.message import MessageCreate, MessageUpdate, MessageTypeEnum

class CRUDMessage:
    """消息CRUD操作"""
    
    def create(self, db: Session, sender_id: int, message_data: MessageCreate) -> Message:
        """创建消息"""
        db_message = Message(
            sender_id=sender_id,
            receiver_id=message_data.receiver_id,
            type=message_data.message_type.value,
            title=message_data.title,
            content=message_data.content,
            related_id=message_data.related_id,
            related_type=message_data.related_type,
            attachment_url=message_data.attachment_url if hasattr(message_data, 'attachment_url') else None
        )
        db.add(db_message)
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def get_multi_by_type(
        self, 
        db: Session, 
        user_id: int, 
        message_type: Optional[MessageTypeEnum] = None,
        page: int = 1, 
        page_size: int = 20
    ) -> tuple[List[Message], int]:
        """按类型获取用户消息列表"""
        query = db.query(Message).filter(Message.receiver_id == user_id)
        
        if message_type:
            query = query.filter(Message.type == message_type.value)
        
        # 获取总数
        total = query.count()
        
        # 分页查询，按时间倒序
        messages = query.order_by(desc(Message.create_time))\
                       .offset((page - 1) * page_size)\
                       .limit(page_size)\
                       .all()
        
        return messages, total
    
    def count_unread_by_type(
        self, 
        db: Session, 
        user_id: int, 
        message_type: Optional[MessageTypeEnum] = None
    ) -> int:
        """统计指定类型的未读消息数（数据库中1=未读，0=已读）"""
        query = db.query(Message).filter(
            and_(
                Message.receiver_id == user_id,
                Message.is_unread == 1
            )
        )
        
        if message_type:
            query = query.filter(Message.type == message_type.value)
        
        return query.count()
    
    def get_by_id(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        """根据ID获取消息（验证用户权限）"""
        return db.query(Message).filter(
            and_(
                Message.id == message_id,
                or_(
                    Message.receiver_id == user_id,
                    Message.sender_id == user_id
                )
            )
        ).first()
    
    def update(self, db: Session, message_id: int, user_id: int, message_data: MessageUpdate) -> Optional[Message]:
        """更新消息"""
        db_message = self.get_by_id(db, message_id, user_id)
        if not db_message:
            return None
        
        update_data = message_data.dict(exclude_unset=True)
        
        # 处理布尔类型转换
        if 'is_read' in update_data:
            update_data['is_read'] = 1 if update_data['is_read'] else 0
            if update_data['is_read'] == 1:
                update_data['read_time'] = datetime.now()
        
        for field, value in update_data.items():
            if hasattr(db_message, field):
                setattr(db_message, field, value)
        
        db.commit()
        db.refresh(db_message)
        return db_message
    
    def mark_as_read(self, db: Session, message_id: int, user_id: int) -> Optional[Message]:
        """标记消息为已读"""
        db_message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.receiver_id == user_id,
                Message.is_unread == 0
            )
        ).first()
        
        if db_message:
            db_message.is_unread = 1
            db_message.read_time = datetime.now()
            db.commit()
            db.refresh(db_message)
        
        return db_message
    
    def batch_mark_as_read(self, db: Session, message_ids: List[int], user_id: int) -> int:
        """批量标记消息为已读"""
        updated_count = db.query(Message).filter(
            and_(
                Message.id.in_(message_ids),
                Message.receiver_id == user_id,
                Message.is_unread == 0
            )
        ).update({
            "is_read": 1,
            "read_time": datetime.now()
        }, synchronize_session=False)
        
        db.commit()
        return updated_count
    
    def delete(self, db: Session, message_id: int, user_id: int) -> bool:
        """删除消息（仅接收方可删除）"""
        db_message = db.query(Message).filter(
            and_(
                Message.id == message_id,
                Message.receiver_id == user_id
            )
        ).first()
        
        if not db_message:
            return False
        
        db.delete(db_message)
        db.commit()
        return True
    
    def batch_delete(self, db: Session, message_ids: List[int], user_id: int) -> int:
        """批量删除消息"""
        deleted_count = db.query(Message).filter(
            and_(
                Message.id.in_(message_ids),
                Message.receiver_id == user_id
            )
        ).delete(synchronize_session=False)
        
        db.commit()
        return deleted_count
    
    def get_conversation_history(
        self, 
        db: Session, 
        user_id: int, 
        other_user_id: int, 
        limit: int = 10
    ) -> List[Message]:
        """获取与特定用户的对话历史"""
        return db.query(Message).filter(
            or_(
                and_(
                    Message.sender_id == user_id,
                    Message.receiver_id == other_user_id
                ),
                and_(
                    Message.sender_id == other_user_id,
                    Message.receiver_id == user_id
                )
            )
        ).order_by(desc(Message.create_time)).limit(limit).all()
    
    def get_message_replies(self, db: Session, message_id: int, user_id: int) -> List[Message]:
        """获取消息的回复列表 (注意：需要通过message_reply表查询)"""
        # TODO: 通过message_reply表查询回复
        return []
    
    def cleanup_old_messages(self, db: Session, days: int = 30) -> int:
        """清理过期消息"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        deleted_count = db.query(Message).filter(
            Message.create_time < cutoff_time
        ).delete()
        
        db.commit()
        return deleted_count

# 创建CRUD实例
crud_message = CRUDMessage() 