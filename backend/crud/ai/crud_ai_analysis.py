from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from typing import List, Optional
from datetime import datetime, timedelta

from models.ai import AIAnalysisRecord
from models.schemas.ai import AnalysisType

class CRUDAIAnalysisRecord:
    """AI分析记录CRUD操作"""
    
    def create_analysis_record(
        self,
        db: Session,
        user_id: int,
        analysis_type: AnalysisType,
        analysis_content: str,
        analysis_tags: Optional[List[str]] = None,
        analysis_data: Optional[dict] = None,
        confidence_score: Optional[float] = None,
        expire_hours: int = 24
    ) -> AIAnalysisRecord:
        """创建分析记录"""
        expire_time = datetime.now() + timedelta(hours=expire_hours)
        
        db_record = AIAnalysisRecord(
            user_id=user_id,
            analysis_type=analysis_type.value,
            analysis_content=analysis_content,
            analysis_tags=analysis_tags or [],
            analysis_data=analysis_data,
            confidence_score=confidence_score,
            expire_time=expire_time
        )
        db.add(db_record)
        db.commit()
        db.refresh(db_record)
        return db_record
    
    def get_latest_analysis(
        self,
        db: Session,
        user_id: int,
        analysis_type: AnalysisType
    ) -> Optional[AIAnalysisRecord]:
        """获取用户最新的有效分析记录"""
        now = datetime.now()
        
        return db.query(AIAnalysisRecord).filter(
            and_(
                AIAnalysisRecord.user_id == user_id,
                AIAnalysisRecord.analysis_type == analysis_type.value,
                AIAnalysisRecord.expire_time > now
            )
        ).order_by(desc(AIAnalysisRecord.create_time)).first()
    
    def get_user_analysis_history(
        self,
        db: Session,
        user_id: int,
        analysis_type: Optional[AnalysisType] = None,
        days: int = 30,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[List[AIAnalysisRecord], int]:
        """获取用户分析历史"""
        start_time = datetime.now() - timedelta(days=days)
        
        query = db.query(AIAnalysisRecord).filter(
            and_(
                AIAnalysisRecord.user_id == user_id,
                AIAnalysisRecord.create_time >= start_time
            )
        )
        
        if analysis_type:
            query = query.filter(AIAnalysisRecord.analysis_type == analysis_type.value)
        
        # 获取总数
        total = query.count()
        
        # 分页查询
        records = query.order_by(desc(AIAnalysisRecord.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size)\
                      .all()
        
        return records, total
    
    def delete_expired_records(
        self,
        db: Session
    ) -> int:
        """删除过期的分析记录"""
        now = datetime.now()
        
        deleted_count = db.query(AIAnalysisRecord).filter(
            AIAnalysisRecord.expire_time <= now
        ).delete()
        
        db.commit()
        return deleted_count
    
    def update_analysis_data(
        self,
        db: Session,
        record_id: int,
        analysis_data: dict
    ) -> Optional[AIAnalysisRecord]:
        """更新分析数据"""
        record = db.query(AIAnalysisRecord).filter(
            AIAnalysisRecord.id == record_id
        ).first()
        
        if record:
            record.analysis_data = analysis_data
            db.commit()
            db.refresh(record)
        
        return record
    
    def get_analysis_stats(
        self,
        db: Session,
        user_id: int,
        days: int = 30
    ) -> dict:
        """获取用户分析统计"""
        start_time = datetime.now() - timedelta(days=days)
        
        # 按类型统计分析次数
        type_stats = db.query(
            AIAnalysisRecord.analysis_type,
            db.func.count(AIAnalysisRecord.id).label('count')
        ).filter(
            and_(
                AIAnalysisRecord.user_id == user_id,
                AIAnalysisRecord.create_time >= start_time
            )
        ).group_by(AIAnalysisRecord.analysis_type).all()
        
        # 平均置信度
        avg_confidence = db.query(
            db.func.avg(AIAnalysisRecord.confidence_score)
        ).filter(
            and_(
                AIAnalysisRecord.user_id == user_id,
                AIAnalysisRecord.create_time >= start_time,
                AIAnalysisRecord.confidence_score.isnot(None)
            )
        ).scalar()
        
        return {
            "type_stats": {stat.analysis_type: stat.count for stat in type_stats},
            "avg_confidence": float(avg_confidence) if avg_confidence else None,
            "total_analyses": sum(stat.count for stat in type_stats)
        }

# 创建CRUD实例
crud_ai_analysis = CRUDAIAnalysisRecord() 