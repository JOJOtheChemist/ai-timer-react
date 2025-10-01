from sqlalchemy import Column, BigInteger, String, DateTime, DECIMAL, Integer, JSON
from sqlalchemy.sql import func
from core.database import Base

class StatisticWeekly(Base):
    """周统计表"""
    __tablename__ = "statistic_weekly"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    year_week = Column(String(20), nullable=False)  # 年周，如"2025-38"
    total_study_hours = Column(DECIMAL(10,1), default=0.0)
    high_freq_complete = Column(String(20), default='0/0')  # 高频任务完成情况，如"4/5"
    overcome_complete = Column(String(20), default='0/0')  # 待克服任务完成情况，如"1/2"
    ai_accept_rate = Column(Integer, default=0)  # AI推荐采纳率
    category_hours = Column(JSON, default={})  # 各类型时长，如{"学习":8.5,"生活":5,"工作":4}
    mood_distribution = Column(JSON, default={})  # 心情分布统计
    efficiency_score = Column(DECIMAL(3,1), nullable=True)  # 效率评分
    improvement_rate = Column(DECIMAL(5,2), nullable=True)  # 相比上周的改进率
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class StatisticDaily(Base):
    """日统计表"""
    __tablename__ = "statistic_daily"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    date = Column(DateTime(timezone=True), nullable=False)
    total_study_hours = Column(DECIMAL(5,1), default=0.0)
    completed_tasks = Column(Integer, default=0)
    total_tasks = Column(Integer, default=0)
    completion_rate = Column(DECIMAL(5,2), default=0.0)
    focus_time = Column(DECIMAL(5,1), default=0.0)  # 专注时长
    break_time = Column(DECIMAL(5,1), default=0.0)  # 休息时长
    dominant_mood = Column(String(20), nullable=True)  # 主要心情
    category_hours = Column(JSON, default={})  # 各类型时长分布
    create_time = Column(DateTime(timezone=True), server_default=func.now()) 