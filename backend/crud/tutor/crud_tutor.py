from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, date

from models.tutor import Tutor, TutorService, TutorReview, TutorExpertise, TutorServiceOrder

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
            # status=1 表示正常，status=0表示待审核，status=2表示禁用
            query = db.query(Tutor).filter(Tutor.status == 1)
            
            # 应用筛选条件
            if filters.get('tutor_type') is not None:
                query = query.filter(Tutor.type == int(filters['tutor_type']))
            
            if filters.get('domain'):
                query = query.filter(Tutor.domain.ilike(f"%{filters['domain']}%"))
            
            # 应用排序
            if sort_by == "rating":
                query = query.order_by(desc(Tutor.rating))
            elif sort_by == "price":
                # 价格排序需要关联 tutor_service 表，暂时按 rating 排序
                query = query.order_by(desc(Tutor.rating))
            elif sort_by == "experience":
                # 按学生数量排序
                query = query.order_by(desc(Tutor.student_count))
            else:
                query = query.order_by(desc(Tutor.create_time))
            
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
                    Tutor.status == 1,
                    or_(
                        Tutor.username.ilike(search_term),
                        Tutor.domain.ilike(search_term),
                        Tutor.education.ilike(search_term),
                        Tutor.experience.ilike(search_term)
                    )
                )
            ).order_by(desc(Tutor.rating))
            
            return query.offset(skip).limit(limit).all()
        except Exception as e:
            raise Exception(f"关键词搜索导师失败: {str(e)}")

    async def get_by_id_with_relations(
        self,
        db: Session,
        tutor_id: int
    ) -> Optional[Tutor]:
        """查询导师完整信息（含服务、评价等关联数据）"""
        try:
            tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            return tutor
        except Exception as e:
            raise Exception(f"查询导师详情失败: {str(e)}")

    async def get_tutor_domains(self, db: Session) -> List[str]:
        """获取所有导师的擅长领域列表（去重）"""
        try:
            # 查询所有正常状态的导师的 domain 字段
            domains = db.query(Tutor.domain).filter(Tutor.status == 1).distinct().all()
            return [d[0] for d in domains if d[0]]
        except Exception as e:
            raise Exception(f"查询导师领域失败: {str(e)}")

    async def get_tutor_types(self, db: Session) -> List[str]:
        """获取所有导师类型列表"""
        try:
            # type: 0=普通导师, 1=认证导师
            return ["普通导师", "认证导师"]
        except Exception as e:
            raise Exception(f"查询导师类型失败: {str(e)}")

    async def get_tutor_stats_summary(self, db: Session) -> Dict[str, Any]:
        """计算导师全局统计数据（总数、类型分布等）"""
        try:
            total_count = db.query(func.count(Tutor.id)).filter(Tutor.status == 1).scalar()
            normal_count = db.query(func.count(Tutor.id)).filter(
                and_(Tutor.status == 1, Tutor.type == 0)
            ).scalar()
            certified_count = db.query(func.count(Tutor.id)).filter(
                and_(Tutor.status == 1, Tutor.type == 1)
            ).scalar()
            
            return {
                "total_count": total_count or 0,
                "normal_count": normal_count or 0,
                "certified_count": certified_count or 0
            }
        except Exception as e:
            raise Exception(f"查询导师统计失败: {str(e)}")

    async def get_popular_tutors(
        self,
        db: Session,
        limit: int = 5
    ) -> List[Tutor]:
        """按热度（如月度指导次数、评分）推荐热门导师"""
        try:
            return db.query(Tutor).filter(Tutor.status == 1).order_by(
                desc(Tutor.monthly_guide_count),
                desc(Tutor.rating)
            ).limit(limit).all()
        except Exception as e:
            raise Exception(f"查询热门导师失败: {str(e)}")

    async def get_tutor_services(
        self,
        db: Session,
        tutor_id: int
    ) -> List[TutorService]:
        """查询导师的服务列表"""
        try:
            return db.query(TutorService).filter(
                and_(
                    TutorService.tutor_id == tutor_id,
                    TutorService.is_active == 1
                )
            ).order_by(TutorService.sort_order).all()
        except Exception as e:
            raise Exception(f"查询导师服务失败: {str(e)}")

    async def get_tutor_reviews(
        self,
        db: Session,
        tutor_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[TutorReview]:
        """查询导师的学员评价列表"""
        try:
            return db.query(TutorReview).filter(
                TutorReview.tutor_id == tutor_id
            ).order_by(desc(TutorReview.create_time)).offset(skip).limit(limit).all()
        except Exception as e:
            raise Exception(f"查询导师评价失败: {str(e)}")

    async def get_tutor_metrics(
        self,
        db: Session,
        tutor_id: int
    ) -> Dict[str, Any]:
        """查询导师的指导数据面板"""
        try:
            tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            if not tutor:
                return {}
            
            return {
                "student_count": tutor.student_count,
                "success_rate": tutor.success_rate,
                "monthly_guide_count": tutor.monthly_guide_count,
                "rating": tutor.rating
            }
        except Exception as e:
            raise Exception(f"查询导师指导数据失败: {str(e)}")

    async def record_tutor_view(
        self,
        db: Session,
        tutor_id: int,
        user_id: int
    ) -> bool:
        """记录导师页面浏览（可用于统计热度）"""
        try:
            # 简单实现：不记录浏览记录，直接返回成功
            # 如果需要记录，可以创建 tutor_view_record 表
            return True
        except Exception as e:
            raise Exception(f"记录浏览失败: {str(e)}")

    async def get_similar_tutors(
        self,
        db: Session,
        tutor_id: int,
        limit: int = 5
    ) -> List[Tutor]:
        """基于领域、类型相似度推荐相似导师"""
        try:
            # 先获取当前导师信息
            current_tutor = db.query(Tutor).filter(Tutor.id == tutor_id).first()
            if not current_tutor:
                return []
            
            # 查找相同领域和类型的其他导师
            return db.query(Tutor).filter(
                and_(
                    Tutor.status == 1,
                    Tutor.id != tutor_id,
                    or_(
                        Tutor.domain.ilike(f"%{current_tutor.domain}%"),
                        Tutor.type == current_tutor.type
                    )
                )
            ).order_by(desc(Tutor.rating)).limit(limit).all()
        except Exception as e:
            raise Exception(f"查询相似导师失败: {str(e)}")

crud_tutor = CRUDTutor() 