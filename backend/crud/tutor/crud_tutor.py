from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, date

# 注意：这里假设有对应的数据库模型，实际使用时需要根据具体的模型进行调整
# from models.tutor import Tutor, TutorService, TutorMetrics, TutorViewRecord

class CRUDTutor:
    def __init__(self):
        pass

    async def get_multi_by_filters(
        self,
        db: Session,
        filters: Dict[str, Any],
        sort_by: str = "rating",
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        """按筛选条件+排序执行数据库查询"""
        try:
            query = db.query(Tutor).filter(Tutor.is_active == True)
            
            # 应用筛选条件
            if filters.get('tutor_type'):
                query = query.filter(Tutor.tutor_type == filters['tutor_type'])
            
            if filters.get('domain'):
                query = query.filter(Tutor.domains.ilike(f"%{filters['domain']}%"))
            
            if filters.get('price_range'):
                # 解析价格区间
                price_range = filters['price_range']
                if '-' in price_range:
                    min_price, max_price = price_range.split('-')
                    query = query.filter(
                        and_(
                            Tutor.min_price >= int(min_price),
                            Tutor.max_price <= int(max_price)
                        )
                    )
            
            # 应用排序
            if sort_by == "rating":
                query = query.order_by(desc(Tutor.rating))
            elif sort_by == "price":
                query = query.order_by(Tutor.min_price)
            elif sort_by == "experience":
                query = query.order_by(desc(Tutor.experience_years))
            else:
                query = query.order_by(desc(Tutor.created_at))
            
            # 分页
            query = query.offset(skip).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"按筛选条件查询导师失败: {str(e)}")

    async def search_by_keyword(
        self,
        db: Session,
        keyword: str,
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        """关键词搜索导师（关联领域标签）"""
        try:
            search_term = f"%{keyword}%"
            
            query = db.query(Tutor).filter(
                and_(
                    Tutor.is_active == True,
                    or_(
                        Tutor.name.ilike(search_term),
                        Tutor.title.ilike(search_term),
                        Tutor.domains.ilike(search_term),
                        Tutor.bio.ilike(search_term)
                    )
                )
            )
            
            # 按相关性排序（这里简化为按评分排序）
            query = query.order_by(desc(Tutor.rating))
            query = query.offset(skip).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"搜索导师失败: {str(e)}")

    async def get_by_id_with_relations(self, db: Session, tutor_id: int) -> Optional[Any]:
        """查询导师基础信息，关联查询服务表、评价表、指导数据表"""
        try:
            tutor = db.query(Tutor).filter(
                and_(
                    Tutor.id == tutor_id,
                    Tutor.is_active == True
                )
            ).first()
            
            return tutor
        except Exception as e:
            raise Exception(f"查询导师详情失败: {str(e)}")

    async def get_by_id(self, db: Session, tutor_id: int) -> Optional[Any]:
        """查询导师基础信息"""
        try:
            tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            return tutor
        except Exception as e:
            raise Exception(f"查询导师失败: {str(e)}")

    async def get_tutor_services(self, db: Session, tutor_id: int) -> List[Any]:
        """获取导师的服务列表"""
        try:
            services = db.query(TutorService).filter(
                and_(
                    TutorService.tutor_id == tutor_id,
                    TutorService.is_available == True
                )
            ).all()
            
            return services
        except Exception as e:
            raise Exception(f"获取导师服务失败: {str(e)}")

    async def get_tutor_metrics(self, db: Session, tutor_id: int) -> Optional[Any]:
        """获取导师的指导数据"""
        try:
            metrics = db.query(TutorMetrics).filter(
                TutorMetrics.tutor_id == tutor_id
            ).first()
            
            return metrics
        except Exception as e:
            raise Exception(f"获取导师数据失败: {str(e)}")

    async def get_all_domains(self, db: Session) -> List[str]:
        """获取所有导师擅长领域"""
        try:
            domains = db.query(Tutor.domains).distinct().filter(
                Tutor.is_active == True
            ).all()
            
            # 解析逗号分隔的领域
            all_domains = set()
            for domain_row in domains:
                if domain_row[0]:
                    for domain in domain_row[0].split(','):
                        all_domains.add(domain.strip())
            
            return list(all_domains)
        except Exception as e:
            raise Exception(f"获取导师领域失败: {str(e)}")

    async def get_all_types(self, db: Session) -> List[str]:
        """获取所有导师类型"""
        try:
            types = db.query(Tutor.tutor_type).distinct().filter(
                Tutor.is_active == True
            ).all()
            
            return [type_row[0] for type_row in types if type_row[0]]
        except Exception as e:
            raise Exception(f"获取导师类型失败: {str(e)}")

    async def count_total_tutors(self, db: Session) -> int:
        """统计总导师数"""
        try:
            return db.query(Tutor).filter(Tutor.is_active == True).count()
        except Exception as e:
            raise Exception(f"统计总导师数失败: {str(e)}")

    async def count_by_type(self, db: Session) -> Dict[str, int]:
        """按类型统计导师数量"""
        try:
            type_stats = db.query(
                Tutor.tutor_type,
                func.count(Tutor.id).label('count')
            ).filter(
                Tutor.is_active == True
            ).group_by(Tutor.tutor_type).all()
            
            return {tutor_type: count for tutor_type, count in type_stats}
        except Exception as e:
            raise Exception(f"按类型统计导师失败: {str(e)}")

    async def count_online_tutors(self, db: Session) -> int:
        """统计在线导师数"""
        try:
            return db.query(Tutor).filter(
                and_(
                    Tutor.is_active == True,
                    Tutor.is_online == True
                )
            ).count()
        except Exception as e:
            raise Exception(f"统计在线导师数失败: {str(e)}")

    async def count_verified_tutors(self, db: Session) -> int:
        """统计认证导师数"""
        try:
            return db.query(Tutor).filter(
                and_(
                    Tutor.is_active == True,
                    Tutor.is_verified == True
                )
            ).count()
        except Exception as e:
            raise Exception(f"统计认证导师数失败: {str(e)}")

    async def count_tutors_since(self, db: Session, since_date: datetime) -> int:
        """统计指定日期以来的新增导师数"""
        try:
            return db.query(Tutor).filter(
                and_(
                    Tutor.is_active == True,
                    Tutor.created_at >= since_date
                )
            ).count()
        except Exception as e:
            raise Exception(f"统计新增导师数失败: {str(e)}")

    async def get_popular_tutors(self, db: Session, limit: int = 5) -> List[Any]:
        """获取热门导师（按评分和学生数综合排序）"""
        try:
            tutors = db.query(Tutor).filter(
                Tutor.is_active == True
            ).order_by(
                desc(Tutor.rating),
                desc(Tutor.student_count)
            ).limit(limit).all()
            
            return tutors
        except Exception as e:
            raise Exception(f"获取热门导师失败: {str(e)}")

    async def get_similar_tutors(
        self,
        db: Session,
        tutor_type: str,
        domains: str,
        exclude_id: int,
        limit: int = 5
    ) -> List[Any]:
        """基于领域和类型查找相似导师"""
        try:
            query = db.query(Tutor).filter(
                and_(
                    Tutor.is_active == True,
                    Tutor.id != exclude_id
                )
            )
            
            # 优先匹配相同类型
            if tutor_type:
                query = query.filter(Tutor.tutor_type == tutor_type)
            
            # 如果有领域，进行领域匹配
            if domains:
                domain_list = domains.split(',')
                domain_conditions = []
                for domain in domain_list:
                    domain_conditions.append(Tutor.domains.ilike(f"%{domain.strip()}%"))
                
                if domain_conditions:
                    query = query.filter(or_(*domain_conditions))
            
            # 按评分排序
            query = query.order_by(desc(Tutor.rating)).limit(limit)
            
            return query.all()
        except Exception as e:
            raise Exception(f"查找相似导师失败: {str(e)}")

    async def check_user_viewed_today(self, db: Session, tutor_id: int, user_id: int) -> bool:
        """检查用户今天是否已浏览过此导师"""
        try:
            today = date.today()
            view_record = db.query(TutorViewRecord).filter(
                and_(
                    TutorViewRecord.tutor_id == tutor_id,
                    TutorViewRecord.user_id == user_id,
                    TutorViewRecord.view_date == today
                )
            ).first()
            
            return view_record is not None
        except Exception as e:
            raise Exception(f"检查浏览记录失败: {str(e)}")

    async def increment_views(self, db: Session, tutor_id: int) -> bool:
        """增加导师浏览次数"""
        try:
            tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            if tutor:
                tutor.views = (tutor.views or 0) + 1
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise Exception(f"增加浏览次数失败: {str(e)}")

    async def create_view_record(self, db: Session, tutor_id: int, user_id: int) -> bool:
        """创建用户浏览记录"""
        try:
            view_record = TutorViewRecord(
                tutor_id=tutor_id,
                user_id=user_id,
                view_date=date.today(),
                view_time=datetime.now()
            )
            
            db.add(view_record)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"创建浏览记录失败: {str(e)}")

    async def check_user_followed_tutor(self, db: Session, user_id: int, tutor_id: int) -> bool:
        """检查用户是否已关注此导师"""
        try:
            # 这里需要查询用户关系表
            # 暂时返回False，待用户关系表实现后替换
            return False
        except Exception as e:
            raise Exception(f"检查关注状态失败: {str(e)}")

    async def update_fan_count(self, db: Session, tutor_id: int, increment: int) -> bool:
        """更新导师粉丝数"""
        try:
            tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            if tutor:
                tutor.fan_count = max(0, (tutor.fan_count or 0) + increment)
                db.commit()
                return True
            return False
        except Exception as e:
            db.rollback()
            raise Exception(f"更新粉丝数失败: {str(e)}")

    async def create_tutor(self, db: Session, tutor_data: Dict[str, Any]) -> Any:
        """创建新导师"""
        try:
            new_tutor = Tutor(**tutor_data)
            db.add(new_tutor)
            db.commit()
            db.refresh(new_tutor)
            return new_tutor
        except Exception as e:
            db.rollback()
            raise Exception(f"创建导师失败: {str(e)}")

    async def update_tutor(self, db: Session, tutor_id: int, update_data: Dict[str, Any]) -> bool:
        """更新导师信息"""
        try:
            tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            if not tutor:
                return False
            
            for key, value in update_data.items():
                if hasattr(tutor, key):
                    setattr(tutor, key, value)
            
            tutor.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新导师失败: {str(e)}")

    async def get_service_by_id(self, db: Session, service_id: int) -> Optional[Any]:
        """根据服务ID获取服务信息"""
        try:
            service = db.query(TutorService).filter(TutorService.id == service_id).first()
            return service
        except Exception as e:
            raise Exception(f"查询服务失败: {str(e)}") 