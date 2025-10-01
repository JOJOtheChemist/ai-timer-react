from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

class CRUDBadge:
    def get_by_id(self, db: Session, badge_id: int):
        """查询徽章的基础信息（名称、描述、图标）"""
        try:
            query = """
            SELECT 
                id,
                name,
                description,
                icon,
                category,
                level,
                rarity,
                unlock_condition,
                unlock_type,
                is_active,
                sort_order,
                create_time,
                update_time
            FROM badges 
            WHERE id = :badge_id AND is_active = true
            """
            
            result = db.execute(query, {"badge_id": badge_id}).fetchone()
            
            if result:
                return BadgeData(
                    id=result.id,
                    name=result.name,
                    description=result.description,
                    icon=result.icon,
                    category=result.category,
                    level=result.level,
                    rarity=result.rarity,
                    unlock_condition=result.unlock_condition,
                    unlock_type=result.unlock_type,
                    is_active=result.is_active,
                    sort_order=result.sort_order,
                    create_time=result.create_time,
                    update_time=result.update_time
                )
            return None
        except Exception as e:
            print(f"查询徽章信息失败: {e}")
            return None
    
    def get_all_badges(self, db: Session, category: Optional[str] = None, limit: int = 50, offset: int = 0):
        """获取所有徽章列表"""
        try:
            base_query = """
            SELECT 
                id,
                name,
                description,
                icon,
                category,
                level,
                rarity,
                unlock_condition,
                unlock_type,
                is_active,
                sort_order,
                create_time,
                update_time
            FROM badges 
            WHERE is_active = true
            """
            
            params = {"limit": limit, "offset": offset}
            
            if category:
                base_query += " AND category = :category"
                params["category"] = category
            
            base_query += " ORDER BY sort_order ASC, create_time DESC LIMIT :limit OFFSET :offset"
            
            results = db.execute(base_query, params).fetchall()
            
            badges = []
            for result in results:
                badges.append(BadgeData(
                    id=result.id,
                    name=result.name,
                    description=result.description,
                    icon=result.icon,
                    category=result.category,
                    level=result.level,
                    rarity=result.rarity,
                    unlock_condition=result.unlock_condition,
                    unlock_type=result.unlock_type,
                    is_active=result.is_active,
                    sort_order=result.sort_order,
                    create_time=result.create_time,
                    update_time=result.update_time
                ))
            
            return badges
        except Exception as e:
            print(f"获取徽章列表失败: {e}")
            return []
    
    def get_user_badge_relations(self, db: Session, user_id: int):
        """查询用户与徽章的关联数据（获得时间等）"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                badge_id,
                obtain_date,
                obtain_reason,
                is_displayed,
                display_order,
                create_time
            FROM user_badges 
            WHERE user_id = :user_id
            """
            
            results = db.execute(query, {"user_id": user_id}).fetchall()
            
            relations = []
            for result in results:
                relations.append(UserBadgeRelationData(
                    id=result.id,
                    user_id=result.user_id,
                    badge_id=result.badge_id,
                    obtain_date=result.obtain_date,
                    obtain_reason=result.obtain_reason,
                    is_displayed=result.is_displayed,
                    display_order=result.display_order,
                    create_time=result.create_time
                ))
            
            return relations
        except Exception as e:
            print(f"查询用户徽章关联失败: {e}")
            return []
    
    def get_user_badge_relation(self, db: Session, user_id: int, badge_id: int):
        """查询用户与特定徽章的关联信息"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                badge_id,
                obtain_date,
                obtain_reason,
                is_displayed,
                display_order,
                create_time
            FROM user_badges 
            WHERE user_id = :user_id AND badge_id = :badge_id
            """
            
            result = db.execute(query, {"user_id": user_id, "badge_id": badge_id}).fetchone()
            
            if result:
                return UserBadgeRelationData(
                    id=result.id,
                    user_id=result.user_id,
                    badge_id=result.badge_id,
                    obtain_date=result.obtain_date,
                    obtain_reason=result.obtain_reason,
                    is_displayed=result.is_displayed,
                    display_order=result.display_order,
                    create_time=result.create_time
                )
            return None
        except Exception as e:
            print(f"查询用户徽章关联失败: {e}")
            return None
    
    def update_user_badge_display(
        self, 
        db: Session, 
        user_id: int, 
        badge_id: int, 
        is_displayed: bool, 
        display_order: Optional[int] = None
    ) -> bool:
        """更新用户徽章展示设置"""
        try:
            update_fields = ["is_displayed = :is_displayed", "update_time = :update_time"]
            params = {
                "user_id": user_id,
                "badge_id": badge_id,
                "is_displayed": is_displayed,
                "update_time": datetime.now()
            }
            
            if display_order is not None:
                update_fields.append("display_order = :display_order")
                params["display_order"] = display_order
            
            query = f"""
            UPDATE user_badges 
            SET {', '.join(update_fields)}
            WHERE user_id = :user_id AND badge_id = :badge_id
            """
            
            result = db.execute(query, params)
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"更新徽章展示设置失败: {e}")
            db.rollback()
            return False
    
    def get_displayed_user_badges(self, db: Session, user_id: int):
        """获取用户当前展示的徽章"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                badge_id,
                obtain_date,
                obtain_reason,
                is_displayed,
                display_order,
                create_time
            FROM user_badges 
            WHERE user_id = :user_id AND is_displayed = true
            ORDER BY display_order ASC, obtain_date DESC
            """
            
            results = db.execute(query, {"user_id": user_id}).fetchall()
            
            relations = []
            for result in results:
                relations.append(UserBadgeRelationData(
                    id=result.id,
                    user_id=result.user_id,
                    badge_id=result.badge_id,
                    obtain_date=result.obtain_date,
                    obtain_reason=result.obtain_reason,
                    is_displayed=result.is_displayed,
                    display_order=result.display_order,
                    create_time=result.create_time
                ))
            
            return relations
        except Exception as e:
            print(f"获取展示徽章失败: {e}")
            return []
    
    def award_badge_to_user(
        self, 
        db: Session, 
        user_id: int, 
        badge_id: int, 
        reason: Optional[str] = None
    ) -> bool:
        """颁发徽章给用户"""
        try:
            # 检查用户是否已经获得该徽章
            existing = self.get_user_badge_relation(db, user_id, badge_id)
            if existing:
                return False  # 已经获得了
            
            query = """
            INSERT INTO user_badges (
                user_id, badge_id, obtain_date, obtain_reason, 
                is_displayed, display_order, create_time
            ) VALUES (
                :user_id, :badge_id, :obtain_date, :obtain_reason,
                :is_displayed, :display_order, :create_time
            )
            """
            
            params = {
                "user_id": user_id,
                "badge_id": badge_id,
                "obtain_date": datetime.now(),
                "obtain_reason": reason or "系统自动颁发",
                "is_displayed": True,
                "display_order": 0,
                "create_time": datetime.now()
            }
            
            db.execute(query, params)
            db.commit()
            return True
        except Exception as e:
            print(f"颁发徽章失败: {e}")
            db.rollback()
            return False
    
    def count_total_users(self, db: Session) -> int:
        """统计总用户数"""
        try:
            query = "SELECT COUNT(*) as count FROM users WHERE is_active = true"
            result = db.execute(query).fetchone()
            return result.count if result else 0
        except Exception as e:
            print(f"统计总用户数失败: {e}")
            return 0
    
    def count_badge_obtained_users(self, db: Session, badge_id: int) -> int:
        """统计获得特定徽章的用户数"""
        try:
            query = """
            SELECT COUNT(DISTINCT user_id) as count
            FROM user_badges 
            WHERE badge_id = :badge_id
            """
            result = db.execute(query, {"badge_id": badge_id}).fetchone()
            return result.count if result else 0
        except Exception as e:
            print(f"统计徽章获得用户数失败: {e}")
            return 0
    
    def create_badge(self, db: Session, badge_data: Dict[str, Any]) -> bool:
        """创建新徽章"""
        try:
            query = """
            INSERT INTO badges (
                name, description, icon, category, level, rarity,
                unlock_condition, unlock_type, is_active, sort_order,
                create_time, update_time
            ) VALUES (
                :name, :description, :icon, :category, :level, :rarity,
                :unlock_condition, :unlock_type, :is_active, :sort_order,
                :create_time, :update_time
            )
            """
            
            params = {
                "name": badge_data["name"],
                "description": badge_data["description"],
                "icon": badge_data["icon"],
                "category": badge_data["category"],
                "level": badge_data.get("level", "bronze"),
                "rarity": badge_data.get("rarity", "common"),
                "unlock_condition": badge_data["unlock_condition"],
                "unlock_type": badge_data["unlock_type"],
                "is_active": badge_data.get("is_active", True),
                "sort_order": badge_data.get("sort_order", 0),
                "create_time": datetime.now(),
                "update_time": datetime.now()
            }
            
            db.execute(query, params)
            db.commit()
            return True
        except Exception as e:
            print(f"创建徽章失败: {e}")
            db.rollback()
            return False

class BadgeData:
    """徽章数据类"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.icon = kwargs.get('icon')
        self.category = kwargs.get('category')
        self.level = kwargs.get('level')
        self.rarity = kwargs.get('rarity')
        self.unlock_condition = kwargs.get('unlock_condition', {})
        self.unlock_type = kwargs.get('unlock_type')
        self.is_active = kwargs.get('is_active', True)
        self.sort_order = kwargs.get('sort_order', 0)
        self.create_time = kwargs.get('create_time')
        self.update_time = kwargs.get('update_time')

class UserBadgeRelationData:
    """用户徽章关联数据类"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.badge_id = kwargs.get('badge_id')
        self.obtain_date = kwargs.get('obtain_date')
        self.obtain_reason = kwargs.get('obtain_reason')
        self.is_displayed = kwargs.get('is_displayed', True)
        self.display_order = kwargs.get('display_order', 0)
        self.create_time = kwargs.get('create_time') 