from sqlalchemy.orm import Session
from typing import Optional
from decimal import Decimal

from crud.user.crud_user_profile import CRUDUserProfile
from models.schemas.user import UserProfileResponse, UserProfileUpdate, UserSimpleInfoResponse
# from services.statistic.statistic_service import StatisticService

class UserProfileService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_user_profile = CRUDUserProfile()
        # self.statistic_service = StatisticService(db)
    
    async def get_current_user_profile(self, user_id: int) -> Optional[UserProfileResponse]:
        """查询当前用户的个人信息（关联学习时长统计）"""
        try:
            # 获取用户基础信息
            user_profile = self.crud_user_profile.get_by_user_id(self.db, user_id)
            if not user_profile:
                return None
            
            # 获取学习统计数据（暂时返回空，待StatisticService修复后启用）
            # study_stats = await self.statistic_service.get_user_study_stats(user_id)
            study_stats = {"total_hours": Decimal('0.0')}
            
            # 获取动态和徽章统计
            moment_count = await self._get_user_moment_count(user_id)
            badge_count = await self._get_user_badge_count(user_id)
            
            # 构建响应数据
            profile_data = UserProfileResponse(
                user_id=user_profile.user_id,
                username=user_profile.username,
                avatar=user_profile.avatar,
                phone=user_profile.phone,
                goal=user_profile.goal,
                major=user_profile.major,
                real_name=user_profile.real_name,
                bio=user_profile.bio,
                total_study_hours=study_stats.get('total_hours', Decimal('0.0')),
                total_moments=moment_count,
                total_badges=badge_count,
                created_at=user_profile.created_at,
                updated_at=user_profile.updated_at
            )
            
            return profile_data
        except Exception as e:
            print(f"获取用户个人信息失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    async def update_user_profile(self, user_id: int, profile_data: UserProfileUpdate) -> bool:
        """更新用户个人信息（校验数据合法性）"""
        try:
            # 数据校验
            if not await self._validate_profile_data(user_id, profile_data):
                return False
            
            # 更新用户信息
            success = self.crud_user_profile.update(self.db, user_id, profile_data)
            
            return success
        except Exception as e:
            print(f"更新用户个人信息失败: {e}")
            return False
    
    async def _validate_profile_data(self, user_id: int, profile_data: UserProfileUpdate) -> bool:
        """校验用户信息数据"""
        try:
            # 用户名唯一性检查
            if profile_data.username:
                existing_user = self.crud_user_profile.get_by_username(self.db, profile_data.username)
                if existing_user and existing_user.user_id != user_id:
                    print(f"用户名 {profile_data.username} 已存在")
                    return False
            
            # 手机号格式检查
            if profile_data.phone:
                import re
                phone_pattern = r'^1[3-9]\d{9}$'
                if not re.match(phone_pattern, profile_data.phone):
                    print(f"手机号格式不正确: {profile_data.phone}")
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

    async def get_simple_user_info(self, user_id: int) -> Optional[UserSimpleInfoResponse]:
        """获取用户简易信息（仅名称、头像等非敏感信息，用于案例作者展示）"""
        try:
            # 获取用户基础信息
            user_profile = self.crud_user_profile.get_simple_info(self.db, user_id)
            if not user_profile:
                return None
            
            # 构建简易信息响应
            simple_info = UserSimpleInfoResponse(
                id=user_profile.user_id,
                username=user_profile.username,
                nickname=user_profile.real_name,  # 使用real_name作为nickname
                avatar=user_profile.avatar,
                is_verified=False,  # 默认未认证
                created_at=user_profile.created_at
            )
            
            return simple_info
        except Exception as e:
            raise Exception(f"获取用户简易信息失败: {str(e)}") 