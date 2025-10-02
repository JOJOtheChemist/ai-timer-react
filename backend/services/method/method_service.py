from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import json
from datetime import datetime, timedelta

from crud.method.crud_method import CRUDMethod
from services.statistic.statistic_service import StatisticService
from models.schemas.method import (
    MethodListResponse,
    MethodDetailResponse,
    MethodFilterParams,
    MethodStatsResponse
)

class MethodService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_method = CRUDMethod()
        self.statistic_service = StatisticService()
        self.cache_ttl = 3600  # 1小时缓存
    
    async def get_method_list(
        self, 
        filters: MethodFilterParams, 
        page: int = 1, 
        page_size: int = 20
    ) -> List[MethodListResponse]:
        """按筛选条件查询方法列表，调用statistic_service补充打卡人数和评分
        缓存热门方法列表（调用cache_service.set，有效期1小时）"""
        try:
            # 尝试从缓存获取（如果是热门方法列表）
            cache_key = f"method_list_{filters.category}_{page}_{page_size}"
            cached_data = await self._get_from_cache(cache_key)
            
            if cached_data and not filters.category:  # 只缓存无分类筛选的列表
                return cached_data
            
            # 从数据库查询方法基础数据
            methods = self.crud_method.get_multi_by_category(
                self.db, 
                category=filters.category,
                page=page,
                page_size=page_size
            )
            
            # 补充统计数据
            method_responses = []
            for method in methods:
                # method现在是一个字典
                # 获取打卡人数和评分（直接从数据库字段获取）
                checkin_count = method.get('checkin_count', 0)
                rating = method.get('rating', 0.0)
                
                # 构建响应数据
                method_response = {
                    'id': method['id'],
                    'name': method['name'],
                    'category': method['category'],
                    'type': method.get('type'),
                    'meta': {
                        'scope': method.get('type'),
                        'checkinCount': checkin_count,
                        'tutor': None if method.get('tutor_id') is None else f"导师ID: {method['tutor_id']}"
                    },
                    'description': method['description'],
                    'steps': method.get('steps', []),
                    'scene': method.get('scene', ''),
                    'stats': {
                        'rating': float(rating) if rating else 0.0,
                        'reviews': method.get('review_count', 0)
                    },
                    'create_time': method['create_time'].isoformat() if method.get('create_time') else None,
                    'update_time': method['update_time'].isoformat() if method.get('update_time') else None
                }
                method_responses.append(method_response)
            
            # 缓存结果（如果是热门方法）
            if not filters.category and page == 1:
                await self._set_cache(cache_key, method_responses)
            
            return method_responses
        except Exception as e:
            print(f"获取方法列表失败: {e}")
            return []
    
    async def get_method_detail(self, method_id: int) -> Optional[MethodDetailResponse]:
        """查询方法完整信息，校验方法状态（如是否已下架）
        复用statistic_service获取实时打卡人数和评分"""
        try:
            # 查询方法基础信息
            method = self.crud_method.get_by_id(self.db, method_id)
            if not method:
                return None
            
            # 校验方法状态
            if not method.is_active:
                return None  # 方法已下架
            
            # 获取统计数据
            checkin_count = await self.statistic_service.count_method_checkins(
                self.db, method_id
            )
            rating = await self.statistic_service.calculate_method_rating(
                self.db, method_id
            )
            completion_rate = await self._calculate_completion_rate(method_id)
            
            # 构建详情响应
            method_detail = MethodDetailResponse(
                id=method.id,
                name=method.name,
                description=method.description,
                category=method.category,
                difficulty_level=method.difficulty_level,
                estimated_time=method.estimated_time,
                steps=method.steps or [],
                scene=method.scene,
                meta=method.meta or {},
                tags=method.tags or [],
                author_info=method.author_info,
                stats=MethodStatsResponse(
                    checkin_count=checkin_count,
                    rating=rating,
                    completion_rate=completion_rate
                ),
                create_time=method.create_time,
                update_time=method.update_time
            )
            
            return method_detail
        except Exception as e:
            print(f"获取方法详情失败: {e}")
            return None
    
    async def get_popular_methods(self, limit: int = 10) -> List[MethodListResponse]:
        """获取热门方法列表（按打卡人数排序，使用缓存）"""
        try:
            cache_key = f"popular_methods_{limit}"
            cached_data = await self._get_from_cache(cache_key)
            
            if cached_data:
                return cached_data
            
            # 获取热门方法
            popular_methods = self.crud_method.get_popular_methods(self.db, limit=limit)
            
            # 补充统计数据
            method_responses = []
            for method in popular_methods:
                checkin_count = await self.statistic_service.count_method_checkins(
                    self.db, method.id
                )
                rating = await self.statistic_service.calculate_method_rating(
                    self.db, method.id
                )
                
                method_response = MethodListResponse(
                    id=method.id,
                    name=method.name,
                    description=method.description,
                    category=method.category,
                    difficulty_level=method.difficulty_level,
                    estimated_time=method.estimated_time,
                    tags=method.tags or [],
                    author_info=method.author_info,
                    stats=MethodStatsResponse(
                        checkin_count=checkin_count,
                        rating=rating,
                        completion_rate=await self._calculate_completion_rate(method.id)
                    ),
                    create_time=method.create_time,
                    update_time=method.update_time
                )
                method_responses.append(method_response)
            
            # 缓存结果
            await self._set_cache(cache_key, method_responses)
            
            return method_responses
        except Exception as e:
            print(f"获取热门方法失败: {e}")
            return []
    
    async def get_method_categories(self) -> List[Dict[str, Any]]:
        """获取方法分类列表"""
        try:
            categories = self.crud_method.get_categories(self.db)
            
            # 补充每个分类的方法数量
            category_list = []
            for category in categories:
                method_count = self.crud_method.count_by_category(self.db, category.name)
                category_list.append({
                    "name": category.name,
                    "display_name": category.display_name,
                    "description": category.description,
                    "method_count": method_count,
                    "icon": category.icon
                })
            
            return category_list
        except Exception as e:
            print(f"获取方法分类失败: {e}")
            return []
    
    async def get_method_stats(self, method_id: int) -> Optional[Dict[str, Any]]:
        """获取方法统计信息"""
        try:
            method = self.crud_method.get_by_id(self.db, method_id)
            if not method:
                return None
            
            checkin_count = await self.statistic_service.count_method_checkins(
                self.db, method_id
            )
            rating = await self.statistic_service.calculate_method_rating(
                self.db, method_id
            )
            completion_rate = await self._calculate_completion_rate(method_id)
            
            return {
                "method_id": method_id,
                "checkin_count": checkin_count,
                "rating": rating,
                "completion_rate": completion_rate,
                "difficulty_level": method.difficulty_level,
                "estimated_time": method.estimated_time
            }
        except Exception as e:
            print(f"获取方法统计失败: {e}")
            return None
    
    async def _calculate_completion_rate(self, method_id: int) -> float:
        """计算方法完成率"""
        try:
            # 这里需要根据实际业务逻辑计算
            # 暂时返回模拟数据
            return 0.75  # 75%完成率
        except Exception:
            return 0.0
    
    async def _get_from_cache(self, cache_key: str) -> Optional[List[MethodListResponse]]:
        """从缓存获取数据（模拟实现）"""
        try:
            # 这里应该对接Redis等缓存服务
            # 暂时返回None，表示缓存未命中
            return None
        except Exception:
            return None
    
    async def _set_cache(self, cache_key: str, data: List[MethodListResponse]) -> bool:
        """设置缓存数据（模拟实现）"""
        try:
            # 这里应该对接Redis等缓存服务
            # cache_service.set(cache_key, data, ttl=self.cache_ttl)
            print(f"缓存已设置: {cache_key}")
            return True
        except Exception as e:
            print(f"设置缓存失败: {e}")
            return False 