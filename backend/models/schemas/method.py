from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举类型
class CheckinTypeEnum(str, Enum):
    """打卡类型枚举"""
    STUDY = "study"  # 学习打卡
    PRACTICE = "practice"  # 练习打卡
    REVIEW = "review"  # 复习打卡
    COMPLETE = "complete"  # 完成打卡

class DifficultyLevelEnum(str, Enum):
    """难度等级枚举"""
    BEGINNER = "初级"
    INTERMEDIATE = "中级"
    ADVANCED = "高级"
    EXPERT = "专家级"

# 基础模型
class MethodFilterParams(BaseModel):
    """筛选参数模型（仅category字段）"""
    category: Optional[str] = Field(None, description="方法分类")

class MethodStatsResponse(BaseModel):
    """方法统计响应模型"""
    checkin_count: int = Field(default=0, description="打卡人数")
    rating: float = Field(default=0.0, description="评分")
    completion_rate: float = Field(default=0.0, description="完成率")

# 学习方法相关模型
class MethodListResponse(BaseModel):
    """学习方法列表响应模型（含name、category、meta、stats等）"""
    id: int
    name: str = Field(..., description="方法名称")
    description: str = Field(..., description="方法描述")
    category: str = Field(..., description="方法分类")
    difficulty_level: DifficultyLevelEnum = Field(..., description="难度等级")
    estimated_time: int = Field(..., description="预估时间（分钟）")
    tags: List[str] = Field(default=[], description="标签列表")
    author_info: Optional[Dict[str, Any]] = Field(None, description="作者信息")
    stats: MethodStatsResponse = Field(..., description="统计信息")
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

class MethodDetailResponse(BaseModel):
    """学习方法详情响应模型（含description、steps、scene、stats等）"""
    id: int
    name: str = Field(..., description="方法名称")
    description: str = Field(..., description="方法描述")
    category: str = Field(..., description="方法分类")
    difficulty_level: DifficultyLevelEnum = Field(..., description="难度等级")
    estimated_time: int = Field(..., description="预估时间（分钟）")
    steps: List[Dict[str, Any]] = Field(default=[], description="学习步骤")
    scene: Optional[str] = Field(None, description="适用场景")
    meta: Dict[str, Any] = Field(default={}, description="元数据")
    tags: List[str] = Field(default=[], description="标签列表")
    author_info: Optional[Dict[str, Any]] = Field(None, description="作者信息")
    stats: MethodStatsResponse = Field(..., description="统计信息")
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

# 打卡相关模型
class CheckinCreate(BaseModel):
    """打卡请求模型（checkin_type、progress、note）"""
    checkin_type: CheckinTypeEnum = Field(..., description="打卡类型")
    progress: int = Field(..., ge=0, le=100, description="进度百分比")
    note: Optional[str] = Field(None, max_length=500, description="打卡心得")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分1-5")

class CheckinResponse(BaseModel):
    """打卡响应模型（含checkin_time、progress、note等）"""
    id: int
    user_id: int
    method_id: int
    checkin_type: CheckinTypeEnum
    progress: int = Field(..., description="进度百分比")
    note: Optional[str] = Field(None, description="打卡心得")
    rating: Optional[int] = Field(None, description="评分")
    checkin_time: datetime = Field(..., description="打卡时间")
    create_time: datetime
    
    class Config:
        from_attributes = True

class CheckinHistoryResponse(BaseModel):
    """打卡历史响应模型"""
    id: int
    checkin_type: CheckinTypeEnum
    progress: int = Field(..., description="进度百分比")
    note: Optional[str] = Field(None, description="打卡心得")
    rating: Optional[int] = Field(None, description="评分")
    checkin_time: datetime = Field(..., description="打卡时间")
    create_time: datetime
    
    # 额外的历史信息
    days_ago: int = Field(..., description="距今天数")
    is_continuous: bool = Field(..., description="是否连续打卡")
    
    class Config:
        from_attributes = True

# 方法创建和更新模型
class MethodCreate(BaseModel):
    """学习方法创建模型"""
    name: str = Field(..., min_length=1, max_length=100, description="方法名称")
    description: str = Field(..., min_length=1, description="方法描述")
    category: str = Field(..., description="方法分类")
    difficulty_level: DifficultyLevelEnum = Field(default=DifficultyLevelEnum.BEGINNER, description="难度等级")
    estimated_time: int = Field(default=30, ge=5, le=480, description="预估时间（分钟）")
    steps: List[Dict[str, Any]] = Field(default=[], description="学习步骤")
    scene: Optional[str] = Field(None, description="适用场景")
    meta: Dict[str, Any] = Field(default={}, description="元数据")
    tags: List[str] = Field(default=[], description="标签列表")
    author_info: Optional[Dict[str, Any]] = Field(None, description="作者信息")

class MethodUpdate(BaseModel):
    """学习方法更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="方法名称")
    description: Optional[str] = Field(None, min_length=1, description="方法描述")
    category: Optional[str] = Field(None, description="方法分类")
    difficulty_level: Optional[DifficultyLevelEnum] = Field(None, description="难度等级")
    estimated_time: Optional[int] = Field(None, ge=5, le=480, description="预估时间（分钟）")
    steps: Optional[List[Dict[str, Any]]] = Field(None, description="学习步骤")
    scene: Optional[str] = Field(None, description="适用场景")
    meta: Optional[Dict[str, Any]] = Field(None, description="元数据")
    tags: Optional[List[str]] = Field(None, description="标签列表")
    author_info: Optional[Dict[str, Any]] = Field(None, description="作者信息")
    is_active: Optional[bool] = Field(None, description="是否启用")

# 分类相关模型
class MethodCategoryResponse(BaseModel):
    """方法分类响应模型"""
    name: str = Field(..., description="分类名称")
    display_name: str = Field(..., description="显示名称")
    description: Optional[str] = Field(None, description="分类描述")
    icon: Optional[str] = Field(None, description="分类图标")
    method_count: int = Field(default=0, description="该分类下的方法数量")

# 统计相关模型
class UserMethodStatsResponse(BaseModel):
    """用户方法统计响应模型"""
    method_id: int
    method_name: str
    total_checkins: int = Field(default=0, description="总打卡次数")
    continuous_days: int = Field(default=0, description="连续打卡天数")
    last_checkin_date: Optional[datetime] = Field(None, description="最后打卡日期")
    average_progress: float = Field(default=0.0, description="平均进度")
    current_month_checkins: int = Field(default=0, description="本月打卡次数")
    checkin_rate: float = Field(default=0.0, description="打卡率")

class CheckinCalendarResponse(BaseModel):
    """打卡日历响应模型"""
    year: int
    month: int
    days_in_month: int = Field(..., description="该月天数")
    checkin_days: int = Field(..., description="打卡天数")
    total_checkins: int = Field(..., description="总打卡次数")
    checkin_rate: float = Field(..., description="打卡率")
    calendar_data: Dict[int, List[Dict[str, Any]]] = Field(..., description="日历数据")

# 操作响应模型
class MethodOperationResponse(BaseModel):
    """方法操作响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")

# 推荐相关模型（在ai.py中定义，这里引用）
class MethodRecommendationResponse(BaseModel):
    """方法推荐响应模型"""
    method: MethodListResponse
    recommendation_reason: str = Field(..., description="推荐理由")
    relevance_score: float = Field(..., description="相关性分数")
    popularity_score: float = Field(..., description="热门度分数")
    total_score: float = Field(..., description="总分")

# 搜索相关模型
class MethodSearchRequest(BaseModel):
    """方法搜索请求模型"""
    keyword: Optional[str] = Field(None, description="关键词")
    category: Optional[str] = Field(None, description="分类筛选")
    difficulty_level: Optional[DifficultyLevelEnum] = Field(None, description="难度筛选")
    min_time: Optional[int] = Field(None, description="最小时间")
    max_time: Optional[int] = Field(None, description="最大时间")
    tags: Optional[List[str]] = Field(None, description="标签筛选")
    sort_by: Optional[str] = Field("popularity", description="排序方式")  # popularity, rating, time
    page: int = Field(1, ge=1, description="页码")
    page_size: int = Field(20, ge=1, le=100, description="每页数量")

class MethodSearchResponse(BaseModel):
    """方法搜索响应模型"""
    methods: List[MethodListResponse] = Field(..., description="方法列表")
    total: int = Field(..., description="总数量")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页数量")
    has_more: bool = Field(..., description="是否有更多")
    search_time: float = Field(..., description="搜索耗时（秒）")

# 批量操作模型
class BatchCheckinRequest(BaseModel):
    """批量打卡请求模型"""
    checkins: List[Dict[str, Any]] = Field(..., description="打卡列表")

class BatchCheckinResponse(BaseModel):
    """批量打卡响应模型"""
    success_count: int = Field(..., description="成功数量")
    failed_count: int = Field(..., description="失败数量")
    results: List[Dict[str, Any]] = Field(..., description="详细结果")

# 导出相关模型
class MethodExportRequest(BaseModel):
    """方法导出请求模型"""
    method_ids: List[int] = Field(..., description="方法ID列表")
    export_format: str = Field("json", description="导出格式")  # json, csv, pdf
    include_stats: bool = Field(True, description="是否包含统计信息")

class CheckinExportRequest(BaseModel):
    """打卡导出请求模型"""
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    method_ids: Optional[List[int]] = Field(None, description="方法ID列表")
    export_format: str = Field("csv", description="导出格式")  # csv, excel, json 