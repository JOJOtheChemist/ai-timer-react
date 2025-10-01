from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import Optional, Dict, Any
from datetime import datetime

from models.schemas.user import UserProfileUpdate

class CRUDUserProfile:
    def get_by_user_id(self, db: Session, user_id: int):
        """从数据库查询用户个人信息"""
        try:
            # 这里需要根据实际的数据库模型来实现
            # 暂时返回模拟数据结构
            query = """
            SELECT 
                user_id,
                username,
                nickname,
                avatar,
                email,
                phone,
                goal,
                bio,
                is_public,
                allow_follow,
                create_time,
                update_time
            FROM user_profiles 
            WHERE user_id = :user_id
            """
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if result:
                return UserProfileData(
                    user_id=result.user_id,
                    username=result.username,
                    nickname=result.nickname,
                    avatar=result.avatar,
                    email=result.email,
                    phone=result.phone,
                    goal=result.goal,
                    bio=result.bio,
                    is_public=result.is_public,
                    allow_follow=result.allow_follow,
                    create_time=result.create_time,
                    update_time=result.update_time
                )
            return None
        except Exception as e:
            print(f"查询用户个人信息失败: {e}")
            return None
    
    def get_by_username(self, db: Session, username: str):
        """根据用户名查询用户信息（用于唯一性检查）"""
        try:
            query = """
            SELECT user_id, username 
            FROM user_profiles 
            WHERE username = :username
            """
            
            result = db.execute(query, {"username": username}).fetchone()
            return result
        except Exception as e:
            print(f"根据用户名查询失败: {e}")
            return None
    
    def update(self, db: Session, user_id: int, profile_data: UserProfileUpdate) -> bool:
        """更新数据库中的用户个人信息"""
        try:
            # 构建更新字段
            update_fields = []
            params = {"user_id": user_id, "update_time": datetime.now()}
            
            if profile_data.username is not None:
                update_fields.append("username = :username")
                params["username"] = profile_data.username
            
            if profile_data.nickname is not None:
                update_fields.append("nickname = :nickname")
                params["nickname"] = profile_data.nickname
            
            if profile_data.avatar is not None:
                update_fields.append("avatar = :avatar")
                params["avatar"] = profile_data.avatar
            
            if profile_data.email is not None:
                update_fields.append("email = :email")
                params["email"] = profile_data.email
            
            if profile_data.phone is not None:
                update_fields.append("phone = :phone")
                params["phone"] = profile_data.phone
            
            if profile_data.goal is not None:
                update_fields.append("goal = :goal")
                params["goal"] = profile_data.goal
            
            if profile_data.bio is not None:
                update_fields.append("bio = :bio")
                params["bio"] = profile_data.bio
            
            if profile_data.is_public is not None:
                update_fields.append("is_public = :is_public")
                params["is_public"] = profile_data.is_public
            
            if profile_data.allow_follow is not None:
                update_fields.append("allow_follow = :allow_follow")
                params["allow_follow"] = profile_data.allow_follow
            
            if not update_fields:
                return True  # 没有需要更新的字段
            
            # 添加更新时间
            update_fields.append("update_time = :update_time")
            
            query = f"""
            UPDATE user_profiles 
            SET {', '.join(update_fields)}
            WHERE user_id = :user_id
            """
            
            result = db.execute(query, params)
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"更新用户个人信息失败: {e}")
            db.rollback()
            return False
    
    def create(self, db: Session, user_data: Dict[str, Any]) -> bool:
        """创建用户个人信息记录"""
        try:
            query = """
            INSERT INTO user_profiles (
                user_id, username, nickname, avatar, email, phone, 
                goal, bio, is_public, allow_follow, create_time, update_time
            ) VALUES (
                :user_id, :username, :nickname, :avatar, :email, :phone,
                :goal, :bio, :is_public, :allow_follow, :create_time, :update_time
            )
            """
            
            params = {
                "user_id": user_data["user_id"],
                "username": user_data.get("username"),
                "nickname": user_data.get("nickname"),
                "avatar": user_data.get("avatar"),
                "email": user_data.get("email"),
                "phone": user_data.get("phone"),
                "goal": user_data.get("goal"),
                "bio": user_data.get("bio"),
                "is_public": user_data.get("is_public", True),
                "allow_follow": user_data.get("allow_follow", True),
                "create_time": datetime.now(),
                "update_time": datetime.now()
            }
            
            db.execute(query, params)
            db.commit()
            return True
        except Exception as e:
            print(f"创建用户个人信息失败: {e}")
            db.rollback()
            return False

class UserProfileData:
    """用户个人信息数据类"""
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.username = kwargs.get('username')
        self.nickname = kwargs.get('nickname')
        self.avatar = kwargs.get('avatar')
        self.email = kwargs.get('email')
        self.phone = kwargs.get('phone')
        self.goal = kwargs.get('goal')
        self.bio = kwargs.get('bio')
        self.is_public = kwargs.get('is_public', True)
        self.allow_follow = kwargs.get('allow_follow', True)
        self.create_time = kwargs.get('create_time')
        self.update_time = kwargs.get('update_time') 