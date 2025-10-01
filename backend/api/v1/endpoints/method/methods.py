from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db, get_current_user
from models.schemas.method import (
    MethodListResponse,
    MethodDetailResponse,
    MethodFilterParams
)
from services.method.method_service import MethodService

router = APIRouter()

@router.get("/", response_model=List[MethodListResponse])
async def get_method_list(
    category: Optional[str] = Query(None, description="方法分类筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习方法列表（支持筛选参数：category，如"通用方法/导师独创"）
    自动返回方法的打卡人数、评分（关联统计数据）"""
    try:
        method_service = MethodService(db)
        
        # 构建筛选条件
        filters = MethodFilterParams(category=category)
        
        # 获取方法列表
        methods = await method_service.get_method_list(
            filters=filters,
            page=page,
            page_size=page_size
        )
        
        return methods
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习方法列表失败: {str(e)}"
        )

@router.get("/{method_id}", response_model=MethodDetailResponse)
async def get_method_detail(
    method_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个学习方法的完整详情（含description、steps、scene、meta等）"""
    try:
        method_service = MethodService(db)
        
        # 获取方法详情
        method_detail = await method_service.get_method_detail(method_id)
        
        if not method_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习方法不存在"
            )
        
        return method_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习方法详情失败: {str(e)}"
        )

@router.get("/popular/trending")
async def get_popular_methods(
    limit: int = Query(10, ge=1, le=50, description="返回数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取热门学习方法列表（按打卡人数排序）"""
    try:
        method_service = MethodService(db)
        
        # 获取热门方法（使用缓存）
        popular_methods = await method_service.get_popular_methods(limit=limit)
        
        return {
            "methods": popular_methods,
            "total": len(popular_methods),
            "cache_info": "数据已缓存，每小时更新"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门方法失败: {str(e)}"
        )

@router.get("/categories/list")
async def get_method_categories(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习方法分类列表"""
    try:
        method_service = MethodService(db)
        
        categories = await method_service.get_method_categories()
        
        return {
            "categories": categories,
            "total": len(categories)
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取方法分类失败: {str(e)}"
        )

@router.get("/{method_id}/stats")
async def get_method_stats(
    method_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取学习方法统计信息（打卡人数、评分等）"""
    try:
        method_service = MethodService(db)
        
        stats = await method_service.get_method_stats(method_id)
        
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="学习方法不存在"
            )
        
        return stats
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取方法统计失败: {str(e)}"
        ) 