from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime, date

# 周统计相关模型
class WeeklyOverviewResponse(BaseModel):
    """本周统计概览响应"""
    total_study_hours: float = Field(0.0, description="总学习时长")
    high_freq_complete: str = Field("0/0", description="高频任务完成情况，如'4/5'")
    overcome_complete: str = Field("0/0", description="待克服任务完成情况，如'1/2'")
    ai_accept_rate: int = Field(0, description="AI推荐采纳率")
    efficiency_score: Optional[float] = Field(None, description="效率评分")
    improvement_rate: Optional[float] = Field(None, description="相比上周的改进率")
    week_start: date = Field(..., description="本周开始日期")
    week_end: date = Field(..., description="本周结束日期")

class CategoryHours(BaseModel):
    """分类时长统计"""
    category: str = Field(..., description="分类名称")
    hours: float = Field(0.0, description="时长")
    percentage: float = Field(0.0, description="占比")
    color: str = Field("#3498db", description="图表颜色")

class DailyHours(BaseModel):
    """每日时长统计"""
    date: date = Field(..., description="日期")
    hours: float = Field(0.0, description="时长")
    completion_rate: float = Field(0.0, description="完成率")
    mood: Optional[str] = Field(None, description="主要心情")

class WeeklyChartResponse(BaseModel):
    """本周图表数据响应"""
    # 柱状图数据（每日时长）
    daily_chart: Dict[str, Any] = Field(..., description="每日时长柱状图数据")
    # 环形图数据（分类占比）
    category_chart: Dict[str, Any] = Field(..., description="分类时长环形图数据")
    # 详细数据
    daily_details: List[DailyHours] = Field(..., description="每日详细数据")
    category_details: List[CategoryHours] = Field(..., description="分类详细数据")

# 日统计相关模型
class DailyStatisticResponse(BaseModel):
    """日统计响应"""
    date: date = Field(..., description="日期")
    total_study_hours: float = Field(0.0, description="总学习时长")
    completed_tasks: int = Field(0, description="完成任务数")
    total_tasks: int = Field(0, description="总任务数")
    completion_rate: float = Field(0.0, description="完成率")
    focus_time: float = Field(0.0, description="专注时长")
    break_time: float = Field(0.0, description="休息时长")
    dominant_mood: Optional[str] = Field(None, description="主要心情")
    category_hours: Dict[str, float] = Field({}, description="各类型时长分布")

# 统计趋势相关模型
class WeeklyTrendResponse(BaseModel):
    """周趋势响应"""
    current_week: WeeklyOverviewResponse = Field(..., description="本周统计")
    previous_week: Optional[WeeklyOverviewResponse] = Field(None, description="上周统计")
    trend_analysis: Dict[str, Any] = Field({}, description="趋势分析")

class MonthlyTrendResponse(BaseModel):
    """月趋势响应"""
    month: str = Field(..., description="月份，如'2025-01'")
    weekly_data: List[WeeklyOverviewResponse] = Field(..., description="各周数据")
    monthly_summary: Dict[str, Any] = Field({}, description="月度汇总")

# 效率分析相关模型
class EfficiencyAnalysis(BaseModel):
    """效率分析"""
    efficiency_score: float = Field(0.0, description="效率评分")
    focus_periods: List[str] = Field([], description="高效时段")
    distraction_periods: List[str] = Field([], description="低效时段")
    improvement_suggestions: List[str] = Field([], description="改进建议")
    productivity_trend: str = Field("stable", description="生产力趋势：improving/stable/declining")

class TaskEfficiencyResponse(BaseModel):
    """任务效率响应"""
    task_id: int = Field(..., description="任务ID")
    task_name: str = Field(..., description="任务名称")
    planned_hours: float = Field(0.0, description="计划时长")
    actual_hours: float = Field(0.0, description="实际时长")
    efficiency_ratio: float = Field(0.0, description="效率比率")
    completion_rate: float = Field(0.0, description="完成率")
    avg_mood_score: float = Field(0.0, description="平均心情评分")

# 对比分析相关模型
class ComparisonPeriod(BaseModel):
    """对比时期"""
    start_date: date = Field(..., description="开始日期")
    end_date: date = Field(..., description="结束日期")
    label: str = Field(..., description="时期标签")

class ComparisonAnalysis(BaseModel):
    """对比分析"""
    periods: List[ComparisonPeriod] = Field(..., description="对比时期")
    metrics: Dict[str, List[float]] = Field({}, description="各项指标对比")
    insights: List[str] = Field([], description="分析洞察")

# 统计查询参数
class StatisticQueryParams(BaseModel):
    """统计查询参数"""
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    category: Optional[str] = Field(None, description="任务分类筛选")
    task_type: Optional[str] = Field(None, description="任务类型筛选")
    include_weekends: bool = Field(True, description="是否包含周末")
    group_by: str = Field("day", description="分组方式：day/week/month")

# 统计导出相关
class StatisticExportRequest(BaseModel):
    """统计导出请求"""
    format: str = Field("excel", description="导出格式：excel/csv/pdf")
    include_charts: bool = Field(True, description="是否包含图表")
    date_range: StatisticQueryParams = Field(..., description="日期范围")

class StatisticExportResponse(BaseModel):
    """统计导出响应"""
    success: bool = Field(True, description="导出是否成功")
    file_url: str = Field(..., description="文件下载链接")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(0, description="文件大小（字节）")
    expires_at: datetime = Field(..., description="链接过期时间") 