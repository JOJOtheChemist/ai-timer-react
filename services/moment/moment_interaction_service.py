from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from models.schemas.moment import (
    InteractionResponse, CommentCreate, CommentResponse, CommentListResponse,
    ShareCreate, ShareResponse, UserInfo
)
from crud.moment.crud_moment_interaction import crud_moment_interaction
from services.moment.moment_service import moment_service

class MomentInteractionService:
    """动态互动服务层"""
    
    def toggle_like(self, db: Session, user_id: int, moment_id: int) -> InteractionResponse:
        """切换点赞状态（检查是否已点赞，避免重复）"""
        try:
            is_liked, current_count = crud_moment_interaction.toggle_like(db, user_id, moment_id)
            
            return InteractionResponse(
                success=True,
                message="点赞成功" if is_liked else "取消点赞成功",
                is_liked=is_liked,
                current_count=current_count,
                data={
                    "moment_id": moment_id,
                    "like_count": current_count,
                    "action": "like" if is_liked else "unlike"
                }
            )
        
        except Exception as e:
            return InteractionResponse(
                success=False,
                message=f"点赞操作失败: {str(e)}"
            )
    
    def toggle_bookmark(self, db: Session, user_id: int, moment_id: int) -> InteractionResponse:
        """切换收藏状态"""
        try:
            is_bookmarked, current_count = crud_moment_interaction.toggle_bookmark(db, user_id, moment_id)
            
            return InteractionResponse(
                success=True,
                message="收藏成功" if is_bookmarked else "取消收藏成功",
                is_bookmarked=is_bookmarked,
                current_count=current_count,
                data={
                    "moment_id": moment_id,
                    "bookmark_count": current_count,
                    "action": "bookmark" if is_bookmarked else "unbookmark"
                }
            )
        
        except Exception as e:
            return InteractionResponse(
                success=False,
                message=f"收藏操作失败: {str(e)}"
            )
    
    def get_comments(
        self, 
        db: Session, 
        moment_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> CommentListResponse:
        """获取评论列表"""
        comments, total = crud_moment_interaction.get_comments_by_moment(
            db, moment_id, page, page_size
        )
        
        # 转换为响应模型
        comment_responses = []
        for comment in comments:
            comment_response = self._convert_comment_to_response(db, comment)
            
            # 获取回复
            replies = crud_moment_interaction.get_comment_replies(db, comment.id)
            comment_response.replies = [
                self._convert_comment_to_response(db, reply) for reply in replies
            ]
            
            comment_responses.append(comment_response)
        
        return CommentListResponse(
            comments=comment_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def create_comment(
        self, 
        db: Session, 
        user_id: int, 
        moment_id: int, 
        comment_data: CommentCreate
    ) -> CommentResponse:
        """提交评论"""
        # 校验评论内容
        if not comment_data.content or len(comment_data.content.strip()) == 0:
            raise ValueError("评论内容不能为空")
        
        if len(comment_data.content) > 1000:
            raise ValueError("评论内容不能超过1000字符")
        
        # 如果是回复评论，检查父评论是否存在
        if comment_data.parent_comment_id:
            parent_comment = db.query(crud_moment_interaction.MomentComment).filter(
                crud_moment_interaction.MomentComment.id == comment_data.parent_comment_id
            ).first()
            
            if not parent_comment:
                raise ValueError("回复的评论不存在")
            
            if parent_comment.moment_id != moment_id:
                raise ValueError("回复的评论不属于该动态")
        
        # 创建评论
        db_comment = crud_moment_interaction.create_comment(
            db, user_id, moment_id, comment_data.content, comment_data.parent_comment_id
        )
        
        return self._convert_comment_to_response(db, db_comment)
    
    def delete_comment(self, db: Session, comment_id: int, user_id: int) -> InteractionResponse:
        """删除评论"""
        try:
            success = crud_moment_interaction.delete_comment(db, comment_id, user_id)
            
            if success:
                return InteractionResponse(
                    success=True,
                    message="评论删除成功",
                    data={"comment_id": comment_id}
                )
            else:
                return InteractionResponse(
                    success=False,
                    message="评论不存在或无权限删除"
                )
        
        except Exception as e:
            return InteractionResponse(
                success=False,
                message=f"删除评论失败: {str(e)}"
            )
    
    def record_share(
        self, 
        db: Session, 
        user_id: int, 
        moment_id: int, 
        share_data: ShareCreate
    ) -> ShareResponse:
        """记录分享行为（不重复计数）"""
        try:
            success = crud_moment_interaction.record_share(
                db, user_id, moment_id, share_data.share_type
            )
            
            # 获取当前分享数
            stats = crud_moment_interaction.get_interaction_stats(db, moment_id)
            share_count = stats.get('share_count', 0)
            
            if success:
                return ShareResponse(
                    success=True,
                    message="分享成功",
                    share_count=share_count
                )
            else:
                return ShareResponse(
                    success=True,
                    message="今日已分享过该内容",
                    share_count=share_count
                )
        
        except Exception as e:
            return ShareResponse(
                success=False,
                message=f"分享失败: {str(e)}",
                share_count=0
            )
    
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
        try:
            return crud_moment_interaction.record_view(
                db, moment_id, user_id, ip_address, user_agent, view_duration
            )
        except Exception:
            return False
    
    def get_user_interaction_status(
        self, 
        db: Session, 
        user_id: int, 
        moment_id: int
    ) -> Dict[str, bool]:
        """获取用户对动态的互动状态"""
        return crud_moment_interaction.get_user_interaction_status(db, user_id, moment_id)
    
    def get_user_bookmarks(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取用户收藏的动态"""
        moments, total = crud_moment_interaction.get_user_bookmarks(db, user_id, page, page_size)
        
        # 转换为响应模型
        moment_responses = []
        for moment in moments:
            moment_response = moment_service._convert_to_response(db, moment, user_id)
            moment_responses.append(moment_response)
        
        return {
            "bookmarks": moment_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": page * page_size < total
        }
    
    def get_user_likes(
        self, 
        db: Session, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 10
    ) -> Dict[str, Any]:
        """获取用户点赞的动态"""
        moments, total = crud_moment_interaction.get_user_likes(db, user_id, page, page_size)
        
        # 转换为响应模型
        moment_responses = []
        for moment in moments:
            moment_response = moment_service._convert_to_response(db, moment, user_id)
            moment_responses.append(moment_response)
        
        return {
            "liked_moments": moment_responses,
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_next": page * page_size < total
        }
    
    def get_interaction_stats(self, db: Session, moment_id: int) -> Dict[str, int]:
        """获取动态的互动统计"""
        return crud_moment_interaction.get_interaction_stats(db, moment_id)
    
    def get_user_interaction_stats(self, db: Session, user_id: int) -> Dict[str, int]:
        """获取用户的互动统计"""
        return crud_moment_interaction.get_user_interaction_stats(db, user_id)
    
    def get_moment_interaction_summary(
        self, 
        db: Session, 
        moment_id: int, 
        current_user_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """获取动态的互动摘要"""
        # 获取统计数据
        stats = self.get_interaction_stats(db, moment_id)
        
        # 获取用户互动状态
        user_status = {}
        if current_user_id:
            user_status = self.get_user_interaction_status(db, current_user_id, moment_id)
        
        return {
            "moment_id": moment_id,
            "stats": stats,
            "user_status": user_status,
            "summary": {
                "total_interactions": (
                    stats.get('like_count', 0) + 
                    stats.get('comment_count', 0) + 
                    stats.get('share_count', 0) + 
                    stats.get('bookmark_count', 0)
                ),
                "engagement_rate": self._calculate_engagement_rate(stats)
            }
        }
    
    def _convert_comment_to_response(self, db: Session, comment) -> CommentResponse:
        """转换评论为响应模型"""
        # 获取用户信息
        user_info = self._get_user_info(db, comment.user_id)
        
        return CommentResponse(
            id=comment.id,
            user=user_info,
            content=comment.content,
            parent_comment_id=comment.parent_comment_id,
            like_count=comment.like_count,
            create_time=comment.create_time,
            replies=[]  # 将在调用方填充
        )
    
    def _get_user_info(self, db: Session, user_id: int) -> UserInfo:
        """获取用户基础信息"""
        # 这里应该调用用户服务获取用户信息
        # 目前返回模拟数据
        return UserInfo(
            user_id=user_id,
            username=f"user_{user_id}",
            nickname=f"用户{user_id}",
            avatar=f"/avatars/user_{user_id}.png"
        )
    
    def _calculate_engagement_rate(self, stats: Dict[str, int]) -> float:
        """计算互动率"""
        view_count = stats.get('view_count', 0)
        if view_count == 0:
            return 0.0
        
        total_interactions = (
            stats.get('like_count', 0) + 
            stats.get('comment_count', 0) + 
            stats.get('share_count', 0) + 
            stats.get('bookmark_count', 0)
        )
        
        return round((total_interactions / view_count) * 100, 2)

# 创建服务实例
moment_interaction_service = MomentInteractionService() 