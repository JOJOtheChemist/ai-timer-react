from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from core.dependencies import get_db, get_current_user
from models.schemas.ai import AIStudyMethodResponse
from services.ai.ai_recommend_service import AIRecommendService

router = APIRouter()

@router.get("/recommendations/method", response_model=List[AIStudyMethodResponse])
async def get_study_method_recommendations(
    limit: int = Query(5, ge=1, le=20, description="推荐数量"),
    category: Optional[str] = Query(None, description="方法分类筛选"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取针对用户的学习方法推荐（基于时间表数据，如"复习频率低"推荐艾宾浩斯法）"""
    try:
        ai_recommend_service = AIRecommendService(db)
        
        # 获取AI推荐的学习方法
        recommendations = await ai_recommend_service.recommend_study_method(
            user_id=current_user["id"],
            limit=limit,
            category=category
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取学习方法推荐失败: {str(e)}"
        )

@router.get("/recommendations/method/explain/{method_id}")
async def explain_method_recommendation(
    method_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """解释为什么推荐某个学习方法"""
    try:
        ai_recommend_service = AIRecommendService(db)
        
        # 获取推荐理由详细解释
        explanation = await ai_recommend_service.explain_method_recommendation(
            user_id=current_user["id"],
            method_id=method_id
        )
        
        if not explanation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="未找到该方法的推荐理由"
            )
        
        return explanation
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取推荐理由失败: {str(e)}"
        )

@router.get("/recommendations/personalized")
async def get_personalized_recommendations(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个性化推荐（综合学习方法、任务安排等）"""
    try:
        ai_recommend_service = AIRecommendService(db)
        
        # 获取个性化推荐
        recommendations = await ai_recommend_service.get_personalized_recommendations(
            user_id=current_user["id"]
        )
        
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取个性化推荐失败: {str(e)}"
        )

@router.post("/recommendations/feedback")
async def submit_recommendation_feedback(
    method_id: int,
    feedback_type: str,  # "helpful", "not_helpful", "tried"
    rating: Optional[int] = Query(None, ge=1, le=5, description="评分1-5"),
    comment: Optional[str] = Query(None, description="反馈评论"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交推荐反馈，用于改进推荐算法"""
    try:
        ai_recommend_service = AIRecommendService(db)
        
        # 提交反馈
        success = await ai_recommend_service.submit_recommendation_feedback(
            user_id=current_user["id"],
            method_id=method_id,
            feedback_type=feedback_type,
            rating=rating,
            comment=comment
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="提交反馈失败"
            )
        
        return {"message": "反馈提交成功，感谢您的参与！"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交反馈失败: {str(e)}"
        )

@router.get("/analysis/user-behavior")
async def get_user_behavior_analysis(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户行为分析（用于推荐算法的数据基础）"""
    try:
        ai_recommend_service = AIRecommendService(db)
        
        # 获取用户行为分析
        analysis = await ai_recommend_service.analyze_user_behavior(
            user_id=current_user["id"]
        )
        
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取行为分析失败: {str(e)}"
    ) 