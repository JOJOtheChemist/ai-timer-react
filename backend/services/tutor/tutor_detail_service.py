from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from crud.tutor.crud_tutor import crud_tutor
from models.schemas.tutor import (
    TutorDetailResponse,
    TutorServiceResponse,
    TutorReviewResponse,
    TutorMetricsResponse
)

class TutorDetailService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_tutor = crud_tutor

    async def get_tutor_detail(
        self,
        tutor_id: int,
        user_id: Optional[int] = None
    ) -> Optional[TutorDetailResponse]:
        """获取导师完整详情"""
        try:
            # 查询导师基础信息
            tutor = await self.crud_tutor.get_by_id_with_relations(self.db, tutor_id)
            if not tutor:
                return None
            
            # 查询服务列表
            services = await self.crud_tutor.get_tutor_services(self.db, tutor_id)
            services_data = [
                {
                    "id": s.id,
                    "name": s.name,
                    "price": s.price,
                    "description": s.description,
                    "service_type": s.service_type
                }
                for s in services
            ]
            
            # 查询评价列表（前5条）
            reviews = await self.crud_tutor.get_tutor_reviews(self.db, tutor_id, skip=0, limit=5)
            reviews_data = [
                {
                    "id": r.id,
                    "reviewer_name": r.reviewer_name,
                    "rating": r.rating,
                    "content": r.content,
                    "create_time": r.create_time.isoformat()
                }
                for r in reviews
            ]
            
            return TutorDetailResponse(
                id=tutor.id,
                username=tutor.username,
                avatar=tutor.avatar,
                type=tutor.type,
                domain=tutor.domain,
                education=tutor.education,
                experience=tutor.experience,
                work_experience=tutor.work_experience,
                philosophy=tutor.philosophy,
                rating=tutor.rating,
                student_count=tutor.student_count,
                success_rate=tutor.success_rate,
                monthly_guide_count=tutor.monthly_guide_count,
                status=tutor.status,
                create_time=tutor.create_time,
                update_time=tutor.update_time,
                services=services_data,
                reviews=reviews_data
            )
        except Exception as e:
            raise Exception(f"获取导师详情失败: {str(e)}")

    async def get_tutor_services(self, tutor_id: int) -> List[TutorServiceResponse]:
        """获取导师的服务列表"""
        try:
            services = await self.crud_tutor.get_tutor_services(self.db, tutor_id)
            return [TutorServiceResponse.from_orm(s) for s in services]
        except Exception as e:
            raise Exception(f"获取导师服务失败: {str(e)}")

    async def get_tutor_reviews(
        self,
        tutor_id: int,
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取导师的学员评价列表"""
        try:
            skip = (page - 1) * page_size
            reviews = await self.crud_tutor.get_tutor_reviews(
                self.db, tutor_id, skip=skip, limit=page_size
            )
            
            # 计算总数
            from models.tutor import TutorReview
            from sqlalchemy import func
            total = self.db.query(func.count(TutorReview.id)).filter(
                TutorReview.tutor_id == tutor_id
            ).scalar() or 0
            
            return {
                "reviews": [TutorReviewResponse.from_orm(r) for r in reviews],
                "total": total,
                "page": page,
                "page_size": page_size,
                "has_next": page * page_size < total
            }
        except Exception as e:
            raise Exception(f"获取导师评价失败: {str(e)}")

    async def get_tutor_metrics(self, tutor_id: int) -> TutorMetricsResponse:
        """获取导师的指导数据面板"""
        try:
            metrics = await self.crud_tutor.get_tutor_metrics(self.db, tutor_id)
            return TutorMetricsResponse(**metrics)
        except Exception as e:
            raise Exception(f"获取导师数据失败: {str(e)}")

    async def record_tutor_view(self, tutor_id: int, user_id: int) -> bool:
        """记录导师页面浏览次数"""
        try:
            return await self.crud_tutor.record_tutor_view(self.db, tutor_id, user_id)
        except Exception as e:
            raise Exception(f"记录浏览失败: {str(e)}")

    async def get_similar_tutors(
        self,
        tutor_id: int,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """获取相似推荐导师"""
        try:
            tutors = await self.crud_tutor.get_similar_tutors(self.db, tutor_id, limit)
            
            return [
                {
                    "id": t.id,
                    "username": t.username,
                    "avatar": t.avatar,
                    "domain": t.domain,
                    "rating": t.rating,
                    "student_count": t.student_count,
                    "type": t.type
                }
                for t in tutors
            ]
        except Exception as e:
            raise Exception(f"获取相似导师失败: {str(e)}") 