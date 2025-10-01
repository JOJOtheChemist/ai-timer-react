from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.schemas.ai import AIStudyMethodResponse, UserBehaviorAnalysisResponse
from models.task import TimeSlot


class AIRecommendService:
    def __init__(self, db: Session):
        self.db = db
    
    async def recommend_study_method(
        self, 
        user_id: int, 
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[AIStudyMethodResponse]:
        """推荐学习方法"""
        try:
            # 从数据库获取学习方法
            from models.statistic import StudyMethod
            
            query = self.db.query(StudyMethod).filter(StudyMethod.status == 1)
            if category:
                query = query.filter(StudyMethod.category == category)
            
            methods = query.order_by(StudyMethod.checkin_count.desc()).limit(limit).all()
            
            # 构建推荐响应
            recommendations = []
            for idx, method in enumerate(methods):
                suitable_scenarios = []
                if method.scene:
                    suitable_scenarios = [method.scene]
                else:
                    suitable_scenarios = ["适合系统化学习"]
                
                recommendation = AIStudyMethodResponse(
                    method_id=method.id,
                    name=method.name,
                    description=method.description,
                    category=method.category,
                    suitable_scenarios=suitable_scenarios,
                    recommendation_reason=f"这个方法已有{method.checkin_count}人打卡，评分{method.rating}，适合你当前的学习需求",
                    match_score=0.8 - (idx * 0.1),  # 简单的分数递减
                    priority=5 - idx if idx < 5 else 1
                )
                recommendations.append(recommendation)
            
            return recommendations
        except Exception as e:
            print(f"推荐学习方法失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    async def analyze_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """分析用户行为"""
        try:
            # 统计最近30天的学习数据
            thirty_days_ago = datetime.now() - timedelta(days=30)
            
            stats_query = self.db.query(
                func.count(TimeSlot.id).label('total_slots'),
                func.sum(TimeSlot.duration_minutes).label('total_minutes'),
                func.avg(TimeSlot.completion_rate).label('avg_completion')
            ).filter(
                TimeSlot.user_id == user_id,
                TimeSlot.start_time >= thirty_days_ago
            ).first()
            
            total_slots = stats_query.total_slots or 0
            total_minutes = float(stats_query.total_minutes or 0)
            avg_completion = float(stats_query.avg_completion or 0)
            daily_study_hours = (total_minutes / 60) / 30 if total_minutes > 0 else 0
            
            # 分析学习模式
            behavior_tags = []
            if total_slots < 30:
                behavior_tags.append("学习频率较低")
            if daily_study_hours < 2:
                behavior_tags.append("时间碎片化")
            if avg_completion < 40:
                behavior_tags.append("完成率较低")
            
            return {
                "user_id": user_id,
                "behavior_tags": behavior_tags,
                "total_study_sessions": total_slots,
                "daily_average_hours": round(daily_study_hours, 2),
                "average_completion_rate": round(avg_completion, 2),
                "analysis_time": datetime.now()
            }
        except Exception as e:
            print(f"分析用户行为失败: {e}")
            return {
                "user_id": user_id,
                "behavior_tags": [],
                "total_study_sessions": 0,
                "daily_average_hours": 0,
                "average_completion_rate": 0,
                "analysis_time": datetime.now()
            }
    
    async def explain_method_recommendation(
        self, 
        user_id: int, 
        method_id: int
    ) -> Optional[Dict[str, Any]]:
        """解释推荐理由"""
        try:
            from models.statistic import StudyMethod
            
            method = self.db.query(StudyMethod).filter(StudyMethod.id == method_id).first()
            if not method:
                return None
            
            user_behavior = await self.analyze_user_behavior(user_id)
            
            return {
                "method_id": method_id,
                "method_name": method.name,
                "explanation": f"{method.name}是一个经过{method.checkin_count}人验证的有效学习方法，评分达到{method.rating}",
                "user_behavior_insights": user_behavior.get("behavior_tags", []),
                "expected_benefits": ["提高学习效率", "养成良好习惯", "系统化学习"],
                "implementation_tips": ["每天坚持", "记录进度", "及时复习"]
            }
        except Exception as e:
            print(f"解释推荐理由失败: {e}")
            return None
    
    async def get_personalized_recommendations(self, user_id: int) -> Dict[str, Any]:
        """获取个性化推荐"""
        try:
            method_recommendations = await self.recommend_study_method(user_id, limit=3)
            user_behavior = await self.analyze_user_behavior(user_id)
            
            return {
                "user_id": user_id,
                "study_methods": method_recommendations,
                "task_suggestions": ["每天固定时间学习", "使用番茄工作法"],
                "schedule_optimization": {"建议": "合理分配学习时间"},
                "motivational_tips": ["坚持就是胜利", "每天进步一点点"],
                "behavior_analysis": user_behavior
            }
        except Exception as e:
            print(f"获取个性化推荐失败: {e}")
            return {}
    
    async def submit_recommendation_feedback(
        self, 
        user_id: int, 
        method_id: int,
        feedback_type: str,
        rating: Optional[int] = None,
        comment: Optional[str] = None
    ) -> bool:
        """提交推荐反馈"""
        try:
            # 这里可以保存反馈到数据库
            print(f"用户{user_id}对方法{method_id}的反馈: {feedback_type}, 评分: {rating}")
            return True
        except Exception as e:
            print(f"提交反馈失败: {e}")
            return False 