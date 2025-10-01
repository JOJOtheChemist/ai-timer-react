from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.message import (
    MessageResponse, MessageReplyCreate, InteractionResponse
)
from services.message.message_interaction_service import message_interaction_service

router = APIRouter()

@router.post("/{message_id}/reply", response_model=MessageResponse)
async def reply_to_message(
    message_id: int,
    reply_data: MessageReplyCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """
    回复消息（支持对导师反馈/私信的回复，自动关联原消息）
    """
    try:
        reply_message = message_interaction_service.reply_to_message(
            db=db,
            user_id=current_user_id,
            message_id=message_id,
            reply_data=reply_data
        )
        
        if not reply_message:
            raise HTTPException(status_code=403, detail="无权限回复此消息或消息不存在")
        
        return reply_message
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"回复消息失败: {str(e)}")

@router.post("/{message_id}/mark-read", response_model=InteractionResponse)
async def mark_message_as_read(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """标记消息为已读"""
    try:
        result = message_interaction_service.mark_as_read(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"标记消息已读失败: {str(e)}")

@router.post("/batch/mark-read", response_model=InteractionResponse)
async def batch_mark_messages_as_read(
    message_ids: List[int],
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """批量标记消息为已读"""
    try:
        if not message_ids:
            raise HTTPException(status_code=400, detail="消息ID列表不能为空")
        
        result = message_interaction_service.batch_mark_as_read(
            db=db,
            user_id=current_user_id,
            message_ids=message_ids
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量标记已读失败: {str(e)}")

@router.delete("/{message_id}", response_model=InteractionResponse)
async def delete_message(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """删除消息"""
    try:
        result = message_interaction_service.delete_message(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除消息失败: {str(e)}")

@router.post("/batch/delete", response_model=InteractionResponse)
async def batch_delete_messages(
    message_ids: List[int],
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """批量删除消息"""
    try:
        if not message_ids:
            raise HTTPException(status_code=400, detail="消息ID列表不能为空")
        
        result = message_interaction_service.batch_delete_messages(
            db=db,
            user_id=current_user_id,
            message_ids=message_ids
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除消息失败: {str(e)}")

@router.get("/{message_id}/reply-chain", response_model=List[MessageResponse])
async def get_reply_chain(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息的完整回复链"""
    try:
        reply_chain = message_interaction_service.get_reply_chain(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        return reply_chain
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取回复链失败: {str(e)}")

@router.get("/{message_id}/can-reply")
async def check_can_reply(
    message_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """检查是否可以回复消息"""
    try:
        can_reply = message_interaction_service.check_can_reply(
            db=db,
            user_id=current_user_id,
            message_id=message_id
        )
        
        return {
            "message_id": message_id,
            "can_reply": can_reply,
            "reason": "可以回复" if can_reply else "无权限回复或消息类型不支持回复"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"检查回复权限失败: {str(e)}")

@router.post("/auto-process-system", response_model=InteractionResponse)
async def auto_process_system_messages(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """自动处理系统消息（根据用户设置自动标记已读）"""
    try:
        result = message_interaction_service.auto_process_system_messages(
            db=db,
            user_id=current_user_id
        )
        
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"自动处理系统消息失败: {str(e)}")

@router.get("/interaction-stats")
async def get_interaction_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户消息互动统计"""
    try:
        # 这里可以添加更多统计信息
        from services.message.message_stat_service import message_stat_service
        
        unread_stats = message_stat_service.calculate_unread_stats(db, current_user_id)
        overview = message_stat_service.get_message_overview(db, current_user_id, days=7)
        
        return {
            "user_id": current_user_id,
            "unread_stats": unread_stats.dict(),
            "weekly_overview": overview["summary"],
            "response_rate": overview["response_stats"]["response_rate"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取互动统计失败: {str(e)}") 