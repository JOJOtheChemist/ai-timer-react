from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional, Dict, Any
from datetime import datetime

class CRUDMethod:
    def get_by_id(self, db: Session, method_id: int):
        """查询方法完整基础数据（含steps、scene等）"""
        try:
            query = """
            SELECT 
                id,
                name,
                description,
                category,
                difficulty_level,
                estimated_time,
                steps,
                scene,
                meta,
                tags,
                author_info,
                is_active,
                checkin_count,
                create_time,
                update_time
            FROM study_methods 
            WHERE id = :method_id
            """
            
            result = db.execute(query, {"method_id": method_id}).fetchone()
            
            if result:
                return MethodData(
                    id=result.id,
                    name=result.name,
                    description=result.description,
                    category=result.category,
                    difficulty_level=result.difficulty_level,
                    estimated_time=result.estimated_time,
                    steps=result.steps,
                    scene=result.scene,
                    meta=result.meta,
                    tags=result.tags,
                    author_info=result.author_info,
                    is_active=result.is_active,
                    checkin_count=result.checkin_count,
                    create_time=result.create_time,
                    update_time=result.update_time
                )
            return None
        except Exception as e:
            print(f"查询方法失败: {e}")
            return None
    
    def get_multi_by_category(
        self, 
        db: Session, 
        category: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ):
        """按分类查询学习方法基础数据"""
        try:
            base_query = """
            SELECT 
                id,
                name,
                description,
                category,
                type,
                steps,
                scene,
                tutor_id,
                checkin_count,
                rating,
                review_count,
                status,
                create_time,
                update_time
            FROM study_method 
            WHERE status = 0
            """
            
            params = {
                "limit": page_size,
                "offset": (page - 1) * page_size
            }
            
            if category:
                base_query += " AND category = :category"
                params["category"] = category
            
            base_query += " ORDER BY checkin_count DESC, create_time DESC LIMIT :limit OFFSET :offset"
            
            results = db.execute(text(base_query), params).fetchall()
            
            methods = []
            for result in results:
                method_dict = {
                    'id': result[0],
                    'name': result[1],
                    'description': result[2],
                    'category': result[3],
                    'type': result[4],
                    'steps': result[5],
                    'scene': result[6],
                    'tutor_id': result[7],
                    'checkin_count': result[8],
                    'rating': result[9],
                    'review_count': result[10],
                    'status': result[11],
                    'create_time': result[12],
                    'update_time': result[13]
                }
                methods.append(method_dict)
            
            return methods
        except Exception as e:
            print(f"按分类查询方法失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def get_suitable_by_user_behavior(
        self, 
        db: Session, 
        user_behavior_tags: List[str],
        category: Optional[str] = None,
        limit: int = 10
    ):
        """根据用户行为标签（如"复习不足"）查询适配的学习方法"""
        try:
            # 构建标签匹配条件
            tag_conditions = []
            params = {"limit": limit}
            
            for i, tag in enumerate(user_behavior_tags):
                tag_param = f"tag_{i}"
                if tag == "复习不足":
                    tag_conditions.append(f"(name LIKE '%艾宾浩斯%' OR tags LIKE '%复习%' OR tags LIKE '%记忆%')")
                elif tag == "专注度不足":
                    tag_conditions.append(f"(name LIKE '%番茄%' OR tags LIKE '%专注%' OR tags LIKE '%注意力%')")
                elif tag == "时间碎片化":
                    tag_conditions.append(f"estimated_time <= 30")
                elif tag == "学习不规律":
                    tag_conditions.append(f"(tags LIKE '%习惯%' OR tags LIKE '%规律%')")
                else:
                    # 通用标签匹配
                    tag_conditions.append(f"tags LIKE :{tag_param}")
                    params[tag_param] = f"%{tag}%"
            
            base_query = """
            SELECT 
                id,
                name,
                description,
                category,
                difficulty_level,
                estimated_time,
                steps,
                tags,
                author_info,
                is_active,
                checkin_count,
                create_time,
                update_time
            FROM study_methods 
            WHERE is_active = true
            """
            
            if category:
                base_query += " AND category = :category"
                params["category"] = category
            
            if tag_conditions:
                base_query += f" AND ({' OR '.join(tag_conditions)})"
            
            base_query += " ORDER BY checkin_count DESC LIMIT :limit"
            
            results = db.execute(base_query, params).fetchall()
            
            methods = []
            for result in results:
                methods.append(MethodData(
                    id=result.id,
                    name=result.name,
                    description=result.description,
                    category=result.category,
                    difficulty_level=result.difficulty_level,
                    estimated_time=result.estimated_time,
                    steps=result.steps,
                    tags=result.tags,
                    author_info=result.author_info,
                    is_active=result.is_active,
                    checkin_count=result.checkin_count,
                    create_time=result.create_time,
                    update_time=result.update_time
                ))
            
            return methods
        except Exception as e:
            print(f"根据行为标签查询方法失败: {e}")
            return []
    
    def get_popular_methods(self, db: Session, limit: int = 10):
        """获取热门方法（按打卡人数排序）"""
        try:
            query = """
            SELECT 
                id,
                name,
                description,
                category,
                difficulty_level,
                estimated_time,
                tags,
                author_info,
                is_active,
                checkin_count,
                create_time,
                update_time
            FROM study_methods 
            WHERE is_active = true
            ORDER BY checkin_count DESC, create_time DESC
            LIMIT :limit
            """
            
            results = db.execute(query, {"limit": limit}).fetchall()
            
            methods = []
            for result in results:
                methods.append(MethodData(
                    id=result.id,
                    name=result.name,
                    description=result.description,
                    category=result.category,
                    difficulty_level=result.difficulty_level,
                    estimated_time=result.estimated_time,
                    tags=result.tags,
                    author_info=result.author_info,
                    is_active=result.is_active,
                    checkin_count=result.checkin_count,
                    create_time=result.create_time,
                    update_time=result.update_time
                ))
            
            return methods
        except Exception as e:
            print(f"获取热门方法失败: {e}")
            return []
    
    def get_categories(self, db: Session):
        """获取方法分类列表"""
        try:
            query = """
            SELECT 
                name,
                display_name,
                description,
                icon,
                sort_order
            FROM method_categories 
            WHERE is_active = true
            ORDER BY sort_order ASC, name ASC
            """
            
            results = db.execute(query).fetchall()
            
            categories = []
            for result in results:
                categories.append(CategoryData(
                    name=result.name,
                    display_name=result.display_name,
                    description=result.description,
                    icon=result.icon,
                    sort_order=result.sort_order
                ))
            
            return categories
        except Exception as e:
            print(f"获取方法分类失败: {e}")
            return []
    
    def count_by_category(self, db: Session, category: str) -> int:
        """统计某分类下的方法数量"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM study_methods 
            WHERE category = :category AND is_active = true
            """
            
            result = db.execute(query, {"category": category}).fetchone()
            return result.count if result else 0
        except Exception as e:
            print(f"统计分类方法数量失败: {e}")
            return 0
    
    def update_checkin_count(self, db: Session, method_id: int) -> bool:
        """更新StudyMethod表的checkin_count字段（打卡人数变更时同步）"""
        try:
            # 重新计算打卡人数（去重用户）
            count_query = """
            SELECT COUNT(DISTINCT user_id) as count
            FROM checkin_records 
            WHERE method_id = :method_id
            """
            
            count_result = db.execute(count_query, {"method_id": method_id}).fetchone()
            new_count = count_result.count if count_result else 0
            
            # 更新方法表的打卡人数
            update_query = """
            UPDATE study_methods 
            SET checkin_count = :checkin_count, update_time = :update_time
            WHERE id = :method_id
            """
            
            result = db.execute(update_query, {
                "method_id": method_id,
                "checkin_count": new_count,
                "update_time": datetime.now()
            })
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"更新方法打卡数失败: {e}")
            db.rollback()
            return False
    
    def create_method(self, db: Session, method_data: Dict[str, Any]) -> bool:
        """创建新的学习方法"""
        try:
            query = """
            INSERT INTO study_methods (
                name, description, category, difficulty_level, estimated_time,
                steps, scene, meta, tags, author_info, is_active, checkin_count,
                create_time, update_time
            ) VALUES (
                :name, :description, :category, :difficulty_level, :estimated_time,
                :steps, :scene, :meta, :tags, :author_info, :is_active, :checkin_count,
                :create_time, :update_time
            )
            """
            
            params = {
                "name": method_data["name"],
                "description": method_data["description"],
                "category": method_data["category"],
                "difficulty_level": method_data.get("difficulty_level", "初级"),
                "estimated_time": method_data.get("estimated_time", 30),
                "steps": method_data.get("steps"),
                "scene": method_data.get("scene"),
                "meta": method_data.get("meta"),
                "tags": method_data.get("tags"),
                "author_info": method_data.get("author_info"),
                "is_active": method_data.get("is_active", True),
                "checkin_count": 0,
                "create_time": datetime.now(),
                "update_time": datetime.now()
            }
            
            db.execute(query, params)
            db.commit()
            return True
        except Exception as e:
            print(f"创建学习方法失败: {e}")
            db.rollback()
            return False
    
    def update_method(self, db: Session, method_id: int, method_data: Dict[str, Any]) -> bool:
        """更新学习方法"""
        try:
            # 构建更新字段
            update_fields = []
            params = {"method_id": method_id, "update_time": datetime.now()}
            
            for field in ["name", "description", "category", "difficulty_level", 
                         "estimated_time", "steps", "scene", "meta", "tags", 
                         "author_info", "is_active"]:
                if field in method_data:
                    update_fields.append(f"{field} = :{field}")
                    params[field] = method_data[field]
            
            if not update_fields:
                return True
            
            update_fields.append("update_time = :update_time")
            
            query = f"""
            UPDATE study_methods 
            SET {', '.join(update_fields)}
            WHERE id = :method_id
            """
            
            result = db.execute(query, params)
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"更新学习方法失败: {e}")
            db.rollback()
            return False

class MethodData:
    """学习方法数据类"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.name = kwargs.get('name')
        self.description = kwargs.get('description')
        self.category = kwargs.get('category')
        self.difficulty_level = kwargs.get('difficulty_level')
        self.estimated_time = kwargs.get('estimated_time')
        self.steps = kwargs.get('steps')
        self.scene = kwargs.get('scene')
        self.meta = kwargs.get('meta')
        self.tags = kwargs.get('tags')
        self.author_info = kwargs.get('author_info')
        self.is_active = kwargs.get('is_active', True)
        self.checkin_count = kwargs.get('checkin_count', 0)
        self.create_time = kwargs.get('create_time')
        self.update_time = kwargs.get('update_time')

class CategoryData:
    """方法分类数据类"""
    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.display_name = kwargs.get('display_name')
        self.description = kwargs.get('description')
        self.icon = kwargs.get('icon')
        self.sort_order = kwargs.get('sort_order', 0) 