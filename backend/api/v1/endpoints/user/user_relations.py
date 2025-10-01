from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from models.schemas.user import (
    RelationStatsResponse,
    FollowedTutorResponse,
    RecentFanResponse,
    UserOperationResponse
)
from services.user.user_relation_service import UserRelationService

router = APIRouter()

@router.get("/me/relations/stats", response_model=RelationStatsResponse)
async def get_user_relation_stats(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户关系统计（关注导师数、粉丝数）"""
    try:
        user_relation_service = UserRelationService(db)
        stats = await user_relation_service.get_relation_stats(current_user["id"])
        
        return stats
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取关系统计失败: {str(e)}"
        )

@router.get("/me/relations/tutors", response_model=FollowedTutorResponse)
async def get_followed_tutors(
    limit: int = 3,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户关注的导师列表（紧凑版，默认前3条）"""
    try:
        user_relation_service = UserRelationService(db)
        tutors = await user_relation_service.get_followed_tutors(
            current_user["id"], 
            limit=limit, 
            offset=offset
        )
        
        return tutors
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取关注导师列表失败: {str(e)}"
        )

@router.get("/me/relations/fans", response_model=RecentFanResponse)
async def get_recent_fans(
    limit: int = 4,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户的最近粉丝列表（紧凑版，默认前4条）"""
    try:
        user_relation_service = UserRelationService(db)
        fans = await user_relation_service.get_recent_fans(
            current_user["id"], 
            limit=limit, 
            offset=offset
        )
        
        return fans
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取粉丝列表失败: {str(e)}"
        )

@router.post("/me/relations/follow/{target_user_id}", response_model=UserOperationResponse)
async def follow_user(
    target_user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """关注用户"""
    try:
        if target_user_id == current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="不能关注自己"
            )
        
        user_relation_service = UserRelationService(db)
        success = await user_relation_service.follow_user(
            current_user["id"], 
            target_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="关注失败"
            )
        
        return UserOperationResponse(
            success=True,
            message="关注成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"关注操作失败: {str(e)}"
        )

@router.delete("/me/relations/unfollow/{target_user_id}", response_model=UserOperationResponse)
async def unfollow_user(
    target_user_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """取消关注用户"""
    try:
        user_relation_service = UserRelationService(db)
        success = await user_relation_service.unfollow_user(
            current_user["id"], 
            target_user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="取消关注失败"
            )
        
        return UserOperationResponse(
            success=True,
            message="取消关注成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"取消关注操作失败: {str(e)}"
        ) 