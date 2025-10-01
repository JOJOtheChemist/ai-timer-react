from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas.case import CaseDetailResponse
from services.case.case_detail_service import CaseDetailService

router = APIRouter()

@router.get("/{case_id}", response_model=CaseDetailResponse)
async def get_case_detail(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个案例的详细信息（含完整描述、时间规划、经验总结等）"""
    try:
        case_detail_service = CaseDetailService(db)
        case_detail = await case_detail_service.get_case_detail(
            case_id=case_id,
            user_id=current_user["id"]
        )
        
        if not case_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="案例不存在"
            )
        
        return case_detail
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取案例详情失败: {str(e)}"
        )

@router.post("/{case_id}/view")
async def record_case_view(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """记录案例浏览次数（用于统计热门案例）"""
    try:
        case_detail_service = CaseDetailService(db)
        await case_detail_service.record_case_view(
            case_id=case_id,
            user_id=current_user["id"]
        )
        
        return {"message": "浏览记录已更新"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"记录浏览失败: {str(e)}"
        )

@router.get("/{case_id}/related", response_model=list)
async def get_related_cases(
    case_id: int,
    limit: int = 5,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取相关推荐案例（基于标签、分类等相似度）"""
    try:
        case_detail_service = CaseDetailService(db)
        related_cases = await case_detail_service.get_related_cases(
            case_id=case_id,
            limit=limit
        )
        
        return related_cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取相关案例失败: {str(e)}"
        ) 