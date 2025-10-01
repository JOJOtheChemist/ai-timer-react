from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from datetime import datetime

from models.tutor import TutorReview

class CRUDTutorReview:
    def __init__(self):
        pass

    async def get_multi_by_tutor(
        self,
        db: Session,
        tutor_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[TutorReview]:
        """查询指定导师的学员评价（默认取前10条）"""
        try:
            reviews = db.query(TutorReview).filter(
                TutorReview.tutor_id == tutor_id
            ).order_by(desc(TutorReview.create_time)).offset(skip).limit(limit).all()
            
            return reviews
        except Exception as e:
            raise Exception(f"查询导师评价失败: {str(e)}")

    async def get_by_id(self, db: Session, review_id: int) -> Optional[TutorReview]:
        """根据ID获取评价详情"""
        try:
            review = db.query(TutorReview).filter(TutorReview.id == review_id).first()
            return review
        except Exception as e:
            raise Exception(f"查询评价详情失败: {str(e)}")

    async def create_review(self, db: Session, review_data: Dict[str, Any]) -> TutorReview:
        """创建导师评价"""
        try:
            new_review = TutorReview(**review_data)
            db.add(new_review)
            db.commit()
            db.refresh(new_review)
            return new_review
        except Exception as e:
            db.rollback()
            raise Exception(f"创建评价失败: {str(e)}")

    async def update_review(self, db: Session, review_id: int, update_data: Dict[str, Any]) -> bool:
        """更新评价内容"""
        try:
            review = db.query(TutorReview).filter(TutorReview.id == review_id).first()
            if not review:
                return False
            
            for key, value in update_data.items():
                if hasattr(review, key):
                    setattr(review, key, value)
            
            review.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新评价失败: {str(e)}")

    async def delete_review(self, db: Session, review_id: int) -> bool:
        """软删除评价"""
        try:
            review = db.query(TutorReview).filter(TutorReview.id == review_id).first()
            if not review:
                return False
            
            review.is_active = False
            review.deleted_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"删除评价失败: {str(e)}")

    async def get_review_stats(self, db: Session, tutor_id: int) -> Dict[str, Any]:
        """获取导师评价统计"""
        try:
            # 总评价数
            total_reviews = db.query(TutorReview).filter(
                TutorReview.tutor_id == tutor_id
            ).count()
            
            # 平均评分
            avg_rating = db.query(func.avg(TutorReview.rating)).filter(
                TutorReview.tutor_id == tutor_id
            ).scalar() or 0.0
            
            # 各星级评价数量
            rating_distribution = db.query(
                TutorReview.rating,
                func.count(TutorReview.id).label('count')
            ).filter(
                TutorReview.tutor_id == tutor_id
            ).group_by(TutorReview.rating).all()
            
            rating_dist_dict = {rating: count for rating, count in rating_distribution}
            
            return {
                "total_reviews": total_reviews,
                "average_rating": float(avg_rating),
                "rating_distribution": rating_dist_dict
            }
        except Exception as e:
            raise Exception(f"获取评价统计失败: {str(e)}")

    async def get_reviews_by_rating(
        self,
        db: Session,
        tutor_id: int,
        rating: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[TutorReview]:
        """按评分筛选评价"""
        try:
            reviews = db.query(TutorReview).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.rating == rating
                )
            ).order_by(desc(TutorReview.create_time)).offset(skip).limit(limit).all()
            
            return reviews
        except Exception as e:
            raise Exception(f"按评分筛选评价失败: {str(e)}")

    async def check_user_reviewed(self, db: Session, tutor_id: int, user_id: int) -> bool:
        """检查用户是否已评价过此导师"""
        try:
            review = db.query(TutorReview).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.user_id == user_id
                )
            ).first()
            
            return review is not None
        except Exception as e:
            raise Exception(f"检查评价状态失败: {str(e)}")

    async def get_user_reviews(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[TutorReview]:
        """获取用户发表的所有评价"""
        try:
            reviews = db.query(TutorReview).filter(
                TutorReview.user_id == user_id
            ).order_by(desc(TutorReview.create_time)).offset(skip).limit(limit).all()
            
            return reviews
        except Exception as e:
            raise Exception(f"获取用户评价失败: {str(e)}")

crud_tutor_review = CRUDTutorReview() 