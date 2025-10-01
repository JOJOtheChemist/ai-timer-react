from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas.tutor import TutorDetailResponse
from services.tutor.tutor_detail_service import TutorDetailService

router = APIRouter()

@router.get("/{tutor_id}", response_model=TutorDetailResponse)
async def get_tutor_detail(
    tutor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个导师的完整详情（含profile、服务详情、指导数据、学员评价）"""
    try:
        tutor_detail_service = TutorDetailService(db)
        tutor_detail = await tutor_detail_service.get_tutor_detail(
            tutor_id=tutor_id,
            user_id=current_user["id"]
        )
        
        if not tutor_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="导师不存在"
            )
        
        return tutor_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师详情失败: {str(e)}"
        )

@router.get("/{tutor_id}/services")
async def get_tutor_services(
    tutor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取导师的服务列表"""
    try:
        tutor_detail_service = TutorDetailService(db)
        services = await tutor_detail_service.get_tutor_services(tutor_id)
        
        return services
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师服务失败: {str(e)}"
        )

@router.get("/{tutor_id}/reviews")
async def get_tutor_reviews(
    tutor_id: int,
    page: int = 1,
    page_size: int = 10,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取导师的学员评价列表"""
    try:
        tutor_detail_service = TutorDetailService(db)
        reviews = await tutor_detail_service.get_tutor_reviews(
            tutor_id=tutor_id,
            page=page,
            page_size=page_size
        )
        
        return reviews
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师评价失败: {str(e)}"
        )

@router.get("/{tutor_id}/metrics")
async def get_tutor_metrics(
    tutor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取导师的指导数据面板"""
    try:
        tutor_detail_service = TutorDetailService(db)
        metrics = await tutor_detail_service.get_tutor_metrics(tutor_id)
        
        return metrics
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取导师数据失败: {str(e)}"
        )

@router.post("/{tutor_id}/view")
async def record_tutor_view(
    tutor_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录导师页面浏览次数"""
    try:
        tutor_detail_service = TutorDetailService(db)
        await tutor_detail_service.record_tutor_view(
            tutor_id=tutor_id,
            user_id=current_user["id"]
        )
        
        return {"message": "浏览记录已更新"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录浏览失败: {str(e)}"
        )

@router.get("/{tutor_id}/similar")
async def get_similar_tutors(
    tutor_id: int,
    limit: int = 5,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取相似推荐导师（基于领域、类型等相似度）"""
    try:
        tutor_detail_service = TutorDetailService(db)
        similar_tutors = await tutor_detail_service.get_similar_tutors(
            tutor_id=tutor_id,
            limit=limit
        )
        
        return similar_tutors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相似导师失败: {str(e)}"
        ) 