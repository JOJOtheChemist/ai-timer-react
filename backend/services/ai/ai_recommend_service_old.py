from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from crud.method.crud_method import CRUDMethod
from services.method.method_service import MethodService
from services.statistic.statistic_service import StatisticService
from models.schemas.ai import AIStudyMethodResponse

class AIRecommendService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_method = CRUDMethod()
        self.method_service = MethodService(db)
        self.statistic_service = StatisticService()
    
    async def recommend_study_method(
        self, 
        user_id: int, 
        limit: int = 5,
        category: Optional[str] = None
    ) -> List[AIStudyMethodResponse]:
        """分析用户时间表数据（调用schedule业务域接口），匹配适配的学习方法（调用method业务域接口获取方法基础信息）
        按"相关性+打卡人数"排序推荐结果"""
        try:
            # 分析用户行为特征
            user_behavior = await self.analyze_user_behavior(user_id)
            
            # 根据用户行为标签获取适配的学习方法
            suitable_methods = self.crud_method.get_suitable_by_user_behavior(
                self.db, 
                user_behavior_tags=user_behavior.get("behavior_tags", []),
                category=category,
                limit=limit * 2  # 获取更多候选方法用于排序
            )
            
            # 构建推荐响应
            recommendations = []
            for method in suitable_methods:
                # 获取方法统计数据（直接从数据库）
                checkin_count = method.checkin_count if hasattr(method, 'checkin_count') else 0
                rating = float(method.rating) if hasattr(method, 'rating') and method.rating else 0.0
                
                # 计算推荐分数（相关性 + 打卡人数 + 评分）
                relevance_score = await self._calculate_relevance_score(
                    user_behavior, method
                )
                popularity_score = min(checkin_count / 100.0, 1.0)  # 归一化到0-1
                rating_score = rating / 5.0 if rating else 0  # 归一化到0-1
                
                total_score = (relevance_score * 0.5 + 
                              popularity_score * 0.3 + 
                              rating_score * 0.2)
                
                # 生成推荐理由
                recommendation_reason = await self._generate_recommendation_reason(
                    user_behavior, method
                )
                
                # 提取适用场景
                suitable_scenarios = []
                if hasattr(method, 'scene') and method.scene:
                    suitable_scenarios = [method.scene]
                elif hasattr(method, 'steps') and method.steps:
                    suitable_scenarios = ["适合系统化学习"]
                
                recommendation = AIStudyMethodResponse(
                    method_id=method.id,
                    name=method.name,
                    description=method.description,
                    category=method.category,
                    suitable_scenarios=suitable_scenarios,
                    recommendation_reason=recommendation_reason,
                    match_score=round(total_score, 2),
                    priority=min(5, max(1, int(total_score * 5) + 1))  # 转换为1-5优先级
                )
                recommendations.append(recommendation)
            
            # 按匹配分数排序并限制数量
            recommendations.sort(key=lambda x: x.match_score, reverse=True)
            return recommendations[:limit]
        except Exception as e:
            print(f"生成学习方法推荐失败: {e}")
            return []
    
    async def analyze_user_behavior(self, user_id: int) -> Dict[str, Any]:
        """分析用户行为（基于时间表数据、学习习惯等）"""
        try:
            # 获取用户学习统计数据（简化版本，直接从数据库查询）
            from sqlalchemy import func
            from models.task import TimeSlot
            from datetime import datetime, timedelta
            
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
            analysis_data = {}
            
            # 分析复习频率（基于时间段数量）
            review_frequency = min(total_slots / 90, 1.0)  # 假设90个时间段为充分
            if review_frequency < 0.3:
                behavior_tags.append("复习不足")
                analysis_data["review_issue"] = "用户复习频率较低，建议使用艾宾浩斯遗忘曲线法"
            elif review_frequency > 0.8:
                behavior_tags.append("复习充分")
                analysis_data["review_strength"] = "用户复习习惯良好"
            
            # 分析学习时长分布
            if daily_study_hours < 2:
                behavior_tags.append("时间碎片化")
                analysis_data["time_pattern"] = "适合短时高效的学习方法"
            elif daily_study_hours > 6:
                behavior_tags.append("长时间学习")
                analysis_data["time_pattern"] = "适合深度学习方法"
            
            # 分析学习一致性（基于完成率）
            consistency_score = avg_completion / 100.0 if avg_completion > 0 else 0.5
            if consistency_score < 0.4:
                behavior_tags.append("学习不规律")
                analysis_data["consistency_issue"] = "建议使用习惯养成类方法"
            elif consistency_score > 0.8:
                behavior_tags.append("学习规律")
                analysis_data["consistency_strength"] = "学习习惯稳定"
            
            # 分析专注度（基于完成率）
            focus_score = consistency_score
            if focus_score < 0.4:
                behavior_tags.append("专注度不足")
                analysis_data["focus_issue"] = "建议使用番茄工作法等专注力训练方法"
            
            # 分析学习偏好（简化为空列表）
            preferred_subjects = []
            if len(preferred_subjects) > 0:
                behavior_tags.append(f"偏好{preferred_subjects[0]}")
                analysis_data["subject_preference"] = preferred_subjects
            
            return {
                "user_id": user_id,
                "behavior_tags": behavior_tags,
                "analysis_data": analysis_data,
                "study_stats": study_stats,
                "analysis_time": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"分析用户行为失败: {e}")
            return {
                "user_id": user_id,
                "behavior_tags": ["通用学习者"],
                "analysis_data": {},
                "study_stats": {},
                "analysis_time": datetime.now().isoformat()
            }
    
    async def explain_method_recommendation(
        self, 
        user_id: int, 
        method_id: int
    ) -> Optional[Dict[str, Any]]:
        """解释为什么推荐某个学习方法"""
        try:
            # 获取方法信息
            method = self.crud_method.get_by_id(self.db, method_id)
            if not method:
                return None
            
            # 获取用户行为分析
            user_behavior = await self.analyze_user_behavior(user_id)
            
            # 生成详细解释
            explanation = {
                "method_id": method_id,
                "method_name": method.name,
                "user_behavior_summary": user_behavior.get("behavior_tags", []),
                "recommendation_reasons": [],
                "matching_analysis": {},
                "expected_benefits": [],
                "usage_suggestions": []
            }
            
            # 根据用户行为标签生成具体解释
            behavior_tags = user_behavior.get("behavior_tags", [])
            
            if "复习不足" in behavior_tags and "艾宾浩斯" in method.name:
                explanation["recommendation_reasons"].append(
                    "您的复习频率较低，艾宾浩斯遗忘曲线法能帮助您建立科学的复习节奏"
                )
                explanation["expected_benefits"].append("提高记忆保持率")
                explanation["usage_suggestions"].append("建议按照1-3-7-15天的复习周期执行")
            
            if "时间碎片化" in behavior_tags and method.estimated_time <= 30:
                explanation["recommendation_reasons"].append(
                    "您的学习时间较为碎片化，这个方法适合短时间内完成"
                )
                explanation["expected_benefits"].append("充分利用碎片时间")
            
            if "专注度不足" in behavior_tags and "番茄" in method.name:
                explanation["recommendation_reasons"].append(
                    "您的专注度有待提升，番茄工作法能帮助您提高专注力"
                )
                explanation["expected_benefits"].append("提升学习专注度")
                explanation["usage_suggestions"].append("建议从25分钟专注时间开始")
            
            # 添加方法的热门程度说明
            checkin_count = await self.statistic_service.count_method_checkins(
                self.db, method_id
            )
            if checkin_count > 100:
                explanation["recommendation_reasons"].append(
                    f"该方法已有{checkin_count}人使用，效果得到验证"
                )
            
            return explanation
        except Exception as e:
            print(f"生成推荐解释失败: {e}")
            return None
    
    async def get_personalized_recommendations(self, user_id: int) -> Dict[str, Any]:
        """获取个性化推荐（综合学习方法、任务安排等）"""
        try:
            # 获取学习方法推荐
            method_recommendations = await self.recommend_study_method(user_id, limit=3)
            
            # 获取用户行为分析
            user_behavior = await self.analyze_user_behavior(user_id)
            
            # 生成学习建议
            study_suggestions = await self._generate_study_suggestions(user_behavior)
            
            # 生成时间安排建议
            schedule_suggestions = await self._generate_schedule_suggestions(user_behavior)
            
            return {
                "user_id": user_id,
                "method_recommendations": method_recommendations,
                "study_suggestions": study_suggestions,
                "schedule_suggestions": schedule_suggestions,
                "behavior_analysis": user_behavior,
                "generated_at": datetime.now().isoformat()
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
        """提交推荐反馈，用于改进推荐算法"""
        try:
            # 这里应该保存反馈数据到数据库
            feedback_data = {
                "user_id": user_id,
                "method_id": method_id,
                "feedback_type": feedback_type,
                "rating": rating,
                "comment": comment,
                "create_time": datetime.now()
            }
            
            # 模拟保存反馈（实际应该保存到recommendation_feedback表）
            print(f"收到推荐反馈: {feedback_data}")
            
            return True
        except Exception as e:
            print(f"提交推荐反馈失败: {e}")
            return False
    
    async def _calculate_relevance_score(
        self, 
        user_behavior: Dict[str, Any], 
        method: Any
    ) -> float:
        """计算方法与用户的相关性分数"""
        try:
            score = 0.5  # 基础分数
            behavior_tags = user_behavior.get("behavior_tags", [])
            method_tags = method.tags or []
            
            # 根据行为标签和方法标签的匹配度计算分数
            matching_tags = set(behavior_tags) & set(method_tags)
            if matching_tags:
                score += len(matching_tags) * 0.2
            
            # 根据具体的行为问题匹配方法
            if "复习不足" in behavior_tags and "艾宾浩斯" in method.name:
                score += 0.3
            
            if "专注度不足" in behavior_tags and "番茄" in method.name:
                score += 0.3
            
            if "时间碎片化" in behavior_tags and method.estimated_time <= 30:
                score += 0.2
            
            return min(score, 1.0)  # 限制在0-1范围内
        except Exception:
            return 0.5
    
    async def _generate_recommendation_reason(
        self, 
        user_behavior: Dict[str, Any], 
        method: Any
    ) -> str:
        """生成推荐理由"""
        try:
            behavior_tags = user_behavior.get("behavior_tags", [])
            reasons = []
            
            if "复习不足" in behavior_tags and "艾宾浩斯" in method.name:
                reasons.append("根据您的复习频率分析，推荐使用科学的复习方法")
            
            if "专注度不足" in behavior_tags and "番茄" in method.name:
                reasons.append("您的专注度有提升空间，此方法专门训练专注力")
            
            if "时间碎片化" in behavior_tags and method.estimated_time <= 30:
                reasons.append("适合您的碎片化时间学习模式")
            
            if not reasons:
                reasons.append("基于您的学习习惯，这个方法可能对您有帮助")
            
            return "；".join(reasons)
        except Exception:
            return "推荐给您尝试"
    
    async def _generate_study_suggestions(self, user_behavior: Dict[str, Any]) -> List[str]:
        """生成学习建议"""
        suggestions = []
        behavior_tags = user_behavior.get("behavior_tags", [])
        
        if "复习不足" in behavior_tags:
            suggestions.append("建议增加复习频率，可以尝试间隔重复学习法")
        
        if "专注度不足" in behavior_tags:
            suggestions.append("建议使用番茄工作法，每25分钟专注学习后休息5分钟")
        
        if "时间碎片化" in behavior_tags:
            suggestions.append("充分利用碎片时间，可以准备一些短时间内能完成的学习任务")
        
        if "学习不规律" in behavior_tags:
            suggestions.append("建议制定固定的学习时间表，培养良好的学习习惯")
        
        return suggestions
    
    async def _generate_schedule_suggestions(self, user_behavior: Dict[str, Any]) -> List[str]:
        """生成时间安排建议"""
        suggestions = []
        study_stats = user_behavior.get("study_stats", {})
        
        daily_hours = study_stats.get("daily_average_hours", 0)
        if daily_hours < 2:
            suggestions.append("建议每天至少安排2小时的专门学习时间")
        elif daily_hours > 8:
            suggestions.append("学习时间较长，注意劳逸结合，避免过度疲劳")
        
        consistency_score = study_stats.get("consistency_score", 0.5)
        if consistency_score < 0.4:
            suggestions.append("建议固定每天的学习时间段，提高学习的规律性")
        
        return suggestions 