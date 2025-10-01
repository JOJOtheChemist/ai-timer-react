from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

class CRUDUserRelation:
    def count_relations(self, db: Session, user_id: int, relation_type: str) -> int:
        """统计指定类型的关系数量（导师/粉丝）"""
        try:
            if relation_type == "tutor":
                # 统计关注的导师数
                query = """
                SELECT COUNT(*) as count
                FROM user_relations 
                WHERE follower_id = :user_id AND relation_type = 'tutor'
                """
            elif relation_type == "fan":
                # 统计粉丝数（有多少人关注了这个用户）
                query = """
                SELECT COUNT(*) as count
                FROM user_relations 
                WHERE target_id = :user_id AND relation_type IN ('following', 'tutor')
                """
            elif relation_type == "following":
                # 统计关注的普通用户数
                query = """
                SELECT COUNT(*) as count
                FROM user_relations 
                WHERE follower_id = :user_id AND relation_type = 'following'
                """
            else:
                return 0
            
            result = db.execute(query, {"user_id": user_id}).fetchone()
            return result.count if result else 0
        except Exception as e:
            print(f"统计关系数量失败: {e}")
            return 0
    
    def get_followed_by_type(
        self, 
        db: Session, 
        user_id: int, 
        relation_type: str, 
        limit: int, 
        offset: int = 0
    ):
        """查询指定类型的关系列表"""
        try:
            query = """
            SELECT 
                id,
                follower_id,
                target_id,
                relation_type,
                create_time
            FROM user_relations 
            WHERE follower_id = :user_id AND relation_type = :relation_type
            ORDER BY create_time DESC
            LIMIT :limit OFFSET :offset
            """
            
            results = db.execute(query, {
                "user_id": user_id,
                "relation_type": relation_type,
                "limit": limit,
                "offset": offset
            }).fetchall()
            
            relations = []
            for result in results:
                relations.append(UserRelationData(
                    id=result.id,
                    follower_id=result.follower_id,
                    target_id=result.target_id,
                    relation_type=result.relation_type,
                    create_time=result.create_time
                ))
            
            return relations
        except Exception as e:
            print(f"查询关系列表失败: {e}")
            return []
    
    def get_fans_by_user_id(self, db: Session, user_id: int, limit: int, offset: int = 0):
        """查询用户的粉丝列表"""
        try:
            query = """
            SELECT 
                id,
                follower_id,
                target_id,
                relation_type,
                create_time
            FROM user_relations 
            WHERE target_id = :user_id AND relation_type IN ('following', 'tutor')
            ORDER BY create_time DESC
            LIMIT :limit OFFSET :offset
            """
            
            results = db.execute(query, {
                "user_id": user_id,
                "limit": limit,
                "offset": offset
            }).fetchall()
            
            relations = []
            for result in results:
                relations.append(UserRelationData(
                    id=result.id,
                    follower_id=result.follower_id,
                    target_id=result.target_id,
                    relation_type=result.relation_type,
                    create_time=result.create_time
                ))
            
            return relations
        except Exception as e:
            print(f"查询粉丝列表失败: {e}")
            return []
    
    def get_relation(self, db: Session, follower_id: int, target_id: int):
        """查询两个用户之间的关系"""
        try:
            query = """
            SELECT 
                id,
                follower_id,
                target_id,
                relation_type,
                create_time
            FROM user_relations 
            WHERE follower_id = :follower_id AND target_id = :target_id
            """
            
            result = db.execute(query, {
                "follower_id": follower_id,
                "target_id": target_id
            }).fetchone()
            
            if result:
                return UserRelationData(
                    id=result.id,
                    follower_id=result.follower_id,
                    target_id=result.target_id,
                    relation_type=result.relation_type,
                    create_time=result.create_time
                )
            return None
        except Exception as e:
            print(f"查询用户关系失败: {e}")
            return None
    
    def create_relation(self, db: Session, relation_data: dict) -> bool:
        """创建关注关系"""
        try:
            query = """
            INSERT INTO user_relations (
                follower_id, target_id, relation_type, create_time
            ) VALUES (
                :follower_id, :target_id, :relation_type, :create_time
            )
            """
            
            params = {
                "follower_id": relation_data["follower_id"],
                "target_id": relation_data["target_id"],
                "relation_type": relation_data["relation_type"],
                "create_time": datetime.now()
            }
            
            db.execute(query, params)
            db.commit()
            return True
        except Exception as e:
            print(f"创建关注关系失败: {e}")
            db.rollback()
            return False
    
    def delete_relation(self, db: Session, follower_id: int, target_id: int) -> bool:
        """删除关注关系"""
        try:
            query = """
            DELETE FROM user_relations 
            WHERE follower_id = :follower_id AND target_id = :target_id
            """
            
            result = db.execute(query, {
                "follower_id": follower_id,
                "target_id": target_id
            })
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"删除关注关系失败: {e}")
            db.rollback()
            return False
    
    def update_relation_type(
        self, 
        db: Session, 
        follower_id: int, 
        target_id: int, 
        new_relation_type: str
    ) -> bool:
        """更新关系类型"""
        try:
            query = """
            UPDATE user_relations 
            SET relation_type = :relation_type, update_time = :update_time
            WHERE follower_id = :follower_id AND target_id = :target_id
            """
            
            result = db.execute(query, {
                "follower_id": follower_id,
                "target_id": target_id,
                "relation_type": new_relation_type,
                "update_time": datetime.now()
            })
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"更新关系类型失败: {e}")
            db.rollback()
            return False

class UserRelationData:
    """用户关系数据类"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.follower_id = kwargs.get('follower_id')
        self.target_id = kwargs.get('target_id')
        self.relation_type = kwargs.get('relation_type')
        self.create_time = kwargs.get('create_time') 