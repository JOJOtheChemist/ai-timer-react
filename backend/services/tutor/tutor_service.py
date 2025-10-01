from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from crud.tutor.crud_tutor import CRUDTutor
from models.schemas.tutor import (
    TutorListResponse,
    TutorFilterParams,
    TutorSearchResponse
)

class TutorService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_tutor = CRUDTutor()

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
            parsed_filters = await self.parse_filters(filters)
            
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
            raise Exception(f"获取导师列表失败: {str(e)}")

    async def search_tutors(
        self, 
        keyword: str, 
        page: int = 1, 
        page_size: int = 20
    ) -> List[TutorSearchResponse]:
        """按关键词模糊匹配导师（姓名/领域）"""
        try:
            # 执行搜索
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
                    name=tutor.name,
                    avatar=tutor.avatar,
                    title=tutor.title,
                    tutor_type=tutor.tutor_type,
                    domains=tutor.domains.split(',') if tutor.domains else [],
                    rating=tutor.rating,
                    review_count=tutor.review_count,
                    price_range=tutor.price_range,
                    is_verified=tutor.is_verified,
                    match_score=getattr(tutor, 'match_score', 1.0),  # 搜索相关性评分
                    highlight_fields=getattr(tutor, 'highlight_fields', [])  # 高亮字段
                ))
            
            return result
        except Exception as e:
            raise Exception(f"搜索导师失败: {str(e)}")

    async def get_tutor_domains(self) -> List[str]:
        """获取所有导师擅长领域列表"""
        try:
            domains = await self.crud_tutor.get_all_domains(self.db)
            return domains
        except Exception as e:
            raise Exception(f"获取导师领域失败: {str(e)}")

    async def get_tutor_types(self) -> List[str]:
        """获取所有导师类型列表"""
        try:
            types = await self.crud_tutor.get_all_types(self.db)
            return types
        except Exception as e:
            raise Exception(f"获取导师类型失败: {str(e)}")

    async def get_tutor_stats_summary(self) -> dict:
        """获取导师统计摘要"""
        try:
            # 获取总导师数
            total_tutors = await self.crud_tutor.count_total_tutors(self.db)
            
            # 获取类型统计
            type_stats = await self.crud_tutor.count_by_type(self.db)
            
            # 获取在线导师数
            online_tutors = await self.crud_tutor.count_online_tutors(self.db)
            
            # 获取认证导师数
            verified_tutors = await self.crud_tutor.count_verified_tutors(self.db)
            
            # 获取最近7天新增导师数
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_tutors = await self.crud_tutor.count_tutors_since(self.db, seven_days_ago)
            
            return {
                "total_tutors": total_tutors,
                "online_tutors": online_tutors,
                "verified_tutors": verified_tutors,
                "type_stats": type_stats,
                "recent_tutors_7d": recent_tutors,
                "last_updated": datetime.now()
            }
        except Exception as e:
            raise Exception(f"获取导师统计失败: {str(e)}")

    async def get_popular_tutors(self, limit: int = 5) -> List[TutorListResponse]:
        """获取热门推荐导师"""
        try:
            # 获取热门导师（按评分和学生数综合排序）
            popular_tutors = await self.crud_tutor.get_popular_tutors(self.db, limit=limit)
            
            # 转换为响应模型
            result = []
            for tutor in popular_tutors:
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
            raise Exception(f"获取热门导师失败: {str(e)}")

    async def parse_filters(self, filters: TutorFilterParams) -> dict:
        """解析前端筛选参数，转换为数据库查询条件"""
        parsed = {}
        
        if filters.tutor_type:
            parsed['tutor_type'] = filters.tutor_type
        
        if filters.domain:
            parsed['domain'] = filters.domain
        
        if filters.price_range:
            # 解析价格区间（如"100-500"）
            parsed['price_range'] = filters.price_range
        
        return parsed 