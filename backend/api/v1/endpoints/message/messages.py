from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.message import (
    MessageListResponse, MessageTypeEnum, MessageCreate, MessageResponse,
    MessageBatchOperation, MessageBatchResponse, UnreadStatsResponse
)
from services.message.message_service import message_service
from services.message.message_stat_service import message_stat_service

router = APIRouter()

@router.get("/unread-stats", response_model=UnreadStatsResponse)
async def get_unread_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取各类型消息的未读数量（用于标签页徽章显示）"""
    try:
        unread_stats = message_stat_service.calculate_unread_stats(db, current_user_id)
        return unread_stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取未读统计失败: {str(e)}")

@router.get("", response_model=MessageListResponse)
async def get_messages(
    message_type: Optional[MessageTypeEnum] = Query(None, description="消息类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """
    获取消息列表（支持type参数：tutor/private/system，默认tutor）
    自动区分未读/已读状态，返回未读消息数用于徽章显示
    """
    try:
        # 如果没有指定类型，默认显示导师反馈
        if message_type is None:
            message_type = MessageTypeEnum.TUTOR
        
        message_list = message_service.get_message_list(
            db=db,
            user_id=current_user_id,
            message_type=message_type,
            page=page,
            page_size=page_size
        )
        
        return message_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息列表失败: {str(e)}")

@router.post("", response_model=MessageResponse)
async def create_message(
    message_data: MessageCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """创建新消息"""
    try:
        message = message_service.create_message(
            db=db,
            sender_id=current_user_id,
            message_data=message_data
        )
        
        return message
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建消息失败: {str(e)}")

@router.get("/conversation/{other_user_id}", response_model=list[MessageResponse])
async def get_conversation_history(
    other_user_id: int,
    limit: int = Query(10, ge=1, le=50, description="消息数量限制"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取与特定用户的对话历史"""
    try:
        messages = message_service.get_conversation_history(
            db=db,
            user_id=current_user_id,
            other_user_id=other_user_id,
            limit=limit
        )
        
        return messages
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对话历史失败: {str(e)}")

@router.post("/batch", response_model=MessageBatchResponse)
async def batch_operation_messages(
    batch_data: MessageBatchOperation,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """批量操作消息（标记已读/删除）"""
    try:
        if batch_data.operation == "mark_read":
            processed_count = message_service.batch_mark_as_read(
                db=db,
                message_ids=batch_data.message_ids,
                user_id=current_user_id
            )
            
            return MessageBatchResponse(
                success=True,
                processed_count=processed_count,
                failed_count=len(batch_data.message_ids) - processed_count,
                message=f"成功标记 {processed_count} 条消息为已读"
            )
        
        elif batch_data.operation == "delete":
            processed_count = message_service.batch_delete_messages(
                db=db,
                message_ids=batch_data.message_ids,
                user_id=current_user_id
            )
            
            return MessageBatchResponse(
                success=True,
                processed_count=processed_count,
                failed_count=len(batch_data.message_ids) - processed_count,
                message=f"成功删除 {processed_count} 条消息"
            )
        
        else:
            raise HTTPException(status_code=400, detail="不支持的批量操作类型")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量操作失败: {str(e)}")

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """删除单条消息"""
    try:
        success = message_service.delete_message(
            db=db,
            message_id=message_id,
            user_id=current_user_id
        )
        
        if success:
            return {"success": True, "message": "消息删除成功"}
        else:
            raise HTTPException(status_code=404, detail="消息不存在或无权限删除")
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")

@router.get("/health")
async def health_check():
    """消息服务健康检查"""
    return {"status": "healthy", "service": "message_service"} 