from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

# 枚举类型
class MessageTypeEnum(int, Enum):
    TUTOR = 0
    PRIVATE = 1
    SYSTEM = 2

class ReminderTypeEnum(str, Enum):
    PUSH = "push"
    EMAIL = "email"
    BOTH = "both"

# 消息基础模型
class MessageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200, description="消息标题")
    content: str = Field(..., min_length=1, description="消息内容")
    message_type: MessageTypeEnum = Field(..., description="消息类型")
    related_id: Optional[int] = Field(None, description="关联资源ID")
    related_type: Optional[str] = Field(None, max_length=20, description="关联资源类型")

class MessageCreate(MessageBase):
    receiver_id: int = Field(..., description="接收方用户ID")
    parent_message_id: Optional[int] = Field(None, description="回复的原消息ID")

class MessageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    is_read: Optional[bool] = Field(None, description="是否已读")

class MessageResponse(MessageBase):
    id: int
    sender_id: int
    receiver_id: int
    parent_message_id: Optional[int] = None
    is_read: bool = False
    read_time: Optional[datetime] = None
    create_time: datetime
    
    # 扩展字段（由服务层填充）
    sender_name: Optional[str] = Field(None, description="发送方姓名")
    sender_avatar: Optional[str] = Field(None, description="发送方头像")
    is_unread: bool = Field(True, description="是否未读（用于前端显示）")
    reply_count: int = Field(0, description="回复数量")
    
    class Config:
        from_attributes = True

class MessageListResponse(BaseModel):
    """消息列表响应"""
    messages: List[MessageResponse] = Field(..., description="消息列表")
    total: int = Field(..., description="总消息数")
    unread_count: int = Field(0, description="未读消息数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    has_next: bool = Field(..., description="是否有下一页")

class MessageDetailResponse(MessageResponse):
    """消息详情响应"""
    context_messages: List[MessageResponse] = Field([], description="上下文消息（如历史对话）")
    related_resource: Optional[Dict[str, Any]] = Field(None, description="关联资源信息")
    can_reply: bool = Field(True, description="是否可以回复")

# 消息回复相关
class MessageReplyCreate(BaseModel):
    content: str = Field(..., min_length=1, description="回复内容")

class InteractionResponse(BaseModel):
    """互动操作响应"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")

# 未读统计相关
class UnreadStatsResponse(BaseModel):
    """未读统计响应"""
    tutor_count: int = Field(0, description="导师反馈未读数")
    private_count: int = Field(0, description="私信未读数")
    system_count: int = Field(0, description="系统通知未读数")
    total_count: int = Field(0, description="总未读数")

# 用户消息设置相关
class MessageSettingResponse(BaseModel):
    """消息设置响应"""
    tutor_reminder: bool = Field(True, description="导师反馈提醒")
    private_reminder: bool = Field(True, description="私信提醒")
    system_reminder: bool = Field(True, description="系统通知提醒")
    reminder_type: ReminderTypeEnum = Field(ReminderTypeEnum.PUSH, description="提醒方式")
    keep_days: int = Field(30, description="消息保留天数")
    auto_read_system: bool = Field(False, description="系统消息自动已读")

class MessageSettingUpdate(BaseModel):
    """消息设置更新"""
    tutor_reminder: Optional[bool] = Field(None, description="导师反馈提醒")
    private_reminder: Optional[bool] = Field(None, description="私信提醒")
    system_reminder: Optional[bool] = Field(None, description="系统通知提醒")
    reminder_type: Optional[ReminderTypeEnum] = Field(None, description="提醒方式")
    keep_days: Optional[int] = Field(None, ge=1, le=365, description="消息保留天数")
    auto_read_system: Optional[bool] = Field(None, description="系统消息自动已读")

# 消息模板相关
class MessageTemplateResponse(BaseModel):
    """消息模板响应"""
    id: int
    template_type: str
    title_template: str
    content_template: str
    is_active: bool
    create_time: datetime
    
    class Config:
        from_attributes = True

# 消息查询参数
class MessageQueryParams(BaseModel):
    """消息查询参数"""
    message_type: Optional[MessageTypeEnum] = Field(None, description="消息类型筛选")
    is_read: Optional[bool] = Field(None, description="已读状态筛选")
    sender_id: Optional[int] = Field(None, description="发送方筛选")
    start_date: Optional[datetime] = Field(None, description="开始时间")
    end_date: Optional[datetime] = Field(None, description="结束时间")

# 批量操作
class MessageBatchOperation(BaseModel):
    """消息批量操作"""
    message_ids: List[int] = Field(..., description="消息ID列表")
    operation: str = Field(..., description="操作类型：mark_read/delete")

class MessageBatchResponse(BaseModel):
    """批量操作响应"""
    success: bool = Field(True, description="操作是否成功")
    processed_count: int = Field(0, description="处理数量")
    failed_count: int = Field(0, description="失败数量")
    message: str = Field("操作完成", description="响应消息")

# 通用响应模型
class MessageOperationResponse(BaseModel):
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据") 