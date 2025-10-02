from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user_dev
from models.schemas.user import UserProfileResponse, UserProfileUpdate, UserOperationResponse, UserSimpleInfoResponse
from services.user.user_profile_service import UserProfileService

router = APIRouter()

@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user_id: int = Depends(get_current_user_dev),
    db: Session = Depends(get_db)
):
    """获取当前登录用户的完整个人信息（含基础信息、总学习时长）"""
    try:
        user_profile_service = UserProfileService(db)
        profile = await user_profile_service.get_current_user_profile(current_user_id)
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户个人信息不存在"
            )
        
        return profile
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户个人信息失败: {str(e)}"
        )

@router.put("/me/profile", response_model=UserOperationResponse)
async def update_current_user_profile(
    profile_data: UserProfileUpdate,
    current_user_id: int = Depends(get_current_user_dev),
    db: Session = Depends(get_db)
):
    """更新当前用户的个人信息（如修改goal、username）"""
    try:
        user_profile_service = UserProfileService(db)
        success = await user_profile_service.update_user_profile(
            current_user_id, 
            profile_data
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="更新用户个人信息失败"
            )
        
        return UserOperationResponse(
            success=True,
            message="个人信息更新成功"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户个人信息失败: {str(e)}"
        )

@router.get("/{target_user_id}/simple-info", response_model=UserSimpleInfoResponse)
async def get_user_simple_info(
    target_user_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Query(None, description="当前用户ID（可选）")
):
    """获取用户简易信息（仅名称、头像等非敏感信息，用于案例作者展示）"""
    try:
        user_profile_service = UserProfileService(db)
        simple_info = await user_profile_service.get_simple_user_info(target_user_id)
        
        if not simple_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return simple_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户简易信息失败: {str(e)}"
        ) 