from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from crud.schedule.crud_time_slot import crud_time_slot, crud_mood_record
from models.schemas.schedule import (
    TodayScheduleResponse, TimeSlotDetail, ScheduleOverview
)
from models.schemas.task import (
    TimeSlotCreate, TimeSlotUpdate, MoodCreate, TaskSlotBinding,
    TimeSlotResponse, MoodResponse, TaskStatus, MoodType
)

class TimeSlotService:
    """时间段服务"""
    
    def get_today_time_slots(self, db: Session, user_id: int, target_date: Optional[date] = None) -> TodayScheduleResponse:
        """获取今日时间表"""
        if target_date is None:
            target_date = date.today()
        
        # 获取时间段数据
        time_slots = crud_time_slot.get_today_by_user(db=db, user_id=user_id, target_date=target_date)
        
        # 转换为详细响应模型
        slot_details = []
        for slot in time_slots:
            # 获取心情
            mood = None
            mood_emoji = None
            if slot.mood_record:
                mood = slot.mood_record.mood
                mood_emoji = self._get_mood_emoji(mood)
            
            # 获取任务信息
            task_name = slot.task.name if slot.task else None
            subtask_name = slot.subtask.name if slot.subtask else None
            task_type = slot.task.type if slot.task else None
            is_high_frequency = bool(slot.task.is_high_frequency) if slot.task else False
            is_overcome = bool(slot.task.is_overcome) if slot.task else False
            
            slot_detail = TimeSlotDetail(
                id=slot.id,
                user_id=slot.user_id,
                date=slot.date,
                time_range=slot.time_range,
                task_id=slot.task_id,
                subtask_id=slot.subtask_id,
                status=TaskStatus(slot.status),
                note=slot.note,
                ai_tip=slot.ai_tip,
                is_ai_recommended=bool(slot.is_ai_recommended),
                task=None,  # 避免循环引用，使用单独字段
                subtask=None,
                mood=mood,
                create_time=slot.create_time,
                update_time=slot.update_time,
                # 扩展字段
                task_name=task_name,
                subtask_name=subtask_name,
                task_type=task_type,
                is_high_frequency=is_high_frequency,
                is_overcome=is_overcome,
                mood_emoji=mood_emoji
            )
            slot_details.append(slot_detail)
        
        # 计算概览统计
        overview = self._calculate_overview(slot_details, target_date)
        
        # 获取心情统计
        mood_summary = crud_mood_record.get_mood_statistics(
            db=db, user_id=user_id, start_date=target_date, end_date=target_date
        )
        
        # 获取AI推荐
        ai_recommendations = self._get_ai_recommendations(db, user_id, target_date)
        
        return TodayScheduleResponse(
            overview=overview,
            time_slots=slot_details,
            mood_summary=mood_summary.get("mood_distribution", {}),
            ai_recommendations=ai_recommendations
        )
    
    def save_mood_record(self, db: Session, user_id: int, slot_id: int, mood: MoodType) -> MoodResponse:
        """保存时段心情"""
        mood_data = MoodCreate(time_slot_id=slot_id, mood=mood)
        db_mood = crud_mood_record.create_mood_record(db=db, user_id=user_id, mood_data=mood_data)
        
        return MoodResponse(
            id=db_mood.id,
            user_id=db_mood.user_id,
            time_slot_id=db_mood.time_slot_id,
            mood=MoodType(db_mood.mood),
            create_time=db_mood.create_time
        )
    
    def add_task_to_slot(self, db: Session, user_id: int, slot_id: int, task_id: int, subtask_id: Optional[int] = None) -> Optional[TimeSlotResponse]:
        """为时段绑定任务"""
        db_slot = crud_time_slot.add_task_to_slot(
            db=db, user_id=user_id, slot_id=slot_id, task_id=task_id, subtask_id=subtask_id
        )
        
        if not db_slot:
            return None
        
        return self._convert_to_response(db_slot)
    
    def update_time_slot(self, db: Session, slot_id: int, user_id: int, slot_data: TimeSlotUpdate) -> Optional[TimeSlotResponse]:
        """更新时间段"""
        db_slot = crud_time_slot.update(db=db, slot_id=slot_id, user_id=user_id, slot_data=slot_data)
        
        if not db_slot:
            return None
        
        return self._convert_to_response(db_slot)
    
    def create_time_slot(self, db: Session, user_id: int, slot_data: TimeSlotCreate) -> TimeSlotResponse:
        """创建时间段"""
        db_slot = crud_time_slot.create(db=db, user_id=user_id, slot_data=slot_data)
        return self._convert_to_response(db_slot)
    
    def batch_update_status(self, db: Session, user_id: int, slot_ids: List[int], status: TaskStatus) -> int:
        """批量更新时间段状态"""
        return crud_time_slot.batch_update_status(db=db, user_id=user_id, slot_ids=slot_ids, status=status)
    
    def get_completion_stats(self, db: Session, user_id: int, target_date: Optional[date] = None) -> Dict[str, Any]:
        """获取完成情况统计"""
        return crud_time_slot.get_completion_stats(db=db, user_id=user_id, target_date=target_date)
    
    def get_ai_recommended_slots(self, db: Session, user_id: int, target_date: Optional[date] = None) -> List[TimeSlotResponse]:
        """获取AI推荐的时间段"""
        slots = crud_time_slot.get_ai_recommended_slots(db=db, user_id=user_id, target_date=target_date)
        return [self._convert_to_response(slot) for slot in slots]
    
    def _convert_to_response(self, db_slot) -> TimeSlotResponse:
        """转换为响应模型"""
        mood = None
        if db_slot.mood_record:
            mood = db_slot.mood_record.mood
        
        return TimeSlotResponse(
            id=db_slot.id,
            user_id=db_slot.user_id,
            date=db_slot.date,
            time_range=db_slot.time_range,
            task_id=db_slot.task_id,
            subtask_id=db_slot.subtask_id,
            status=TaskStatus(db_slot.status),
            note=db_slot.note,
            ai_tip=db_slot.ai_tip,
            is_ai_recommended=bool(db_slot.is_ai_recommended),
            task=None,  # 避免循环引用
            subtask=None,
            mood=mood,
            create_time=db_slot.create_time,
            update_time=db_slot.update_time
        )
    
    def _calculate_overview(self, slot_details: List[TimeSlotDetail], target_date: date) -> ScheduleOverview:
        """计算时间表概览"""
        total_slots = len(slot_details)
        completed_slots = len([s for s in slot_details if s.status == TaskStatus.COMPLETED])
        in_progress_slots = len([s for s in slot_details if s.status == TaskStatus.IN_PROGRESS])
        pending_slots = len([s for s in slot_details if s.status == TaskStatus.PENDING])
        empty_slots = len([s for s in slot_details if s.status == TaskStatus.EMPTY])
        
        completion_rate = (completed_slots / total_slots * 100) if total_slots > 0 else 0.0
        
        # 计算总学习时长（假设每个完成的时间段为1小时）
        total_study_hours = float(completed_slots)
        
        return ScheduleOverview(
            date=target_date,
            total_slots=total_slots,
            completed_slots=completed_slots,
            in_progress_slots=in_progress_slots,
            pending_slots=pending_slots,
            empty_slots=empty_slots,
            completion_rate=completion_rate,
            total_study_hours=total_study_hours
        )
    
    def _get_mood_emoji(self, mood: str) -> str:
        """获取心情对应的表情"""
        mood_emojis = {
            "happy": "😊",
            "focused": "🎯",
            "tired": "😴",
            "stressed": "😰",
            "excited": "🤩"
        }
        return mood_emojis.get(mood, "😐")
    
    def _get_ai_recommendations(self, db: Session, user_id: int, target_date: date) -> List[Dict[str, Any]]:
        """获取AI推荐（简化实现）"""
        # 这里可以集成AI推荐逻辑
        # 目前返回模拟数据
        return [
            {
                "type": "task_suggestion",
                "title": "建议在上午安排高难度任务",
                "description": "根据你的学习习惯，上午时段专注度更高",
                "priority": 1
            },
            {
                "type": "break_reminder",
                "title": "记得适当休息",
                "description": "连续学习2小时后建议休息15分钟",
                "priority": 2
            }
        ]

# 创建服务实例
time_slot_service = TimeSlotService() 