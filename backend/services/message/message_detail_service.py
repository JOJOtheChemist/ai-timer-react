from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List

from models.schemas.message import MessageDetailResponse, MessageResponse
from crud.message.crud_message_detail import crud_message_detail
from services.message.message_service import message_service

class MessageDetailService:
    """消息详情服务层"""
    
    def get_message_detail(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> Optional[MessageDetailResponse]:
        """查询消息详情，验证消息归属（确保用户只能查看自己的消息）"""
        # 获取消息详情及上下文
        detail_data = crud_message_detail.get_by_id_with_context(db, user_id, message_id)
        if not detail_data:
            return None
        
        main_message = detail_data["message"]
        context_messages = detail_data["context_messages"]
        replies = detail_data["replies"]
        
        # 转换主消息为响应模型
        message_response = MessageResponse.from_orm(main_message)
        message_response.sender_name = message_service._get_sender_name(db, main_message.sender_id)
        message_response.sender_avatar = message_service._get_sender_avatar(db, main_message.sender_id)
        message_response.is_unread = main_message.is_unread == 0
        message_response.reply_count = len(replies)
        
        # 转换上下文消息
        context_responses = []
        for msg in context_messages:
            ctx_response = MessageResponse.from_orm(msg)
            ctx_response.sender_name = message_service._get_sender_name(db, msg.sender_id)
            ctx_response.sender_avatar = message_service._get_sender_avatar(db, msg.sender_id)
            ctx_response.is_unread = msg.is_unread == 0
            ctx_response.reply_count = message_service._get_reply_count(db, msg.id)
            context_responses.append(ctx_response)
        
        # 获取关联资源信息
        related_resource = None
        if main_message.related_type and main_message.related_id:
            related_resource = crud_message_detail.get_related_resource_info(
                db, main_message.related_type, main_message.related_id
            )
        
        # 检查是否可以回复
        can_reply = crud_message_detail.check_can_reply(main_message, user_id)
        
        # 创建详情响应
        detail_response = MessageDetailResponse(
            **message_response.dict(),
            context_messages=context_responses,
            related_resource=related_resource,
            can_reply=can_reply
        )
        
        # 自动标记为已读（如果是接收方查看且未读）
        if main_message.receiver_id == user_id and main_message.is_unread == 0:
            self._mark_as_read_async(db, message_id, user_id)
            detail_response.is_unread = False
            detail_response.is_unread = True
        
        return detail_response
    
    def _mark_as_read_async(self, db: Session, message_id: int, user_id: int):
        """异步标记消息为已读"""
        try:
            from crud.message.crud_message import crud_message
            crud_message.mark_as_read(db, message_id, user_id)
        except Exception as e:
            # 记录日志但不影响主流程
            print(f"Failed to mark message {message_id} as read: {e}")
    
    def get_tutor_feedback_history(
        self,
        db: Session,
        user_id: int,
        tutor_id: int,
        limit: int = 10
    ) -> List[MessageResponse]:
        """获取与特定导师的历史反馈记录"""
        # 这里可以扩展为更复杂的导师反馈历史查询
        from crud.message.crud_message import crud_message
        
        messages = crud_message.get_multi_by_type(
            db, user_id, type=0, page=1, page_size=limit
        )[0]
        
        # 过滤特定导师的消息
        tutor_messages = [
            msg for msg in messages 
            if msg.related_id == tutor_id and msg.related_type == 0
        ]
        
        # 转换为响应模型
        message_responses = []
        for message in tutor_messages:
            message_response = MessageResponse.from_orm(message)
            message_response.sender_name = f"导师{tutor_id}"
            message_response.sender_avatar = f"/avatars/tutor_{tutor_id}.png"
            message_response.is_unread = message.is_unread == 0
            message_response.reply_count = message_service._get_reply_count(db, message.id)
            message_responses.append(message_response)
        
        return message_responses
    
    def get_message_thread(
        self,
        db: Session,
        user_id: int,
        message_id: int
    ) -> List[MessageResponse]:
        """获取消息的完整对话线程"""
        from crud.message.crud_message_interaction import crud_message_interaction
        
        thread_messages = crud_message_interaction.get_reply_chain(db, message_id, user_id)
        
        message_responses = []
        for message in thread_messages:
            message_response = MessageResponse.from_orm(message)
            message_response.sender_name = message_service._get_sender_name(db, message.sender_id)
            message_response.sender_avatar = message_service._get_sender_avatar(db, message.sender_id)
            message_response.is_unread = message.is_unread == 0
            message_response.reply_count = 0  # 线程中的消息不需要显示回复数
            message_responses.append(message_response)
        
        return message_responses
    
    def check_message_access_permission(
        self,
        db: Session,
        message_id: int,
        user_id: int
    ) -> bool:
        """检查用户是否有权限访问消息"""
        from crud.message.crud_message_interaction import crud_message_interaction
        return crud_message_interaction.check_message_permission(
            db, message_id, user_id, "read"
        )

# 创建服务实例
message_detail_service = MessageDetailService() 