from sqlalchemy import Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Date, SmallInteger, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from core.database import Base
import enum


class TaskCategory(str, enum.Enum):
    STUDY = "study"
    WORK = "work"
    LIFE = "life"
    OTHER = "other"

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in-progress"
    COMPLETED = "completed"
    EMPTY = "empty"
    CANCELLED = "cancelled"

class Task(Base):
    """任务模型"""
    __tablename__ = "task"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    type = Column(String(20), nullable=False)  # study, life, work
    category = Column(String(20))
    weekly_hours = Column(Numeric(5, 1), default=0.0)
    is_high_frequency = Column(SmallInteger, default=0)
    is_overcome = Column(SmallInteger, default=0)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    time_slots = relationship("TimeSlot", back_populates="task")
    subtasks = relationship("Subtask", back_populates="task")

class Subtask(Base):
    """子任务模型"""
    __tablename__ = "subtask"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("task.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    hours = Column(Numeric(5, 1), default=0.0)
    is_high_frequency = Column(SmallInteger, default=0)
    is_overcome = Column(SmallInteger, default=0)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    task = relationship("Task", back_populates="subtasks")

class TimeSlot(Base):
    """时间段模型"""
    __tablename__ = "time_slot"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False)
    time_range = Column(String(20), nullable=False)  # 格式：07:30-08:30
    task_id = Column(Integer, ForeignKey("task.id", ondelete="SET NULL"), nullable=True)
    subtask_id = Column(Integer, ForeignKey("subtask.id", ondelete="SET NULL"), nullable=True)
    status = Column(String(20), default='pending')  # completed, in-progress, pending, empty
    is_ai_recommended = Column(SmallInteger, default=0)
    note = Column(Text)
    ai_tip = Column(Text)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    task = relationship("Task", back_populates="time_slots", foreign_keys=[task_id])
    subtask = relationship("Subtask", foreign_keys=[subtask_id])
    mood_record = relationship("MoodRecord", back_populates="time_slot", uselist=False)

class MoodRecord(Base):
    """心情记录模型"""
    __tablename__ = "mood_record"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    time_slot_id = Column(Integer, ForeignKey("time_slot.id", ondelete="CASCADE"), nullable=False, unique=True)
    mood = Column(String(20), nullable=False)  # happy, focused, tired, stressed, excited
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    time_slot = relationship("TimeSlot", back_populates="mood_record") 