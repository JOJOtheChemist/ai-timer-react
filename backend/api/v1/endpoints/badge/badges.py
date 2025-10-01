from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from models.schemas.badge import (
    UserBadgeListResponse,
    BadgeDetailResponse,
    BadgeDisplayUpdate,
    BadgeDisplayResponse,
    BadgeOperationResponse
)
from services.badge.badge_service import BadgeService

router = APIRouter()

@router.get("/my", response_model=UserBadgeListResponse)
async def get_user_badges(
    category: str = None,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的徽章列表（含已获得/未解锁状态）"""
    try:
        badge_service = BadgeService(db)
        badges = await badge_service.get_user_badges(
            current_user["id"], 
            category=category
        )
        
        return badges
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户徽章列表失败: {str(e)}"
        )

@router.get("/{badge_id}", response_model=BadgeDetailResponse)
async def get_badge_detail(
    badge_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取单个徽章的详情（描述、获得时间/解锁条件）"""
    try:
        badge_service = BadgeService(db)
        badge_detail = await badge_service.get_badge_detail(
            badge_id, 
            current_user["id"]
        )
        
        if not badge_detail:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="徽章不存在"
            )
        
        return badge_detail
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取徽章详情失败: {str(e)}"
        )

@router.get("/", response_model=List[BadgeDetailResponse])
async def get_all_badges(
    category: str = None,
    limit: int = 50,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有徽章列表（含用户获得状态）"""
    try:
        badge_service = BadgeService(db)
        badges = await badge_service.get_all_badges(
            user_id=current_user["id"],
            category=category,
            limit=limit,
            offset=offset
        )
        
        return badges
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取徽章列表失败: {str(e)}"
        )

@router.put("/display", response_model=BadgeOperationResponse)
async def update_badge_display(
    display_updates: List[BadgeDisplayUpdate],
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新徽章展示设置"""
    try:
        badge_service = BadgeService(db)
        success = await badge_service.update_badge_display(
            current_user["id"], 
            display_updates
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新徽章展示设置失败"
            )
        
        return BadgeOperationResponse(
            success=True,
            message="徽章展示设置更新成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新徽章展示设置失败: {str(e)}"
        )

@router.get("/display/current", response_model=BadgeDisplayResponse)
async def get_displayed_badges(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前展示的徽章列表"""
    try:
        badge_service = BadgeService(db)
        displayed_badges = await badge_service.get_displayed_badges(current_user["id"])
        
        return displayed_badges
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取展示徽章失败: {str(e)}"
        ) 