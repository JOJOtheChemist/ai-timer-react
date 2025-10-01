from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, or_
from typing import List, Optional, Dict, Any

from models.message import Message
from crud.message.crud_message import crud_message

class CRUDMessageDetail:
    """消息详情CRUD操作"""
    
    def get_by_id_with_context(
        self, 
        db: Session, 
        user_id: int, 
        message_id: int
    ) -> Optional[Dict[str, Any]]:
        """查询消息详情及关联上下文"""
        # 获取主消息
        main_message = crud_message.get_by_id(db, message_id, user_id)
        if not main_message:
            return None
        
        result = {
            "message": main_message,
            "context_messages": [],
            "replies": []
        }
        
        # 根据消息类型获取不同的上下文
        if main_message.message_type == 0:
            # 导师反馈：获取与同一导师的历史互动
            result["context_messages"] = self._get_tutor_context(
                db, user_id, main_message.related_id, message_id
            )
        elif main_message.message_type == 1:
            # 私信：获取与发送方的对话历史
            result["context_messages"] = self._get_private_context(
                db, user_id, main_message.sender_id, message_id
            )
        
        # 获取回复消息
        result["replies"] = crud_message.get_message_replies(db, message_id, user_id)
        
        return result
    
    def _get_tutor_context(
        self, 
        db: Session, 
        user_id: int, 
        tutor_id: Optional[int], 
        exclude_message_id: int,
        limit: int = 5
    ) -> List[Message]:
        """获取导师反馈的历史上下文"""
        if not tutor_id:
            return []
        
        return db.query(Message).filter(
            and_(
                Message.receiver_id == user_id,
                Message.type == 0,
                Message.related_id == tutor_id,
                Message.id != exclude_message_id
            )
        ).order_by(desc(Message.create_time)).limit(limit).all()
    
    def _get_private_context(
        self, 
        db: Session, 
        user_id: int, 
        other_user_id: int, 
        exclude_message_id: int,
        limit: int = 5
    ) -> List[Message]:
        """获取私信的对话历史上下文"""
        return db.query(Message).filter(
            and_(
                or_(
                    and_(
                        Message.sender_id == user_id,
                        Message.receiver_id == other_user_id
                    ),
                    and_(
                        Message.sender_id == other_user_id,
                        Message.receiver_id == user_id
                    )
                ),
                Message.type == 1,
                Message.id != exclude_message_id
            )
        ).order_by(desc(Message.create_time)).limit(limit).all()
    
    def get_related_resource_info(
        self, 
        db: Session, 
        related_type: Optional[str], 
        related_id: Optional[int]
    ) -> Optional[Dict[str, Any]]:
        """获取关联资源信息"""
        if not related_type or not related_id:
            return None
        
        # 这里可以根据不同的关联类型获取相应的资源信息
        # 目前返回基础信息，实际项目中需要调用对应业务域的服务
        
        resource_info = {
            "type": related_type,
            "id": related_id,
            "title": f"{related_type}#{related_id}",
            "url": f"/{related_type}/{related_id}"
        }
        
        # 根据类型补充特定信息
        if related_type == 0:
            resource_info.update({
                "title": "导师服务",
                "url": f"/tutors/{related_id}"
            })
        elif related_type == "schedule":
            resource_info.update({
                "title": "时间表",
                "url": f"/schedule/{related_id}"
            })
        elif related_type == "task":
            resource_info.update({
                "title": "任务",
                "url": f"/tasks/{related_id}"
            })
        
        return resource_info
    
    def check_can_reply(self, message: Message, user_id: int) -> bool:
        """检查是否可以回复消息"""
        # 系统消息不能回复
        if message.message_type == 2:
            return False
        
        # 只有接收方可以回复
        if message.receiver_id != user_id:
            return False
        
        return True

# 创建CRUD实例
crud_message_detail = CRUDMessageDetail() 