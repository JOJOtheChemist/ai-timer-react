from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from crud.tutor.crud_tutor import crud_tutor
from models.tutor import Tutor, TutorService, TutorReview
from models.schemas.tutor import (
    TutorListResponse,
    TutorFilterParams,
    TutorSearchResponse,
    TutorStatsResponse
)

class TutorService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_tutor = crud_tutor

    async def get_tutor_list(
        self, 
        filters: TutorFilterParams, 
        sort_by: str = "rating",
        page: int = 1, 
        page_size: int = 20
    ) -> List[TutorListResponse]:
        """按筛选条件+排序规则查询导师列表，计算分页信息"""
        try:
            # 解析筛选参数
            parsed_filters = {
                'tutor_type': filters.tutor_type,
                'domain': filters.domain,
                'price_range': filters.price_range
            }
            
            # 从数据库查询
            tutors = await self.crud_tutor.get_multi_by_filters(
                self.db,
                filters=parsed_filters,
                sort_by=sort_by,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # 转换为响应模型
            result = []
            for tutor in tutors:
                # 查询该导师的最低和最高服务价格
                price_stats = self.db.query(
                    func.min(TutorService.price).label('min_price'),
                    func.max(TutorService.price).label('max_price')
                ).filter(
                    TutorService.tutor_id == tutor.id,
                    TutorService.is_active == 1
                ).first()
                
                # 查询评价数量
                review_count = self.db.query(func.count(TutorReview.id)).filter(
                    TutorReview.tutor_id == tutor.id
                ).scalar() or 0
                
                result.append(TutorListResponse(
                    id=tutor.id,
                    username=tutor.username,
                    avatar=tutor.avatar,
                    type=tutor.type,
                    domain=tutor.domain,
                    education=tutor.education,
                    experience=tutor.experience,
                    rating=tutor.rating,
                    student_count=tutor.student_count,
                    success_rate=tutor.success_rate,
                    monthly_guide_count=tutor.monthly_guide_count,
                    min_price=price_stats.min_price if price_stats else None,
                    max_price=price_stats.max_price if price_stats else None,
                    review_count=review_count,
                    create_time=tutor.create_time,
                    update_time=tutor.update_time
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取导师列表失败: {str(e)}")

    async def search_tutors(
        self, 
        keyword: str, 
        page: int = 1, 
        page_size: int = 20
    ) -> List[TutorSearchResponse]:
        """按关键词搜索导师"""
        try:
            tutors = await self.crud_tutor.search_by_keyword(
                self.db,
                keyword=keyword,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # 转换为响应模型
            result = []
            for tutor in tutors:
                result.append(TutorSearchResponse(
                    id=tutor.id,
                    username=tutor.username,
                    avatar=tutor.avatar,
                    domain=tutor.domain,
                    education=tutor.education,
                    rating=tutor.rating,
                    student_count=tutor.student_count,
                    type=tutor.type
                ))
            
            return result
        except Exception as e:
            raise Exception(f"搜索导师失败: {str(e)}")

    async def get_tutor_domains(self) -> List[str]:
        """获取所有导师擅长领域列表"""
        try:
            domains = await self.crud_tutor.get_tutor_domains(self.db)
            return domains
        except Exception as e:
            raise Exception(f"获取导师领域失败: {str(e)}")

    async def get_tutor_types(self) -> List[str]:
        """获取所有导师类型列表"""
        try:
            types = await self.crud_tutor.get_tutor_types(self.db)
            return types
        except Exception as e:
            raise Exception(f"获取导师类型失败: {str(e)}")

    async def get_tutor_stats_summary(self) -> TutorStatsResponse:
        """获取导师统计摘要"""
        try:
            stats = await self.crud_tutor.get_tutor_stats_summary(self.db)
            return TutorStatsResponse(**stats)
        except Exception as e:
            raise Exception(f"获取导师统计失败: {str(e)}")

    async def get_popular_tutors(self, limit: int = 5) -> List[TutorListResponse]:
        """获取热门推荐导师"""
        try:
            tutors = await self.crud_tutor.get_popular_tutors(self.db, limit=limit)
            
            # 转换为响应模型
            result = []
            for tutor in tutors:
                # 查询该导师的最低和最高服务价格
                price_stats = self.db.query(
                    func.min(TutorService.price).label('min_price'),
                    func.max(TutorService.price).label('max_price')
                ).filter(
                    TutorService.tutor_id == tutor.id,
                    TutorService.is_active == 1
                ).first()
                
                # 查询评价数量
                review_count = self.db.query(func.count(TutorReview.id)).filter(
                    TutorReview.tutor_id == tutor.id
                ).scalar() or 0
                
                result.append(TutorListResponse(
                    id=tutor.id,
                    username=tutor.username,
                    avatar=tutor.avatar,
                    type=tutor.type,
                    domain=tutor.domain,
                    education=tutor.education,
                    experience=tutor.experience,
                    rating=tutor.rating,
                    student_count=tutor.student_count,
                    success_rate=tutor.success_rate,
                    monthly_guide_count=tutor.monthly_guide_count,
                    min_price=price_stats.min_price if price_stats else None,
                    max_price=price_stats.max_price if price_stats else None,
                    review_count=review_count,
                    create_time=tutor.create_time,
                    update_time=tutor.update_time
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取热门导师失败: {str(e)}") 