from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from crud.user.crud_user_profile import CRUDUserProfile
from models.schemas.user import UserProfileResponse, UserProfileUpdate
from services.statistic.statistic_service import StatisticService

class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_user_profile = CRUDUserProfile()
        self.statistic_service = StatisticService(db)
    
    async def get_current_user_profile(self, user_id: int) -> Optional[UserProfileResponse]:
        """查询当前用户的个人信息（关联学习时长统计）"""
        try:
            # 获取用户基础信息
            user_profile = self.crud_user_profile.get_by_user_id(self.db, user_id)
            if not user_profile:
                return None
            
            # 获取学习统计数据
            study_stats = await self.statistic_service.get_user_study_stats(user_id)
            
            # 获取动态和徽章统计
            moment_count = await self._get_user_moment_count(user_id)
            badge_count = await self._get_user_badge_count(user_id)
            
            # 构建响应数据
            profile_data = UserProfileResponse(
                user_id=user_profile.user_id,
                username=user_profile.username,
                nickname=user_profile.nickname,
                avatar=user_profile.avatar,
                email=user_profile.email,
                phone=user_profile.phone,
                goal=user_profile.goal,
                bio=user_profile.bio,
                total_study_hours=study_stats.get('total_hours', Decimal('0.0')),
                total_moments=moment_count,
                total_badges=badge_count,
                is_public=user_profile.is_public,
                allow_follow=user_profile.allow_follow,
                create_time=user_profile.create_time,
                update_time=user_profile.update_time
            )
            
            return profile_data
        except Exception as e:
            print(f"获取用户个人信息失败: {e}")
            return None
    
    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> bool:
        """更新用户个人信息（校验数据合法性）"""
        try:
            # 数据校验
            if not await self._validate_profile_data(profile_data):
                return False
            
            # 更新用户信息
            success = self.crud_user_profile.update(self.db, user_id, profile_data)
            
            return success
        except Exception as e:
            print(f"更新用户个人信息失败: {e}")
            return False
    
    async def _validate_profile_data(self, profile_data: UserProfileUpdate) -> bool:
        """校验用户信息数据"""
        try:
            # 用户名唯一性检查
            if profile_data.username:
                existing_user = self.crud_user_profile.get_by_username(self.db, profile_data.username)
                if existing_user:
                    return False
            
            # 邮箱格式检查
            if profile_data.email:
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, profile_data.email):
                    return False
            
            # 手机号格式检查
            if profile_data.phone:
                phone_pattern = r'^1[3-9]\d{9}$'
                if not re.match(phone_pattern, profile_data.phone):
                    return False
            
            return True
        except Exception as e:
            print(f"数据校验失败: {e}")
            return False
    
    async def _get_user_moment_count(self, user_id: int) -> int:
        """获取用户发布的动态数量"""
        try:
            # 这里应该调用moment服务获取数量
            # 暂时返回0，待moment服务实现后替换
            return 0
        except Exception:
            return 0
    
    async def _get_user_badge_count(self, user_id: int) -> int:
        """获取用户获得的徽章数量"""
        try:
            # 这里应该调用badge服务获取数量
            # 暂时返回0，待badge服务实现后替换
            return 0
        except Exception:
            return 0 