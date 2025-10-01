from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, cast, Date
from typing import List, Optional
from datetime import datetime, date, timedelta

from models.task import TimeSlot, MoodRecord, Task, Subtask
from models.schemas.task import TimeSlotCreate, TimeSlotUpdate, MoodCreate, TaskStatus

class CRUDTimeSlot:
    """时间段CRUD操作"""
    
    def create(self, db: Session, user_id: int, slot_data: TimeSlotCreate) -> TimeSlot:
        """创建时间段"""
        db_slot = TimeSlot(
            user_id=user_id,
            date=slot_data.date,
            time_range=slot_data.time_range,
            task_id=slot_data.task_id,
            subtask_id=slot_data.subtask_id,
            status=slot_data.status.value,
            note=slot_data.note,
            ai_tip=slot_data.ai_tip
        )
        db.add(db_slot)
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    def get_today_by_user(self, db: Session, user_id: int, target_date: Optional[date] = None) -> List[TimeSlot]:
        """获取用户今日时间段"""
        if target_date is None:
            target_date = date.today()
        
        return db.query(TimeSlot).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) == target_date
            )
        ).options(
            joinedload(TimeSlot.task),
            joinedload(TimeSlot.subtask),
            joinedload(TimeSlot.mood_record)
        ).order_by(TimeSlot.time_range).all()
    
    def get_by_date_range(
        self, 
        db: Session, 
        user_id: int, 
        start_date: date, 
        end_date: date
    ) -> List[TimeSlot]:
        """获取日期范围内的时间段"""
        return db.query(TimeSlot).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date
            )
        ).options(
            joinedload(TimeSlot.task),
            joinedload(TimeSlot.subtask),
            joinedload(TimeSlot.mood_record)
        ).order_by(TimeSlot.date, TimeSlot.time_range).all()
    
    def get_by_id(self, db: Session, slot_id: int, user_id: int) -> Optional[TimeSlot]:
        """根据ID获取时间段"""
        return db.query(TimeSlot).filter(
            and_(
                TimeSlot.id == slot_id,
                TimeSlot.user_id == user_id
            )
        ).options(
            joinedload(TimeSlot.task),
            joinedload(TimeSlot.subtask),
            joinedload(TimeSlot.mood_record)
        ).first()
    
    def update(self, db: Session, slot_id: int, user_id: int, slot_data: TimeSlotUpdate) -> Optional[TimeSlot]:
        """更新时间段"""
        db_slot = self.get_by_id(db, slot_id, user_id)
        if not db_slot:
            return None
        
        update_data = slot_data.dict(exclude_unset=True)
        
        # 处理枚举类型
        if 'status' in update_data and update_data['status']:
            update_data['status'] = update_data['status'].value
        
        for field, value in update_data.items():
            setattr(db_slot, field, value)
        
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    def update_slot_task(self, db: Session, slot_id: int, task_id: Optional[int], subtask_id: Optional[int] = None) -> Optional[TimeSlot]:
        """更新时间段绑定的任务"""
        db_slot = db.query(TimeSlot).filter(TimeSlot.id == slot_id).first()
        if not db_slot:
            return None
        
        db_slot.task_id = task_id
        db_slot.subtask_id = subtask_id
        
        db.commit()
        db.refresh(db_slot)
        return db_slot
    
    def add_task_to_slot(self, db: Session, user_id: int, slot_id: int, task_id: int, subtask_id: Optional[int] = None) -> Optional[TimeSlot]:
        """为时段绑定任务"""
        return self.update_slot_task(db, slot_id, task_id, subtask_id)
    
    def batch_update_status(self, db: Session, user_id: int, slot_ids: List[int], status: TaskStatus) -> int:
        """批量更新时间段状态"""
        updated_count = db.query(TimeSlot).filter(
            and_(
                TimeSlot.id.in_(slot_ids),
                TimeSlot.user_id == user_id
            )
        ).update({"status": status.value}, synchronize_session=False)
        
        db.commit()
        return updated_count
    
    def delete(self, db: Session, slot_id: int, user_id: int) -> bool:
        """删除时间段"""
        db_slot = self.get_by_id(db, slot_id, user_id)
        if not db_slot:
            return False
        
        db.delete(db_slot)
        db.commit()
        return True
    
    def get_completion_stats(self, db: Session, user_id: int, target_date: Optional[date] = None) -> dict:
        """获取完成情况统计"""
        if target_date is None:
            target_date = date.today()
        
        stats = db.query(
            TimeSlot.status,
            func.count(TimeSlot.id).label('count')
        ).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) == target_date
            )
        ).group_by(TimeSlot.status).all()
        
        result = {
            "completed": 0,
            "in_progress": 0,
            "pending": 0,
            "empty": 0,
            "total": 0
        }
        
        for stat in stats:
            status_key = stat.status.replace('-', '_')
            if status_key in result:
                result[status_key] = stat.count
            result["total"] += stat.count
        
        # 计算完成率
        if result["total"] > 0:
            result["completion_rate"] = (result["completed"] / result["total"]) * 100
        else:
            result["completion_rate"] = 0.0
        
        return result
    
    def get_ai_recommended_slots(self, db: Session, user_id: int, target_date: Optional[date] = None) -> List[TimeSlot]:
        """获取AI推荐的时间段"""
        if target_date is None:
            target_date = date.today()
        
        return db.query(TimeSlot).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) == target_date,
                TimeSlot.is_ai_recommended == 1
            )
        ).options(
            joinedload(TimeSlot.task),
            joinedload(TimeSlot.subtask)
        ).all()

class CRUDMoodRecord:
    """心情记录CRUD操作"""
    
    def create_mood_record(self, db: Session, user_id: int, mood_data: MoodCreate) -> MoodRecord:
        """创建心情记录"""
        # 检查是否已存在该时间段的心情记录
        existing_mood = db.query(MoodRecord).filter(
            MoodRecord.time_slot_id == mood_data.time_slot_id
        ).first()
        
        if existing_mood:
            # 更新现有记录
            existing_mood.mood = mood_data.mood.value
            db.commit()
            db.refresh(existing_mood)
            return existing_mood
        else:
            # 创建新记录
            db_mood = MoodRecord(
                user_id=user_id,
                time_slot_id=mood_data.time_slot_id,
                mood=mood_data.mood.value
            )
            db.add(db_mood)
            db.commit()
            db.refresh(db_mood)
            return db_mood
    
    def save_mood_record(self, db: Session, user_id: int, slot_id: int, mood: str) -> MoodRecord:
        """保存时段心情"""
        mood_data = MoodCreate(time_slot_id=slot_id, mood=mood)
        return self.create_mood_record(db, user_id, mood_data)
    
    def get_mood_by_date(self, db: Session, user_id: int, target_date: date) -> List[MoodRecord]:
        """获取指定日期的心情记录"""
        return db.query(MoodRecord).join(TimeSlot).filter(
            and_(
                MoodRecord.user_id == user_id,
                cast(TimeSlot.date, Date) == target_date
            )
        ).all()
    
    def get_mood_statistics(self, db: Session, user_id: int, start_date: date, end_date: date) -> dict:
        """获取心情统计"""
        stats = db.query(
            MoodRecord.mood,
            func.count(MoodRecord.id).label('count')
        ).join(TimeSlot).filter(
            and_(
                MoodRecord.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date
            )
        ).group_by(MoodRecord.mood).all()
        
        mood_distribution = {}
        total_records = 0
        
        for stat in stats:
            mood_distribution[stat.mood] = stat.count
            total_records += stat.count
        
        # 找出主要心情
        dominant_mood = None
        if mood_distribution:
            dominant_mood = max(mood_distribution, key=mood_distribution.get)
        
        return {
            "mood_distribution": mood_distribution,
            "dominant_mood": dominant_mood,
            "total_records": total_records
        }

# 创建CRUD实例
crud_time_slot = CRUDTimeSlot()
crud_mood_record = CRUDMoodRecord() 