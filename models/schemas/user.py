from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from models.schemas.message import MessageSettingResponse, MessageSettingUpdate, ReminderTypeEnum

# 用户基础信息
class UserBase(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=100, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")

class UserResponse(UserBase):
    id: int
    is_active: bool = True
    create_time: datetime
    
    class Config:
        from_attributes = True

# 用户消息设置（继承自message模块）
class UserMessageSettingResponse(MessageSettingResponse):
    """用户消息设置响应"""
    user_id: int = Field(..., description="用户ID")
    create_time: datetime
    update_time: datetime
    
    class Config:
        from_attributes = True

class UserMessageSettingUpdate(MessageSettingUpdate):
    """用户消息设置更新"""
    pass

# 用户操作响应
class UserOperationResponse(BaseModel):
    success: bool = Field(True, description="操作是否成功")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[dict] = Field(None, description="响应数据") 