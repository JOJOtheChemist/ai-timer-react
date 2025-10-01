from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, JSON, Integer
from sqlalchemy.sql import func
from core.database import Base

class Moment(Base):
    """动态/干货内容表"""
    __tablename__ = "moment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    type = Column(SmallInteger, nullable=False, index=True)  # 0-dynamic, 1-dryGoods, 2-ad
    title = Column(String(200), nullable=True)  # 干货标题，动态可为空
    content = Column(Text, nullable=False)
    image_url = Column(String(255), nullable=True)  # 图片URL
    tags = Column(JSON, default=[])  # 标签列表（JSONB in PostgreSQL）
    is_top = Column(SmallInteger, default=0)  # 0-否，1-是（置顶广告用）
    ad_info = Column(String(200), nullable=True)  # 广告信息
    status = Column(SmallInteger, default=0)  # 0-draft, 1-published, 2-deleted
    
    # 统计字段
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MomentComment(Base):
    """动态评论表"""
    __tablename__ = "moment_comment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    content = Column(Text, nullable=False)
    parent_id = Column(BigInteger, nullable=True)  # 回复的评论ID
    like_count = Column(Integer, default=0)
    is_anonymous = Column(SmallInteger, default=0)  # 0-否，1-是
    status = Column(SmallInteger, default=0)  # 0-正常，1-已删除，2-已隐藏
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class MomentInteraction(Base):
    """动态互动表（统一管理点赞/收藏/分享）"""
    __tablename__ = "moment_interaction"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    interaction_type = Column(SmallInteger, nullable=False, index=True)  # 0-like, 1-bookmark, 2-share
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class MomentAttachment(Base):
    """动态附件表（干货的时间表、文件等关联）"""
    __tablename__ = "moment_attachment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    attachment_type = Column(String(20), nullable=False)  # 'schedule', 'file', 'image', 'link'
    attachment_id = Column(BigInteger, nullable=True)  # 关联资源ID（如schedule_id）
    attachment_url = Column(String(500), nullable=True)  # 文件/图片URL
    attachment_name = Column(String(200), nullable=True)  # 附件名称
    attachment_size = Column(BigInteger, nullable=True)  # 文件大小（字节）
    create_time = Column(DateTime(timezone=True), server_default=func.now()) 