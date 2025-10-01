from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum

# 枚举类型
class MessageRole(str, Enum):
    USER = "user"
    AI = "ai"

class RecommendationType(str, Enum):
    METHOD = "method"
    CASE = "case"
    TUTOR = "tutor"
    SCHEDULE = "schedule"
    TASK = "task"

class AnalysisType(str, Enum):
    SCHEDULE = "schedule"
    HABIT = "habit"
    PROGRESS = "progress"
    EFFICIENCY = "efficiency"

# 聊天相关模型
class ChatMessageCreate(BaseModel):
    """用户消息请求模型"""
    content: str = Field(..., min_length=1, max_length=2000, description="消息内容")
    session_id: Optional[str] = Field(None, description="会话ID，用于关联对话")

class ChatResponse(BaseModel):
    """AI回复响应模型"""
    content: str = Field(..., description="AI回复内容")
    is_analysis: bool = Field(False, description="是否为分析型回复")
    analysis_tags: Optional[List[str]] = Field(None, description="分析标签")
    session_id: str = Field(..., description="会话ID")
    token_count: int = Field(0, description="消耗的token数")

class ChatMessage(BaseModel):
    """聊天消息模型"""
    id: int
    role: MessageRole
    content: str
    is_analysis: bool = False
    analysis_tags: Optional[List[str]] = None
    create_time: datetime
    
    class Config:
        from_attributes = True

class ChatHistoryResponse(BaseModel):
    """聊天历史响应模型"""
    messages: List[ChatMessage] = Field(..., description="消息列表")
    total: int = Field(..., description="总消息数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")

# 分析相关模型
class ScheduleAnalysisResponse(BaseModel):
    """时间表分析响应模型"""
    tags: List[str] = Field(..., description="问题标签，如['复习不足','时间碎片化']")
    analysis: str = Field(..., description="详细分析内容")
    recommendations: List[str] = Field(..., description="优化建议列表")
    confidence_score: Optional[float] = Field(None, description="分析置信度")
    analysis_time: datetime = Field(..., description="分析时间")

# 推荐相关模型
class RecommendationItem(BaseModel):
    """推荐项模型"""
    type: RecommendationType = Field(..., description="推荐类型")
    icon: str = Field(..., description="图标")
    name: str = Field(..., description="名称")
    desc: str = Field(..., description="描述")
    path: str = Field(..., description="跳转路径")
    related_id: Optional[int] = Field(None, description="关联资源ID")
    priority: int = Field(1, description="优先级1-5")
    reason: Optional[str] = Field(None, description="推荐理由")

class RecommendationsResponse(BaseModel):
    """推荐列表响应模型"""
    recommendations: List[RecommendationItem] = Field(..., description="推荐列表")
    total: int = Field(..., description="推荐总数")
    analysis_based: bool = Field(True, description="是否基于分析生成")

# 工具相关模型
class StudySummaryResponse(BaseModel):
    """复盘总结响应模型"""
    total_hours: float = Field(..., description="总学习时长")
    completion_rate: float = Field(..., description="完成率")
    category_distribution: Dict[str, float] = Field(..., description="各类型时长分布")
    mood_distribution: Dict[str, int] = Field(..., description="心情分布")
    improvement_suggestions: List[str] = Field(..., description="改进建议")
    summary_time: datetime = Field(..., description="总结时间")

class StudyPlanCreate(BaseModel):
    """学习计划生成参数模型"""
    goal: str = Field(..., description="学习目标")
    duration_days: int = Field(..., ge=1, le=365, description="计划周期（天）")
    daily_hours: float = Field(..., ge=0.5, le=16, description="每日学习时长")
    subjects: List[str] = Field(..., description="学习科目列表")
    difficulty_level: int = Field(1, ge=1, le=5, description="难度等级1-5")
    sync_to_schedule: bool = Field(False, description="是否同步到时间表")

class StudyPlanResponse(BaseModel):
    """学习计划响应模型"""
    plan_id: int = Field(..., description="计划ID")
    title: str = Field(..., description="计划标题")
    description: str = Field(..., description="计划描述")
    daily_tasks: List[Dict[str, Any]] = Field(..., description="每日任务安排")
    milestones: List[Dict[str, Any]] = Field(..., description="里程碑")
    synced_to_schedule: bool = Field(False, description="是否已同步到时间表")
    create_time: datetime = Field(..., description="创建时间")

# 流式响应模型
class StreamChatResponse(BaseModel):
    """流式聊天响应模型"""
    delta: str = Field(..., description="增量内容")
    is_complete: bool = Field(False, description="是否完成")
    session_id: str = Field(..., description="会话ID")
    token_count: Optional[int] = Field(None, description="当前token数")

# 通用响应模型
class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(True, description="是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")

class ErrorResponse(BaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="是否成功")
    message: str = Field(..., description="错误消息")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Dict[str, Any]] = Field(None, description="错误详情")

# 学习方法推荐相关模型
class AIStudyMethodResponse(BaseModel):
    """AI学习方法推荐响应"""
    method_id: int = Field(..., description="方法ID")
    name: str = Field(..., description="方法名称")
    description: str = Field(..., description="方法描述")
    category: str = Field(..., description="方法分类")
    suitable_scenarios: List[str] = Field(..., description="适用场景")
    recommendation_reason: str = Field(..., description="推荐理由")
    match_score: float = Field(..., ge=0, le=1, description="匹配度0-1")
    priority: int = Field(1, ge=1, le=5, description="优先级1-5")
    
    class Config:
        from_attributes = True

class UserBehaviorAnalysisResponse(BaseModel):
    """用户行为分析响应"""
    user_id: int = Field(..., description="用户ID")
    learning_patterns: Dict[str, Any] = Field(..., description="学习模式分析")
    time_preferences: Dict[str, Any] = Field(..., description="时间偏好分析")
    task_completion_rate: float = Field(..., ge=0, le=1, description="任务完成率")
    common_issues: List[str] = Field(..., description="常见问题列表")
    suggested_improvements: List[str] = Field(..., description="改进建议")
    analysis_time: datetime = Field(..., description="分析时间")
    
    class Config:
        from_attributes = True

class RecommendationExplanationResponse(BaseModel):
    """推荐理由详细解释响应"""
    method_id: int = Field(..., description="方法ID")
    method_name: str = Field(..., description="方法名称")
    explanation: str = Field(..., description="详细解释")
    user_behavior_insights: List[str] = Field(..., description="基于用户行为的洞察")
    expected_benefits: List[str] = Field(..., description="预期收益")
    implementation_tips: List[str] = Field(..., description="实施建议")
    
    class Config:
        from_attributes = True

class PersonalizedRecommendationResponse(BaseModel):
    """个性化推荐响应"""
    study_methods: List[AIStudyMethodResponse] = Field(..., description="学习方法推荐")
    task_suggestions: List[Dict[str, Any]] = Field(..., description="任务安排建议")
    schedule_optimization: Dict[str, Any] = Field(..., description="时间表优化建议")
    motivational_tips: List[str] = Field(..., description="激励建议")
    
    class Config:
        from_attributes = True

class RecommendationFeedbackRequest(BaseModel):
    """推荐反馈请求"""
    method_id: int = Field(..., description="方法ID")
    feedback_type: str = Field(..., description="反馈类型: helpful/not_helpful/tried")
    rating: Optional[int] = Field(None, ge=1, le=5, description="评分1-5")
    comment: Optional[str] = Field(None, max_length=500, description="反馈评论")
    
    class Config:
        from_attributes = True

class RecommendationFeedbackResponse(BaseModel):
    """推荐反馈响应"""
    success: bool = Field(True, description="是否成功")
    message: str = Field(..., description="反馈消息")
    feedback_id: Optional[int] = Field(None, description="反馈ID")
    
    class Config:
        from_attributes = True 