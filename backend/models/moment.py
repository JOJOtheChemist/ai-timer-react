from sqlalchemy import Column, BigInteger, String, Text, SmallInteger, DateTime, JSON, Integer, DECIMAL
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from core.database import Base

class Moment(Base):
    """动态/干货内容表"""
    __tablename__ = "moment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    moment_type = Column(String(20), nullable=False, index=True)  # 'dynamic', 'dryGoods', 'ad'
    title = Column(String(200), nullable=True)  # 干货标题，动态可为空
    content = Column(Text, nullable=False)
    tags = Column(JSON, default=[])  # 标签列表
    attachments = Column(JSON, default=[])  # 附件信息（干货用）
    is_top = Column(SmallInteger, default=0)  # 是否置顶（广告用）
    status = Column(String(20), default='published')  # 'published', 'draft', 'deleted'
    
    # 统计字段
    like_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    share_count = Column(Integer, default=0)
    bookmark_count = Column(Integer, default=0)
    view_count = Column(Integer, default=0)
    
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关联关系
    comments = relationship("MomentComment", back_populates="moment", cascade="all, delete-orphan")
    likes = relationship("MomentLike", back_populates="moment", cascade="all, delete-orphan")
    bookmarks = relationship("MomentBookmark", back_populates="moment", cascade="all, delete-orphan")

class MomentComment(Base):
    """动态评论表"""
    __tablename__ = "moment_comment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    parent_comment_id = Column(BigInteger, nullable=True)  # 回复的评论ID
    content = Column(Text, nullable=False)
    like_count = Column(Integer, default=0)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    moment = relationship("Moment", back_populates="comments")

class MomentLike(Base):
    """动态点赞表"""
    __tablename__ = "moment_like"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    moment = relationship("Moment", back_populates="likes")
    
    # 唯一约束：同一用户对同一动态只能点赞一次
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )

class MomentBookmark(Base):
    """动态收藏表"""
    __tablename__ = "moment_bookmark"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关联关系
    moment = relationship("Moment", back_populates="bookmarks")
    
    # 唯一约束：同一用户对同一动态只能收藏一次
    __table_args__ = (
        {"mysql_engine": "InnoDB"},
    )

class MomentShare(Base):
    """动态分享记录表"""
    __tablename__ = "moment_share"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)
    share_type = Column(String(20), default='general')  # 分享类型
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class MomentAttachment(Base):
    """动态附件表"""
    __tablename__ = "moment_attachment"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    attachment_type = Column(String(20), nullable=False)  # 'schedule', 'file', 'image', 'link'
    attachment_id = Column(BigInteger, nullable=True)  # 关联资源ID
    attachment_url = Column(String(500), nullable=True)  # 文件/图片URL
    attachment_name = Column(String(200), nullable=True)  # 附件名称
    attachment_size = Column(BigInteger, nullable=True)  # 文件大小
    create_time = Column(DateTime(timezone=True), server_default=func.now())

class MomentTag(Base):
    """动态标签表"""
    __tablename__ = "moment_tag"
    
    id = Column(BigInteger, primary_key=True, index=True)
    tag_name = Column(String(50), unique=True, nullable=False, index=True)
    tag_type = Column(String(20), default='general')  # 标签类型
    use_count = Column(Integer, default=0)  # 使用次数
    create_time = Column(DateTime(timezone=True), server_default=func.now())
    update_time = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

class MomentView(Base):
    """动态浏览记录表"""
    __tablename__ = "moment_view"
    
    id = Column(BigInteger, primary_key=True, index=True)
    moment_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=True, index=True)  # 可为空（匿名浏览）
    ip_address = Column(String(45), nullable=True)  # IP地址
    user_agent = Column(Text, nullable=True)  # 用户代理
    view_duration = Column(Integer, default=0)  # 浏览时长（秒）
    create_time = Column(DateTime(timezone=True), server_default=func.now()) 