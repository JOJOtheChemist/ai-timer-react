from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Message(Base):
    """消息表"""
    __tablename__ = "message"
    
    id = Column(BigInteger, primary_key=True, index=True)
    sender_id = Column(BigInteger, nullable=False, index=True)  # 发送方用户ID
    receiver_id = Column(BigInteger, nullable=False, index=True)  # 接收方用户ID
    message_type = Column(String(20), nullable=False, index=True)  # 'tutor', 'private', 'system'
    title = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    related_id = Column(BigInteger, nullable=True)  # 关联资源ID（如导师ID、时间表ID等）
    related_type = Column(String(20), nullable=True)  # 关联资源类型
    parent_message_id = Column(BigInteger, ForeignKey("message.id"), nullable=True)  # 回复的原消息ID
    is_read = Column(SmallInteger, default=0)  # 0-未读，1-已读
    read_time = Column(DateTime(timezone=True), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    replies = relationship("Message", back_populates="parent_message", remote_side=[id])
    parent_message = relationship("Message", back_populates="replies", remote_side=[parent_message_id])

class MessageTemplate(Base):
    """消息模板表"""
    __tablename__ = "message_template"
    
    id = Column(BigInteger, primary_key=True, index=True)
    template_type = Column(String(20), nullable=False)  # 'system', 'tutor_feedback', etc.
    title_template = Column(String(200), nullable=False)
    content_template = Column(Text, nullable=False)
    is_active = Column(SmallInteger, default=1)
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class UserMessageSetting(Base):
    """用户消息设置表"""
    __tablename__ = "user_message_setting"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, unique=True, nullable=False, index=True)
    tutor_reminder = Column(SmallInteger, default=1)  # 导师反馈提醒：0-关闭，1-开启
    private_reminder = Column(SmallInteger, default=1)  # 私信提醒：0-关闭，1-开启
    system_reminder = Column(SmallInteger, default=1)  # 系统通知提醒：0-关闭，1-开启
    reminder_type = Column(String(20), default='push')  # 提醒方式：'push', 'email', 'both'
    keep_days = Column(SmallInteger, default=30)  # 消息保留天数
    auto_read_system = Column(SmallInteger, default=0)  # 系统消息自动标记已读：0-否，1-是
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 