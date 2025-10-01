from sqlalchemy.orm import Session
from typing import Dict, Any, List

from models.schemas.message import UnreadStatsResponse
from crud.message.crud_message_stat import crud_message_stat

class MessageStatService:
    """消息统计服务层"""
    
    def calculate_unread_stats(self, db: Session, user_id: int) -> UnreadStatsResponse:
        """统计用户所有类型消息的未读数量（tutor/private/system）"""
        stats = crud_message_stat.count_unread_by_all_types(db, user_id)
        
        return UnreadStatsResponse(
            tutor_count=stats["tutor_count"],
            private_count=stats["private_count"],
            system_count=stats["system_count"],
            total_count=stats["total_count"]
        )
    
    def get_message_overview(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 7
    ) -> Dict[str, Any]:
        """获取消息概览统计"""
        # 获取基础统计
        period_stats = crud_message_stat.get_message_stats_by_period(db, user_id, days)
        
        # 获取未读统计
        unread_stats = self.calculate_unread_stats(db, user_id)
        
        # 获取回复率统计
        response_stats = crud_message_stat.get_response_rate_stats(db, user_id)
        
        # 获取发送方统计
        sender_stats = crud_message_stat.get_sender_stats(db, user_id, limit=5)
        
        return {
            "period_stats": period_stats,
            "unread_stats": unread_stats.dict(),
            "response_stats": response_stats,
            "top_senders": sender_stats,
            "summary": {
                "total_messages": period_stats["total_messages"],
                "read_rate": period_stats["read_rate"],
                "response_rate": response_stats["response_rate"],
                "most_active_type": self._get_most_active_message_type(period_stats["type_stats"])
            }
        }
    
    def get_message_activity_analysis(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取消息活动分析"""
        activity_trend = crud_message_stat.get_message_activity_trend(db, user_id, days)
        
        # 分析活跃时段
        hourly_data = activity_trend["hourly_distribution"]
        peak_hours = self._analyze_peak_hours(hourly_data)
        
        # 分析周趋势
        weekly_data = activity_trend["weekly_trend"]
        trend_analysis = self._analyze_weekly_trend(weekly_data)
        
        return {
            "activity_trend": activity_trend,
            "peak_hours": peak_hours,
            "trend_analysis": trend_analysis,
            "recommendations": self._generate_activity_recommendations(peak_hours, trend_analysis)
        }
    
    def get_detailed_type_stats(
        self, 
        db: Session, 
        user_id: int, 
        days: int = 30
    ) -> Dict[str, Any]:
        """获取详细的消息类型统计"""
        period_stats = crud_message_stat.get_message_stats_by_period(db, user_id, days)
        type_stats = period_stats["type_stats"]
        
        # 计算各类型占比
        total = sum(type_stats.values())
        type_percentages = {
            msg_type: (count / total * 100) if total > 0 else 0
            for msg_type, count in type_stats.items()
        }
        
        # 分析各类型的特点
        type_analysis = {}
        for msg_type in [0, 1, 2]:
            count = type_stats.get(msg_type, 0)
            percentage = type_percentages.get(msg_type, 0)
            
            type_analysis[msg_type] = {
                "count": count,
                "percentage": round(percentage, 1),
                "status": self._get_type_status(msg_type, count, percentage),
                "suggestion": self._get_type_suggestion(msg_type, count, percentage)
            }
        
        return {
            "type_stats": type_stats,
            "type_percentages": type_percentages,
            "type_analysis": type_analysis,
            "period_days": days,
            "total_messages": total
        }
    
    def _get_most_active_message_type(self, type_stats: Dict[str, int]) -> str:
        """获取最活跃的消息类型"""
        if not type_stats:
            return "无"
        
        max_type = max(type_stats.items(), key=lambda x: x[1])
        return max_type[0]
    
    def _analyze_peak_hours(self, hourly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析消息活跃的高峰时段"""
        if not hourly_data:
            return {"peak_hour": None, "peak_count": 0, "activity_level": "低"}
        
        # 找出最活跃的时段
        peak_data = max(hourly_data, key=lambda x: x["count"])
        
        # 分析活跃程度
        total_messages = sum(item["count"] for item in hourly_data)
        avg_per_hour = total_messages / 24 if total_messages > 0 else 0
        
        activity_level = "低"
        if peak_data["count"] > avg_per_hour * 2:
            activity_level = "高"
        elif peak_data["count"] > avg_per_hour * 1.5:
            activity_level = "中"
        
        return {
            "peak_hour": peak_data["hour"],
            "peak_count": peak_data["count"],
            "activity_level": activity_level,
            "avg_per_hour": round(avg_per_hour, 1)
        }
    
    def _analyze_weekly_trend(self, weekly_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析周趋势"""
        if len(weekly_data) < 2:
            return {"trend": "无法分析", "change_rate": 0}
        
        # 计算趋势
        recent_week = weekly_data[-1]["count"]
        previous_week = weekly_data[-2]["count"]
        
        if previous_week == 0:
            change_rate = 100 if recent_week > 0 else 0
        else:
            change_rate = ((recent_week - previous_week) / previous_week) * 100
        
        trend = "上升" if change_rate > 5 else "下降" if change_rate < -5 else "稳定"
        
        return {
            "trend": trend,
            "change_rate": round(change_rate, 1),
            "recent_count": recent_week,
            "previous_count": previous_week
        }
    
    def _generate_activity_recommendations(
        self, 
        peak_hours: Dict[str, Any], 
        trend_analysis: Dict[str, Any]
    ) -> List[str]:
        """生成活动建议"""
        recommendations = []
        
        # 基于高峰时段的建议
        if peak_hours["activity_level"] == "高":
            recommendations.append(f"您在{peak_hours['peak_hour']}点最活跃，建议在此时段处理重要消息")
        
        # 基于趋势的建议
        if trend_analysis["trend"] == "上升":
            recommendations.append("消息量呈上升趋势，建议及时处理避免积压")
        elif trend_analysis["trend"] == "下降":
            recommendations.append("消息量有所减少，可以关注消息质量")
        
        return recommendations
    
    def _get_type_status(self, msg_type: str, count: int, percentage: float) -> str:
        """获取消息类型状态"""
        if count == 0:
            return "无消息"
        elif percentage > 50:
            return "主要类型"
        elif percentage > 20:
            return "常见类型"
        else:
            return "较少类型"
    
    def _get_type_suggestion(self, msg_type: str, count: int, percentage: float) -> str:
        """获取消息类型建议"""
        if msg_type == 0 and percentage > 40:
            return "导师反馈较多，建议及时查看和回复"
        elif msg_type == 1 and percentage > 60:
            return "私信较多，注意保持良好的沟通"
        elif msg_type == 2 and percentage > 50:
            return "系统通知较多，可考虑开启自动已读"
        else:
            return "消息分布正常"

# 创建服务实例
message_stat_service = MessageStatService() 