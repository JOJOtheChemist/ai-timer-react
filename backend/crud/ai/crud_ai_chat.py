from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from models.ai import AIChatRecord
from models.schemas.ai import ChatMessageCreate, MessageRole

class CRUDAIChatRecord:
    """AI聊天记录CRUD操作"""
    
    def create_chat_record(
        self, 
        db: Session, 
        user_id: int, 
        role: MessageRole,
        content: str,
        session_id: str,
        is_analysis: bool = False,
        analysis_tags: Optional[List[str]] = None,
        related_data: Optional[dict] = None,
        token_count: int = 0
    ) -> AIChatRecord:
        """创建聊天记录"""
        db_record = AIChatRecord(
            user_id=user_id,
            session_id=session_id,
            role=role.value,
            content=content,
            is_analysis=1 if is_analysis else 0,
            analysis_tags=analysis_tags,
            related_data=related_data,
            token_count=token_count
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    def get_multi_by_user(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20,
        session_id: Optional[str] = None
    ) -> tuple[List[AIChatRecord], int]:
        """获取用户的聊天记录（分页）"""
        query = db.query(AIChatRecord).filter(AIChatRecord.user_id == user_id)
        
        if session_id:
            query = query.filter(AIChatRecord.session_id == session_id)
        
        # 获取总数
        total = query.count()
        
        # 分页查询，按时间倒序
        records = query.order_by(desc(AIChatRecord.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size)\
                      .all()
        
        return records, total
    
    def get_chat_history_by_time(
        self,
        db: Session,
        user_id: int,
        start_time: datetime,
        end_time: datetime,
        session_id: Optional[str] = None
    ) -> List[AIChatRecord]:
        """按时间范围获取聊天记录"""
        query = db.query(AIChatRecord).filter(
            and_(
                AIChatRecord.user_id == user_id,
                AIChatRecord.create_time >= start_time,
                AIChatRecord.create_time <= end_time
            )
        )
        
        if session_id:
            query = query.filter(AIChatRecord.session_id == session_id)
        
        return query.order_by(AIChatRecord.create_time).all()
    
    def get_recent_chat_by_session(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        limit: int = 10
    ) -> List[AIChatRecord]:
        """获取会话的最近聊天记录"""
        return db.query(AIChatRecord).filter(
            and_(
                AIChatRecord.user_id == user_id,
                AIChatRecord.session_id == session_id
            )
        ).order_by(desc(AIChatRecord.create_time)).limit(limit).all()
    
    def get_user_sessions(
        self,
        db: Session,
        user_id: int,
        days: int = 7
    ) -> List[dict]:
        """获取用户的会话列表"""
        start_time = datetime.now() - timedelta(days=days)
        
        # 查询会话信息
        sessions = db.query(
            AIChatRecord.session_id,
            func.max(AIChatRecord.create_time).label('last_message_time'),
            func.count(AIChatRecord.id).label('message_count')
        ).filter(
            and_(
                AIChatRecord.user_id == user_id,
                AIChatRecord.create_time >= start_time
            )
        ).group_by(AIChatRecord.session_id)\
         .order_by(desc('last_message_time'))\
         .all()
        
        return [
            {
                "session_id": session.session_id,
                "last_message_time": session.last_message_time,
                "message_count": session.message_count
            }
            for session in sessions
        ]
    
    def delete_old_records(
        self,
        db: Session,
        days: int = 90
    ) -> int:
        """删除过期的聊天记录"""
        cutoff_time = datetime.now() - timedelta(days=days)
        
        deleted_count = db.query(AIChatRecord).filter(
            AIChatRecord.create_time < cutoff_time
        ).delete()
        
        db.commit()
        return deleted_count
    
    def generate_session_id(self) -> str:
        """生成新的会话ID"""
        return str(uuid.uuid4())

# 创建CRUD实例
crud_ai_chat = CRUDAIChatRecord() 