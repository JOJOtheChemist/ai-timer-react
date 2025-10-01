from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, date

from crud.tutor.crud_tutor import CRUDTutor
from crud.tutor.crud_tutor_review import CRUDTutorReview
from models.schemas.tutor import TutorDetailResponse, TutorListResponse

class TutorDetailService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_tutor = CRUDTutor()
        self.crud_tutor_review = CRUDTutorReview()

    async def get_tutor_detail(self, tutor_id: int, user_id: int) -> Optional[TutorDetailResponse]:
        """查询导师完整信息，关联查询服务列表、评价列表、指导数据"""
        try:
            # 获取导师基础信息和关联数据
            tutor_detail = await self.crud_tutor.get_by_id_with_relations(self.db, tutor_id)
            
            if not tutor_detail:
                return None
            
            # 校验导师状态
            if not await self._validate_tutor_status(tutor_detail):
                return None
            
            # 获取服务列表
            services = await self.get_tutor_services(tutor_id)
            
            # 获取评价列表（默认前10条）
            reviews = await self.get_tutor_reviews(tutor_id, page=1, page_size=10)
            
            # 获取指导数据
            metrics = await self.get_tutor_metrics(tutor_id)
            
            # 检查用户是否已关注此导师
            is_followed = await self._check_user_followed(tutor_id, user_id)
            
            return TutorDetailResponse(
                id=tutor_detail.id,
                name=tutor_detail.name,
                avatar=tutor_detail.avatar,
                title=tutor_detail.title,
                bio=tutor_detail.bio,
                tutor_type=tutor_detail.tutor_type,
                domains=tutor_detail.domains.split(',') if tutor_detail.domains else [],
                experience_years=tutor_detail.experience_years,
                education_background=tutor_detail.education_background,
                certifications=tutor_detail.certifications.split(',') if tutor_detail.certifications else [],
                rating=tutor_detail.rating,
                review_count=tutor_detail.review_count,
                student_count=tutor_detail.student_count,
                success_rate=tutor_detail.success_rate,
                response_rate=tutor_detail.response_rate,
                response_time=tutor_detail.response_time,
                is_verified=tutor_detail.is_verified,
                is_online=tutor_detail.is_online,
                last_active=tutor_detail.last_active,
                service_details=services,
                data_panel=metrics,
                reviews=reviews,
                is_followed=is_followed,
                created_at=tutor_detail.created_at,
                updated_at=tutor_detail.updated_at
            )
        except Exception as e:
            raise Exception(f"获取导师详情失败: {str(e)}")

    async def get_tutor_services(self, tutor_id: int) -> List[dict]:
        """获取导师的服务列表"""
        try:
            services = await self.crud_tutor.get_tutor_services(self.db, tutor_id)
            
            result = []
            for service in services:
                result.append({
                    "id": service.id,
                    "name": service.name,
                    "description": service.description,
                    "price": service.price,
                    "currency": service.currency,
                    "duration": service.duration,
                    "service_type": service.service_type,
                    "is_available": service.is_available,
                    "created_at": service.created_at
                })
            
            return result
        except Exception as e:
            raise Exception(f"获取导师服务失败: {str(e)}")

    async def get_tutor_reviews(self, tutor_id: int, page: int = 1, page_size: int = 10) -> List[dict]:
        """获取导师的学员评价列表"""
        try:
            reviews = await self.crud_tutor_review.get_multi_by_tutor(
                self.db, 
                tutor_id, 
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            result = []
            for review in reviews:
                result.append({
                    "id": review.id,
                    "reviewer_name": review.reviewer_name,
                    "reviewer_avatar": review.reviewer_avatar,
                    "rating": review.rating,
                    "content": review.content,
                    "service_name": review.service_name,
                    "is_anonymous": review.is_anonymous,
                    "created_at": review.created_at
                })
            
            return result
        except Exception as e:
            raise Exception(f"获取导师评价失败: {str(e)}")

    async def get_tutor_metrics(self, tutor_id: int) -> dict:
        """获取导师的指导数据面板"""
        try:
            metrics = await self.crud_tutor.get_tutor_metrics(self.db, tutor_id)
            
            if not metrics:
                return {
                    "total_students": 0,
                    "success_cases": 0,
                    "average_improvement": 0.0,
                    "teaching_hours": 0,
                    "monthly_active_students": 0,
                    "satisfaction_rate": 0.0
                }
            
            return {
                "total_students": metrics.total_students,
                "success_cases": metrics.success_cases,
                "average_improvement": metrics.average_improvement,
                "teaching_hours": metrics.teaching_hours,
                "monthly_active_students": metrics.monthly_active_students,
                "satisfaction_rate": metrics.satisfaction_rate,
                "last_updated": metrics.updated_at
            }
        except Exception as e:
            raise Exception(f"获取导师数据失败: {str(e)}")

    async def record_tutor_view(self, tutor_id: int, user_id: int) -> bool:
        """记录导师页面浏览次数"""
        try:
            # 检查是否已记录过（防止重复计数）
            today_viewed = await self.crud_tutor.check_user_viewed_today(
                self.db, tutor_id, user_id
            )
            
            if not today_viewed:
                # 增加浏览次数
                await self.crud_tutor.increment_views(self.db, tutor_id)
                
                # 记录用户浏览历史
                await self.crud_tutor.create_view_record(
                    self.db, tutor_id, user_id
                )
            
            return True
        except Exception as e:
            raise Exception(f"记录浏览失败: {str(e)}")

    async def get_similar_tutors(self, tutor_id: int, limit: int = 5) -> List[TutorListResponse]:
        """获取相似推荐导师（基于领域、类型等相似度）"""
        try:
            # 获取当前导师信息
            current_tutor = await self.crud_tutor.get_by_id(self.db, tutor_id)
            
            if not current_tutor:
                return []
            
            # 基于领域和类型查找相似导师
            similar_tutors = await self.crud_tutor.get_similar_tutors(
                self.db,
                tutor_type=current_tutor.tutor_type,
                domains=current_tutor.domains,
                exclude_id=tutor_id,
                limit=limit
            )
            
            # 转换为响应模型
            result = []
            for tutor in similar_tutors:
                result.append(TutorListResponse(
                    id=tutor.id,
                    name=tutor.name,
                    avatar=tutor.avatar,
                    title=tutor.title,
                    tutor_type=tutor.tutor_type,
                    domains=tutor.domains.split(',') if tutor.domains else [],
                    experience_years=tutor.experience_years,
                    rating=tutor.rating,
                    review_count=tutor.review_count,
                    student_count=tutor.student_count,
                    price_range=tutor.price_range,
                    is_verified=tutor.is_verified,
                    is_online=tutor.is_online,
                    response_rate=tutor.response_rate,
                    service_summary=tutor.service_summary,
                    created_at=tutor.created_at,
                    updated_at=tutor.updated_at
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取相似导师失败: {str(e)}")

    async def _validate_tutor_status(self, tutor) -> bool:
        """校验导师状态（如是否已认证、服务是否可用）"""
        try:
            # 检查导师是否激活
            if not tutor.is_active:
                return False
            
            # 检查导师是否被禁用
            if tutor.is_banned:
                return False
            
            return True
        except Exception:
            return False

    async def _check_user_followed(self, tutor_id: int, user_id: int) -> bool:
        """检查用户是否已关注此导师"""
        try:
            followed = await self.crud_tutor.check_user_followed_tutor(
                self.db, user_id, tutor_id
            )
            return followed
        except Exception:
            return False 