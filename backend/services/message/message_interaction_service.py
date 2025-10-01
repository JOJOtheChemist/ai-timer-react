from sqlalchemy.orm import Session
from typing import Optional, List

from models.schemas.message import (
    MessageResponse, MessageReplyCreate, InteractionResponse
)
from crud.message.crud_message_interaction import crud_message_interaction
from services.message.message_service import message_service

class MessageInteractionService:
    """消息互动服务层"""
    
    def reply_to_message(
        self,
        db: Session,
        user_id: int,
        message_id: int,
        reply_data: MessageReplyCreate
    ) -> Optional[MessageResponse]:
        """回复消息（自动填充接收方、关联原消息ID）"""
        # 检查权限
        if not crud_message_interaction.check_message_permission(
            db, message_id, user_id, "reply"
        ):
            return None
        
        # 创建回复消息
        reply_message = crud_message_interaction.create_reply(
            db, user_id, message_id, reply_data.content
        )
        
        if not reply_message:
            return None
        
        # 转换为响应模型
        message_response = MessageResponse.from_orm(reply_message)
        message_response.sender_name = message_service._get_sender_name(db, user_id)
        message_response.sender_avatar = message_service._get_sender_avatar(db, user_id)
        message_response.is_unread = True
        message_response.reply_count = 0
        
        return message_response
    
    def mark_as_read(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> InteractionResponse:
        """标记消息为已读（更新is_unread状态）"""
        # 检查权限
        if not crud_message_interaction.check_message_permission(
            db, message_id, user_id, "mark_read"
        ):
            return InteractionResponse(
                success=False,
                message="无权限标记此消息为已读"
            )
        
        # 更新已读状态
        updated_message = crud_message_interaction.update_read_status(
            db, user_id, message_id
        )
        
        if updated_message:
            return InteractionResponse(
                success=True,
                message="消息已标记为已读",
                data={"message_id": message_id, "read_time": updated_message.read_time}
            )
        else:
            return InteractionResponse(
                success=False,
                message="消息不存在或已经是已读状态"
            )
    
    def batch_mark_as_read(
        self,
        db: Session,
        user_id: int,
        message_ids: List[int]
    ) -> InteractionResponse:
        """批量标记消息为已读"""
        # 验证权限（简化处理，实际项目中可能需要逐个验证）
        updated_count = crud_message_interaction.batch_update_read_status(
            db, user_id, message_ids
        )
        
        return InteractionResponse(
            success=True,
            message=f"成功标记 {updated_count} 条消息为已读",
            data={"updated_count": updated_count}
        )
    
    def delete_message(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> InteractionResponse:
        """删除消息"""
        # 检查权限
        if not crud_message_interaction.check_message_permission(
            db, message_id, user_id, "delete"
        ):
            return InteractionResponse(
                success=False,
                message="无权限删除此消息"
            )
        
        # 删除消息
        from crud.message.crud_message import crud_message
        success = crud_message.delete(db, message_id, user_id)
        
        if success:
            return InteractionResponse(
                success=True,
                message="消息删除成功",
                data={"message_id": message_id}
            )
        else:
            return InteractionResponse(
                success=False,
                message="消息删除失败"
            )
    
    def batch_delete_messages(
        self,
        db: Session,
        user_id: int,
        message_ids: List[int]
    ) -> InteractionResponse:
        """批量删除消息"""
        from crud.message.crud_message import crud_message
        deleted_count = crud_message.batch_delete(db, message_ids, user_id)
        
        return InteractionResponse(
            success=True,
            message=f"成功删除 {deleted_count} 条消息",
            data={"deleted_count": deleted_count}
        )
    
    def auto_process_system_messages(
        self,
        db: Session,
        user_id: int
    ) -> InteractionResponse:
        """自动处理系统消息（根据用户设置自动标记已读）"""
        # 检查用户是否启用了系统消息自动已读
        from crud.user.crud_user_message_setting import crud_user_message_setting
        
        setting = crud_user_message_setting.get_by_user_id(db, user_id)
        if not setting or setting.auto_read_system == 0:
            return InteractionResponse(
                success=False,
                message="用户未启用系统消息自动已读功能"
            )
        
        # 自动标记系统消息为已读
        updated_count = crud_message_interaction.auto_mark_system_messages_read(
            db, user_id
        )
        
        return InteractionResponse(
            success=True,
            message=f"自动标记 {updated_count} 条系统消息为已读",
            data={"updated_count": updated_count}
        )
    
    def get_reply_chain(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> List[MessageResponse]:
        """获取消息的完整回复链"""
        messages = crud_message_interaction.get_reply_chain(db, message_id, user_id)
        
        message_responses = []
        for message in messages:
            message_response = MessageResponse.from_orm(message)
            message_response.sender_name = message_service._get_sender_name(db, message.sender_id)
            message_response.sender_avatar = message_service._get_sender_avatar(db, message.sender_id)
            message_response.is_unread = message.is_read == 0
            message_response.reply_count = 0  # 回复链中不显示嵌套回复数
            message_responses.append(message_response)
        
        return message_responses
    
    def check_can_reply(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> bool:
        """检查是否可以回复消息"""
        return crud_message_interaction.check_message_permission(
            db, message_id, user_id, "reply"
        )

# 创建服务实例
message_interaction_service = MessageInteractionService() 