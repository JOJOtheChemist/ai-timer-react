from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Badge(Base):
    """徽章表"""
    __tablename__ = "badge"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(500), nullable=False)  # 徽章图标URL
    
    # 徽章分类和等级
    category = Column(String(50), nullable=False)  # 'study', 'social', 'achievement'等
    level = Column(String(20), default='bronze')   # 'bronze', 'silver', 'gold', 'diamond'
    rarity = Column(String(20), default='common')  # 'common', 'rare', 'epic', 'legendary'
    
    # 获得条件
    unlock_condition = Column(JSON, nullable=False)  # 解锁条件（JSON格式）
    unlock_type = Column(String(20), nullable=False) # 'auto', 'manual', 'event'
    
    # 徽章属性
    is_active = Column(SmallInteger, default=1)      # 是否启用
    sort_order = Column(Integer, default=0)          # 排序权重
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    user_badges = relationship("UserBadge", back_populates="badge")

class UserBadge(Base):
    """用户徽章关联表"""
    __tablename__ = "user_badge"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    badge_id = Column(BigInteger, nullable=False, index=True)
    
    # 获得信息
    obtain_date = Column(DateTime(timezone=True), server_default=func.now())
    obtain_reason = Column(String(200), nullable=True)  # 获得原因
    
    # 展示设置
    is_displayed = Column(SmallInteger, default=1)      # 是否在个人页面展示
    display_order = Column(Integer, default=0)          # 展示顺序
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    badge = relationship("Badge", back_populates="user_badges")
    
    # 唯一约束：同一用户不能重复获得同一徽章
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )

class BadgeProgress(Base):
    """徽章进度表"""
    __tablename__ = "badge_progress"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    badge_id = Column(BigInteger, nullable=False, index=True)
    
    # 进度信息
    current_progress = Column(Integer, default=0)       # 当前进度
    target_progress = Column(Integer, nullable=False)   # 目标进度
    progress_data = Column(JSON, nullable=True)         # 进度详细数据
    
    # 状态
    status = Column(String(20), default='in_progress')  # 'in_progress', 'completed', 'failed'
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class BadgeCategory(Base):
    """徽章分类表"""
    __tablename__ = "badge_category"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    icon = Column(String(500), nullable=True)
    
    # 分类属性
    sort_order = Column(Integer, default=0)
    is_active = Column(SmallInteger, default=1)
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 