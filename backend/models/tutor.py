from sqlalchemy import Column, BigInteger, String, SmallInteger, Integer, Text, TIMESTAMP, Numeric
from sqlalchemy.sql import func
from core.database import Base

class Tutor(Base):
    """导师模型"""
    __tablename__ = "tutor"
    
    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(String(50), nullable=False)
    avatar = Column(String(255), nullable=True)
    type = Column(SmallInteger, default=0)  # 0=普通导师, 1=认证导师
    domain = Column(String(200), nullable=False)  # 擅长领域
    education = Column(String(200), nullable=True)  # 学历
    experience = Column(String(200), nullable=True)  # 经验
    work_experience = Column(Text, nullable=True)  # 工作经历
    philosophy = Column(Text, nullable=True)  # 教学理念
    rating = Column(Integer, default=0)  # 评分 (0-100)
    student_count = Column(Integer, default=0)  # 学生数量
    success_rate = Column(Integer, default=0)  # 成功率 (0-100)
    monthly_guide_count = Column(Integer, default=0)  # 月度指导次数
    status = Column(SmallInteger, default=0)  # 状态: 0=待审核, 1=正常, 2=禁用
    create_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    update_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class TutorService(Base):
    """导师服务模型"""
    __tablename__ = "tutor_service"
    
    id = Column(BigInteger, primary_key=True, index=True)
    tutor_id = Column(BigInteger, nullable=False, index=True)
    name = Column(String(100), nullable=False)
    price = Column(Integer, nullable=False)  # 价格（钻石）
    description = Column(Text, nullable=False)
    unit = Column(String(20), nullable=True)  # 单位
    service_type = Column(String(20), default='consultation')  # consultation/review/planning/correction
    estimated_hours = Column(Numeric(3, 1), nullable=True)  # 预计时长
    is_active = Column(SmallInteger, default=1)  # 0=停用, 1=启用
    sort_order = Column(Integer, default=0)  # 排序
    create_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    update_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp())


class TutorReview(Base):
    """导师评价模型"""
    __tablename__ = "tutor_review"
    
    id = Column(BigInteger, primary_key=True, index=True)
    tutor_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    reviewer_name = Column(String(50), nullable=False)
    rating = Column(Integer, nullable=False)  # 评分 1-5
    content = Column(Text, nullable=False)
    attachment = Column(String(200), nullable=True)
    service_id = Column(BigInteger, nullable=True, index=True)
    is_anonymous = Column(SmallInteger, default=0)  # 0=不匿名, 1=匿名
    create_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())


class TutorExpertise(Base):
    """导师专业领域模型"""
    __tablename__ = "tutor_expertise"
    
    id = Column(BigInteger, primary_key=True, index=True)
    tutor_id = Column(BigInteger, nullable=False, index=True)
    expertise_name = Column(String(50), nullable=False)
    proficiency_level = Column(SmallInteger, default=1)  # 1-5级
    create_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())


class TutorServiceOrder(Base):
    """导师服务订单模型"""
    __tablename__ = "tutor_service_order"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    tutor_id = Column(BigInteger, nullable=False, index=True)
    service_id = Column(BigInteger, nullable=False, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    amount = Column(Integer, nullable=False)  # 订单金额
    status = Column(SmallInteger, default=0)  # 0=待支付, 1=已支付, 2=已完成, 3=已取消
    payment_time = Column(TIMESTAMP(timezone=True), nullable=True)
    complete_time = Column(TIMESTAMP(timezone=True), nullable=True)
    create_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp())
    update_time = Column(TIMESTAMP(timezone=True), server_default=func.current_timestamp(), onupdate=func.current_timestamp()) 