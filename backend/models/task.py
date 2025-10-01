from sqlalchemy import Column, Integer, String, Float, Text, DateTime, Date, Time, Enum, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum

class TaskCategory(str, enum.Enum):
    """任务分类枚举"""
    STUDY = "study"
    WORK = "work"
    REST = "rest"
    EXERCISE = "exercise"
    OTHER = "other"

class TaskStatus(str, enum.Enum):
    """任务状态枚举"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class Task(Base):
    """任务模型"""
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), default=TaskCategory.STUDY.value)
    status = Column(String(50), default=TaskStatus.PENDING.value)
    priority = Column(Integer, default=3)  # 1-5
    estimated_hours = Column(Float, default=1.0)
    actual_hours = Column(Float)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    deadline = Column(DateTime)
    is_recurring = Column(Boolean, default=False)
    recurring_pattern = Column(String(100))
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    time_slots = relationship("TimeSlot", back_populates="task")

class TimeSlot(Base):
    """时间段模型"""
    __tablename__ = "time_slots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(String(50), default=TaskCategory.STUDY.value)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer)
    is_completed = Column(Boolean, default=False)
    completion_rate = Column(Float, default=0.0)  # 0-100
    mood = Column(String(50))  # happy, neutral, sad, etc.
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # 关系
    task = relationship("Task", back_populates="time_slots")

class MoodRecord(Base):
    """心情记录模型"""
    __tablename__ = "mood_records"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    time_slot_id = Column(Integer, ForeignKey("time_slots.id"), nullable=True)
    mood_type = Column(String(50), nullable=False)  # happy, sad, anxious, calm, energetic, tired, etc.
    intensity = Column(Integer, default=3)  # 1-5
    note = Column(Text)
    recorded_at = Column(DateTime, server_default=func.now(), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now()) 