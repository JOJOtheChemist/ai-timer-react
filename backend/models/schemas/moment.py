from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举类型
class MomentTypeEnum(str, Enum):
    DYNAMIC = "dynamic"
    DRY_GOODS = "dryGoods"
    AD = "ad"

class HotTypeEnum(str, Enum):
    LATEST = "latest"
    HOT = "hot"
    MOST_LIKED = "most_liked"
    MOST_COMMENTED = "most_commented"

class AttachmentTypeEnum(str, Enum):
    SCHEDULE = "schedule"
    FILE = "file"
    IMAGE = "image"
    LINK = "link"

# 基础模型
class MomentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="内容")
    tags: List[str] = Field(default=[], description="标签列表")

class DynamicCreate(MomentBase):
    """动态发布请求模型"""
    pass

class DryGoodsCreate(MomentBase):
    """干货发布请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="标题")
    attachments: List[Dict[str, Any]] = Field(default=[], description="附件列表")

class MomentCreate(BaseModel):
    """通用动态创建模型"""
    moment_type: MomentTypeEnum = Field(..., description="动态类型")
    title: Optional[str] = Field(None, max_length=200, description="标题（干货必填）")
    content: str = Field(..., min_length=1, max_length=5000, description="内容")
    tags: List[str] = Field(default=[], description="标签列表")
    attachments: List[Dict[str, Any]] = Field(default=[], description="附件列表")

class MomentUpdate(BaseModel):
    """动态更新模型"""
    title: Optional[str] = Field(None, max_length=200, description="标题")
    content: Optional[str] = Field(None, min_length=1, max_length=5000, description="内容")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    attachments: Optional[List[Dict[str, Any]]] = Field(None, description="附件列表")

# 响应模型
class UserInfo(BaseModel):
    """用户基础信息"""
    user_id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

class AttachmentInfo(BaseModel):
    """附件信息"""
    attachment_type: AttachmentTypeEnum
    attachment_id: Optional[int] = None
    attachment_url: Optional[str] = None
    attachment_name: Optional[str] = None
    attachment_size: Optional[int] = None

class MomentStats(BaseModel):
    """动态统计信息"""
    like_count: int = 0
    comment_count: int = 0
    share_count: int = 0
    bookmark_count: int = 0
    view_count: int = 0

class MomentResponse(BaseModel):
    """动态响应模型"""
    id: int
    user: UserInfo
    moment_type: MomentTypeEnum
    title: Optional[str] = None
    content: str
    tags: List[str] = []
    attachments: List[AttachmentInfo] = []
    stats: MomentStats
    is_top: bool = False
    create_time: datetime
    update_time: datetime
    
    # 用户互动状态
    is_liked: bool = False
    is_bookmarked: bool = False
    
    class Config:
        from_attributes = True

class MomentListResponse(BaseModel):
    """动态列表响应"""
    moments: List[MomentResponse] = Field(..., description="动态列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")

# 评论相关
class CommentCreate(BaseModel):
    """评论创建模型"""
    content: str = Field(..., min_length=1, max_length=1000, description="评论内容")
    parent_comment_id: Optional[int] = Field(None, description="回复的评论ID")

class CommentResponse(BaseModel):
    """评论响应模型"""
    id: int
    user: UserInfo
    content: str
    parent_comment_id: Optional[int] = None
    like_count: int = 0
    create_time: datetime
    
    # 回复列表（如果是父评论）
    replies: List["CommentResponse"] = []
    
    class Config:
        from_attributes = True

class CommentListResponse(BaseModel):
    """评论列表响应"""
    comments: List[CommentResponse] = Field(..., description="评论列表")
    total: int = Field(..., description="总评论数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")

# 互动相关
class InteractionResponse(BaseModel):
    """互动操作响应"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    
    # 当前状态
    is_liked: Optional[bool] = Field(None, description="是否已点赞")
    is_bookmarked: Optional[bool] = Field(None, description="是否已收藏")
    current_count: Optional[int] = Field(None, description="当前计数")

# 筛选相关
class MomentFilterParams(BaseModel):
    """筛选参数模型"""
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    time_range: Optional[str] = Field(None, description="时间范围：today/week/month/all")
    hot_type: Optional[HotTypeEnum] = Field(None, description="热度排序类型")
    user_id: Optional[int] = Field(None, description="用户筛选")

class SearchParams(BaseModel):
    """搜索参数模型"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    moment_type: Optional[MomentTypeEnum] = Field(None, description="动态类型筛选")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    time_range: Optional[str] = Field(None, description="时间范围")

# 标签相关
class TagInfo(BaseModel):
    """标签信息"""
    tag_name: str
    use_count: int = 0
    tag_type: str = "general"

class PopularTagsResponse(BaseModel):
    """热门标签响应"""
    tags: List[TagInfo] = Field(..., description="标签列表")
    total: int = Field(..., description="总标签数")

# 统计相关
class MomentStatsResponse(BaseModel):
    """动态统计响应"""
    total_moments: int = 0
    total_dynamics: int = 0
    total_dry_goods: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_shares: int = 0
    total_bookmarks: int = 0

class UserMomentStatsResponse(BaseModel):
    """用户动态统计响应"""
    user_id: int
    published_count: int = 0
    total_likes_received: int = 0
    total_comments_received: int = 0
    total_shares_received: int = 0
    total_bookmarks_received: int = 0
    most_popular_moment: Optional[MomentResponse] = None

# 分享相关
class ShareCreate(BaseModel):
    """分享创建模型"""
    share_type: str = Field(default="general", description="分享类型")

class ShareResponse(BaseModel):
    """分享响应模型"""
    success: bool = True
    message: str = "分享成功"
    share_count: int = 0

# 通用操作响应
class MomentOperationResponse(BaseModel):
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")

# 解决前向引用问题
CommentResponse.model_rebuild() 