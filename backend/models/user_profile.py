from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, DECIMAL, Integer, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class UserProfile(Base):
    """用户个人信息表"""
    __tablename__ = "user_profile"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    username = Column(String(50), nullable=False)
    nickname = Column(String(100), nullable=True)
    avatar = Column(String(500), nullable=True)
    email = Column(String(100), nullable=True)
    phone = Column(String(20), nullable=True)
    
    # 个人目标和描述
    goal = Column(Text, nullable=True)  # 学习目标
    bio = Column(Text, nullable=True)   # 个人简介
    
    # 个人设置
    is_public = Column(SmallInteger, default=1)  # 是否公开个人信息
    allow_follow = Column(SmallInteger, default=1)  # 是否允许被关注
    
    # 统计字段（冗余存储，提高查询性能）
    total_study_hours = Column(DECIMAL(10,1), default=0.0)  # 总学习时长
    total_moments = Column(Integer, default=0)  # 发布动态数
    total_badges = Column(Integer, default=0)   # 获得徽章数
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserAsset(Base):
    """用户资产表"""
    __tablename__ = "user_asset"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    diamond_count = Column(Integer, default=0)  # 钻石数量
    total_recharge = Column(DECIMAL(10,2), default=0.00)  # 总充值金额
    total_consume = Column(Integer, default=0)  # 总消费钻石数
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserAssetRecord(Base):
    """用户资产记录表"""
    __tablename__ = "user_asset_record"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    record_type = Column(String(20), nullable=False)  # 'recharge', 'consume', 'reward'
    amount = Column(Integer, nullable=False)  # 变动数量（正数为增加，负数为减少）
    balance_after = Column(Integer, nullable=False)  # 变动后余额
    
    # 关联信息
    related_type = Column(String(20), nullable=True)  # 关联类型：'tutor_service', 'shop_item'等
    related_id = Column(BigInteger, nullable=True)    # 关联ID
    description = Column(String(200), nullable=True)  # 记录描述
    
    # 充值相关
    order_id = Column(String(100), nullable=True)     # 充值订单号
    payment_method = Column(String(20), nullable=True) # 支付方式
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class UserRelation(Base):
    """用户关系表"""
    __tablename__ = "user_relation"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)      # 关注者
    target_id = Column(BigInteger, nullable=False, index=True)    # 被关注者
    relation_type = Column(String(20), nullable=False)           # 'follow_tutor', 'follow_user'
    status = Column(String(20), default='active')                # 'active', 'cancelled'
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 唯一约束：同一用户对同一目标只能有一种关系类型
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )

class RechargeOrder(Base):
    """充值订单表"""
    __tablename__ = "recharge_order"
    
    id = Column(BigInteger, primary_key=True, index=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    
    # 订单信息
    amount = Column(DECIMAL(10,2), nullable=False)    # 充值金额
    diamond_count = Column(Integer, nullable=False)   # 获得钻石数
    payment_method = Column(String(20), nullable=True) # 支付方式
    
    # 订单状态
    status = Column(String(20), default='pending')    # 'pending', 'paid', 'failed', 'cancelled'
    
    # 支付信息
    payment_id = Column(String(100), nullable=True)   # 第三方支付ID
    payment_url = Column(String(500), nullable=True)  # 支付链接
    paid_time = Column(DateTime(timezone=True), nullable=True)
    
    # 时间信息
    expire_time = Column(DateTime(timezone=True), nullable=True)  # 订单过期时间
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class UserSetting(Base):
    """用户设置表"""
    __tablename__ = "user_setting"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    
    # 隐私设置
    profile_visibility = Column(String(20), default='public')    # 'public', 'friends', 'private'
    allow_follow = Column(SmallInteger, default=1)               # 是否允许被关注
    show_study_stats = Column(SmallInteger, default=1)           # 是否显示学习统计
    
    # 通知设置
    email_notification = Column(SmallInteger, default=1)         # 邮件通知
    push_notification = Column(SmallInteger, default=1)          # 推送通知
    
    # 其他设置
    theme = Column(String(20), default='light')                  # 主题：'light', 'dark'
    language = Column(String(10), default='zh-CN')               # 语言
    timezone = Column(String(50), default='Asia/Shanghai')       # 时区
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 