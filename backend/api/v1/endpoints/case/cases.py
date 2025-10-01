from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db, get_current_user
from models.schemas.case import (
    HotCaseResponse,
    CaseListResponse,
    CaseFilterParams
)
from services.case.case_service import CaseService

router = APIRouter()

@router.get("/hot", response_model=List[HotCaseResponse])
async def get_hot_cases(
    limit: int = Query(3, ge=1, le=10, description="热门案例数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取热门推荐案例（按浏览量/热度排序）"""
    try:
        case_service = CaseService(db)
        hot_cases = await case_service.get_hot_cases(limit=limit)
        return hot_cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门案例失败: {str(e)}"
        )

@router.get("/", response_model=List[CaseListResponse])
async def get_case_list(
    category: Optional[str] = Query(None, description="案例分类筛选"),
    duration: Optional[str] = Query(None, description="备考时长筛选"),
    experience: Optional[str] = Query(None, description="经历背景筛选"),
    foundation: Optional[str] = Query(None, description="基础水平筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取案例列表（支持筛选参数：category、duration、experience、foundation等）"""
    try:
        case_service = CaseService(db)
        
        # 构建筛选参数
        filters = CaseFilterParams(
            category=category,
            duration=duration,
            experience=experience,
            foundation=foundation,
            page=page,
            page_size=page_size
        )
        
        cases = await case_service.get_filtered_cases(filters)
        return cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取案例列表失败: {str(e)}"
        )

@router.get("/search", response_model=List[CaseListResponse])
async def search_cases(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按关键词搜索案例（支持title、tags、author等字段匹配）"""
    try:
        case_service = CaseService(db)
        search_results = await case_service.search_cases(
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        return search_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索案例失败: {str(e)}"
        )

@router.get("/categories", response_model=List[str])
async def get_case_categories(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有案例分类列表"""
    try:
        case_service = CaseService(db)
        categories = await case_service.get_case_categories()
        return categories
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取案例分类失败: {str(e)}"
        )

@router.get("/stats/summary")
async def get_case_stats_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取案例统计摘要（总数、分类统计等）"""
    try:
        case_service = CaseService(db)
        stats = await case_service.get_case_stats_summary()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取案例统计失败: {str(e)}"
        ) 