from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import Dict, Any
from datetime import datetime, timedelta

from models.message import Message
from models.schemas.message import MessageTypeEnum

class CRUDMessageStat:
    """消息统计CRUD操作"""
    
    def count_unread_by_all_types(self, db: Session, user_id: int) -> Dict[str, int]:
        """按类型统计未读消息数量"""
        # 查询各类型未读消息数
        stats = db.query(
            Message.type,
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.receiver_id == user_id,
                Message.is_unread == 0
            )
        ).group_by(Message.type).all()
        
        # 初始化结果
        result = {
            "tutor_count": 0,
            "private_count": 0,
            "system_count": 0,
            "total_count": 0
        }
        
        # 填充统计数据
        for stat in stats:
            count = stat.count
            result["total_count"] += count
            
            if stat.message_type == 0:
                result["tutor_count"] = count
            elif stat.message_type == 1:
                result["private_count"] = count
            elif stat.message_type == 2:
                result["system_count"] = count
        
        return result
    
    def get_message_stats_by_period(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 7
    ) -> Dict[str, Any]:
        """获取指定时期的消息统计"""
        start_date = datetime.now() - timedelta(days=days)
        
        # 总消息数
        total_messages = db.query(func.count(Message.id)).filter(
            and_(
                Message.receiver_id == user_id,
                Message.create_time >= start_date
            )
        ).scalar() or 0
        
        # 已读消息数
        read_messages = db.query(func.count(Message.id)).filter(
            and_(
                Message.receiver_id == user_id,
                Message.create_time >= start_date,
                Message.is_unread == 1
            )
        ).scalar() or 0
        
        # 按类型统计
        type_stats = db.query(
            Message.type,
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.receiver_id == user_id,
                Message.create_time >= start_date
            )
        ).group_by(Message.type).all()
        
        # 按日期统计
        daily_stats = db.query(
            func.date(Message.create_time).label('date'),
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.receiver_id == user_id,
                Message.create_time >= start_date
            )
        ).group_by(func.date(Message.create_time)).all()
        
        return {
            "period_days": days,
            "total_messages": total_messages,
            "read_messages": read_messages,
            "unread_messages": total_messages - read_messages,
            "read_rate": (read_messages / total_messages * 100) if total_messages > 0 else 0,
            "type_stats": {stat.message_type: stat.count for stat in type_stats},
            "daily_stats": [
                {"date": str(stat.date), "count": stat.count} 
                for stat in daily_stats
            ]
        }
    
    def get_sender_stats(self, db: Session, user_id: int, limit: int = 10) -> list[Dict[str, Any]]:
        """获取发送方统计（最活跃的发送方）"""
        stats = db.query(
            Message.sender_id,
            func.count(Message.id).label('message_count'),
            func.sum(func.case([(Message.is_unread == 0, 1)], else_=0)).label('unread_count')
        ).filter(
            Message.receiver_id == user_id
        ).group_by(Message.sender_id)\
         .order_by(func.count(Message.id).desc())\
         .limit(limit).all()
        
        return [
            {
                "sender_id": stat.sender_id,
                "message_count": stat.message_count,
                "unread_count": stat.unread_count or 0
            }
            for stat in stats
        ]
    
    def get_response_rate_stats(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取回复率统计"""
        # 收到的消息（排除系统消息）
        received_messages = db.query(func.count(Message.id)).filter(
            and_(
                Message.receiver_id == user_id,
                Message.type != 2
            )
        ).scalar() or 0
        
        # 已回复的消息
        replied_messages = db.query(func.count(func.distinct(Message.parent_message_id))).filter(
            and_(
                Message.sender_id == user_id,
                Message.parent_message_id.isnot(None)
            )
        ).scalar() or 0
        
        return {
            "received_messages": received_messages,
            "replied_messages": replied_messages,
            "response_rate": (replied_messages / received_messages * 100) if received_messages > 0 else 0
        }
    
    def get_message_activity_trend(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取消息活动趋势"""
        start_date = datetime.now() - timedelta(days=days)
        
        # 按周统计
        weekly_stats = db.query(
            func.extract('week', Message.create_time).label('week'),
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.receiver_id == user_id,
                Message.create_time >= start_date
            )
        ).group_by(func.extract('week', Message.create_time)).all()
        
        # 按小时统计（一天中的活跃时段）
        hourly_stats = db.query(
            func.extract('hour', Message.create_time).label('hour'),
            func.count(Message.id).label('count')
        ).filter(
            and_(
                Message.receiver_id == user_id,
                Message.create_time >= start_date
            )
        ).group_by(func.extract('hour', Message.create_time)).all()
        
        return {
            "weekly_trend": [
                {"week": int(stat.week), "count": stat.count}
                for stat in weekly_stats
            ],
            "hourly_distribution": [
                {"hour": int(stat.hour), "count": stat.count}
                for stat in hourly_stats
            ]
        }

# 创建CRUD实例
crud_message_stat = CRUDMessageStat() 