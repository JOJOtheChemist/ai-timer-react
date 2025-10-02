from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional, Dict, Any
from datetime import datetime

from models.schemas.user import UserProfileUpdate

class CRUDUserProfile:
    def get_by_user_id(self, db: Session, user_id: int):
        """从数据库查询用户个人信息（联合user和user_profile表）"""
        try:
            query = text("""
            SELECT 
                u.id as user_id,
                u.username,
                u.avatar,
                u.phone,
                u.goal,
                u.major,
                up.real_name,
                up.bio,
                up.total_study_hours,
                u.created_at,
                u.updated_at
            FROM "user" u
            LEFT JOIN user_profile up ON u.id = up.user_id
            WHERE u.id = :user_id
            """)
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if result:
                return UserProfileData(
                    user_id=result.user_id,
                    username=result.username,
                    avatar=result.avatar,
                    phone=result.phone,
                    goal=result.goal,
                    major=result.major,
                    real_name=result.real_name,
                    bio=result.bio,
                    total_study_hours=result.total_study_hours or 0.0,
                    created_at=result.created_at,
                    updated_at=result.updated_at
                )
            return None
        except Exception as e:
            print(f"查询用户个人信息失败: {e}")
            return None
    
    def get_by_username(self, db: Session, username: str):
        """根据用户名查询用户信息（用于唯一性检查）"""
        try:
            query = text("""
            SELECT id as user_id, username 
            FROM "user" 
            WHERE username = :username
            """)
            
            result = db.execute(query, {"username": username}).fetchone()
            return result
        except Exception as e:
            print(f"根据用户名查询失败: {e}")
            return None
    
    def update(self, db: Session, user_id: int, profile_data: UserProfileUpdate) -> bool:
        """更新数据库中的用户个人信息（分别更新user和user_profile表）"""
        try:
            # 构建user表更新字段
            user_update_fields = []
            user_params = {"user_id": user_id}
            
            if profile_data.username is not None:
                user_update_fields.append("username = :username")
                user_params["username"] = profile_data.username
            
            if profile_data.avatar is not None:
                user_update_fields.append("avatar = :avatar")
                user_params["avatar"] = profile_data.avatar
            
            if profile_data.phone is not None:
                user_update_fields.append("phone = :phone")
                user_params["phone"] = profile_data.phone
            
            if profile_data.goal is not None:
                user_update_fields.append("goal = :goal")
                user_params["goal"] = profile_data.goal
            
            # 更新user表
            if user_update_fields:
                user_update_fields.append("updated_at = CURRENT_TIMESTAMP")
                user_query = text(f"""
                UPDATE "user" 
                SET {', '.join(user_update_fields)}
                WHERE id = :user_id
                """)
                db.execute(user_query, user_params)
            
            # 构建user_profile表更新字段
            profile_update_fields = []
            profile_params = {"user_id": user_id}
            
            if profile_data.real_name is not None:
                profile_update_fields.append("real_name = :real_name")
                profile_params["real_name"] = profile_data.real_name
            
            if profile_data.bio is not None:
                profile_update_fields.append("bio = :bio")
                profile_params["bio"] = profile_data.bio
            
            # 更新user_profile表
            if profile_update_fields:
                profile_update_fields.append("updated_at = CURRENT_TIMESTAMP")
                profile_query = text(f"""
                UPDATE user_profile 
                SET {', '.join(profile_update_fields)}
                WHERE user_id = :user_id
                """)
                db.execute(profile_query, profile_params)
            
            db.commit()
            return True
        except Exception as e:
            print(f"更新用户个人信息失败: {e}")
            db.rollback()
            return False
    
    def create(self, db: Session, user_data: Dict[str, Any]) -> bool:
        """创建用户个人信息记录（同时创建user和user_profile）"""
        try:
            # 创建user记录
            user_query = text("""
            INSERT INTO "user" (
                id, username, password_hash, phone, avatar, goal, major
            ) VALUES (
                :id, :username, :password_hash, :phone, :avatar, :goal, :major
            )
            """)
            
            user_params = {
                "id": user_data["user_id"],
                "username": user_data.get("username"),
                "password_hash": user_data.get("password_hash", ""),
                "phone": user_data.get("phone"),
                "avatar": user_data.get("avatar"),
                "goal": user_data.get("goal"),
                "major": user_data.get("major")
            }
            
            db.execute(user_query, user_params)
            
            # 创建user_profile记录
            profile_query = text("""
            INSERT INTO user_profile (
                user_id, real_name, bio, total_study_hours
            ) VALUES (
                :user_id, :real_name, :bio, :total_study_hours
            )
            """)
            
            profile_params = {
                "user_id": user_data["user_id"],
                "real_name": user_data.get("real_name"),
                "bio": user_data.get("bio"),
                "total_study_hours": user_data.get("total_study_hours", 0.0)
            }
            
            db.execute(profile_query, profile_params)
            db.commit()
            return True
        except Exception as e:
            print(f"创建用户个人信息失败: {e}")
            db.rollback()
            return False
    
    def get_simple_info(self, db: Session, user_id: int):
        """从数据库查询用户简易信息（仅名称、头像等非敏感信息）"""
        try:
            query = text("""
            SELECT 
                u.id as user_id,
                u.username,
                u.avatar,
                up.real_name,
                u.created_at
            FROM "user" u
            LEFT JOIN user_profile up ON u.id = up.user_id
            WHERE u.id = :user_id
            """)
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            
            if result:
                return UserProfileData(
                    user_id=result.user_id,
                    username=result.username,
                    avatar=result.avatar,
                    real_name=result.real_name,
                    created_at=result.created_at,
                    # 其他字段设为None或默认值
                    phone=None,
                    goal=None,
                    major=None,
                    bio=None,
                    total_study_hours=0.0,
                    updated_at=None
                )
            return None
        except Exception as e:
            raise Exception(f"查询用户简易信息失败: {str(e)}")

class UserProfileData:
    """用户个人信息数据类"""
    def __init__(self, **kwargs):
        self.user_id = kwargs.get('user_id')
        self.username = kwargs.get('username')
        self.avatar = kwargs.get('avatar')
        self.phone = kwargs.get('phone')
        self.goal = kwargs.get('goal')
        self.major = kwargs.get('major')
        self.real_name = kwargs.get('real_name')
        self.bio = kwargs.get('bio')
        self.total_study_hours = kwargs.get('total_study_hours', 0.0)
        self.created_at = kwargs.get('created_at')
        self.updated_at = kwargs.get('updated_at') 