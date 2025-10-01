from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime

# 注意：这里假设有对应的数据库模型，实际使用时需要根据具体的模型进行调整
# from models.case import SuccessCase

class CRUDCase:
    def __init__(self):
        pass

    async def get_hot_by_views(self, db: Session, limit: int = 3) -> List[Any]:
        """按浏览量倒序查询热门案例"""
        try:
            # 这里需要根据实际的数据库模型进行查询
            # 示例查询逻辑（需要根据实际模型调整）
            query = db.query(SuccessCase).filter(
                SuccessCase.is_active == True
            ).order_by(desc(SuccessCase.views)).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"查询热门案例失败: {str(e)}")

    async def get_multi_by_filters(
        self, 
        db: Session, 
        filters: Dict[str, Any], 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Any]:
        """按筛选条件从数据库查询案例"""
        try:
            query = db.query(SuccessCase).filter(SuccessCase.is_active == True)
            
            # 应用筛选条件
            if filters.get('category'):
                query = query.filter(SuccessCase.category == filters['category'])
            
            if filters.get('duration'):
                query = query.filter(SuccessCase.duration == filters['duration'])
            
            if filters.get('experience'):
                query = query.filter(SuccessCase.experience_background == filters['experience'])
            
            if filters.get('foundation'):
                query = query.filter(SuccessCase.foundation_level == filters['foundation'])
            
            # 排序和分页
            query = query.order_by(desc(SuccessCase.created_at))
            query = query.offset(skip).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"按筛选条件查询案例失败: {str(e)}")

    async def search_by_keyword(
        self, 
        db: Session, 
        keyword: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Any]:
        """执行数据库模糊查询，匹配案例相关字段"""
        try:
            search_term = f"%{keyword}%"
            
            query = db.query(SuccessCase).filter(
                and_(
                    SuccessCase.is_active == True,
                    or_(
                        SuccessCase.title.ilike(search_term),
                        SuccessCase.tags.ilike(search_term),
                        SuccessCase.author_name.ilike(search_term),
                        SuccessCase.target_exam.ilike(search_term),
                        SuccessCase.description.ilike(search_term)
                    )
                )
            )
            
            # 按相关性排序（这里简化为按创建时间排序）
            query = query.order_by(desc(SuccessCase.created_at))
            query = query.offset(skip).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"搜索案例失败: {str(e)}")

    async def get_categories(self, db: Session) -> List[str]:
        """获取所有案例分类"""
        try:
            categories = db.query(SuccessCase.category).distinct().filter(
                SuccessCase.is_active == True
            ).all()
            
            return [category[0] for category in categories if category[0]]
        except Exception as e:
            raise Exception(f"获取案例分类失败: {str(e)}")

    async def count_total_cases(self, db: Session) -> int:
        """统计总案例数"""
        try:
            return db.query(SuccessCase).filter(SuccessCase.is_active == True).count()
        except Exception as e:
            raise Exception(f"统计总案例数失败: {str(e)}")

    async def count_by_category(self, db: Session) -> Dict[str, int]:
        """按分类统计案例数量"""
        try:
            category_stats = db.query(
                SuccessCase.category,
                func.count(SuccessCase.id).label('count')
            ).filter(
                SuccessCase.is_active == True
            ).group_by(SuccessCase.category).all()
            
            return {category: count for category, count in category_stats}
        except Exception as e:
            raise Exception(f"按分类统计案例失败: {str(e)}")

    async def count_cases_since(self, db: Session, since_date: datetime) -> int:
        """统计指定日期以来的新增案例数"""
        try:
            return db.query(SuccessCase).filter(
                and_(
                    SuccessCase.is_active == True,
                    SuccessCase.created_at >= since_date
                )
            ).count()
        except Exception as e:
            raise Exception(f"统计新增案例失败: {str(e)}")

    async def increment_views(self, db: Session, case_id: int) -> bool:
        """增加案例浏览次数"""
        try:
            case = db.query(SuccessCase).filter(SuccessCase.id == case_id).first()
            if case:
                case.views = (case.views or 0) + 1
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise Exception(f"增加浏览次数失败: {str(e)}")

    async def get_related_cases(
        self, 
        db: Session, 
        category: str, 
        tags: str, 
        exclude_id: int, 
        limit: int = 5
    ) -> List[Any]:
        """基于标签和分类查找相关案例"""
        try:
            query = db.query(SuccessCase).filter(
                and_(
                    SuccessCase.is_active == True,
                    SuccessCase.id != exclude_id
                )
            )
            
            # 优先匹配相同分类
            if category:
                query = query.filter(SuccessCase.category == category)
            
            # 如果有标签，进行标签匹配（简化实现）
            if tags:
                tag_list = tags.split(',')
                tag_conditions = []
                for tag in tag_list:
                    tag_conditions.append(SuccessCase.tags.ilike(f"%{tag.strip()}%"))
                
                if tag_conditions:
                    query = query.filter(or_(*tag_conditions))
            
            # 按浏览量排序
            query = query.order_by(desc(SuccessCase.views)).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"查找相关案例失败: {str(e)}")

    async def create_case(self, db: Session, case_data: Dict[str, Any]) -> Any:
        """创建新案例"""
        try:
            new_case = SuccessCase(**case_data)
            db.add(new_case)
            db.commit()
            db.refresh(new_case)
            return new_case
        except Exception as e:
            db.rollback()
            raise Exception(f"创建案例失败: {str(e)}")

    async def update_case(self, db: Session, case_id: int, update_data: Dict[str, Any]) -> bool:
        """更新案例信息"""
        try:
            case = db.query(SuccessCase).filter(SuccessCase.id == case_id).first()
            if not case:
                return False
            
            for key, value in update_data.items():
                if hasattr(case, key):
                    setattr(case, key, value)
            
            case.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新案例失败: {str(e)}") 