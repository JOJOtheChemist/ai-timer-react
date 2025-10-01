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
        
        # 转换为响应模型
        return UserMessageSettingResponse(
            user_id=db_setting.user_id,
            tutor_reminder=bool(db_setting.tutor_reminder),
            private_reminder=bool(db_setting.private_reminder),
            system_reminder=bool(db_setting.system_reminder),
            reminder_type=db_setting.reminder_type,
            keep_days=db_setting.keep_days,
            auto_read_system=bool(db_setting.auto_read_system),
            create_time=db_setting.create_time,
            update_time=db_setting.update_time
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
                        "update_time": updated_setting.update_time
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
                    "reset_time": reset_setting.update_time,
                    "default_settings": {
                        "tutor_reminder": True,
                        "private_reminder": True,
                        "system_reminder": True,
                        "reminder_type": "push",
                        "keep_days": 30,
                        "auto_read_system": False
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
        
        return {
            "user_id": user_id,
            "tutor_reminder_enabled": bool(db_setting.tutor_reminder),
            "private_reminder_enabled": bool(db_setting.private_reminder),
            "system_reminder_enabled": bool(db_setting.system_reminder),
            "reminder_type": db_setting.reminder_type,
            "auto_read_system": bool(db_setting.auto_read_system)
        }
    
    def check_should_send_reminder(
        self,
        db: Session,
        user_id: int,
        message_type: str
    ) -> bool:
        """检查是否应该发送提醒"""
        preferences = self.get_reminder_preferences(db, user_id)
        
        if message_type == "tutor":
            return preferences["tutor_reminder_enabled"]
        elif message_type == "private":
            return preferences["private_reminder_enabled"]
        elif message_type == "system":
            return preferences["system_reminder_enabled"]
        else:
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
            if setting_data.keep_days < 0 or setting_data.keep_days > 365:
                return False, "消息保留天数必须在0-365之间"
        
        # 验证提醒类型
        if setting_data.reminder_type is not None:
            valid_types = ["push", "email", "both"]
            if setting_data.reminder_type.value not in valid_types:
                return False, f"提醒类型必须是以下之一: {', '.join(valid_types)}"
        
        return True, "验证通过"
    
    def get_setting_summary(self, db: Session, user_id: int) -> dict:
        """获取用户消息设置摘要"""
        db_setting = crud_user_message_setting.get_or_create(db, user_id)
        
        # 统计启用的提醒类型
        enabled_reminders = []
        if db_setting.tutor_reminder:
            enabled_reminders.append("导师反馈")
        if db_setting.private_reminder:
            enabled_reminders.append("私信")
        if db_setting.system_reminder:
            enabled_reminders.append("系统通知")
        
        return {
            "user_id": user_id,
            "enabled_reminders": enabled_reminders,
            "reminder_count": len(enabled_reminders),
            "reminder_type": db_setting.reminder_type,
            "keep_days": db_setting.keep_days,
            "auto_read_system": bool(db_setting.auto_read_system),
            "is_default_settings": self._is_default_settings(db_setting)
        }
    
    def _is_default_settings(self, setting) -> bool:
        """检查是否为默认设置"""
        return (
            setting.tutor_reminder == 1 and
            setting.private_reminder == 1 and
            setting.system_reminder == 1 and
            setting.reminder_type == "push" and
            setting.keep_days == 30 and
            setting.auto_read_system == 0
        )

# 创建服务实例
user_message_setting_service = UserMessageSettingService() 