from sqlalchemy.orm import Session
from typing import List, Optional

from crud.user.crud_user_relation import CRUDUserRelation
from models.schemas.user import (
    RelationStatsResponse,
    FollowedTutorResponse,
    RecentFanResponse,
    TutorInfo,
    UserInfo
)

class UserRelationService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_user_relation = CRUDUserRelation()
    
    async def get_relation_stats(self, user_id: int) -> RelationStatsResponse:
        """统计用户的关注导师数、粉丝数"""
        try:
            # 统计关注的导师数
            tutor_count = self.crud_user_relation.count_relations(
                self.db, user_id, relation_type="tutor"
            )
            
            # 统计粉丝数
            fan_count = self.crud_user_relation.count_relations(
                self.db, user_id, relation_type="fan"
            )
            
            # 统计关注的普通用户数
            following_count = self.crud_user_relation.count_relations(
                self.db, user_id, relation_type="following"
            )
            
            return RelationStatsResponse(
                tutor_count=tutor_count,
                fan_count=fan_count,
                following_count=following_count
            )
        except Exception as e:
            print(f"获取关系统计失败: {e}")
            return RelationStatsResponse(
                tutor_count=0,
                fan_count=0,
                following_count=0
            )
    
    async def get_followed_tutors(
        self, 
        user_id: int, 
        limit: int = 3, 
        offset: int = 0
    ) -> FollowedTutorResponse:
        """查询用户关注的导师列表（限制条数）"""
        try:
            # 获取关注的导师关系
            tutor_relations = self.crud_user_relation.get_followed_by_type(
                self.db, user_id, relation_type="tutor", limit=limit, offset=offset
            )
            
            # 获取导师详细信息
            tutors = []
            for relation in tutor_relations:
                tutor_info = await self._get_tutor_info(relation.target_id)
                if tutor_info:
                    tutors.append(tutor_info)
            
            # 获取总数
            total = self.crud_user_relation.count_relations(
                self.db, user_id, relation_type="tutor"
            )
            
            return FollowedTutorResponse(
                tutors=tutors,
                total=total
            )
        except Exception as e:
            print(f"获取关注导师列表失败: {e}")
            return FollowedTutorResponse(tutors=[], total=0)
    
    async def get_recent_fans(
        self, 
        user_id: int, 
        limit: int = 4, 
        offset: int = 0
    ) -> RecentFanResponse:
        """查询用户的最近粉丝列表（限制条数）"""
        try:
            # 获取最近的粉丝关系
            fan_relations = self.crud_user_relation.get_fans_by_user_id(
                self.db, user_id, limit=limit, offset=offset
            )
            
            # 获取粉丝详细信息
            fans = []
            for relation in fan_relations:
                user_info = await self._get_user_info(relation.follower_id)
                if user_info:
                    fans.append(user_info)
            
            # 获取总数
            total = self.crud_user_relation.count_relations(
                self.db, user_id, relation_type="fan"
            )
            
            return RecentFanResponse(
                fans=fans,
                total=total
            )
        except Exception as e:
            print(f"获取粉丝列表失败: {e}")
            return RecentFanResponse(fans=[], total=0)
    
    async def follow_user(self, follower_id: int, target_user_id: int) -> bool:
        """关注用户"""
        try:
            # 检查是否已经关注
            existing_relation = self.crud_user_relation.get_relation(
                self.db, follower_id, target_user_id
            )
            if existing_relation:
                return False  # 已经关注了
            
            # 创建关注关系
            relation_data = {
                "follower_id": follower_id,
                "target_id": target_user_id,
                "relation_type": "following"
            }
            
            success = self.crud_user_relation.create_relation(self.db, relation_data)
            return success
        except Exception as e:
            print(f"关注用户失败: {e}")
            return False
    
    async def unfollow_user(self, follower_id: int, target_user_id: int) -> bool:
        """取消关注用户"""
        try:
            # 删除关注关系
            success = self.crud_user_relation.delete_relation(
                self.db, follower_id, target_user_id
            )
            return success
        except Exception as e:
            print(f"取消关注失败: {e}")
            return False
    
    async def _get_tutor_info(self, tutor_id: int) -> Optional[TutorInfo]:
        """获取导师信息"""
        try:
            # 这里应该调用导师服务获取导师信息
            # 暂时返回模拟数据，待导师服务实现后替换
            return TutorInfo(
                tutor_id=tutor_id,
                name=f"导师{tutor_id}",
                avatar=None,
                title="资深导师",
                is_verified=True
            )
        except Exception as e:
            print(f"获取导师信息失败: {e}")
            return None
    
    async def _get_user_info(self, user_id: int) -> Optional[UserInfo]:
        """获取用户信息"""
        try:
            # 这里应该调用用户服务获取用户基础信息
            # 暂时返回模拟数据，待用户服务完善后替换
            return UserInfo(
                user_id=user_id,
                username=f"用户{user_id}",
                nickname=f"昵称{user_id}",
                avatar=None
            )
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None 