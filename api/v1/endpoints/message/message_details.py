from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.message import MessageDetailResponse, MessageResponse
from services.message.message_detail_service import message_detail_service

router = APIRouter()

@router.get("/{message_id}", response_model=MessageDetailResponse)
async def get_message_detail(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """
    获取单条消息详情（含完整内容、关联上下文，如导师反馈的历史记录）
    """
    try:
        # 检查访问权限
        if not message_detail_service.check_message_access_permission(
            db, message_id, current_user_id
        ):
            raise HTTPException(status_code=403, detail="无权限访问此消息")
        
        # 获取消息详情
        message_detail = message_detail_service.get_message_detail(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        if not message_detail:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        return message_detail
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息详情失败: {str(e)}")

@router.get("/{message_id}/thread", response_model=List[MessageResponse])
async def get_message_thread(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息的完整对话线程"""
    try:
        # 检查访问权限
        if not message_detail_service.check_message_access_permission(
            db, message_id, current_user_id
        ):
            raise HTTPException(status_code=403, detail="无权限访问此消息")
        
        # 获取对话线程
        thread_messages = message_detail_service.get_message_thread(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        return thread_messages
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话线程失败: {str(e)}")

@router.get("/tutor/{tutor_id}/history", response_model=List[MessageResponse])
async def get_tutor_feedback_history(
    tutor_id: int,
    limit: int = Query(10, ge=1, le=50, description="历史记录数量限制"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """
    获取与特定导师的历史反馈记录
    对导师反馈类型，额外关联查询历史互动记录
    """
    try:
        history_messages = message_detail_service.get_tutor_feedback_history(
            db=db,
            user_id=current_user_id,
            tutor_id=tutor_id,
            limit=limit
        )
        
        return history_messages
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取导师反馈历史失败: {str(e)}")

@router.get("/{message_id}/context", response_model=List[MessageResponse])
async def get_message_context(
    message_id: int,
    context_type: str = Query("auto", description="上下文类型：auto/tutor/private"),
    limit: int = Query(5, ge=1, le=20, description="上下文消息数量限制"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息的上下文信息"""
    try:
        # 检查访问权限
        if not message_detail_service.check_message_access_permission(
            db, message_id, current_user_id
        ):
            raise HTTPException(status_code=403, detail="无权限访问此消息")
        
        # 获取消息详情（包含上下文）
        message_detail = message_detail_service.get_message_detail(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        if not message_detail:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        # 返回上下文消息
        context_messages = message_detail.context_messages[:limit]
        return context_messages
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息上下文失败: {str(e)}")

@router.get("/{message_id}/related-resource")
async def get_related_resource(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息关联的资源信息"""
    try:
        # 检查访问权限
        if not message_detail_service.check_message_access_permission(
            db, message_id, current_user_id
        ):
            raise HTTPException(status_code=403, detail="无权限访问此消息")
        
        # 获取消息详情
        message_detail = message_detail_service.get_message_detail(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        if not message_detail:
            raise HTTPException(status_code=404, detail="消息不存在")
        
        # 返回关联资源信息
        if message_detail.related_resource:
            return {
                "success": True,
                "data": message_detail.related_resource
            }
        else:
            return {
                "success": True,
                "data": None,
                "message": "此消息没有关联资源"
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取关联资源失败: {str(e)}") 