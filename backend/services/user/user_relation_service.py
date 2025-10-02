from sqlalchemy.orm import Session
from typing import List, Optional

from crud.user.crud_user_relation import CRUDUserRelation
from models.schemas.user import (
    RelationStatsResponse,
    FollowedTutorResponse,
    RecentFanResponse,
    TutorInfo,
    UserInfo,
    PrivateMessageResponse,
    FollowResponse
)
from crud.user.crud_user_message import CRUDUserMessage
from services.tutor.tutor_service import TutorService

class UserRelationService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_user_relation = CRUDUserRelation()
        self.crud_user_message = CRUDUserMessage()
        self.tutor_service = TutorService(db)
    
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
            
            print(f"DEBUG: tutor_relations count = {len(tutor_relations)}")
            for rel in tutor_relations:
                print(f"DEBUG: relation - user_id={rel.user_id}, target_id={rel.target_id}")
            
            # 获取导师详细信息
            tutors = []
            for relation in tutor_relations:
                tutor_info = await self._get_tutor_info(relation.target_id)
                print(f"DEBUG: tutor_info for id {relation.target_id} = {tutor_info}")
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
            import traceback
            traceback.print_exc()
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
                # relation.user_id is the follower (fan)
                user_info = await self._get_user_info(relation.user_id)
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
            import traceback
            traceback.print_exc()
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
        import sys
        try:
            from sqlalchemy import text
            query = """
            SELECT id, username, avatar
            FROM tutor
            WHERE id = :tutor_id
            """
            print(f"DEBUG _get_tutor_info: Querying for tutor_id={tutor_id}", flush=True)
            sys.stdout.flush()
            result = self.db.execute(text(query), {"tutor_id": tutor_id}).fetchone()
            print(f"DEBUG _get_tutor_info: result={result}", flush=True)
            sys.stdout.flush()
            
            if result:
                tutor_info = TutorInfo(
                    tutor_id=result[0],
                    name=result[1],
                    avatar=result[2],
                    title="资深导师",
                    is_verified=True
                )
                print(f"DEBUG _get_tutor_info: returning {tutor_info}", flush=True)
                sys.stdout.flush()
                return tutor_info
            else:
                print(f"DEBUG _get_tutor_info: No result found for tutor_id={tutor_id}", flush=True)
                sys.stdout.flush()
                return None
        except Exception as e:
            print(f"获取导师信息失败: {e}", flush=True)
            sys.stdout.flush()
            import traceback
            traceback.print_exc()
            return None
    
    async def _get_user_info(self, user_id: int) -> Optional[UserInfo]:
        """获取用户信息"""
        try:
            from sqlalchemy import text
            query = """
            SELECT id, username, avatar
            FROM "user"
            WHERE id = :user_id
            """
            result = self.db.execute(text(query), {"user_id": user_id}).fetchone()
            
            if result:
                return UserInfo(
                    user_id=result[0],
                    username=result[1],
                    nickname=result[1],  # Use username as nickname if no separate nickname field
                    avatar=result[2]
                )
            else:
                return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def send_tutor_message(
        self, 
        user_id: int, 
        tutor_id: int, 
        content: str
    ) -> PrivateMessageResponse:
        """校验导师状态（是否存在），创建私信记录（接收方为导师）"""
        try:
            # 校验导师是否存在
            tutor_exists = await self.tutor_service.check_tutor_exists(tutor_id)
            if not tutor_exists:
                raise Exception("导师不存在")
            
            # 创建私信记录
            message = await self.crud_user_message.create_private_message(
                self.db,
                sender_id=user_id,
                receiver_id=tutor_id,
                content=content,
                message_type="tutor"
            )
            
            # 触发私信提醒（导师的消息中心未读计数+1）
            await self._trigger_message_notification(tutor_id)
            
            return PrivateMessageResponse(
                id=message.id,
                sender_id=message.sender_id,
                receiver_id=message.receiver_id,
                content=message.content,
                message_type=message.message_type,
                is_read=False,
                created_at=message.created_at
            )
        except Exception as e:
            raise Exception(f"发送私信失败: {str(e)}")

    async def follow_tutor(self, user_id: int, tutor_id: int) -> FollowResponse:
        """关注指定导师"""
        try:
            # 校验导师是否存在
            tutor_exists = await self.tutor_service.check_tutor_exists(tutor_id)
            if not tutor_exists:
                raise Exception("导师不存在")
            
            # 检查是否已关注
            existing_relation = self.crud_user_relation.get_relation(
                self.db, user_id, tutor_id, "tutor"
            )
            
            if existing_relation:
                return FollowResponse(
                    is_followed=True,
                    message="已关注此导师",
                    follow_time=existing_relation.created_at
                )
            
            # 创建关注关系
            relation = self.crud_user_relation.create_tutor_follow(
                self.db, user_id, tutor_id
            )
            
            # 同步更新导师粉丝数
            await self.tutor_service.update_tutor_fan_count(tutor_id, increment=1)
            
            return FollowResponse(
                is_followed=True,
                message="关注成功",
                follow_time=relation.created_at
            )
        except Exception as e:
            raise Exception(f"关注导师失败: {str(e)}")

    async def unfollow_tutor(self, user_id: int, tutor_id: int) -> FollowResponse:
        """取消关注导师"""
        try:
            # 检查关注关系是否存在
            existing_relation = self.crud_user_relation.get_relation(
                self.db, user_id, tutor_id, "tutor"
            )
            
            if not existing_relation:
                return FollowResponse(
                    is_followed=False,
                    message="未关注此导师",
                    follow_time=None
                )
            
            # 删除关注关系
            success = self.crud_user_relation.delete_tutor_follow(
                self.db, user_id, tutor_id
            )
            
            if success:
                # 同步更新导师粉丝数
                await self.tutor_service.update_tutor_fan_count(tutor_id, increment=-1)
                
                return FollowResponse(
                    is_followed=False,
                    message="取消关注成功",
                    follow_time=None
                )
            else:
                raise Exception("取消关注失败")
                
        except Exception as e:
            raise Exception(f"取消关注导师失败: {str(e)}")

    async def get_user_followed_tutors(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> List[FollowedTutorResponse]:
        """查询用户关注的导师列表"""
        try:
            tutors = self.crud_user_relation.get_followed_tutors(
                self.db, 
                user_id,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            result = []
            for tutor_relation in tutors:
                tutor_info = await self._get_tutor_info(tutor_relation.target_id)
                if tutor_info:
                    result.append(FollowedTutorResponse(
                        tutor=tutor_info,
                        follow_time=tutor_relation.created_at
                    ))
            
            return result
        except Exception as e:
            raise Exception(f"获取关注导师列表失败: {str(e)}")

    async def _trigger_message_notification(self, tutor_id: int):
        """触发私信提醒（如导师的消息中心未读计数+1）"""
        try:
            # 这里可以实现消息提醒逻辑
            # 例如：更新未读消息计数、发送推送通知等
            pass
        except Exception:
            pass

    async def _get_tutor_info(self, tutor_id: int) -> Optional[TutorInfo]:
        """获取导师基础信息"""
        try:
            tutor = await self.tutor_service.get_tutor_basic_info(tutor_id)
            if tutor:
                return TutorInfo(
                    tutor_id=tutor["id"],
                    name=tutor["name"],
                    avatar=tutor["avatar"],
                    title=tutor["title"],
                    rating=tutor["rating"],
                    is_verified=tutor["is_verified"]
                )
            return None
        except Exception:
            return None 