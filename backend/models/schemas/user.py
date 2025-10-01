from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal
from models.schemas.message import MessageSettingResponse, MessageSettingUpdate, ReminderTypeEnum

# 用户基础信息
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")

class UserResponse(UserBase):
    id: int
    is_active: bool = True
    create_time: datetime
    
    class Config:
        from_attributes = True

# 个人信息相关
class UserProfileResponse(BaseModel):
    """用户个人信息响应模型"""
    user_id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    goal: Optional[str] = None
    bio: Optional[str] = None
    
    # 统计信息
    total_study_hours: Decimal = Field(default=0.0, description="总学习时长")
    total_moments: int = Field(default=0, description="发布动态数")
    total_badges: int = Field(default=0, description="获得徽章数")
    
    # 设置信息
    is_public: bool = Field(default=True, description="是否公开个人信息")
    allow_follow: bool = Field(default=True, description="是否允许被关注")
    
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

class UserProfileUpdate(BaseModel):
    """用户信息更新请求模型"""
    username: Optional[str] = Field(None, min_length=1, max_length=50, description="用户名")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    email: Optional[str] = Field(None, description="邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号")
    goal: Optional[str] = Field(None, max_length=1000, description="学习目标")
    bio: Optional[str] = Field(None, max_length=500, description="个人简介")
    is_public: Optional[bool] = Field(None, description="是否公开个人信息")
    allow_follow: Optional[bool] = Field(None, description="是否允许被关注")

# 资产相关
class UserAssetResponse(BaseModel):
    """用户资产响应模型"""
    user_id: int
    diamond_count: int = Field(default=0, description="钻石数量")
    total_recharge: Decimal = Field(default=0.00, description="总充值金额")
    total_consume: int = Field(default=0, description="总消费钻石数")
    recent_consume: Optional[Dict[str, Any]] = Field(None, description="最近消费记录")
    
    class Config:
        from_attributes = True

class RechargeRequest(BaseModel):
    """充值请求模型"""
    amount: Decimal = Field(..., gt=0, description="充值金额")
    payment_method: Optional[str] = Field(None, description="支付方式")

class RechargeResponse(BaseModel):
    """充值响应模型"""
    order_id: str = Field(..., description="订单号")
    amount: Decimal = Field(..., description="充值金额")
    diamond_count: int = Field(..., description="获得钻石数")
    payment_url: Optional[str] = Field(None, description="支付链接")
    expire_time: Optional[datetime] = Field(None, description="订单过期时间")

class AssetRecordResponse(BaseModel):
    """资产记录响应模型"""
    id: int
    record_type: str
    amount: int
    balance_after: int
    description: Optional[str] = None
    create_time: datetime
    
    class Config:
        from_attributes = True

# 关系链相关
class RelationStatsResponse(BaseModel):
    """关系统计响应模型"""
    tutor_count: int = Field(default=0, description="关注导师数")
    fan_count: int = Field(default=0, description="粉丝数")
    following_count: int = Field(default=0, description="关注用户数")

class TutorInfo(BaseModel):
    """导师信息"""
    tutor_id: int
    name: str
    avatar: Optional[str] = None
    title: Optional[str] = None
    is_verified: bool = False

class UserInfo(BaseModel):
    """用户信息"""
    user_id: int
    username: str
    nickname: Optional[str] = None
    avatar: Optional[str] = None

class FollowedTutorResponse(BaseModel):
    """关注的导师响应"""
    tutors: List[TutorInfo] = Field(..., description="导师列表")
    total: int = Field(..., description="总数")

class RecentFanResponse(BaseModel):
    """最近粉丝响应"""
    fans: List[UserInfo] = Field(..., description="粉丝列表")
    total: int = Field(..., description="总数")

# 用户消息设置（继承自message模块）
class UserMessageSettingResponse(MessageSettingResponse):
    """用户消息设置响应"""
    user_id: int = Field(..., description="用户ID")
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

class UserMessageSettingUpdate(MessageSettingUpdate):
    """用户消息设置更新"""
    pass

# 用户设置相关
class UserSettingResponse(BaseModel):
    """用户设置响应"""
    user_id: int
    profile_visibility: str = Field(default="public", description="个人信息可见性")
    allow_follow: bool = Field(default=True, description="是否允许被关注")
    show_study_stats: bool = Field(default=True, description="是否显示学习统计")
    email_notification: bool = Field(default=True, description="邮件通知")
    push_notification: bool = Field(default=True, description="推送通知")
    theme: str = Field(default="light", description="主题")
    language: str = Field(default="zh-CN", description="语言")
    timezone: str = Field(default="Asia/Shanghai", description="时区")
    
    class Config:
        from_attributes = True

class UserSettingUpdate(BaseModel):
    """用户设置更新"""
    profile_visibility: Optional[str] = Field(None, description="个人信息可见性")
    allow_follow: Optional[bool] = Field(None, description="是否允许被关注")
    show_study_stats: Optional[bool] = Field(None, description="是否显示学习统计")
    email_notification: Optional[bool] = Field(None, description="邮件通知")
    push_notification: Optional[bool] = Field(None, description="推送通知")
    theme: Optional[str] = Field(None, description="主题")
    language: Optional[str] = Field(None, description="语言")
    timezone: Optional[str] = Field(None, description="时区")

# 用户操作响应
class UserOperationResponse(BaseModel):
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据")

# 用户统计相关
class UserStatsResponse(BaseModel):
    """用户统计响应"""
    user_id: int
    total_study_hours: Decimal = Field(default=0.0, description="总学习时长")
    total_study_days: int = Field(default=0, description="总学习天数")
    total_moments: int = Field(default=0, description="发布动态数")
    total_badges: int = Field(default=0, description="获得徽章数")
    total_likes_received: int = Field(default=0, description="获得点赞数")
    total_comments_received: int = Field(default=0, description="获得评论数")
    
    # 本周统计
    week_study_hours: Decimal = Field(default=0.0, description="本周学习时长")
    week_study_days: int = Field(default=0, description="本周学习天数")
    
    # 排名信息
    study_hours_rank: Optional[int] = Field(None, description="学习时长排名")
    badge_count_rank: Optional[int] = Field(None, description="徽章数量排名")

# 用户简易信息响应（用于案例作者展示等场景）
class UserSimpleInfoResponse(BaseModel):
    """用户简易信息响应模型（仅名称、头像等非敏感信息）"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_verified: bool = Field(default=False, description="是否认证用户")
    created_at: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True

# 导师服务相关模型
class TutorServicePurchaseCreate(BaseModel):
    """服务购买请求模型（tutor_id、service_id）"""
    tutor_id: int = Field(..., description="导师ID")
    service_id: int = Field(..., description="服务ID")

class TutorServiceOrderResponse(BaseModel):
    """订单响应模型（含order_id、status、amount等）"""
    order_id: str = Field(..., description="订单ID")
    user_id: int = Field(..., description="用户ID")
    tutor_id: int = Field(..., description="导师ID")
    service_id: int = Field(..., description="服务ID")
    service_name: str = Field(..., description="服务名称")
    amount: float = Field(..., description="订单金额")
    currency: str = Field(default="diamonds", description="货币类型")
    status: str = Field(..., description="订单状态")
    created_at: datetime = Field(..., description="创建时间")

# 私信相关模型
class PrivateMessageCreate(BaseModel):
    """私信发送请求模型（receiver_id、content）"""
    content: str = Field(..., min_length=1, max_length=1000, description="消息内容")

class PrivateMessageResponse(BaseModel):
    """私信响应模型（含sender、receiver、content、time等）"""
    id: int = Field(..., description="消息ID")
    sender_id: int = Field(..., description="发送者ID")
    receiver_id: int = Field(..., description="接收者ID")
    content: str = Field(..., description="消息内容")
    message_type: str = Field(default="private", description="消息类型")
    is_read: bool = Field(default=False, description="是否已读")
    created_at: datetime = Field(..., description="创建时间")

# 关注相关模型
class FollowResponse(BaseModel):
    """关注操作响应模型（含is_followed状态、follow_time等）"""
    is_followed: bool = Field(..., description="是否已关注")
    message: str = Field(..., description="操作结果消息")
    follow_time: Optional[datetime] = Field(None, description="关注时间")

# 导师信息模型
class TutorInfo(BaseModel):
    """导师基础信息模型"""
    tutor_id: int = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    title: str = Field(..., description="导师头衔")
    rating: float = Field(..., description="评分")
    is_verified: bool = Field(default=False, description="是否认证")

# 个人主页综合响应
class PersonalPageResponse(BaseModel):
    """个人主页综合响应"""
    profile: UserProfileResponse
    assets: UserAssetResponse
    relations: RelationStatsResponse
    stats: UserStatsResponse

# 导师服务相关模型
class TutorServicePurchaseCreate(BaseModel):
    """服务购买请求模型（tutor_id、service_id）"""
    tutor_id: int = Field(..., description="导师ID")
    service_id: int = Field(..., description="服务ID")

class TutorServiceOrderResponse(BaseModel):
    """订单响应模型（含order_id、status、amount等）"""
    order_id: str = Field(..., description="订单ID")
    user_id: int = Field(..., description="用户ID")
    tutor_id: int = Field(..., description="导师ID")
    service_id: int = Field(..., description="服务ID")
    service_name: str = Field(..., description="服务名称")
    amount: float = Field(..., description="订单金额")
    currency: str = Field(default="diamonds", description="货币类型")
    status: str = Field(..., description="订单状态")
    created_at: datetime = Field(..., description="创建时间")

# 私信相关模型
class PrivateMessageCreate(BaseModel):
    """私信发送请求模型（receiver_id、content）"""
    content: str = Field(..., min_length=1, max_length=1000, description="消息内容")

class PrivateMessageResponse(BaseModel):
    """私信响应模型（含sender、receiver、content、time等）"""
    id: int = Field(..., description="消息ID")
    sender_id: int = Field(..., description="发送者ID")
    receiver_id: int = Field(..., description="接收者ID")
    content: str = Field(..., description="消息内容")
    message_type: str = Field(default="private", description="消息类型")
    is_read: bool = Field(default=False, description="是否已读")
    created_at: datetime = Field(..., description="创建时间")

# 关注相关模型
class FollowResponse(BaseModel):
    """关注操作响应模型（含is_followed状态、follow_time等）"""
    is_followed: bool = Field(..., description="是否已关注")
    message: str = Field(..., description="操作结果消息")
    follow_time: Optional[datetime] = Field(None, description="关注时间")

# 导师信息模型
class TutorInfo(BaseModel):
    """导师基础信息模型"""
    tutor_id: int = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    title: str = Field(..., description="导师头衔")
    rating: float = Field(..., description="评分")
    is_verified: bool = Field(default=False, description="是否认证") 