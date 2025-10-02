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
            reminder_type=0,  # 0=关闭，1=开启
            keep_days=7  # 默认保留7天
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
        """更新用户消息设置"""
        db_setting = self.get_or_create(db, user_id)
        
        update_data = setting_data.dict(exclude_unset=True)
        
        # 只更新存在于数据库中的字段
        if 'reminder_type' in update_data:
            if isinstance(update_data['reminder_type'], str):
                # 映射字符串值到数字
                db_setting.reminder_type = 1 if update_data['reminder_type'] in ['push', 'email', 'both'] else 0
            else:
                db_setting.reminder_type = 1 if update_data['reminder_type'] else 0
        
        if 'keep_days' in update_data:
            db_setting.keep_days = update_data['keep_days']
        
        db.commit()
        db.refresh(db_setting)
        return db_setting
    
    def reset_to_default(self, db: Session, user_id: int) -> UserMessageSetting:
        """重置为默认设置"""
        db_setting = self.get_or_create(db, user_id)
        
        # 重置为默认值
        db_setting.reminder_type = 0
        db_setting.keep_days = 7
        
        db.commit()
        db.refresh(db_setting)
        return db_setting
    
    def get_users_with_reminder_enabled(
        self, 
        db: Session, 
        reminder_type: str = "tutor"
    ) -> list[int]:
        """获取启用了提醒的用户列表"""
        users = db.query(UserMessageSetting.user_id).filter(
            UserMessageSetting.reminder_type == 1
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
        # 由于数据库没有auto_read_system字段，返回空列表
        return []

# 创建CRUD实例
crud_user_message_setting = CRUDUserMessageSetting() 