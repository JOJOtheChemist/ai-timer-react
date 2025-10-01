from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.moment import (
    Moment, MomentComment, MomentLike, MomentBookmark, 
    MomentShare, MomentView
)

class CRUDMomentInteraction:
    """动态互动CRUD操作"""
    
    def toggle_like(self, db: Session, user_id: int, moment_id: int) -> tuple[bool, int]:
        """更新点赞状态（含唯一约束：user_id+moment_id）"""
        # 检查是否已点赞
        existing_like = db.query(MomentLike).filter(
            and_(
                MomentLike.user_id == user_id,
                MomentLike.moment_id == moment_id
            )
        ).first()
        
        if existing_like:
            # 取消点赞
            db.delete(existing_like)
            # 减少动态的点赞数
            db.query(Moment).filter(Moment.id == moment_id).update({
                "like_count": Moment.like_count - 1
            })
            db.commit()
            
            # 获取更新后的点赞数
            moment = db.query(Moment).filter(Moment.id == moment_id).first()
            return False, moment.like_count if moment else 0
        else:
            # 添加点赞
            new_like = MomentLike(user_id=user_id, moment_id=moment_id)
            db.add(new_like)
            # 增加动态的点赞数
            db.query(Moment).filter(Moment.id == moment_id).update({
                "like_count": Moment.like_count + 1
            })
            db.commit()
            
            # 获取更新后的点赞数
            moment = db.query(Moment).filter(Moment.id == moment_id).first()
            return True, moment.like_count if moment else 0
    
    def toggle_bookmark(self, db: Session, user_id: int, moment_id: int) -> tuple[bool, int]:
        """更新收藏状态"""
        # 检查是否已收藏
        existing_bookmark = db.query(MomentBookmark).filter(
            and_(
                MomentBookmark.user_id == user_id,
                MomentBookmark.moment_id == moment_id
            )
        ).first()
        
        if existing_bookmark:
            # 取消收藏
            db.delete(existing_bookmark)
            # 减少动态的收藏数
            db.query(Moment).filter(Moment.id == moment_id).update({
                "bookmark_count": Moment.bookmark_count - 1
            })
            db.commit()
            
            # 获取更新后的收藏数
            moment = db.query(Moment).filter(Moment.id == moment_id).first()
            return False, moment.bookmark_count if moment else 0
        else:
            # 添加收藏
            new_bookmark = MomentBookmark(user_id=user_id, moment_id=moment_id)
            db.add(new_bookmark)
            # 增加动态的收藏数
            db.query(Moment).filter(Moment.id == moment_id).update({
                "bookmark_count": Moment.bookmark_count + 1
            })
            db.commit()
            
            # 获取更新后的收藏数
            moment = db.query(Moment).filter(Moment.id == moment_id).first()
            return True, moment.bookmark_count if moment else 0
    
    def get_comments_by_moment(
        self, 
        db: Session, 
        moment_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> tuple[List[MomentComment], int]:
        """按动态ID查评论"""
        # 只查询顶级评论（parent_comment_id为空）
        query = db.query(MomentComment).filter(
            and_(
                MomentComment.moment_id == moment_id,
                MomentComment.parent_comment_id.is_(None)
            )
        )
        
        total = query.count()
        
        comments = query.order_by(desc(MomentComment.create_time))\
                       .offset((page - 1) * page_size)\
                       .limit(page_size).all()
        
        return comments, total
    
    def get_comment_replies(self, db: Session, comment_id: int) -> List[MomentComment]:
        """获取评论的回复"""
        return db.query(MomentComment).filter(
            MomentComment.parent_comment_id == comment_id
        ).order_by(MomentComment.create_time).all()
    
    def create_comment(self, db: Session, user_id: int, moment_id: int, content: str, parent_comment_id: Optional[int] = None) -> MomentComment:
        """保存评论"""
        db_comment = MomentComment(
            moment_id=moment_id,
            user_id=user_id,
            content=content,
            parent_comment_id=parent_comment_id
        )
        db.add(db_comment)
        
        # 增加动态的评论数
        db.query(Moment).filter(Moment.id == moment_id).update({
            "comment_count": Moment.comment_count + 1
        })
        
        db.commit()
        db.refresh(db_comment)
        return db_comment
    
    def delete_comment(self, db: Session, comment_id: int, user_id: int) -> bool:
        """删除评论"""
        db_comment = db.query(MomentComment).filter(
            and_(
                MomentComment.id == comment_id,
                MomentComment.user_id == user_id
            )
        ).first()
        
        if not db_comment:
            return False
        
        moment_id = db_comment.moment_id
        
        # 删除评论及其回复
        db.query(MomentComment).filter(
            MomentComment.parent_comment_id == comment_id
        ).delete()
        
        db.delete(db_comment)
        
        # 减少动态的评论数
        db.query(Moment).filter(Moment.id == moment_id).update({
            "comment_count": Moment.comment_count - 1
        })
        
        db.commit()
        return True
    
    def record_share(self, db: Session, user_id: int, moment_id: int, share_type: str = 'general') -> bool:
        """记录分享行为（不重复计数）"""
        # 检查是否已经分享过（同一天内）
        today = datetime.now().date()
        existing_share = db.query(MomentShare).filter(
            and_(
                MomentShare.user_id == user_id,
                MomentShare.moment_id == moment_id,
                func.date(MomentShare.create_time) == today
            )
        ).first()
        
        if existing_share:
            # 今天已经分享过，不重复计数
            return False
        
        # 记录分享
        new_share = MomentShare(
            user_id=user_id,
            moment_id=moment_id,
            share_type=share_type
        )
        db.add(new_share)
        
        # 增加动态的分享数
        db.query(Moment).filter(Moment.id == moment_id).update({
            "share_count": Moment.share_count + 1
        })
        
        db.commit()
        return True
    
    def record_view(
        self, 
        db: Session, 
        moment_id: int, 
        user_id: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        view_duration: int = 0
    ) -> bool:
        """记录浏览行为"""
        # 记录浏览
        new_view = MomentView(
            moment_id=moment_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            view_duration=view_duration
        )
        db.add(new_view)
        
        # 增加动态的浏览数
        db.query(Moment).filter(Moment.id == moment_id).update({
            "view_count": Moment.view_count + 1
        })
        
        db.commit()
        return True
    
    def get_user_interaction_status(self, db: Session, user_id: int, moment_id: int) -> Dict[str, bool]:
        """获取用户对动态的互动状态"""
        # 检查点赞状态
        is_liked = db.query(MomentLike).filter(
            and_(
                MomentLike.user_id == user_id,
                MomentLike.moment_id == moment_id
            )
        ).first() is not None
        
        # 检查收藏状态
        is_bookmarked = db.query(MomentBookmark).filter(
            and_(
                MomentBookmark.user_id == user_id,
                MomentBookmark.moment_id == moment_id
            )
        ).first() is not None
        
        return {
            "is_liked": is_liked,
            "is_bookmarked": is_bookmarked
        }
    
    def get_user_bookmarks(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> tuple[List[Moment], int]:
        """获取用户收藏的动态"""
        # 通过收藏表关联查询动态
        query = db.query(Moment).join(MomentBookmark).filter(
            and_(
                MomentBookmark.user_id == user_id,
                Moment.status == 'published'
            )
        )
        
        total = query.count()
        
        moments = query.order_by(desc(MomentBookmark.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size).all()
        
        return moments, total
    
    def get_user_likes(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> tuple[List[Moment], int]:
        """获取用户点赞的动态"""
        # 通过点赞表关联查询动态
        query = db.query(Moment).join(MomentLike).filter(
            and_(
                MomentLike.user_id == user_id,
                Moment.status == 'published'
            )
        )
        
        total = query.count()
        
        moments = query.order_by(desc(MomentLike.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size).all()
        
        return moments, total
    
    def get_interaction_stats(self, db: Session, moment_id: int) -> Dict[str, int]:
        """获取动态的互动统计"""
        moment = db.query(Moment).filter(Moment.id == moment_id).first()
        
        if not moment:
            return {
                "like_count": 0,
                "comment_count": 0,
                "share_count": 0,
                "bookmark_count": 0,
                "view_count": 0
            }
        
        return {
            "like_count": moment.like_count,
            "comment_count": moment.comment_count,
            "share_count": moment.share_count,
            "bookmark_count": moment.bookmark_count,
            "view_count": moment.view_count
        }
    
    def get_user_interaction_stats(self, db: Session, user_id: int) -> Dict[str, int]:
        """获取用户的互动统计"""
        # 用户发布的动态获得的总互动数
        user_moments = db.query(Moment).filter(
            and_(Moment.user_id == user_id, Moment.status == 'published')
        ).all()
        
        total_likes_received = sum(moment.like_count for moment in user_moments)
        total_comments_received = sum(moment.comment_count for moment in user_moments)
        total_shares_received = sum(moment.share_count for moment in user_moments)
        total_bookmarks_received = sum(moment.bookmark_count for moment in user_moments)
        
        # 用户的互动行为统计
        likes_given = db.query(func.count(MomentLike.id)).filter(MomentLike.user_id == user_id).scalar() or 0
        comments_given = db.query(func.count(MomentComment.id)).filter(MomentComment.user_id == user_id).scalar() or 0
        bookmarks_made = db.query(func.count(MomentBookmark.id)).filter(MomentBookmark.user_id == user_id).scalar() or 0
        
        return {
            "published_count": len(user_moments),
            "total_likes_received": total_likes_received,
            "total_comments_received": total_comments_received,
            "total_shares_received": total_shares_received,
            "total_bookmarks_received": total_bookmarks_received,
            "likes_given": likes_given,
            "comments_given": comments_given,
            "bookmarks_made": bookmarks_made
        }

# 创建CRUD实例
crud_moment_interaction = CRUDMomentInteraction() 