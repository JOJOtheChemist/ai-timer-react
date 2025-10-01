from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from models.schemas.task import TimeSlotResponse, MoodType

# 时间表相关模型
class ScheduleOverview(BaseModel):
    """时间表概览"""
    date: date = Field(..., description="日期")
    total_slots: int = Field(..., description="总时间段数")
    completed_slots: int = Field(0, description="已完成时间段数")
    in_progress_slots: int = Field(0, description="进行中时间段数")
    pending_slots: int = Field(0, description="待开始时间段数")
    empty_slots: int = Field(0, description="空白时间段数")
    completion_rate: float = Field(0.0, description="完成率")
    total_study_hours: float = Field(0.0, description="总学习时长")

class TimeSlotDetail(TimeSlotResponse):
    """时间段详情（扩展版）"""
    task_name: Optional[str] = Field(None, description="任务名称")
    subtask_name: Optional[str] = Field(None, description="子任务名称")
    task_type: Optional[str] = Field(None, description="任务类型")
    is_high_frequency: bool = Field(False, description="是否高频任务")
    is_overcome: bool = Field(False, description="是否待克服任务")
    mood_emoji: Optional[str] = Field(None, description="心情表情")

class TodayScheduleResponse(BaseModel):
    """今日时间表完整响应"""
    overview: ScheduleOverview = Field(..., description="时间表概览")
    time_slots: List[TimeSlotDetail] = Field(..., description="时间段详情列表")
    mood_summary: Dict[str, int] = Field({}, description="心情统计")
    ai_recommendations: List[Dict[str, Any]] = Field([], description="AI推荐")

# 心情相关模型
class MoodStatistics(BaseModel):
    """心情统计"""
    date: date = Field(..., description="日期")
    mood_distribution: Dict[MoodType, int] = Field(..., description="心情分布")
    dominant_mood: Optional[MoodType] = Field(None, description="主要心情")
    total_records: int = Field(0, description="总记录数")

class WeeklyMoodTrend(BaseModel):
    """周心情趋势"""
    week_start: date = Field(..., description="周开始日期")
    daily_moods: List[MoodStatistics] = Field(..., description="每日心情统计")
    week_dominant_mood: Optional[MoodType] = Field(None, description="本周主要心情")

# 时间段操作相关
class TimeSlotBatchUpdate(BaseModel):
    """批量更新时间段"""
    slot_ids: List[int] = Field(..., description="时间段ID列表")
    status: Optional[str] = Field(None, description="状态")
    task_id: Optional[int] = Field(None, description="任务ID")
    subtask_id: Optional[int] = Field(None, description="子任务ID")

class TimeSlotBatchResponse(BaseModel):
    """批量操作响应"""
    success: bool = Field(True, description="操作是否成功")
    updated_count: int = Field(0, description="更新数量")
    failed_count: int = Field(0, description="失败数量")
    message: str = Field("操作完成", description="响应消息")

# 时间段模板
class TimeSlotTemplate(BaseModel):
    """时间段模板"""
    name: str = Field(..., description="模板名称")
    time_range: str = Field(..., description="时间段")
    task_id: Optional[int] = Field(None, description="默认任务ID")
    subtask_id: Optional[int] = Field(None, description="默认子任务ID")
    is_active: bool = Field(True, description="是否启用")

class ScheduleTemplate(BaseModel):
    """时间表模板"""
    name: str = Field(..., description="模板名称")
    description: Optional[str] = Field(None, description="模板描述")
    time_slots: List[TimeSlotTemplate] = Field(..., description="时间段模板列表")
    is_default: bool = Field(False, description="是否默认模板")

# 时间表生成
class ScheduleGenerateRequest(BaseModel):
    """生成时间表请求"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    template_id: Optional[int] = Field(None, description="使用的模板ID")
    include_weekends: bool = Field(True, description="是否包含周末")
    daily_start_time: str = Field("07:00", description="每日开始时间")
    daily_end_time: str = Field("23:00", description="每日结束时间")
    slot_duration: int = Field(60, description="时间段时长（分钟）")

class ScheduleGenerateResponse(BaseModel):
    """生成时间表响应"""
    success: bool = Field(True, description="生成是否成功")
    generated_days: int = Field(0, description="生成天数")
    total_slots: int = Field(0, description="总时间段数")
    message: str = Field("生成成功", description="响应消息")
    preview: List[TimeSlotDetail] = Field([], description="预览数据（前10个时间段）") 