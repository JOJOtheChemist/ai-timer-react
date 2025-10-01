from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, Integer, DateTime, JSON
from sqlalchemy.sql import func
from core.database import Base


class SuccessCase(Base):
    """成功案例表"""
    __tablename__ = "success_case"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    title = Column(String(200), nullable=False)
    icon = Column(String(20), default='📚')
    duration = Column(String(20), nullable=False)
    tags = Column(JSON, default=[])
    author_name = Column(String(50), nullable=False)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    collect_count = Column(Integer, default=0)
    is_hot = Column(SmallInteger, default=0)  # 0-否，1-是
    preview_days = Column(Integer, default=3)
    price = Column(String(20))
    content = Column(Text, nullable=False)
    summary = Column(Text)
    difficulty_level = Column(SmallInteger, default=1)  # 1-5
    category = Column(String(50))
    status = Column(SmallInteger, default=0)  # 0-草稿，1-已发布，2-已下架
    admin_review_note = Column(Text)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now())
    publish_time = Column(DateTime(timezone=True))


class CasePurchase(Base):
    """案例购买记录表"""
    __tablename__ = "case_purchase"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    case_id = Column(BigInteger, nullable=False, index=True)
    amount = Column(Integer, nullable=False)  # 购买金额（钻石数）
    purchase_type = Column(SmallInteger, default=0)  # 0-钻石购买，1-其他
    expire_time = Column(DateTime(timezone=True))
    create_time = Column(DateTime(timezone=True), server_default=func.now())


class CaseInteraction(Base):
    """案例交互记录表"""
    __tablename__ = "case_interaction"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    case_id = Column(BigInteger, nullable=False, index=True)
    interaction_type = Column(SmallInteger, nullable=False)  # 1-查看，2-点赞，3-收藏
    create_time = Column(DateTime(timezone=True), server_default=func.now()) 