from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from models.schemas.method import (
    CheckinCreate,
    CheckinResponse,
    CheckinHistoryResponse
)
from services.method.checkin_service import CheckinService

router = APIRouter()

@router.post("/{method_id}/checkin", response_model=CheckinResponse)
async def create_method_checkin(
    method_id: int,
    checkin_data: CheckinCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """提交学习方法打卡（请求体含checkin_type、progress、note）"""
    try:
        checkin_service = CheckinService(db)
        
        # 创建打卡记录
        checkin = await checkin_service.create_checkin(
            user_id=current_user["id"],
            method_id=method_id,
            checkin_data=checkin_data
        )
        
        if not checkin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="打卡失败，请检查输入数据"
            )
        
        return checkin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"提交打卡失败: {str(e)}"
        )

@router.get("/{method_id}/checkins/history", response_model=List[CheckinHistoryResponse])
async def get_checkin_history(
    method_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """查询当前用户的该方法打卡历史"""
    try:
        checkin_service = CheckinService(db)
        
        # 获取用户打卡历史
        history = await checkin_service.get_user_checkin_history(
            user_id=current_user["id"],
            method_id=method_id,
            page=page,
            page_size=page_size
        )
        
        return history
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取打卡历史失败: {str(e)}"
        )

@router.get("/{method_id}/checkins/stats")
async def get_checkin_stats(
    method_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户在该方法的打卡统计"""
    try:
        checkin_service = CheckinService(db)
        
        # 获取用户打卡统计
        stats = await checkin_service.get_user_checkin_stats(
            user_id=current_user["id"],
            method_id=method_id
        )
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取打卡统计失败: {str(e)}"
        )

@router.delete("/{method_id}/checkins/{checkin_id}")
async def delete_checkin(
    method_id: int,
    checkin_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除打卡记录（仅限当天的记录）"""
    try:
        checkin_service = CheckinService(db)
        
        # 删除打卡记录
        success = await checkin_service.delete_checkin(
            user_id=current_user["id"],
            method_id=method_id,
            checkin_id=checkin_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="删除失败，只能删除当天的打卡记录"
            )
        
        return {"message": "打卡记录删除成功"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除打卡记录失败: {str(e)}"
        )

@router.put("/{method_id}/checkins/{checkin_id}")
async def update_checkin(
    method_id: int,
    checkin_id: int,
    checkin_data: CheckinCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新打卡记录（仅限当天的记录）"""
    try:
        checkin_service = CheckinService(db)
        
        # 更新打卡记录
        updated_checkin = await checkin_service.update_checkin(
            user_id=current_user["id"],
            method_id=method_id,
            checkin_id=checkin_id,
            checkin_data=checkin_data
        )
        
        if not updated_checkin:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新失败，只能修改当天的打卡记录"
            )
        
        return updated_checkin
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新打卡记录失败: {str(e)}"
        )

@router.get("/checkins/calendar")
async def get_checkin_calendar(
    year: int = Query(..., description="年份"),
    month: int = Query(..., ge=1, le=12, description="月份"),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的打卡日历（某月的打卡情况）"""
    try:
        checkin_service = CheckinService(db)
        
        # 获取打卡日历
        calendar_data = await checkin_service.get_checkin_calendar(
            user_id=current_user["id"],
            year=year,
            month=month
        )
        
        return calendar_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取打卡日历失败: {str(e)}"
        ) 