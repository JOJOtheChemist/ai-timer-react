from sqlalchemy.orm import Session
from typing import Optional

from models.schemas.user import (
    UserMessageSettingResponse, UserMessageSettingUpdate, UserOperationResponse
)
from crud.user.crud_user_message_setting import crud_user_message_setting

class UserMessageSettingService:
    """用户消息设置服务层"""
    
    def get_message_settings(self, db: Session, user_id: int) -> UserMessageSettingResponse:
        """查询用户的消息偏好设置"""
        # 获取或创建用户消息设置
        db_setting = crud_user_message_setting.get_or_create(db, user_id)
        
        # 根据reminder_type映射到前端格式
        reminder_enabled = bool(db_setting.reminder_type)
        
        # 转换为响应模型
        return UserMessageSettingResponse(
            user_id=db_setting.user_id,
            tutor_reminder=reminder_enabled,
            private_reminder=reminder_enabled,
            system_reminder=reminder_enabled,
            reminder_type="push",  # 默认总是返回push（因为enum不接受none）
            keep_days=db_setting.keep_days,
            auto_read_system=False,
            create_time=db_setting.created_at,
            update_time=db_setting.updated_at
        )
    
    def update_message_settings(
        self,
        db: Session,
        user_id: int,
        setting_data: UserMessageSettingUpdate
    ) -> UserOperationResponse:
        """更新消息设置（如提醒方式、自动清理天数）"""
        try:
            # 更新设置
            updated_setting = crud_user_message_setting.update(db, user_id, setting_data)
            
            if updated_setting:
                return UserOperationResponse(
                    success=True,
                    message="消息设置更新成功",
                    data={
                        "user_id": user_id,
                        "updated_fields": setting_data.dict(exclude_unset=True),
                        "update_time": updated_setting.updated_at
                    }
                )
            else:
                return UserOperationResponse(
                    success=False,
                    message="消息设置更新失败"
                )
        
        except Exception as e:
            return UserOperationResponse(
                success=False,
                message=f"更新消息设置时发生错误: {str(e)}"
            )
    
    def reset_to_default_settings(self, db: Session, user_id: int) -> UserOperationResponse:
        """重置为默认消息设置"""
        try:
            reset_setting = crud_user_message_setting.reset_to_default(db, user_id)
            
            return UserOperationResponse(
                success=True,
                message="消息设置已重置为默认值",
                data={
                    "user_id": user_id,
                    "reset_time": reset_setting.updated_at,
                    "default_settings": {
                        "reminder_type": 0,
                        "keep_days": 7
                    }
                }
            )
        
        except Exception as e:
            return UserOperationResponse(
                success=False,
                message=f"重置消息设置时发生错误: {str(e)}"
            )
    
    def get_reminder_preferences(self, db: Session, user_id: int) -> dict:
        """获取用户的提醒偏好（用于消息推送服务）"""
        db_setting = crud_user_message_setting.get_or_create(db, user_id)
        reminder_enabled = bool(db_setting.reminder_type)
        
        return {
            "user_id": user_id,
            "tutor_reminder_enabled": reminder_enabled,
            "private_reminder_enabled": reminder_enabled,
            "system_reminder_enabled": reminder_enabled,
            "reminder_type": "push" if reminder_enabled else "none",
            "auto_read_system": False
        }
    
    def check_should_send_reminder(
        self,
        db: Session,
        user_id: int,
        message_type: str
    ) -> bool:
        """检查是否应该发送提醒"""
        preferences = self.get_reminder_preferences(db, user_id)
        
        # 简化版：所有类型的提醒状态相同
        if message_type in ["tutor", "private", "system"]:
            return preferences["tutor_reminder_enabled"]
        return False
    
    def get_cleanup_settings(self, db: Session, user_id: int) -> dict:
        """获取用户的消息清理设置"""
        db_setting = crud_user_message_setting.get_or_create(db, user_id)
        
        return {
            "user_id": user_id,
            "keep_days": db_setting.keep_days,
            "auto_cleanup_enabled": db_setting.keep_days > 0
        }
    
    def batch_get_reminder_users(self, db: Session, message_type: str) -> list[int]:
        """批量获取启用了特定类型提醒的用户列表"""
        return crud_user_message_setting.get_users_with_reminder_enabled(db, message_type)
    
    def batch_get_auto_read_users(self, db: Session) -> list[int]:
        """批量获取启用系统消息自动已读的用户列表"""
        return crud_user_message_setting.get_auto_read_system_users(db)
    
    def get_cleanup_candidates(self, db: Session) -> list[dict]:
        """获取需要清理消息的用户及其保留天数"""
        return crud_user_message_setting.get_cleanup_candidates(db)
    
    def validate_setting_update(self, setting_data: UserMessageSettingUpdate) -> tuple[bool, str]:
        """验证设置更新数据"""
        # 验证保留天数
        if setting_data.keep_days is not None:
            if setting_data.keep_days < 1 or setting_data.keep_days > 365:
                return False, "消息保留天数必须在1-365之间"
        
        return True, "验证通过"
    
    def get_setting_summary(self, db: Session, user_id: int) -> dict:
        """获取用户消息设置摘要"""
        db_setting = crud_user_message_setting.get_or_create(db, user_id)
        reminder_enabled = bool(db_setting.reminder_type)
        
        # 统计启用的提醒类型
        enabled_reminders = []
        if reminder_enabled:
            enabled_reminders = ["导师反馈", "私信", "系统通知"]
        
        return {
            "user_id": user_id,
            "enabled_reminders": enabled_reminders,
            "reminder_count": len(enabled_reminders),
            "reminder_type": "push" if reminder_enabled else "none",
            "keep_days": db_setting.keep_days,
            "auto_read_system": False,
            "is_default_settings": db_setting.reminder_type == 0 and db_setting.keep_days == 7
        }

# 创建服务实例
user_message_setting_service = UserMessageSettingService() 