from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举类型
class TaskType(str, Enum):
    STUDY = "study"
    LIFE = "life"
    WORK = "work"

class TaskStatus(str, Enum):
    COMPLETED = "completed"
    IN_PROGRESS = "in-progress"
    PENDING = "pending"
    EMPTY = "empty"

class MoodType(str, Enum):
    HAPPY = "happy"
    FOCUSED = "focused"
    TIRED = "tired"
    STRESSED = "stressed"
    EXCITED = "excited"

# 子任务模型
class SubtaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="子任务名称")
    hours: float = Field(0.0, ge=0, le=24, description="预计时长（小时）")
    is_high_frequency: bool = Field(False, description="是否高频任务")
    is_overcome: bool = Field(False, description="是否待克服任务")

class SubtaskCreate(SubtaskBase):
    pass

class SubtaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    hours: Optional[float] = Field(None, ge=0, le=24)
    is_high_frequency: Optional[bool] = None
    is_overcome: Optional[bool] = None

class SubtaskResponse(SubtaskBase):
    id: int
    task_id: int
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

# 任务模型
class TaskBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    type: TaskType = Field(..., description="任务类型")
    category: Optional[str] = Field(None, max_length=20, description="任务分类")
    weekly_hours: float = Field(0.0, ge=0, le=168, description="本周时长")
    is_high_frequency: bool = Field(False, description="是否高频任务")
    is_overcome: bool = Field(False, description="是否待克服任务")

class TaskCreate(TaskBase):
    subtasks: List[SubtaskCreate] = Field([], description="子任务列表")

class TaskUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    type: Optional[TaskType] = None
    category: Optional[str] = Field(None, max_length=20)
    weekly_hours: Optional[float] = Field(None, ge=0, le=168)
    is_high_frequency: Optional[bool] = None
    is_overcome: Optional[bool] = None

class TaskResponse(TaskBase):
    id: int
    user_id: int
    subtasks: List[SubtaskResponse] = Field([], description="子任务列表")
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

class TaskListResponse(BaseModel):
    """任务列表响应"""
    tasks: List[TaskResponse] = Field(..., description="任务列表")
    total: int = Field(..., description="总任务数")
    high_frequency_count: int = Field(0, description="高频任务数")
    overcome_count: int = Field(0, description="待克服任务数")

# 快捷创建任务
class TaskQuickCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    type: Optional[TaskType] = Field(TaskType.STUDY, description="任务类型，默认为学习")
    category: Optional[str] = Field(None, max_length=20, description="任务分类")

# 时间段相关模型
class TimeSlotBase(BaseModel):
    date: datetime = Field(..., description="日期")
    time_range: str = Field(..., description="时间段，如'07:30-08:30'")
    status: TaskStatus = Field(TaskStatus.PENDING, description="状态")
    note: Optional[str] = Field(None, description="备注")
    ai_tip: Optional[str] = Field(None, description="AI提示")

class TimeSlotCreate(TimeSlotBase):
    task_id: Optional[int] = Field(None, description="关联任务ID")
    subtask_id: Optional[int] = Field(None, description="关联子任务ID")

class TimeSlotUpdate(BaseModel):
    task_id: Optional[int] = None
    subtask_id: Optional[int] = None
    status: Optional[TaskStatus] = None
    note: Optional[str] = None
    ai_tip: Optional[str] = None

class TimeSlotResponse(TimeSlotBase):
    id: int
    user_id: int
    task_id: Optional[int] = None
    subtask_id: Optional[int] = None
    is_ai_recommended: bool = False
    task: Optional[TaskResponse] = None
    subtask: Optional[SubtaskResponse] = None
    mood: Optional[str] = None  # 从关联的心情记录获取
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

class TodayTimeSlotResponse(BaseModel):
    """今日时间表响应"""
    time_slots: List[TimeSlotResponse] = Field(..., description="时间段列表")
    total_slots: int = Field(..., description="总时间段数")
    completed_slots: int = Field(0, description="已完成时间段数")
    completion_rate: float = Field(0.0, description="完成率")

# 心情记录模型
class MoodCreate(BaseModel):
    time_slot_id: int = Field(..., description="时间段ID")
    mood: MoodType = Field(..., description="心情类型")

class MoodResponse(BaseModel):
    id: int
    user_id: int
    time_slot_id: int
    mood: MoodType
    create_time: datetime
    
    class Config:
        from_attributes = True

# 任务绑定到时间段
class TaskSlotBinding(BaseModel):
    task_id: Optional[int] = Field(None, description="任务ID")
    subtask_id: Optional[int] = Field(None, description="子任务ID")

# 通用响应模型
class TaskOperationResponse(BaseModel):
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据") 