from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# 徽章基础模型
class BadgeBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="徽章名称")
    description: str = Field(..., min_length=1, description="徽章描述")
    icon: str = Field(..., description="徽章图标URL")
    category: str = Field(..., description="徽章分类")

class BadgeCreate(BadgeBase):
    level: str = Field(default="bronze", description="徽章等级")
    rarity: str = Field(default="common", description="徽章稀有度")
    unlock_condition: Dict[str, Any] = Field(..., description="解锁条件")
    unlock_type: str = Field(..., description="解锁类型")

class BadgeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="徽章名称")
    description: Optional[str] = Field(None, min_length=1, description="徽章描述")
    icon: Optional[str] = Field(None, description="徽章图标URL")
    category: Optional[str] = Field(None, description="徽章分类")
    level: Optional[str] = Field(None, description="徽章等级")
    rarity: Optional[str] = Field(None, description="徽章稀有度")
    unlock_condition: Optional[Dict[str, Any]] = Field(None, description="解锁条件")
    is_active: Optional[bool] = Field(None, description="是否启用")

class BadgeResponse(BadgeBase):
    """徽章响应模型"""
    id: int
    level: str
    rarity: str
    unlock_condition: Dict[str, Any]
    unlock_type: str
    is_active: bool
    sort_order: int
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

# 用户徽章相关
class UserBadgeResponse(BaseModel):
    """用户徽章列表响应模型"""
    badge_id: int
    name: str
    description: str
    icon: str
    category: str
    level: str
    rarity: str
    
    # 用户获得信息
    is_obtained: bool = Field(..., description="是否已获得")
    obtain_date: Optional[datetime] = Field(None, description="获得时间")
    obtain_reason: Optional[str] = Field(None, description="获得原因")
    
    # 进度信息（未获得时显示）
    current_progress: Optional[int] = Field(None, description="当前进度")
    target_progress: Optional[int] = Field(None, description="目标进度")
    progress_percentage: Optional[float] = Field(None, description="进度百分比")
    
    # 展示设置
    is_displayed: bool = Field(default=True, description="是否展示")
    display_order: int = Field(default=0, description="展示顺序")
    
    class Config:
        from_attributes = True

class BadgeDetailResponse(BadgeResponse):
    """徽章详情响应模型"""
    # 用户相关信息
    is_obtained: bool = Field(..., description="用户是否已获得")
    obtain_date: Optional[datetime] = Field(None, description="获得时间")
    obtain_reason: Optional[str] = Field(None, description="获得原因")
    
    # 解锁条件详情
    lock_condition: Optional[str] = Field(None, description="解锁条件描述")
    
    # 进度信息
    current_progress: Optional[int] = Field(None, description="当前进度")
    target_progress: Optional[int] = Field(None, description="目标进度")
    progress_percentage: Optional[float] = Field(None, description="进度百分比")
    progress_data: Optional[Dict[str, Any]] = Field(None, description="进度详细数据")
    
    # 统计信息
    total_obtained_users: int = Field(default=0, description="获得该徽章的用户总数")
    obtain_rate: float = Field(default=0.0, description="获得率")

class UserBadgeListResponse(BaseModel):
    """用户徽章列表响应"""
    badges: List[UserBadgeResponse] = Field(..., description="徽章列表")
    total: int = Field(..., description="总徽章数")
    obtained_count: int = Field(..., description="已获得徽章数")
    categories: List[str] = Field(..., description="徽章分类列表")

# 徽章进度相关
class BadgeProgressResponse(BaseModel):
    """徽章进度响应"""
    badge_id: int
    badge_name: str
    badge_icon: str
    current_progress: int
    target_progress: int
    progress_percentage: float
    status: str
    progress_data: Optional[Dict[str, Any]] = None
    
    class Config:
        from_attributes = True

class BadgeProgressUpdate(BaseModel):
    """徽章进度更新"""
    current_progress: int = Field(..., ge=0, description="当前进度")
    progress_data: Optional[Dict[str, Any]] = Field(None, description="进度数据")

# 徽章分类相关
class BadgeCategoryResponse(BaseModel):
    """徽章分类响应"""
    id: int
    name: str
    display_name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    badge_count: int = Field(default=0, description="该分类下的徽章数量")
    obtained_count: int = Field(default=0, description="用户在该分类下已获得的徽章数")
    
    class Config:
        from_attributes = True

# 徽章操作相关
class BadgeOperationResponse(BaseModel):
    """徽章操作响应"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")

class BadgeAwardRequest(BaseModel):
    """徽章颁发请求"""
    user_id: int = Field(..., description="用户ID")
    badge_id: int = Field(..., description="徽章ID")
    reason: Optional[str] = Field(None, description="颁发原因")

class BadgeAwardResponse(BaseModel):
    """徽章颁发响应"""
    success: bool = Field(True, description="颁发是否成功")
    message: str = Field("徽章颁发成功", description="响应消息")
    badge: Optional[UserBadgeResponse] = Field(None, description="徽章信息")

# 徽章统计相关
class BadgeStatsResponse(BaseModel):
    """徽章统计响应"""
    total_badges: int = Field(default=0, description="总徽章数")
    obtained_badges: int = Field(default=0, description="已获得徽章数")
    completion_rate: float = Field(default=0.0, description="完成率")
    
    # 按分类统计
    category_stats: Dict[str, Dict[str, int]] = Field(default={}, description="分类统计")
    
    # 按等级统计
    level_stats: Dict[str, int] = Field(default={}, description="等级统计")
    
    # 按稀有度统计
    rarity_stats: Dict[str, int] = Field(default={}, description="稀有度统计")
    
    # 最近获得的徽章
    recent_badges: List[UserBadgeResponse] = Field(default=[], description="最近获得的徽章")

# 徽章推荐相关
class BadgeRecommendationResponse(BaseModel):
    """徽章推荐响应"""
    recommended_badges: List[BadgeDetailResponse] = Field(..., description="推荐徽章列表")
    reason: str = Field(..., description="推荐理由")
    priority: int = Field(default=1, description="推荐优先级")

# 徽章展示设置
class BadgeDisplayUpdate(BaseModel):
    """徽章展示设置更新"""
    badge_id: int = Field(..., description="徽章ID")
    is_displayed: bool = Field(..., description="是否展示")
    display_order: Optional[int] = Field(None, description="展示顺序")

class BadgeDisplayResponse(BaseModel):
    """徽章展示响应"""
    displayed_badges: List[UserBadgeResponse] = Field(..., description="展示的徽章列表")
    max_display_count: int = Field(default=6, description="最大展示数量") 