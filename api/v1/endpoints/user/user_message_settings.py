from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.user import (
    UserMessageSettingResponse, UserMessageSettingUpdate, UserOperationResponse
)
from services.user.user_message_setting_service import user_message_setting_service

router = APIRouter()

@router.get("/me/message-settings", response_model=UserMessageSettingResponse)
async def get_user_message_settings(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户消息设置（提醒方式、保留时长等）"""
    try:
        settings = user_message_setting_service.get_message_settings(db, current_user_id)
        return settings
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息设置失败: {str(e)}")

@router.put("/me/message-settings", response_model=UserOperationResponse)
async def update_user_message_settings(
    setting_data: UserMessageSettingUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """更新用户消息设置"""
    try:
        # 验证设置数据
        is_valid, error_msg = user_message_setting_service.validate_setting_update(setting_data)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # 更新设置
        result = user_message_setting_service.update_message_settings(
            db, current_user_id, setting_data
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新消息设置失败: {str(e)}")

@router.post("/me/message-settings/reset", response_model=UserOperationResponse)
async def reset_message_settings(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """重置消息设置为默认值"""
    try:
        result = user_message_setting_service.reset_to_default_settings(db, current_user_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置消息设置失败: {str(e)}")

@router.get("/me/message-settings/summary")
async def get_message_settings_summary(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户消息设置摘要"""
    try:
        summary = user_message_setting_service.get_setting_summary(db, current_user_id)
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取设置摘要失败: {str(e)}")

@router.get("/me/reminder-preferences")
async def get_reminder_preferences(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户的提醒偏好（用于消息推送服务）"""
    try:
        preferences = user_message_setting_service.get_reminder_preferences(db, current_user_id)
        return preferences
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提醒偏好失败: {str(e)}")

@router.get("/me/cleanup-settings")
async def get_cleanup_settings(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户的消息清理设置"""
    try:
        cleanup_settings = user_message_setting_service.get_cleanup_settings(db, current_user_id)
        return cleanup_settings
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取清理设置失败: {str(e)}")

@router.post("/me/check-reminder")
async def check_should_send_reminder(
    message_type: str,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """检查是否应该发送特定类型的提醒"""
    try:
        if message_type not in ["tutor", "private", "system"]:
            raise HTTPException(status_code=400, detail="无效的消息类型")
        
        should_send = user_message_setting_service.check_should_send_reminder(
            db, current_user_id, message_type
        )
        
        return {
            "user_id": current_user_id,
            "message_type": message_type,
            "should_send_reminder": should_send
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查提醒设置失败: {str(e)}")

# 管理员接口（用于系统维护）
@router.get("/admin/reminder-users/{message_type}")
async def get_reminder_users(
    message_type: str,
    db: Session = Depends(get_db),
    # current_user_id: int = Depends(get_current_admin_user)  # 实际项目中需要管理员权限
):
    """获取启用了特定类型提醒的用户列表（管理员接口）"""
    try:
        if message_type not in ["tutor", "private", "system"]:
            raise HTTPException(status_code=400, detail="无效的消息类型")
        
        user_ids = user_message_setting_service.batch_get_reminder_users(db, message_type)
        
        return {
            "message_type": message_type,
            "user_count": len(user_ids),
            "user_ids": user_ids
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提醒用户列表失败: {str(e)}")

@router.get("/admin/auto-read-users")
async def get_auto_read_users(
    db: Session = Depends(get_db),
    # current_user_id: int = Depends(get_current_admin_user)  # 实际项目中需要管理员权限
):
    """获取启用系统消息自动已读的用户列表（管理员接口）"""
    try:
        user_ids = user_message_setting_service.batch_get_auto_read_users(db)
        
        return {
            "user_count": len(user_ids),
            "user_ids": user_ids
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取自动已读用户列表失败: {str(e)}")

@router.get("/admin/cleanup-candidates")
async def get_cleanup_candidates(
    db: Session = Depends(get_db),
    # current_user_id: int = Depends(get_current_admin_user)  # 实际项目中需要管理员权限
):
    """获取需要清理消息的用户及其保留天数（管理员接口）"""
    try:
        candidates = user_message_setting_service.get_cleanup_candidates(db)
        
        return {
            "candidate_count": len(candidates),
            "candidates": candidates
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取清理候选用户失败: {str(e)}")

@router.get("/health")
async def health_check():
    """用户消息设置服务健康检查"""
    return {"status": "healthy", "service": "user_message_setting_service"} 