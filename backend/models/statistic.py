from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, Integer, DateTime, DECIMAL, JSON
from sqlalchemy.sql import func
from core.database import Base

class StatisticDaily(Base):
    """每日统计表"""
    __tablename__ = "statistic_daily"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    stat_date = Column(String(10), nullable=False)  # YYYY-MM-DD
    total_hours = Column(DECIMAL(5,2), default=0.0)
    completed_tasks = Column(Integer, default=0)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class StatisticWeekly(Base):
    """每周统计表"""
    __tablename__ = "statistic_weekly"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    year_week = Column(String(10), nullable=False)  # YYYY-WW
    total_hours = Column(DECIMAL(5,2), default=0.0)
    completed_tasks = Column(Integer, default=0)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class StudyMethod(Base):
    """学习方法表"""
    __tablename__ = "study_method"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    category = Column(String(20), nullable=False)  # 'common' or 'tutor'
    type = Column(String(20))
    description = Column(Text, nullable=False)
    steps = Column(JSON, nullable=False)
    scene = Column(String(200))
    tutor_id = Column(BigInteger)
    checkin_count = Column(Integer, default=0)
    rating = Column(DECIMAL(2,1), default=0.0)
    review_count = Column(Integer, default=0)
    status = Column(SmallInteger, default=0)  # 0-隐藏，1-显示
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now()) 