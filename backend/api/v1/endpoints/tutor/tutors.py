from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db, get_current_user
from models.schemas.tutor import (
    TutorListResponse,
    TutorFilterParams,
    TutorSearchResponse
)
from services.tutor.tutor_service import TutorService

router = APIRouter()

@router.get("/", response_model=List[TutorListResponse])
async def get_tutor_list(
    tutor_type: Optional[str] = Query(None, description="导师类型筛选"),
    domain: Optional[str] = Query(None, description="擅长领域筛选"),
    price_range: Optional[str] = Query(None, description="价格区间筛选"),
    sort_by: Optional[str] = Query("rating", description="排序方式：rating/price/experience"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取导师列表（支持筛选参数：tutor_type、domain、price_range等；支持排序参数：sort_by）"""
    try:
        tutor_service = TutorService(db)
        
        # 构建筛选参数
        filters = TutorFilterParams(
            tutor_type=tutor_type,
            domain=domain,
            price_range=price_range,
            page=page,
            page_size=page_size
        )
        
        tutors = await tutor_service.get_tutor_list(
            filters=filters,
            sort_by=sort_by,
            page=page,
            page_size=page_size
        )
        
        return tutors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师列表失败: {str(e)}"
        )

@router.get("/search", response_model=List[TutorSearchResponse])
async def search_tutors(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """按关键词搜索导师（匹配姓名、擅长领域）"""
    try:
        tutor_service = TutorService(db)
        search_results = await tutor_service.search_tutors(
            keyword=keyword,
            page=page,
            page_size=page_size
        )
        
        return search_results
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索导师失败: {str(e)}"
        )

@router.get("/domains", response_model=List[str])
async def get_tutor_domains(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有导师擅长领域列表"""
    try:
        tutor_service = TutorService(db)
        domains = await tutor_service.get_tutor_domains()
        return domains
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师领域失败: {str(e)}"
        )

@router.get("/types", response_model=List[str])
async def get_tutor_types(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有导师类型列表"""
    try:
        tutor_service = TutorService(db)
        types = await tutor_service.get_tutor_types()
        return types
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师类型失败: {str(e)}"
        )

@router.get("/stats/summary")
async def get_tutor_stats_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取导师统计摘要（总数、类型统计等）"""
    try:
        tutor_service = TutorService(db)
        stats = await tutor_service.get_tutor_stats_summary()
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师统计失败: {str(e)}"
        )

@router.get("/popular", response_model=List[TutorListResponse])
async def get_popular_tutors(
    limit: int = Query(5, ge=1, le=20, description="推荐数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取热门推荐导师"""
    try:
        tutor_service = TutorService(db)
        popular_tutors = await tutor_service.get_popular_tutors(limit=limit)
        return popular_tutors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取热门导师失败: {str(e)}"
        ) 