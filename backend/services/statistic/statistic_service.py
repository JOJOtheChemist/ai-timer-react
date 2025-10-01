from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from crud.statistic.crud_statistic import crud_statistic
from models.schemas.statistic import (
    WeeklyOverviewResponse, WeeklyChartResponse, 
    CategoryHours, DailyHours
)

class StatisticService:
    """统计服务"""
    
    def calculate_weekly_overview(self, db: Session, user_id: int, year_week: Optional[str] = None) -> WeeklyOverviewResponse:
        """计算本周统计概览"""
        return crud_statistic.calculate_weekly_overview(db=db, user_id=user_id, year_week=year_week)
    
    def generate_weekly_chart_data(self, db: Session, user_id: int, year_week: Optional[str] = None) -> WeeklyChartResponse:
        """生成本周图表数据"""
        chart_data = crud_statistic.generate_weekly_chart_data(db=db, user_id=user_id, year_week=year_week)
        
        return WeeklyChartResponse(
            daily_chart=chart_data["daily_chart"],
            category_chart=chart_data["category_chart"],
            daily_details=chart_data["daily_details"],
            category_details=chart_data["category_details"]
        )
    
    def get_weekly_task_hours(self, db: Session, user_id: int, year_week: Optional[str] = None) -> Dict[str, float]:
        """获取本周各任务时长"""
        return crud_statistic.get_weekly_task_hours(db=db, user_id=user_id, year_week=year_week)
    
    def get_weekly_category_hours(self, db: Session, user_id: int, year_week: Optional[str] = None) -> Dict[str, float]:
        """获取本周各类型任务总时长"""
        return crud_statistic.get_weekly_category_hours(db=db, user_id=user_id, year_week=year_week)
    
    def get_efficiency_analysis(self, db: Session, user_id: int, days: int = 7) -> Dict[str, Any]:
        """获取效率分析"""
        # 这里可以实现更复杂的效率分析逻辑
        # 目前返回简化版本
        
        # 获取本周概览
        overview = self.calculate_weekly_overview(db, user_id)
        
        # 计算效率评分（基于完成率和AI采纳率）
        efficiency_score = (overview.ai_accept_rate + 
                          self._calculate_completion_rate(overview.high_freq_complete) + 
                          self._calculate_completion_rate(overview.overcome_complete)) / 3
        
        return {
            "efficiency_score": efficiency_score,
            "focus_periods": ["09:00-11:00", "14:00-16:00"],  # 模拟数据
            "distraction_periods": ["13:00-14:00", "17:00-18:00"],
            "improvement_suggestions": [
                "建议在上午安排重要任务",
                "午休后适当调整学习强度",
                "保持规律的作息时间"
            ],
            "productivity_trend": "improving" if efficiency_score > 70 else "stable"
        }
    
    def get_mood_trend_analysis(self, db: Session, user_id: int, days: int = 7) -> Dict[str, Any]:
        """获取心情趋势分析"""
        from crud.schedule.crud_time_slot import crud_mood_record
        from datetime import timedelta
        
        end_date = date.today()
        start_date = end_date - timedelta(days=days-1)
        
        mood_stats = crud_mood_record.get_mood_statistics(
            db=db, user_id=user_id, start_date=start_date, end_date=end_date
        )
        
        return {
            "dominant_mood": mood_stats.get("dominant_mood"),
            "mood_distribution": mood_stats.get("mood_distribution", {}),
            "total_records": mood_stats.get("total_records", 0),
            "mood_trend": self._analyze_mood_trend(mood_stats.get("mood_distribution", {})),
            "suggestions": self._get_mood_suggestions(mood_stats.get("dominant_mood"))
        }
    
    def get_comparison_analysis(self, db: Session, user_id: int, current_week: str, previous_week: str) -> Dict[str, Any]:
        """获取对比分析"""
        current_overview = crud_statistic.calculate_weekly_overview(db, user_id, current_week)
        previous_overview = crud_statistic.calculate_weekly_overview(db, user_id, previous_week)
        
        # 计算变化率
        study_hours_change = self._calculate_change_rate(
            current_overview.total_study_hours, 
            previous_overview.total_study_hours
        )
        
        ai_accept_change = current_overview.ai_accept_rate - previous_overview.ai_accept_rate
        
        return {
            "current_week": current_overview,
            "previous_week": previous_overview,
            "changes": {
                "study_hours_change": study_hours_change,
                "ai_accept_change": ai_accept_change,
                "trend": "improving" if study_hours_change > 0 else "declining" if study_hours_change < 0 else "stable"
            },
            "insights": self._generate_comparison_insights(current_overview, previous_overview)
        }
    
    def _calculate_completion_rate(self, completion_string: str) -> float:
        """从完成情况字符串计算完成率"""
        try:
            completed, total = map(int, completion_string.split('/'))
            return (completed / total * 100) if total > 0 else 0.0
        except:
            return 0.0
    
    def _calculate_change_rate(self, current: float, previous: float) -> float:
        """计算变化率"""
        if previous == 0:
            return 100.0 if current > 0 else 0.0
        return ((current - previous) / previous) * 100
    
    def _analyze_mood_trend(self, mood_distribution: Dict[str, int]) -> str:
        """分析心情趋势"""
        if not mood_distribution:
            return "stable"
        
        positive_moods = mood_distribution.get("happy", 0) + mood_distribution.get("excited", 0) + mood_distribution.get("focused", 0)
        negative_moods = mood_distribution.get("tired", 0) + mood_distribution.get("stressed", 0)
        
        if positive_moods > negative_moods * 1.5:
            return "positive"
        elif negative_moods > positive_moods * 1.5:
            return "negative"
        else:
            return "stable"
    
    def _get_mood_suggestions(self, dominant_mood: Optional[str]) -> List[str]:
        """根据主要心情提供建议"""
        suggestions_map = {
            "tired": ["保证充足睡眠", "适当增加休息时间", "考虑调整学习强度"],
            "stressed": ["学会放松技巧", "合理安排任务优先级", "寻求帮助和支持"],
            "happy": ["保持当前状态", "可以适当增加学习挑战"],
            "focused": ["很好的专注状态", "继续保持当前学习节奏"],
            "excited": ["利用高涨情绪提高效率", "注意保持持续性"]
        }
        
        return suggestions_map.get(dominant_mood, ["保持规律的学习习惯"])
    
    def _generate_comparison_insights(self, current: WeeklyOverviewResponse, previous: WeeklyOverviewResponse) -> List[str]:
        """生成对比分析洞察"""
        insights = []
        
        if current.total_study_hours > previous.total_study_hours:
            insights.append(f"本周学习时长增加了{current.total_study_hours - previous.total_study_hours:.1f}小时")
        elif current.total_study_hours < previous.total_study_hours:
            insights.append(f"本周学习时长减少了{previous.total_study_hours - current.total_study_hours:.1f}小时")
        
        if current.ai_accept_rate > previous.ai_accept_rate:
            insights.append(f"AI推荐采纳率提升了{current.ai_accept_rate - previous.ai_accept_rate}%")
        elif current.ai_accept_rate < previous.ai_accept_rate:
            insights.append(f"AI推荐采纳率下降了{previous.ai_accept_rate - current.ai_accept_rate}%")
        
        if not insights:
            insights.append("本周表现与上周基本持平")
        
        return insights

# 创建服务实例
statistic_service = StatisticService() 