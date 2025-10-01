from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举类型定义
class TutorTypeEnum(str, Enum):
    """导师类型枚举"""
    ACADEMIC = "学术导师"
    PROFESSIONAL = "职业导师"
    SKILL = "技能导师"
    LANGUAGE = "语言导师"
    EXAM_PREP = "考试辅导"
    CAREER = "职业规划"

class ServiceTypeEnum(str, Enum):
    """服务类型枚举"""
    ONE_ON_ONE = "一对一辅导"
    GROUP_CLASS = "小班课程"
    CONSULTATION = "咨询服务"
    REVIEW = "作业批改"
    PLANNING = "学习规划"
    MOCK_EXAM = "模拟考试"

class OrderStatusEnum(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

# 请求模型
class TutorFilterParams(BaseModel):
    """导师筛选参数"""
    tutor_type: Optional[str] = Field(None, description="导师类型筛选")
    domain: Optional[str] = Field(None, description="擅长领域筛选")
    price_range: Optional[str] = Field(None, description="价格区间筛选")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

# 响应模型
class TutorListResponse(BaseModel):
    """导师列表响应模型（含基础信息、metrics、服务摘要）"""
    id: int = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    title: str = Field(..., description="导师头衔")
    tutor_type: str = Field(..., description="导师类型")
    domains: List[str] = Field(default=[], description="擅长领域")
    experience_years: int = Field(..., description="从业年限")
    rating: float = Field(..., description="评分")
    review_count: int = Field(default=0, description="评价数量")
    student_count: int = Field(default=0, description="学生数量")
    price_range: str = Field(..., description="价格区间")
    is_verified: bool = Field(default=False, description="是否认证")
    is_online: bool = Field(default=False, description="是否在线")
    response_rate: float = Field(default=0.0, description="回复率")
    service_summary: Optional[str] = Field(None, description="服务摘要")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class TutorSearchResponse(BaseModel):
    """导师搜索响应模型"""
    id: int = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    title: str = Field(..., description="导师头衔")
    tutor_type: str = Field(..., description="导师类型")
    domains: List[str] = Field(default=[], description="擅长领域")
    rating: float = Field(..., description="评分")
    review_count: int = Field(default=0, description="评价数量")
    price_range: str = Field(..., description="价格区间")
    is_verified: bool = Field(default=False, description="是否认证")
    match_score: float = Field(default=1.0, description="搜索相关性评分")
    highlight_fields: List[str] = Field(default=[], description="高亮字段")

class TutorDetailResponse(BaseModel):
    """导师详情响应模型（含profile、service_details、data_panel、reviews等）"""
    id: int = Field(..., description="导师ID")
    name: str = Field(..., description="导师姓名")
    avatar: Optional[str] = Field(None, description="头像URL")
    title: str = Field(..., description="导师头衔")
    bio: Optional[str] = Field(None, description="个人简介")
    tutor_type: str = Field(..., description="导师类型")
    domains: List[str] = Field(default=[], description="擅长领域")
    experience_years: int = Field(..., description="从业年限")
    education_background: Optional[str] = Field(None, description="教育背景")
    certifications: List[str] = Field(default=[], description="认证证书")
    rating: float = Field(..., description="评分")
    review_count: int = Field(default=0, description="评价数量")
    student_count: int = Field(default=0, description="学生数量")
    success_rate: float = Field(default=0.0, description="成功率")
    response_rate: float = Field(default=0.0, description="回复率")
    response_time: Optional[str] = Field(None, description="平均回复时间")
    is_verified: bool = Field(default=False, description="是否认证")
    is_online: bool = Field(default=False, description="是否在线")
    last_active: Optional[datetime] = Field(None, description="最后活跃时间")
    service_details: List[Dict[str, Any]] = Field(default=[], description="服务详情")
    data_panel: Dict[str, Any] = Field(default={}, description="数据面板")
    reviews: List[Dict[str, Any]] = Field(default=[], description="评价列表")
    is_followed: bool = Field(default=False, description="是否已关注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class TutorReviewResponse(BaseModel):
    """学员评价响应模型（含reviewer、rating、content等）"""
    id: int = Field(..., description="评价ID")
    reviewer_name: str = Field(..., description="评价者姓名")
    reviewer_avatar: Optional[str] = Field(None, description="评价者头像")
    rating: int = Field(..., ge=1, le=5, description="评分")
    content: str = Field(..., description="评价内容")
    service_name: Optional[str] = Field(None, description="服务名称")
    is_anonymous: bool = Field(default=False, description="是否匿名")
    created_at: datetime = Field(..., description="创建时间")

class TutorServiceResponse(BaseModel):
    """导师服务响应模型"""
    id: int = Field(..., description="服务ID")
    name: str = Field(..., description="服务名称")
    description: str = Field(..., description="服务描述")
    price: float = Field(..., description="服务价格")
    currency: str = Field(default="CNY", description="货币单位")
    duration: Optional[str] = Field(None, description="服务时长")
    service_type: str = Field(..., description="服务类型")
    is_available: bool = Field(default=True, description="是否可用")
    created_at: datetime = Field(..., description="创建时间")

class TutorMetricsResponse(BaseModel):
    """导师数据面板响应模型"""
    total_students: int = Field(default=0, description="总学生数")
    success_cases: int = Field(default=0, description="成功案例数")
    average_improvement: float = Field(default=0.0, description="平均提升幅度")
    teaching_hours: int = Field(default=0, description="授课时长")
    monthly_active_students: int = Field(default=0, description="月活跃学生数")
    satisfaction_rate: float = Field(default=0.0, description="满意度")
    last_updated: Optional[datetime] = Field(None, description="最后更新时间")

# 创建和更新模型
class TutorCreate(BaseModel):
    """创建导师请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="导师姓名")
    title: str = Field(..., min_length=1, max_length=200, description="导师头衔")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    tutor_type: str = Field(..., description="导师类型")
    domains: List[str] = Field(..., min_items=1, description="擅长领域")
    experience_years: int = Field(..., ge=0, description="从业年限")
    education_background: Optional[str] = Field(None, description="教育背景")
    certifications: List[str] = Field(default=[], description="认证证书")
    min_price: float = Field(..., ge=0, description="最低价格")
    max_price: float = Field(..., ge=0, description="最高价格")
    avatar: Optional[str] = Field(None, description="头像URL")

class TutorUpdate(BaseModel):
    """更新导师请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="导师姓名")
    title: Optional[str] = Field(None, min_length=1, max_length=200, description="导师头衔")
    bio: Optional[str] = Field(None, max_length=1000, description="个人简介")
    tutor_type: Optional[str] = Field(None, description="导师类型")
    domains: Optional[List[str]] = Field(None, description="擅长领域")
    experience_years: Optional[int] = Field(None, ge=0, description="从业年限")
    education_background: Optional[str] = Field(None, description="教育背景")
    certifications: Optional[List[str]] = Field(None, description="认证证书")
    min_price: Optional[float] = Field(None, ge=0, description="最低价格")
    max_price: Optional[float] = Field(None, ge=0, description="最高价格")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_online: Optional[bool] = Field(None, description="是否在线")

class TutorServiceCreate(BaseModel):
    """创建导师服务请求模型"""
    name: str = Field(..., min_length=1, max_length=200, description="服务名称")
    description: str = Field(..., min_length=10, description="服务描述")
    price: float = Field(..., ge=0, description="服务价格")
    currency: str = Field(default="CNY", description="货币单位")
    duration: Optional[str] = Field(None, description="服务时长")
    service_type: str = Field(..., description="服务类型")

class TutorServiceUpdate(BaseModel):
    """更新导师服务请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="服务名称")
    description: Optional[str] = Field(None, min_length=10, description="服务描述")
    price: Optional[float] = Field(None, ge=0, description="服务价格")
    currency: Optional[str] = Field(None, description="货币单位")
    duration: Optional[str] = Field(None, description="服务时长")
    service_type: Optional[str] = Field(None, description="服务类型")
    is_available: Optional[bool] = Field(None, description="是否可用")

class TutorReviewCreate(BaseModel):
    """创建导师评价请求模型"""
    rating: int = Field(..., ge=1, le=5, description="评分")
    content: str = Field(..., min_length=10, max_length=1000, description="评价内容")
    service_id: Optional[int] = Field(None, description="服务ID")
    is_anonymous: bool = Field(default=False, description="是否匿名")

# 操作响应模型
class TutorOperationResponse(BaseModel):
    """导师操作响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    tutor_id: Optional[int] = Field(None, description="导师ID")

# 统计模型
class TutorStatsResponse(BaseModel):
    """导师统计响应模型"""
    total_tutors: int = Field(..., description="总导师数")
    online_tutors: int = Field(..., description="在线导师数")
    verified_tutors: int = Field(..., description="认证导师数")
    type_stats: Dict[str, int] = Field(..., description="类型统计")
    recent_tutors_7d: int = Field(..., description="最近7天新增导师数")
    last_updated: datetime = Field(..., description="最后更新时间")

# 搜索模型
class TutorSearchRequest(BaseModel):
    """导师搜索请求模型"""
    keyword: str = Field(..., min_length=1, description="搜索关键词")
    tutor_type: Optional[str] = Field(None, description="导师类型筛选")
    domain: Optional[str] = Field(None, description="领域筛选")
    price_min: Optional[float] = Field(None, ge=0, description="最低价格")
    price_max: Optional[float] = Field(None, ge=0, description="最高价格")
    rating_min: Optional[float] = Field(None, ge=0, le=5, description="最低评分")
    is_verified: Optional[bool] = Field(None, description="是否只看认证导师")
    is_online: Optional[bool] = Field(None, description="是否只看在线导师")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

class TutorSearchResultResponse(BaseModel):
    """导师搜索结果响应模型"""
    tutors: List[TutorSearchResponse] = Field(..., description="搜索结果")
    total: int = Field(..., description="总结果数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    total_pages: int = Field(..., description="总页数")
    keyword: str = Field(..., description="搜索关键词")
    filters_applied: Dict[str, Any] = Field(default={}, description="应用的筛选条件") 