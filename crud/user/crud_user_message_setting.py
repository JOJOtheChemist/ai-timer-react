from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any

from models.message import UserMessageSetting
from models.schemas.user import UserMessageSettingUpdate

class CRUDUserMessageSetting:
    """用户消息设置CRUD操作"""
    
    def get_by_user_id(self, db: Session, user_id: int) -> Optional[UserMessageSetting]:
        """查询用户的消息设置数据"""
        return db.query(UserMessageSetting).filter(
            UserMessageSetting.user_id == user_id
        ).first()
    
    def create_default_settings(self, db: Session, user_id: int) -> UserMessageSetting:
        """为新用户创建默认消息设置"""
        db_setting = UserMessageSetting(
            user_id=user_id,
            tutor_reminder=1,
            private_reminder=1,
            system_reminder=1,
            reminder_type="push",
            keep_days=30,
            auto_read_system=0
        )
        db.add(db_setting)
        db.commit()
        db.refresh(db_setting)
        return db_setting
    
    def get_or_create(self, db: Session, user_id: int) -> UserMessageSetting:
        """获取用户消息设置，不存在则创建默认设置"""
        setting = self.get_by_user_id(db, user_id)
        if not setting:
            setting = self.create_default_settings(db, user_id)
        return setting
    
    def update(
        self, 
        db: Session, 
        user_id: int, 
        setting_data: UserMessageSettingUpdate
    ) -> Optional[UserMessageSetting]:
        """更新数据库中的消息设置"""
        db_setting = self.get_or_create(db, user_id)
        
        update_data = setting_data.dict(exclude_unset=True)
        
        # 处理布尔类型转换
        bool_fields = ['tutor_reminder', 'private_reminder', 'system_reminder', 'auto_read_system']
        for field in bool_fields:
            if field in update_data:
                update_data[field] = 1 if update_data[field] else 0
        
        # 处理枚举类型
        if 'reminder_type' in update_data and update_data['reminder_type']:
            update_data['reminder_type'] = update_data['reminder_type'].value
        
        for field, value in update_data.items():
            if hasattr(db_setting, field):
                setattr(db_setting, field, value)
        
        db.commit()
        db.refresh(db_setting)
        return db_setting
    
    def reset_to_default(self, db: Session, user_id: int) -> UserMessageSetting:
        """重置为默认设置"""
        db_setting = self.get_or_create(db, user_id)
        
        # 重置为默认值
        db_setting.tutor_reminder = 1
        db_setting.private_reminder = 1
        db_setting.system_reminder = 1
        db_setting.reminder_type = "push"
        db_setting.keep_days = 30
        db_setting.auto_read_system = 0
        
        db.commit()
        db.refresh(db_setting)
        return db_setting
    
    def get_users_with_reminder_enabled(
        self, 
        db: Session, 
        reminder_type: str = "tutor"
    ) -> list[int]:
        """获取启用了特定提醒类型的用户ID列表"""
        field_map = {
            "tutor": UserMessageSetting.tutor_reminder,
            "private": UserMessageSetting.private_reminder,
            "system": UserMessageSetting.system_reminder
        }
        
        if reminder_type not in field_map:
            return []
        
        users = db.query(UserMessageSetting.user_id).filter(
            field_map[reminder_type] == 1
        ).all()
        
        return [user.user_id for user in users]
    
    def get_cleanup_candidates(self, db: Session) -> list[Dict[str, Any]]:
        """获取需要清理消息的用户及其保留天数"""
        settings = db.query(
            UserMessageSetting.user_id,
            UserMessageSetting.keep_days
        ).filter(
            UserMessageSetting.keep_days > 0
        ).all()
        
        return [
            {"user_id": setting.user_id, "keep_days": setting.keep_days}
            for setting in settings
        ]
    
    def get_auto_read_system_users(self, db: Session) -> list[int]:
        """获取启用系统消息自动已读的用户ID列表"""
        users = db.query(UserMessageSetting.user_id).filter(
            UserMessageSetting.auto_read_system == 1
        ).all()
        
        return [user.user_id for user in users]

# 创建CRUD实例
crud_user_message_setting = CRUDUserMessageSetting() 