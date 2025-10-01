from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# ================== 请求模型 ==================

class TutorFilterParams(BaseModel):
    """导师筛选参数"""
    tutor_type: Optional[str] = Field(None, description="导师类型筛选 (0=普通, 1=认证)")
    domain: Optional[str] = Field(None, description="擅长领域筛选")
    price_range: Optional[str] = Field(None, description="价格区间筛选")
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

# ================== 响应模型 ==================

class TutorListResponse(BaseModel):
    """导师列表响应模型"""
    id: int = Field(..., description="导师ID")
    username: str = Field(..., description="导师用户名")
    avatar: Optional[str] = Field(None, description="头像URL")
    type: int = Field(..., description="导师类型: 0=普通, 1=认证")
    domain: str = Field(..., description="擅长领域")
    education: Optional[str] = Field(None, description="学历")
    experience: Optional[str] = Field(None, description="经验")
    rating: int = Field(default=0, description="评分 (0-100)")
    student_count: int = Field(default=0, description="学生数量")
    success_rate: int = Field(default=0, description="成功率 (0-100)")
    monthly_guide_count: int = Field(default=0, description="月度指导次数")
    
    # 从 tutor_service 表计算的字段
    min_price: Optional[int] = Field(None, description="最低价格")
    max_price: Optional[int] = Field(None, description="最高价格")
    
    # 从 tutor_review 表计算的字段
    review_count: int = Field(default=0, description="评价数量")
    
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

class TutorSearchResponse(BaseModel):
    """导师搜索响应模型"""
    id: int = Field(..., description="导师ID")
    username: str = Field(..., description="导师用户名")
    avatar: Optional[str] = Field(None, description="头像URL")
    domain: str = Field(..., description="擅长领域")
    education: Optional[str] = Field(None, description="学历")
    rating: int = Field(default=0, description="评分 (0-100)")
    student_count: int = Field(default=0, description="学生数量")
    type: int = Field(..., description="导师类型: 0=普通, 1=认证")
    
    class Config:
        from_attributes = True

class TutorDetailResponse(BaseModel):
    """导师详情响应模型"""
    id: int = Field(..., description="导师ID")
    username: str = Field(..., description="导师用户名")
    avatar: Optional[str] = Field(None, description="头像URL")
    type: int = Field(..., description="导师类型: 0=普通, 1=认证")
    domain: str = Field(..., description="擅长领域")
    education: Optional[str] = Field(None, description="学历")
    experience: Optional[str] = Field(None, description="经验")
    work_experience: Optional[str] = Field(None, description="工作经历")
    philosophy: Optional[str] = Field(None, description="教学理念")
    rating: int = Field(default=0, description="评分 (0-100)")
    student_count: int = Field(default=0, description="学生数量")
    success_rate: int = Field(default=0, description="成功率 (0-100)")
    monthly_guide_count: int = Field(default=0, description="月度指导次数")
    status: int = Field(..., description="状态: 0=待审核, 1=正常, 2=禁用")
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    # 关联数据
    services: List[Dict[str, Any]] = Field(default=[], description="服务列表")
    reviews: List[Dict[str, Any]] = Field(default=[], description="评价列表")
    
    class Config:
        from_attributes = True

class TutorReviewResponse(BaseModel):
    """导师评价响应模型"""
    id: int = Field(..., description="评价ID")
    tutor_id: int = Field(..., description="导师ID")
    user_id: int = Field(..., description="用户ID")
    reviewer_name: str = Field(..., description="评价者姓名")
    rating: int = Field(..., ge=1, le=5, description="评分 (1-5)")
    content: str = Field(..., description="评价内容")
    attachment: Optional[str] = Field(None, description="附件")
    service_id: Optional[int] = Field(None, description="服务ID")
    is_anonymous: int = Field(default=0, description="是否匿名: 0=否, 1=是")
    create_time: datetime = Field(..., description="创建时间")
    
    class Config:
        from_attributes = True

class TutorServiceResponse(BaseModel):
    """导师服务响应模型"""
    id: int = Field(..., description="服务ID")
    tutor_id: int = Field(..., description="导师ID")
    name: str = Field(..., description="服务名称")
    price: int = Field(..., ge=0, description="价格（钻石）")
    description: str = Field(..., description="服务描述")
    unit: Optional[str] = Field(None, description="单位")
    service_type: str = Field(default="consultation", description="服务类型")
    estimated_hours: Optional[float] = Field(None, description="预计时长")
    is_active: int = Field(default=1, description="是否启用: 0=停用, 1=启用")
    sort_order: int = Field(default=0, description="排序")
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    
    class Config:
        from_attributes = True

class TutorMetricsResponse(BaseModel):
    """导师指导数据面板响应模型"""
    student_count: int = Field(default=0, description="学生数量")
    success_rate: int = Field(default=0, description="成功率 (0-100)")
    monthly_guide_count: int = Field(default=0, description="月度指导次数")
    rating: int = Field(default=0, description="评分 (0-100)")

# ================== 统计模型 ==================

class TutorStatsResponse(BaseModel):
    """导师统计响应模型"""
    total_count: int = Field(default=0, description="总导师数")
    normal_count: int = Field(default=0, description="普通导师数")
    certified_count: int = Field(default=0, description="认证导师数")

# ================== 创建/更新模型 ==================

class TutorServiceCreate(BaseModel):
    """创建导师服务请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="服务名称")
    price: int = Field(..., ge=0, description="价格（钻石）")
    description: str = Field(..., min_length=10, description="服务描述")
    unit: Optional[str] = Field(None, max_length=20, description="单位")
    service_type: str = Field(default="consultation", description="服务类型")
    estimated_hours: Optional[float] = Field(None, description="预计时长")
    sort_order: int = Field(default=0, description="排序")

class TutorReviewCreate(BaseModel):
    """创建导师评价请求模型"""
    rating: int = Field(..., ge=1, le=5, description="评分 (1-5)")
    content: str = Field(..., min_length=10, max_length=1000, description="评价内容")
    service_id: Optional[int] = Field(None, description="服务ID")
    is_anonymous: int = Field(default=0, description="是否匿名: 0=否, 1=是")
    attachment: Optional[str] = Field(None, description="附件URL")

# ================== 操作响应模型 ==================

class TutorOperationResponse(BaseModel):
    """导师操作响应模型"""
    success: bool = Field(..., description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="返回数据") 