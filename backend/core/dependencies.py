from fastapi import Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional
import jwt
from datetime import datetime

from core.config import settings
from core.database import get_db

# JWT认证
security = HTTPBearer()

def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    """
    从JWT token中获取当前用户ID
    实际项目中应该验证token的有效性
    """
    try:
        # 解析JWT token
        payload = jwt.decode(
            credentials.credentials, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        user_id: int = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的认证凭据",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的认证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[int]:
    """
    可选的用户认证，用于一些不强制登录的接口
    """
    if not credentials:
        return None
    
    try:
        return get_current_user_id(credentials)
    except HTTPException:
        return None

# 临时的用户ID获取方式（用于开发测试）
def get_current_user_dev(
    user_id: int = Query(..., description="用户ID（开发测试用）")
) -> int:
    """
    开发测试用的用户ID获取方式
    生产环境应该使用get_current_user_id
    """
    return user_id

# 获取当前用户信息（返回字典格式）
def get_current_user(
    user_id: int = Query(..., description="用户ID")
) -> dict:
    """
    获取当前用户信息（简化版，用于开发测试）
    生产环境应该从JWT token解析并查询数据库
    """
    return {
        "id": user_id,
        "username": f"user_{user_id}",
        "is_active": True
    }

# 数据库会话和用户ID的组合依赖
def get_db_and_user(
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_dev)  # 生产环境改为get_current_user_id
) -> tuple[Session, int]:
    """获取数据库会话和当前用户ID"""
    return db, user_id

# 权限验证
def verify_user_permission(
    resource_user_id: int,
    current_user_id: int
) -> bool:
    """
    验证用户是否有权限访问资源
    """
    return resource_user_id == current_user_id

def require_user_permission(
    resource_user_id: int,
    current_user_id: int
) -> None:
    """
    要求用户权限，如果没有权限则抛出异常
    """
    if not verify_user_permission(resource_user_id, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="没有权限访问该资源"
        ) 