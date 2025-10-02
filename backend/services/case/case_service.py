from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from crud.case.crud_case import CRUDCase
from models.schemas.case import (
    HotCaseResponse,
    CaseListResponse,
    CaseFilterParams
)

class CaseService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_case = CRUDCase()

    async def get_hot_cases(self, limit: int = 3) -> List[HotCaseResponse]:
        """获取热门推荐案例（按浏览量/热度排序）"""
        try:
            # 从数据库获取热门案例
            hot_cases = await self.crud_case.get_hot_by_views(self.db, limit=limit)
            
            # 转换为响应模型
            result = []
            for case in hot_cases:
                # 处理tags字段：如果是列表直接使用，如果是字符串则split
                tags = case.tags if isinstance(case.tags, list) else (case.tags.split(',') if case.tags else [])
                
                result.append(HotCaseResponse(
                    id=case.id,
                    title=case.title,
                    tags=tags,
                    author_name=case.author_name,
                    author_id=case.user_id if hasattr(case, 'user_id') else None,
                    views=case.view_count if hasattr(case, 'view_count') else 0,
                    is_hot=bool(case.is_hot),
                    category=case.category,
                    duration=case.duration,
                    price=case.price if case.price else "免费",
                    currency="钻石" if case.price else "",
                    created_at=case.create_time if hasattr(case, 'create_time') else datetime.now()
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取热门案例失败: {str(e)}")

    async def get_filtered_cases(self, filters: CaseFilterParams) -> List[CaseListResponse]:
        """根据筛选条件查询案例列表"""
        try:
            # 解析筛选参数
            parsed_filters = await self.parse_filters(filters)
            
            # 从数据库查询
            cases = await self.crud_case.get_multi_by_filters(
                self.db, 
                filters=parsed_filters,
                skip=(filters.page - 1) * filters.page_size,
                limit=filters.page_size
            )
            
            # 转换为响应模型
            result = []
            for case in cases:
                tags = case.tags if isinstance(case.tags, list) else (case.tags.split(',') if case.tags else [])
                
                result.append(CaseListResponse(
                    id=case.id,
                    title=case.title,
                    tags=tags,
                    author_name=case.author_name,
                    author_id=case.user_id if hasattr(case, 'user_id') else None,
                    duration=case.duration,
                    category=case.category,
                    price=case.price if case.price else "免费",
                    currency="钻石" if case.price else "",
                    views=case.view_count if hasattr(case, 'view_count') else 0,
                    is_featured=bool(case.is_hot) if hasattr(case, 'is_hot') else False,
                    created_at=case.create_time if hasattr(case, 'create_time') else datetime.now(),
                    updated_at=case.update_time if hasattr(case, 'update_time') else datetime.now()
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取筛选案例失败: {str(e)}")

    async def search_cases(self, keyword: str, page: int = 1, page_size: int = 20) -> List[CaseListResponse]:
        """根据关键词搜索案例"""
        try:
            # 执行搜索
            cases = await self.crud_case.search_by_keyword(
                self.db,
                keyword=keyword,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # 转换为响应模型
            result = []
            for case in cases:
                tags = case.tags if isinstance(case.tags, list) else (case.tags.split(',') if case.tags else [])
                
                result.append(CaseListResponse(
                    id=case.id,
                    title=case.title,
                    tags=tags,
                    author_name=case.author_name,
                    author_id=case.user_id if hasattr(case, 'user_id') else None,
                    duration=case.duration,
                    category=case.category,
                    price=case.price if case.price else "免费",
                    currency="钻石" if case.price else "",
                    views=case.view_count if hasattr(case, 'view_count') else 0,
                    is_featured=bool(case.is_hot) if hasattr(case, 'is_hot') else False,
                    created_at=case.create_time if hasattr(case, 'create_time') else datetime.now(),
                    updated_at=case.update_time if hasattr(case, 'update_time') else datetime.now()
                ))
            
            return result
        except Exception as e:
            raise Exception(f"搜索案例失败: {str(e)}")

    async def get_case_categories(self) -> List[str]:
        """获取所有案例分类列表"""
        try:
            categories = await self.crud_case.get_categories(self.db)
            return categories
        except Exception as e:
            raise Exception(f"获取案例分类失败: {str(e)}")

    async def get_case_stats_summary(self) -> dict:
        """获取案例统计摘要"""
        try:
            # 获取总案例数
            total_cases = await self.crud_case.count_total_cases(self.db)
            
            # 获取分类统计
            category_stats = await self.crud_case.count_by_category(self.db)
            
            # 获取最近7天新增案例数
            seven_days_ago = datetime.now() - timedelta(days=7)
            recent_cases = await self.crud_case.count_cases_since(self.db, seven_days_ago)
            
            return {
                "total_cases": total_cases,
                "category_stats": category_stats,
                "recent_cases_7d": recent_cases,
                "last_updated": datetime.now()
            }
        except Exception as e:
            raise Exception(f"获取案例统计失败: {str(e)}")

    async def parse_filters(self, filters: CaseFilterParams) -> dict:
        """解析前端筛选参数，转换为数据库查询条件"""
        parsed = {}
        
        if filters.category:
            parsed['category'] = filters.category
        
        if filters.duration:
            # 解析时长筛选（如"3-6个月"）
            parsed['duration'] = filters.duration
        
        if filters.experience:
            # 解析经历背景筛选
            parsed['experience'] = filters.experience
        
        if filters.foundation:
            # 解析基础水平筛选
            parsed['foundation'] = filters.foundation
        
        return parsed 