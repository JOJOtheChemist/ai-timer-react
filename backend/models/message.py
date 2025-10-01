from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, ForeignKey
from sqlalchemy.sql import func
from core.database import Base


class Message(Base):
    """消息表"""
    __tablename__ = "message"
    
    id = Column(BigInteger, primary_key=True, index=True)
    sender_id = Column(BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, index=True)
    receiver_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    type = Column(SmallInteger, nullable=False, index=True)  # 0-导师，1-私信，2-系统
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    is_unread = Column(SmallInteger, default=1)  # 0-已读，1-未读
    related_id = Column(BigInteger, nullable=True, index=True)
    related_type = Column(String(20), nullable=True)
    attachment_url = Column(String(255), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    read_time = Column(DateTime(timezone=True), nullable=True)


class MessageReply(Base):
    """消息回复表"""
    __tablename__ = "message_reply"
    
    id = Column(BigInteger, primary_key=True, index=True)
    message_id = Column(BigInteger, ForeignKey("message.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True)
    content = Column(Text, nullable=False)
    attachment_url = Column(String(255), nullable=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())


class MessageTemplate(Base):
    """消息模板表"""
    __tablename__ = "message_template"
    
    id = Column(BigInteger, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    type = Column(SmallInteger, nullable=False)
    title_template = Column(String(200), nullable=True)
    content_template = Column(Text, nullable=False)
    variables = Column(Text, nullable=True)
    is_active = Column(SmallInteger, default=1)
    create_time = Column(DateTime(timezone=True), server_default=func.now())


class UserMessageSetting(Base):
    """用户消息设置表"""
    __tablename__ = "user_message_setting"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    reminder_type = Column(SmallInteger, default=0)  # 0-关闭，1-开启
    keep_days = Column(BigInteger, default=7)  # 消息保留天数
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now()) 