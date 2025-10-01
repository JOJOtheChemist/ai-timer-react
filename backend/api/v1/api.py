from fastapi import APIRouter

from api.v1.endpoints.ai import ai_chat, ai_recommendations
from api.v1.endpoints.task import tasks
from api.v1.endpoints.schedule import time_slots
from api.v1.endpoints.statistic import statistics

api_router = APIRouter()

# AI相关路由
api_router.include_router(
    ai_chat.router, 
    prefix="/ai", 
    tags=["AI聊天"]
)

api_router.include_router(
    ai_recommendations.router,
    prefix="/ai",
    tags=["AI推荐"]
)

# 任务相关路由
api_router.include_router(
    tasks.router,
    prefix="/tasks",
    tags=["任务管理"]
)

# 时间表相关路由
api_router.include_router(
    time_slots.router,
    prefix="/schedule",
    tags=["时间表管理"]
)

# 统计相关路由
api_router.include_router(
    statistics.router,
    prefix="/statistics",
    tags=["统计分析"]
) 