from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db_and_user
from services.ai.ai_recommendation_service import ai_recommendation_service
from models.schemas.ai import RecommendationItem, RecommendationsResponse, RecommendationType
from models.schemas.task import TaskOperationResponse

router = APIRouter()

@router.get("/schedule-recommendations", response_model=RecommendationsResponse)
async def get_schedule_recommendations(
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取时间表AI推荐任务
    """
    db, user_id = db_and_user
    
    try:
        recommendations = ai_recommendation_service.generate_schedule_recommendation(
            db=db, user_id=user_id
        )
        
        return RecommendationsResponse(
            recommendations=recommendations,
            total=len(recommendations),
            analysis_based=True
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI推荐失败: {str(e)}")

@router.post("/schedule-recommendations/{rec_id}/accept", response_model=TaskOperationResponse)
async def accept_recommendation(
    rec_id: int = Path(..., description="推荐ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    采纳AI推荐
    
    - **rec_id**: 推荐ID
    """
    db, user_id = db_and_user
    
    try:
        success = ai_recommendation_service.handle_recommendation_accept(
            db=db, user_id=user_id, rec_id=rec_id
        )
        
        if not success:
            raise HTTPException(status_code=404, detail="推荐不存在")
        
        return TaskOperationResponse(
            success=True,
            message="推荐采纳成功",
            data={"rec_id": rec_id}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"采纳推荐失败: {str(e)}")

@router.get("/efficiency-tips")
async def get_efficiency_tips(
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取效率优化建议
    """
    db, user_id = db_and_user
    
    try:
        tips = ai_recommendation_service.generate_efficiency_tips(
            db=db, user_id=user_id
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取效率建议成功",
            data={"tips": tips}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取效率建议失败: {str(e)}")

@router.get("/recommendation-detail/{recommend_type}/{recommend_id}")
async def get_recommendation_detail(
    recommend_type: RecommendationType = Path(..., description="推荐类型"),
    recommend_id: int = Path(..., description="推荐资源ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取推荐资源详情
    
    - **recommend_type**: 推荐类型
    - **recommend_id**: 推荐资源ID
    """
    db, user_id = db_and_user
    
    try:
        detail = ai_recommendation_service.get_recommendation_detail(
            recommend_type=recommend_type, recommend_id=recommend_id
        )
        
        if not detail:
            raise HTTPException(status_code=404, detail="推荐资源不存在")
        
        return TaskOperationResponse(
            success=True,
            message="获取推荐详情成功",
            data=detail
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取推荐详情失败: {str(e)}")

# 健康检查
@router.get("/health/check")
async def ai_recommendations_health_check():
    """AI推荐服务健康检查"""
    return TaskOperationResponse(
        success=True,
        message="AI推荐服务正常运行",
        data={
            "service": "ai_recommendations",
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    ) 