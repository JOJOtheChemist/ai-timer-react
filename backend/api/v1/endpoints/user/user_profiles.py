from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from models.schemas.user import UserProfileResponse, UserProfileUpdate, UserOperationResponse
from services.user.user_profile_service import UserProfileService

router = APIRouter()

@router.get("/me/profile", response_model=UserProfileResponse)
async def get_current_user_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前登录用户的完整个人信息（含基础信息、总学习时长）"""
    try:
        user_profile_service = UserProfileService(db)
        profile = await user_profile_service.get_current_user_profile(current_user["id"])
        
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
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新当前用户的个人信息（如修改goal、username）"""
    try:
        user_profile_service = UserProfileService(db)
        success = await user_profile_service.update_user_profile(
            current_user["id"], 
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