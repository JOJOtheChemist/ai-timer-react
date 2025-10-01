from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举类型定义
class CaseCategoryEnum(str, Enum):
    """案例分类枚举"""
    POSTGRADUATE = "考研"
    CIVIL_SERVICE = "公务员"
    TEACHER_QUALIFICATION = "教师资格证"
    CPA = "注册会计师"
    LANGUAGE = "语言考试"
    IT_CERTIFICATION = "IT认证"
    OTHER = "其他"

class PaymentMethodEnum(str, Enum):
    """支付方式枚举"""
    DIAMONDS = "diamonds"
    WECHAT = "wechat"
    ALIPAY = "alipay"
    CREDIT_CARD = "credit_card"

class PurchaseStatusEnum(str, Enum):
    """购买状态枚举"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

# 请求模型
class CaseFilterParams(BaseModel):
    """案例筛选参数"""
    category: Optional[str] = Field(None, description="案例分类")
    duration: Optional[str] = Field(None, description="备考时长")
    experience: Optional[str] = Field(None, description="经历背景")
    foundation: Optional[str] = Field(None, description="基础水平")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

class CasePurchaseRequest(BaseModel):
    """案例购买请求"""
    payment_method: PaymentMethodEnum = Field(..., description="支付方式")
    remark: Optional[str] = Field(None, description="备注")

# 响应模型
class HotCaseResponse(BaseModel):
    """热门案例响应模型"""
    id: int = Field(..., description="案例ID")
    title: str = Field(..., description="案例标题")
    tags: List[str] = Field(default=[], description="标签列表")
    author_name: str = Field(..., description="作者名称")
    author_id: int = Field(..., description="作者ID")
    views: int = Field(default=0, description="浏览量")
    is_hot: bool = Field(True, description="是否热门")
    category: str = Field(..., description="案例分类")
    duration: str = Field(..., description="备考时长")
    price: float = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币单位")
    created_at: datetime = Field(..., description="创建时间")

class CaseListResponse(BaseModel):
    """案例列表响应模型"""
    id: int = Field(..., description="案例ID")
    title: str = Field(..., description="案例标题")
    tags: List[str] = Field(default=[], description="标签列表")
    author_name: str = Field(..., description="作者名称")
    author_id: int = Field(..., description="作者ID")
    duration: str = Field(..., description="备考时长")
    category: str = Field(..., description="案例分类")
    price: float = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币单位")
    views: int = Field(default=0, description="浏览量")
    is_featured: bool = Field(default=False, description="是否精选")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class CaseDetailResponse(BaseModel):
    """案例详情响应模型"""
    id: int = Field(..., description="案例ID")
    title: str = Field(..., description="案例标题")
    author_name: str = Field(..., description="作者名称")
    author_id: int = Field(..., description="作者ID")
    category: str = Field(..., description="案例分类")
    duration: str = Field(..., description="备考时长")
    tags: List[str] = Field(default=[], description="标签列表")
    description: str = Field(..., description="案例描述")
    content: str = Field(..., description="案例内容（根据权限显示完整或预览）")
    time_schedule: Optional[str] = Field(None, description="时间规划表")
    experience_summary: Optional[str] = Field(None, description="经验总结")
    target_exam: str = Field(..., description="目标考试")
    initial_score: Optional[str] = Field(None, description="初始成绩")
    final_score: Optional[str] = Field(None, description="最终成绩")
    study_methods: List[str] = Field(default=[], description="学习方法")
    resources_used: List[str] = Field(default=[], description="使用资源")
    challenges_faced: Optional[str] = Field(None, description="面临挑战")
    key_insights: Optional[str] = Field(None, description="关键洞察")
    price: float = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币单位")
    views: int = Field(default=0, description="浏览量")
    likes: int = Field(default=0, description="点赞数")
    is_featured: bool = Field(default=False, description="是否精选")
    has_full_access: bool = Field(..., description="是否有完整访问权限")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class CasePermissionResponse(BaseModel):
    """案例权限响应模型"""
    case_id: int = Field(..., description="案例ID")
    preview_days: int = Field(..., description="预览天数")
    price: float = Field(..., description="价格")
    currency: str = Field(default="CNY", description="货币单位")
    has_purchased: bool = Field(..., description="是否已购买")
    is_author: bool = Field(..., description="是否为作者")
    can_preview: bool = Field(..., description="是否可以预览")
    purchase_required: bool = Field(..., description="是否需要购买")
    preview_content_ratio: float = Field(..., description="预览内容比例")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class CasePurchaseResponse(BaseModel):
    """案例购买响应模型"""
    success: bool = Field(..., description="购买是否成功")
    message: str = Field(..., description="响应消息")
    order_id: Optional[str] = Field(None, description="订单ID")
    purchase_time: Optional[datetime] = Field(None, description="购买时间")

# 创建和更新模型
class CaseCreate(BaseModel):
    """创建案例请求模型"""
    title: str = Field(..., min_length=1, max_length=200, description="案例标题")
    category: str = Field(..., description="案例分类")
    duration: str = Field(..., description="备考时长")
    tags: List[str] = Field(default=[], description="标签列表")
    description: str = Field(..., min_length=10, description="案例描述")
    full_content: str = Field(..., min_length=50, description="完整内容")
    preview_content: str = Field(..., min_length=20, description="预览内容")
    time_schedule: Optional[str] = Field(None, description="时间规划表")
    preview_schedule: Optional[str] = Field(None, description="预览时间规划")
    experience_summary: Optional[str] = Field(None, description="经验总结")
    preview_summary: Optional[str] = Field(None, description="预览经验总结")
    target_exam: str = Field(..., description="目标考试")
    initial_score: Optional[str] = Field(None, description="初始成绩")
    final_score: Optional[str] = Field(None, description="最终成绩")
    study_methods: List[str] = Field(default=[], description="学习方法")
    resources_used: List[str] = Field(default=[], description="使用资源")
    challenges_faced: Optional[str] = Field(None, description="面临挑战")
    key_insights: Optional[str] = Field(None, description="关键洞察")
    price: float = Field(..., ge=0, description="价格")
    currency: str = Field(default="CNY", description="货币单位")
    preview_days: int = Field(default=7, ge=1, description="预览天数")
    preview_content_ratio: float = Field(default=0.3, ge=0.1, le=0.8, description="预览内容比例")

class CaseUpdate(BaseModel):
    """更新案例请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="案例标题")
    category: Optional[str] = Field(None, description="案例分类")
    duration: Optional[str] = Field(None, description="备考时长")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    description: Optional[str] = Field(None, min_length=10, description="案例描述")
    full_content: Optional[str] = Field(None, min_length=50, description="完整内容")
    preview_content: Optional[str] = Field(None, min_length=20, description="预览内容")
    time_schedule: Optional[str] = Field(None, description="时间规划表")
    preview_schedule: Optional[str] = Field(None, description="预览时间规划")
    experience_summary: Optional[str] = Field(None, description="经验总结")
    preview_summary: Optional[str] = Field(None, description="预览经验总结")
    target_exam: Optional[str] = Field(None, description="目标考试")
    initial_score: Optional[str] = Field(None, description="初始成绩")
    final_score: Optional[str] = Field(None, description="最终成绩")
    study_methods: Optional[List[str]] = Field(None, description="学习方法")
    resources_used: Optional[List[str]] = Field(None, description="使用资源")
    challenges_faced: Optional[str] = Field(None, description="面临挑战")
    key_insights: Optional[str] = Field(None, description="关键洞察")
    price: Optional[float] = Field(None, ge=0, description="价格")
    currency: Optional[str] = Field(None, description="货币单位")
    preview_days: Optional[int] = Field(None, ge=1, description="预览天数")
    preview_content_ratio: Optional[float] = Field(None, ge=0.1, le=0.8, description="预览内容比例")

# 操作响应模型
class CaseOperationResponse(BaseModel):
    """案例操作响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    case_id: Optional[int] = Field(None, description="案例ID")

# 统计模型
class CaseStatsResponse(BaseModel):
    """案例统计响应模型"""
    total_cases: int = Field(..., description="总案例数")
    category_stats: Dict[str, int] = Field(..., description="分类统计")
    recent_cases_7d: int = Field(..., description="最近7天新增案例数")
    last_updated: datetime = Field(..., description="最后更新时间")

# 搜索模型
class CaseSearchRequest(BaseModel):
    """案例搜索请求模型"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    category: Optional[str] = Field(None, description="分类筛选")
    price_min: Optional[float] = Field(None, ge=0, description="最低价格")
    price_max: Optional[float] = Field(None, ge=0, description="最高价格")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

class CaseSearchResponse(BaseModel):
    """案例搜索响应模型"""
    cases: List[CaseListResponse] = Field(..., description="搜索结果")
    total: int = Field(..., description="总结果数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    keyword: str = Field(..., description="搜索关键词") 