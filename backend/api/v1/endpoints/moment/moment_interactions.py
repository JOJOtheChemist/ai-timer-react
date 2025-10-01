from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.moment import (
    InteractionResponse, CommentCreate, CommentResponse, CommentListResponse,
    ShareCreate, ShareResponse
)
from services.moment.moment_interaction_service import moment_interaction_service

router = APIRouter()

@router.post("/{moment_id}/like", response_model=InteractionResponse)
async def toggle_like(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """点赞/取消点赞"""
    try:
        result = moment_interaction_service.toggle_like(db, current_user_id, moment_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"点赞操作失败: {str(e)}")

@router.post("/{moment_id}/bookmark", response_model=InteractionResponse)
async def toggle_bookmark(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """收藏/取消收藏"""
    try:
        result = moment_interaction_service.toggle_bookmark(db, current_user_id, moment_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"收藏操作失败: {str(e)}")

@router.get("/{moment_id}/comments", response_model=CommentListResponse)
async def get_comments(
    moment_id: int,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    db: Session = Depends(get_db)
):
    """获取评论列表"""
    try:
        comments = moment_interaction_service.get_comments(db, moment_id, page, page_size)
        return comments
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取评论列表失败: {str(e)}")

@router.post("/{moment_id}/comments", response_model=CommentResponse)
async def create_comment(
    moment_id: int,
    comment_data: CommentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """提交评论"""
    try:
        comment = moment_interaction_service.create_comment(
            db, current_user_id, moment_id, comment_data
        )
        return comment
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提交评论失败: {str(e)}")

@router.delete("/comments/{comment_id}", response_model=InteractionResponse)
async def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """删除评论"""
    try:
        result = moment_interaction_service.delete_comment(db, comment_id, current_user_id)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除评论失败: {str(e)}")

@router.post("/{moment_id}/share", response_model=ShareResponse)
async def share_moment(
    moment_id: int,
    share_data: ShareCreate = ShareCreate(),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """记录分享行为"""
    try:
        result = moment_interaction_service.record_share(
            db, current_user_id, moment_id, share_data
        )
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"分享失败: {str(e)}")

@router.post("/{moment_id}/view")
async def record_view(
    moment_id: int,
    request: Request,
    view_duration: int = Query(0, ge=0, description="浏览时长（秒）"),
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_dev)
):
    """记录浏览行为"""
    try:
        # 获取客户端信息
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")
        
        success = moment_interaction_service.record_view(
            db, moment_id, current_user_id, ip_address, user_agent, view_duration
        )
        
        return {
            "success": success,
            "message": "浏览记录成功" if success else "浏览记录失败"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"记录浏览失败: {str(e)}")

@router.get("/{moment_id}/interaction-status")
async def get_interaction_status(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户对动态的互动状态"""
    try:
        status = moment_interaction_service.get_user_interaction_status(
            db, current_user_id, moment_id
        )
        
        return {
            "moment_id": moment_id,
            "user_id": current_user_id,
            **status
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取互动状态失败: {str(e)}")

@router.get("/{moment_id}/stats")
async def get_interaction_stats(
    moment_id: int,
    db: Session = Depends(get_db)
):
    """获取动态的互动统计"""
    try:
        stats = moment_interaction_service.get_interaction_stats(db, moment_id)
        
        return {
            "moment_id": moment_id,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取互动统计失败: {str(e)}")

@router.get("/{moment_id}/summary")
async def get_interaction_summary(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user_id: Optional[int] = Depends(get_current_user_dev)
):
    """获取动态的互动摘要"""
    try:
        summary = moment_interaction_service.get_moment_interaction_summary(
            db, moment_id, current_user_id
        )
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取互动摘要失败: {str(e)}")

@router.get("/me/bookmarks")
async def get_my_bookmarks(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取我的收藏"""
    try:
        bookmarks = moment_interaction_service.get_user_bookmarks(
            db, current_user_id, page, page_size
        )
        
        return bookmarks
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取收藏列表失败: {str(e)}")

@router.get("/me/likes")
async def get_my_likes(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取我点赞的动态"""
    try:
        likes = moment_interaction_service.get_user_likes(
            db, current_user_id, page, page_size
        )
        
        return likes
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取点赞列表失败: {str(e)}")

@router.get("/me/stats")
async def get_my_interaction_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取我的互动统计"""
    try:
        stats = moment_interaction_service.get_user_interaction_stats(db, current_user_id)
        
        return {
            "user_id": current_user_id,
            "stats": stats
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户互动统计失败: {str(e)}")

@router.get("/health")
async def health_check():
    """动态互动服务健康检查"""
    return {"status": "healthy", "service": "moment_interaction_service"} 