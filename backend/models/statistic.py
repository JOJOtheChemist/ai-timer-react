from sqlalchemy import Column, BigInteger, String, Integer, Date, DateTime, DECIMAL, NUMERIC
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from core.database import Base

class StatisticDaily(Base):
    """每日统计表"""
    __tablename__ = "statistic_daily"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    date = Column(Date, nullable=False)
    total_study_hours = Column(NUMERIC(5, 1), default=0.0)
    completed_tasks = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completion_rate = Column(NUMERIC(5, 2), default=0.0)
    focus_time = Column(NUMERIC(5, 1), default=0.0)
    break_time = Column(NUMERIC(5, 1), default=0.0)
    dominant_mood = Column(String(20))
    category_hours = Column(JSONB, default={})
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class StatisticWeekly(Base):
    """每周统计表"""
    __tablename__ = "statistic_weekly"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    year_week = Column(String(20), nullable=False)
    total_study_hours = Column(NUMERIC(10, 1), default=0.0)
    high_freq_complete = Column(String(20), default='0/0')
    overcome_complete = Column(String(20), default='0/0')
    ai_accept_rate = Column(Integer, default=0)
    category_hours = Column(JSONB, default={})
    mood_distribution = Column(JSONB, default={})
    efficiency_score = Column(NUMERIC(3, 1))
    improvement_rate = Column(NUMERIC(5, 2))
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class StudyMethod(Base):
    """学习方法表"""
    __tablename__ = "study_method"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)  # 'common' or 'tutor'
    type = Column(String(20))
    description = Column(String, nullable=False)
    steps = Column(JSONB, nullable=False)
    scene = Column(String(200))
    tutor_id = Column(BigInteger)
    checkin_count = Column(Integer, default=0)
    rating = Column(DECIMAL(2,1), default=0.0)
    review_count = Column(Integer, default=0)
    status = Column(Integer, default=0)  # 0-隐藏，1-显示
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now()) 