from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # 数据库配置
    DATABASE_URL: str = "postgresql://yeya@localhost:5432/ai_time_management"
    
    # API配置
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Time Management System"
    
    # JWT配置
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # AI配置
    AI_MODEL_API_KEY: Optional[str] = None
    AI_MODEL_BASE_URL: str = "https://ark.cn-beijing.volces.com/api/v3"
    AI_MODEL_NAME: str = "ep-20241201141448-xxxxxx"  # 豆包模型endpoint
    
    # Redis配置（用于缓存）
    REDIS_URL: str = "redis://localhost:6379"
    
    # 分页配置
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    class Config:
        env_file = ".env"

settings = Settings() 