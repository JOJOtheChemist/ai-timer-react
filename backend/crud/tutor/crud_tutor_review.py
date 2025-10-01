from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime

# 注意：这里假设有对应的数据库模型，实际使用时需要根据具体的模型进行调整
# from models.tutor import TutorReview

class CRUDTutorReview:
    def __init__(self):
        pass

    async def get_multi_by_tutor(
        self,
        db: Session,
        tutor_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Any]:
        """查询指定导师的学员评价（默认取前10条）"""
        try:
            reviews = db.query(TutorReview).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.is_active == True
                )
            ).order_by(desc(TutorReview.created_at)).offset(skip).limit(limit).all()
            
            return reviews
        except Exception as e:
            raise Exception(f"查询导师评价失败: {str(e)}")

    async def get_by_id(self, db: Session, review_id: int) -> Optional[Any]:
        """根据ID获取评价详情"""
        try:
            review = db.query(TutorReview).filter(TutorReview.id == review_id).first()
            return review
        except Exception as e:
            raise Exception(f"查询评价详情失败: {str(e)}")

    async def create_review(self, db: Session, review_data: Dict[str, Any]) -> Any:
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
            from sqlalchemy import func
            
            # 总评价数
            total_reviews = db.query(TutorReview).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.is_active == True
                )
            ).count()
            
            # 平均评分
            avg_rating = db.query(func.avg(TutorReview.rating)).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.is_active == True
                )
            ).scalar() or 0.0
            
            # 各星级评价数量
            rating_distribution = db.query(
                TutorReview.rating,
                func.count(TutorReview.id).label('count')
            ).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.is_active == True
                )
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
    ) -> List[Any]:
        """按评分筛选评价"""
        try:
            reviews = db.query(TutorReview).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.rating == rating,
                    TutorReview.is_active == True
                )
            ).order_by(desc(TutorReview.created_at)).offset(skip).limit(limit).all()
            
            return reviews
        except Exception as e:
            raise Exception(f"按评分筛选评价失败: {str(e)}")

    async def check_user_reviewed(self, db: Session, tutor_id: int, user_id: int) -> bool:
        """检查用户是否已评价过此导师"""
        try:
            review = db.query(TutorReview).filter(
                and_(
                    TutorReview.tutor_id == tutor_id,
                    TutorReview.reviewer_id == user_id,
                    TutorReview.is_active == True
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
    ) -> List[Any]:
        """获取用户发表的所有评价"""
        try:
            reviews = db.query(TutorReview).filter(
                and_(
                    TutorReview.reviewer_id == user_id,
                    TutorReview.is_active == True
                )
            ).order_by(desc(TutorReview.created_at)).offset(skip).limit(limit).all()
            
            return reviews
        except Exception as e:
            raise Exception(f"获取用户评价失败: {str(e)}") 