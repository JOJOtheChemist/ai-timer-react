from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

# AI推荐学习方法响应模型
class AIStudyMethodResponse(BaseModel):
    """AI推荐学习方法响应模型（含method基础信息、推荐理由desc）"""
    method_id: int = Field(..., description="方法ID")
    method_name: str = Field(..., description="方法名称")
    method_description: str = Field(..., description="方法描述")
    category: str = Field(..., description="方法分类")
    difficulty_level: str = Field(..., description="难度等级")
    estimated_time: int = Field(..., description="预估时间（分钟）")
    tags: List[str] = Field(default=[], description="标签列表")
    
    # 推荐相关信息
    recommendation_reason: str = Field(..., description="推荐理由")
    relevance_score: float = Field(..., description="相关性分数")
    popularity_score: float = Field(..., description="热门度分数")
    total_score: float = Field(..., description="总分")
    
    # 统计信息
    checkin_count: int = Field(default=0, description="打卡人数")
    rating: Optional[float] = Field(None, description="评分")
    
    # 预览信息
    steps_preview: List[Dict[str, Any]] = Field(default=[], description="步骤预览")
    author_info: Optional[Dict[str, Any]] = Field(None, description="作者信息")

# AI分析相关模型
class UserBehaviorAnalysisResponse(BaseModel):
    """用户行为分析响应模型"""
    user_id: int
    behavior_tags: List[str] = Field(..., description="行为标签")
    analysis_data: Dict[str, Any] = Field(..., description="分析数据")
    study_stats: Dict[str, Any] = Field(..., description="学习统计")
    analysis_time: str = Field(..., description="分析时间")

class RecommendationExplanationResponse(BaseModel):
    """推荐解释响应模型"""
    method_id: int
    method_name: str
    user_behavior_summary: List[str] = Field(..., description="用户行为摘要")
    recommendation_reasons: List[str] = Field(..., description="推荐理由列表")
    matching_analysis: Dict[str, Any] = Field(..., description="匹配分析")
    expected_benefits: List[str] = Field(..., description="预期收益")
    usage_suggestions: List[str] = Field(..., description="使用建议")

class PersonalizedRecommendationResponse(BaseModel):
    """个性化推荐响应模型"""
    user_id: int
    method_recommendations: List[AIStudyMethodResponse] = Field(..., description="方法推荐")
    study_suggestions: List[str] = Field(..., description="学习建议")
    schedule_suggestions: List[str] = Field(..., description="时间安排建议")
    behavior_analysis: UserBehaviorAnalysisResponse = Field(..., description="行为分析")
    generated_at: str = Field(..., description="生成时间")

# 反馈相关模型
class RecommendationFeedbackRequest(BaseModel):
    """推荐反馈请求模型"""
    method_id: int = Field(..., description="方法ID")
    feedback_type: str = Field(..., description="反馈类型")  # helpful, not_helpful, tried
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分1-5")
    comment: Optional[str] = Field(None, max_length=500, description="反馈评论")

class RecommendationFeedbackResponse(BaseModel):
    """推荐反馈响应模型"""
    success: bool = Field(True, description="提交是否成功")
    message: str = Field("反馈提交成功", description="响应消息")

# 原有的AI聊天相关模型（保持不变）
class AIChatRequest(BaseModel):
    """AI聊天请求模型"""
    message: str = Field(..., min_length=1, max_length=1000, description="用户消息")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")
    chat_type: str = Field("general", description="聊天类型")

class AIChatResponse(BaseModel):
    """AI聊天响应模型"""
    message: str = Field(..., description="AI回复")
    suggestions: List[str] = Field(default=[], description="建议列表")
    context: Dict[str, Any] = Field(default={}, description="上下文信息")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间")

class AIAnalysisRequest(BaseModel):
    """AI分析请求模型"""
    analysis_type: str = Field(..., description="分析类型")
    data: Dict[str, Any] = Field(..., description="分析数据")
    options: Optional[Dict[str, Any]] = Field(None, description="分析选项")

class AIAnalysisResponse(BaseModel):
    """AI分析响应模型"""
    analysis_type: str = Field(..., description="分析类型")
    results: Dict[str, Any] = Field(..., description="分析结果")
    insights: List[str] = Field(default=[], description="洞察建议")
    confidence: float = Field(..., ge=0, le=1, description="置信度")
    timestamp: datetime = Field(default_factory=datetime.now, description="分析时间")

# 通用AI操作响应模型
class AIOperationResponse(BaseModel):
    """AI操作响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Dict[str, Any]] = Field(None, description="响应数据")
    timestamp: datetime = Field(default_factory=datetime.now, description="响应时间") 