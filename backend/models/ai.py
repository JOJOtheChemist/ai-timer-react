from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, DECIMAL, JSON, Integer
from sqlalchemy.sql import func
from core.database import Base

class AIChatRecord(Base):
    """AI聊天记录表"""
    __tablename__ = "ai_chat_record"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    session_id = Column(String(100), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # 'user' or 'ai'
    content = Column(Text, nullable=False)
    is_analysis = Column(SmallInteger, default=0)  # 0-否，1-是
    analysis_tags = Column(JSON, nullable=True)
    related_data = Column(JSON, nullable=True)
    token_count = Column(Integer, default=0)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class AIAnalysisRecord(Base):
    """AI分析记录表"""
    __tablename__ = "ai_analysis_record"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    analysis_type = Column(String(20), nullable=False)  # 'schedule', 'habit', 'progress', 'efficiency'
    analysis_tags = Column(JSON, default=[])
    analysis_content = Column(Text, nullable=False)
    analysis_data = Column(JSON, nullable=True)
    confidence_score = Column(DECIMAL(3,2), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    expire_time = Column(DateTime(timezone=True), nullable=True)

class AIRecommendation(Base):
    """AI推荐表"""
    __tablename__ = "ai_recommendation"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    rec_type = Column(String(20), nullable=False)  # 'method', 'case', 'tutor', 'schedule', 'task'
    related_id = Column(BigInteger, nullable=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    priority = Column(Integer, default=1)  # 1-5优先级
    is_accepted = Column(SmallInteger, default=0)  # 0-未处理，1-采纳，2-拒绝
    feedback = Column(Text, nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    expire_time = Column(DateTime(timezone=True), nullable=True) 