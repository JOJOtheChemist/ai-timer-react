from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from models.moment import Moment, MomentComment, MomentInteraction

# 互动类型常量
INTERACTION_TYPE_LIKE = 0
INTERACTION_TYPE_BOOKMARK = 1
INTERACTION_TYPE_SHARE = 2

class CRUDMomentInteraction:
    """动态互动CRUD操作（使用统一的 moment_interaction 表）"""
    
    def toggle_like(self, db: Session, user_id: int, moment_id: int) -> Tuple[bool, int]:
        """
        切换点赞状态
        返回: (is_liked, current_like_count)
        """
        # 检查是否已点赞
        existing_like = db.query(MomentInteraction).filter(
            and_(
                MomentInteraction.user_id == user_id,
                MomentInteraction.moment_id == moment_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_LIKE
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
            new_like = MomentInteraction(
                user_id=user_id,
                moment_id=moment_id,
                interaction_type=INTERACTION_TYPE_LIKE
            )
            db.add(new_like)
            # 增加动态的点赞数
            db.query(Moment).filter(Moment.id == moment_id).update({
                "like_count": Moment.like_count + 1
            })
            db.commit()
            
            # 获取更新后的点赞数
            moment = db.query(Moment).filter(Moment.id == moment_id).first()
            return True, moment.like_count if moment else 0
    
    def toggle_bookmark(self, db: Session, user_id: int, moment_id: int) -> Tuple[bool, int]:
        """
        切换收藏状态
        返回: (is_bookmarked, current_bookmark_count)
        """
        # 检查是否已收藏
        existing_bookmark = db.query(MomentInteraction).filter(
            and_(
                MomentInteraction.user_id == user_id,
                MomentInteraction.moment_id == moment_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
            )
        ).first()
        
        if existing_bookmark:
            # 取消收藏
            db.delete(existing_bookmark)
            db.commit()
            
            # 获取当前收藏数（从 interaction 表统计）
            bookmark_count = db.query(func.count(MomentInteraction.id)).filter(
                and_(
                    MomentInteraction.moment_id == moment_id,
                    MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
                )
            ).scalar() or 0
            
            return False, bookmark_count
        else:
            # 添加收藏
            new_bookmark = MomentInteraction(
                user_id=user_id,
                moment_id=moment_id,
                interaction_type=INTERACTION_TYPE_BOOKMARK
            )
            db.add(new_bookmark)
            db.commit()
            
            # 获取当前收藏数
            bookmark_count = db.query(func.count(MomentInteraction.id)).filter(
                and_(
                    MomentInteraction.moment_id == moment_id,
                    MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
                )
            ).scalar() or 0
            
            return True, bookmark_count
    
    def get_comments_by_moment(
        self, 
        db: Session, 
        moment_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> Tuple[List[MomentComment], int]:
        """获取动态的评论列表（只查询顶级评论）"""
        # 只查询顶级评论（parent_id为空），状态正常
        query = db.query(MomentComment).filter(
            and_(
                MomentComment.moment_id == moment_id,
                MomentComment.parent_id.is_(None),
                MomentComment.status == 0  # status=0 正常
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
            and_(
                MomentComment.parent_id == comment_id,
                MomentComment.status == 0
            )
        ).order_by(MomentComment.create_time).all()
    
    def create_comment(
        self, 
        db: Session, 
        user_id: int, 
        moment_id: int, 
        content: str, 
        parent_comment_id: Optional[int] = None
    ) -> MomentComment:
        """创建评论"""
        db_comment = MomentComment(
            moment_id=moment_id,
            user_id=user_id,
            content=content,
            parent_id=parent_comment_id,  # 注意字段名是 parent_id
            status=0  # 默认正常状态
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
        """删除评论（软删除）"""
        db_comment = db.query(MomentComment).filter(
            and_(
                MomentComment.id == comment_id,
                MomentComment.user_id == user_id,
                MomentComment.status == 0
            )
        ).first()
        
        if not db_comment:
            return False
        
        moment_id = db_comment.moment_id
        
        # 软删除评论
        db_comment.status = 1  # status=1 已删除
        
        # 减少动态的评论数
        db.query(Moment).filter(Moment.id == moment_id).update({
            "comment_count": Moment.comment_count - 1
        })
        
        db.commit()
        return True
    
    def record_share(
        self, 
        db: Session, 
        user_id: int, 
        moment_id: int, 
        share_type: str = 'general'
    ) -> bool:
        """
        记录分享行为
        分享不需要唯一约束，允许重复分享
        """
        # 记录分享
        new_share = MomentInteraction(
            user_id=user_id,
            moment_id=moment_id,
            interaction_type=INTERACTION_TYPE_SHARE
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
        """
        记录浏览行为（直接增加计数，不单独存储浏览记录）
        """
        # 增加动态的浏览数
        db.query(Moment).filter(Moment.id == moment_id).update({
            "view_count": Moment.view_count + 1
        })
        
        db.commit()
        return True
    
    def get_user_interaction_status(self, db: Session, user_id: int, moment_id: int) -> Dict[str, bool]:
        """获取用户对动态的互动状态"""
        # 检查点赞状态
        is_liked = db.query(MomentInteraction).filter(
            and_(
                MomentInteraction.user_id == user_id,
                MomentInteraction.moment_id == moment_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_LIKE
            )
        ).first() is not None
        
        # 检查收藏状态
        is_bookmarked = db.query(MomentInteraction).filter(
            and_(
                MomentInteraction.user_id == user_id,
                MomentInteraction.moment_id == moment_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
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
    ) -> Tuple[List[Moment], int]:
        """获取用户收藏的动态"""
        # 通过 interaction 表关联查询动态
        query = db.query(Moment).join(
            MomentInteraction,
            and_(
                MomentInteraction.moment_id == Moment.id,
                MomentInteraction.user_id == user_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
            )
        ).filter(Moment.status == 1)
        
        total = query.count()
        
        moments = query.order_by(desc(MomentInteraction.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size).all()
        
        return moments, total
    
    def get_user_likes(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> Tuple[List[Moment], int]:
        """获取用户点赞的动态"""
        # 通过 interaction 表关联查询动态
        query = db.query(Moment).join(
            MomentInteraction,
            and_(
                MomentInteraction.moment_id == Moment.id,
                MomentInteraction.user_id == user_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_LIKE
            )
        ).filter(Moment.status == 1)
        
        total = query.count()
        
        moments = query.order_by(desc(MomentInteraction.create_time))\
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
                "view_count": 0,
                "bookmark_count": 0
            }
        
        # 统计收藏数（从 interaction 表）
        bookmark_count = db.query(func.count(MomentInteraction.id)).filter(
            and_(
                MomentInteraction.moment_id == moment_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
            )
        ).scalar() or 0
        
        return {
            "like_count": moment.like_count,
            "comment_count": moment.comment_count,
            "share_count": moment.share_count,
            "view_count": moment.view_count,
            "bookmark_count": bookmark_count
        }
    
    def get_user_interaction_stats(self, db: Session, user_id: int) -> Dict[str, int]:
        """获取用户的互动统计"""
        # 用户发布的动态获得的总互动数
        user_moments = db.query(Moment).filter(
            and_(Moment.user_id == user_id, Moment.status == 1)
        ).all()
        
        total_likes_received = sum(moment.like_count for moment in user_moments)
        total_comments_received = sum(moment.comment_count for moment in user_moments)
        total_shares_received = sum(moment.share_count for moment in user_moments)
        
        # 用户的互动行为统计
        likes_given = db.query(func.count(MomentInteraction.id)).filter(
            and_(
                MomentInteraction.user_id == user_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_LIKE
            )
        ).scalar() or 0
        
        comments_given = db.query(func.count(MomentComment.id)).filter(
            and_(
                MomentComment.user_id == user_id,
                MomentComment.status == 0
            )
        ).scalar() or 0
        
        bookmarks_made = db.query(func.count(MomentInteraction.id)).filter(
            and_(
                MomentInteraction.user_id == user_id,
                MomentInteraction.interaction_type == INTERACTION_TYPE_BOOKMARK
            )
        ).scalar() or 0
        
        return {
            "published_count": len(user_moments),
            "total_likes_received": total_likes_received,
            "total_comments_received": total_comments_received,
            "total_shares_received": total_shares_received,
            "likes_given": likes_given,
            "comments_given": comments_given,
            "bookmarks_made": bookmarks_made
        }

# 创建CRUD实例
crud_moment_interaction = CRUDMomentInteraction() 