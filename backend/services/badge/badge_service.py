from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from crud.badge.crud_badge import CRUDBadge
from models.schemas.badge import (
    UserBadgeListResponse,
    BadgeDetailResponse,
    BadgeDisplayUpdate,
    BadgeDisplayResponse,
    UserBadgeResponse
)

class BadgeService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_badge = CRUDBadge()
    
    async def get_user_badges(
        self, 
        user_id: int, 
        category: Optional[str] = None
    ) -> UserBadgeListResponse:
        """查询用户的所有徽章（关联解锁状态和获得时间）"""
        try:
            # 获取用户徽章关联数据
            user_badge_relations = self.crud_badge.get_user_badge_relations(self.db, user_id)
            
            # 获取所有徽章基础信息
            all_badges = self.crud_badge.get_all_badges(self.db, category=category)
            
            # 构建用户徽章响应数据
            badges = []
            obtained_count = 0
            
            for badge in all_badges:
                # 查找用户是否获得该徽章
                user_badge_relation = next(
                    (rel for rel in user_badge_relations if rel.badge_id == badge.id), 
                    None
                )
                
                is_obtained = user_badge_relation is not None
                if is_obtained:
                    obtained_count += 1
                
                # 计算进度信息
                progress_info = await self._calculate_badge_progress(user_id, badge)
                
                user_badge = UserBadgeResponse(
                    badge_id=badge.id,
                    name=badge.name,
                    description=badge.description,
                    icon=badge.icon,
                    category=badge.category,
                    level=badge.level,
                    rarity=badge.rarity,
                    is_obtained=is_obtained,
                    obtain_date=user_badge_relation.obtain_date if user_badge_relation else None,
                    obtain_reason=user_badge_relation.obtain_reason if user_badge_relation else None,
                    current_progress=progress_info.get('current_progress'),
                    target_progress=progress_info.get('target_progress'),
                    progress_percentage=progress_info.get('progress_percentage'),
                    is_displayed=user_badge_relation.is_displayed if user_badge_relation else True,
                    display_order=user_badge_relation.display_order if user_badge_relation else 0
                )
                badges.append(user_badge)
            
            # 获取徽章分类列表
            categories = list(set(badge.category for badge in all_badges))
            
            return UserBadgeListResponse(
                badges=badges,
                total=len(badges),
                obtained_count=obtained_count,
                categories=categories
            )
        except Exception as e:
            print(f"获取用户徽章列表失败: {e}")
            return UserBadgeListResponse(
                badges=[],
                total=0,
                obtained_count=0,
                categories=[]
            )
    
    async def get_badge_detail(
        self, 
        badge_id: int, 
        user_id: int
    ) -> Optional[BadgeDetailResponse]:
        """查询徽章详情（含用户是否已获得）"""
        try:
            # 获取徽章基础信息
            badge = self.crud_badge.get_by_id(self.db, badge_id)
            if not badge:
                return None
            
            # 获取用户徽章关联信息
            user_badge_relation = self.crud_badge.get_user_badge_relation(
                self.db, user_id, badge_id
            )
            
            is_obtained = user_badge_relation is not None
            
            # 计算进度信息
            progress_info = await self._calculate_badge_progress(user_id, badge)
            
            # 获取统计信息
            stats_info = await self._get_badge_stats(badge_id)
            
            badge_detail = BadgeDetailResponse(
                id=badge.id,
                name=badge.name,
                description=badge.description,
                icon=badge.icon,
                category=badge.category,
                level=badge.level,
                rarity=badge.rarity,
                unlock_condition=badge.unlock_condition,
                unlock_type=badge.unlock_type,
                is_active=badge.is_active,
                sort_order=badge.sort_order,
                create_time=badge.create_time,
                update_time=badge.update_time,
                is_obtained=is_obtained,
                obtain_date=user_badge_relation.obtain_date if user_badge_relation else None,
                obtain_reason=user_badge_relation.obtain_reason if user_badge_relation else None,
                lock_condition=await self._generate_lock_condition_text(badge),
                current_progress=progress_info.get('current_progress'),
                target_progress=progress_info.get('target_progress'),
                progress_percentage=progress_info.get('progress_percentage'),
                progress_data=progress_info.get('progress_data'),
                total_obtained_users=stats_info.get('total_obtained_users', 0),
                obtain_rate=stats_info.get('obtain_rate', 0.0)
            )
            
            return badge_detail
        except Exception as e:
            print(f"获取徽章详情失败: {e}")
            return None
    
    async def get_all_badges(
        self,
        user_id: int,
        category: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BadgeDetailResponse]:
        """获取所有徽章列表（含用户获得状态）"""
        try:
            badges = self.crud_badge.get_all_badges(
                self.db, 
                category=category, 
                limit=limit, 
                offset=offset
            )
            
            badge_details = []
            for badge in badges:
                badge_detail = await self.get_badge_detail(badge.id, user_id)
                if badge_detail:
                    badge_details.append(badge_detail)
            
            return badge_details
        except Exception as e:
            print(f"获取徽章列表失败: {e}")
            return []
    
    async def update_badge_display(
        self, 
        user_id: int, 
        display_updates: List[BadgeDisplayUpdate]
    ) -> bool:
        """更新徽章展示设置"""
        try:
            for update in display_updates:
                success = self.crud_badge.update_user_badge_display(
                    self.db,
                    user_id,
                    update.badge_id,
                    update.is_displayed,
                    update.display_order
                )
                if not success:
                    return False
            
            return True
        except Exception as e:
            print(f"更新徽章展示设置失败: {e}")
            return False
    
    async def get_displayed_badges(self, user_id: int) -> BadgeDisplayResponse:
        """获取当前展示的徽章列表"""
        try:
            displayed_relations = self.crud_badge.get_displayed_user_badges(self.db, user_id)
            
            displayed_badges = []
            for relation in displayed_relations:
                badge = self.crud_badge.get_by_id(self.db, relation.badge_id)
                if badge:
                    user_badge = UserBadgeResponse(
                        badge_id=badge.id,
                        name=badge.name,
                        description=badge.description,
                        icon=badge.icon,
                        category=badge.category,
                        level=badge.level,
                        rarity=badge.rarity,
                        is_obtained=True,
                        obtain_date=relation.obtain_date,
                        obtain_reason=relation.obtain_reason,
                        is_displayed=relation.is_displayed,
                        display_order=relation.display_order
                    )
                    displayed_badges.append(user_badge)
            
            # 按展示顺序排序
            displayed_badges.sort(key=lambda x: x.display_order)
            
            return BadgeDisplayResponse(
                displayed_badges=displayed_badges,
                max_display_count=6
            )
        except Exception as e:
            print(f"获取展示徽章失败: {e}")
            return BadgeDisplayResponse(displayed_badges=[], max_display_count=6)
    
    async def _calculate_badge_progress(
        self, 
        user_id: int, 
        badge: Any
    ) -> Dict[str, Any]:
        """计算徽章进度信息"""
        try:
            unlock_condition = badge.unlock_condition
            unlock_type = badge.unlock_type
            
            if unlock_type == "study_hours":
                # 学习时长类型徽章
                target_hours = unlock_condition.get("hours", 0)
                current_hours = await self._get_user_study_hours(user_id)
                progress_percentage = min((current_hours / target_hours) * 100, 100) if target_hours > 0 else 0
                
                return {
                    "current_progress": int(current_hours),
                    "target_progress": target_hours,
                    "progress_percentage": round(progress_percentage, 2),
                    "progress_data": {"current_hours": current_hours, "target_hours": target_hours}
                }
            
            elif unlock_type == "consecutive_days":
                # 连续学习天数类型徽章
                target_days = unlock_condition.get("days", 0)
                current_days = await self._get_user_consecutive_days(user_id)
                progress_percentage = min((current_days / target_days) * 100, 100) if target_days > 0 else 0
                
                return {
                    "current_progress": current_days,
                    "target_progress": target_days,
                    "progress_percentage": round(progress_percentage, 2),
                    "progress_data": {"current_days": current_days, "target_days": target_days}
                }
            
            else:
                # 其他类型徽章，暂时返回默认值
                return {
                    "current_progress": 0,
                    "target_progress": 1,
                    "progress_percentage": 0.0,
                    "progress_data": {}
                }
        except Exception as e:
            print(f"计算徽章进度失败: {e}")
            return {
                "current_progress": 0,
                "target_progress": 1,
                "progress_percentage": 0.0,
                "progress_data": {}
            }
    
    async def _generate_lock_condition_text(self, badge: Any) -> str:
        """生成解锁条件描述文本"""
        try:
            unlock_condition = badge.unlock_condition
            unlock_type = badge.unlock_type
            
            if unlock_type == "study_hours":
                hours = unlock_condition.get("hours", 0)
                return f"累计学习{hours}小时"
            elif unlock_type == "consecutive_days":
                days = unlock_condition.get("days", 0)
                return f"连续学习{days}天"
            else:
                return "完成特定任务"
        except Exception:
            return "完成特定条件"
    
    async def _get_badge_stats(self, badge_id: int) -> Dict[str, Any]:
        """获取徽章统计信息"""
        try:
            total_users = self.crud_badge.count_total_users(self.db)
            obtained_users = self.crud_badge.count_badge_obtained_users(self.db, badge_id)
            obtain_rate = (obtained_users / total_users) * 100 if total_users > 0 else 0
            
            return {
                "total_obtained_users": obtained_users,
                "obtain_rate": round(obtain_rate, 2)
            }
        except Exception:
            return {
                "total_obtained_users": 0,
                "obtain_rate": 0.0
            }
    
    async def _get_user_study_hours(self, user_id: int) -> float:
        """获取用户总学习时长"""
        try:
            # 这里应该调用统计服务获取学习时长
            # 暂时返回模拟数据
            return 0.0
        except Exception:
            return 0.0
    
    async def _get_user_consecutive_days(self, user_id: int) -> int:
        """获取用户连续学习天数"""
        try:
            # 这里应该调用统计服务获取连续学习天数
            # 暂时返回模拟数据
            return 0
        except Exception:
            return 0 