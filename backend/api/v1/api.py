from fastapi import APIRouter

from api.v1.endpoints.ai import ai_chat, ai_recommendations
from api.v1.endpoints.task import tasks
from api.v1.endpoints.schedule import time_slots
from api.v1.endpoints.statistic import statistics
from api.v1.endpoints.message import messages, message_details, message_interactions, message_stats
from api.v1.endpoints.user import user_message_settings, user_profiles, user_assets, user_relations, personal_page
from api.v1.endpoints.moment import moments, moment_interactions
from api.v1.endpoints.badge import badges
from api.v1.endpoints.method import methods, checkins
from api.v1.endpoints.case import cases, case_details, case_permissions
from api.v1.endpoints.tutor import tutors, tutor_details

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

# 消息相关路由
api_router.include_router(
    messages.router,
    prefix="/messages",
    tags=["消息管理"]
)

api_router.include_router(
    message_details.router,
    prefix="/messages",
    tags=["消息详情"]
)

api_router.include_router(
    message_interactions.router,
    prefix="/messages",
    tags=["消息互动"]
)

api_router.include_router(
    message_stats.router,
    prefix="/messages",
    tags=["消息统计"]
)

# 用户相关路由
api_router.include_router(
    user_message_settings.router,
    prefix="/users",
    tags=["用户设置"]
)

api_router.include_router(
    user_profiles.router,
    prefix="/users",
    tags=["用户个人信息"]
)

api_router.include_router(
    user_assets.router,
    prefix="/users",
    tags=["用户资产"]
)

api_router.include_router(
    user_relations.router,
    prefix="/users",
    tags=["用户关系"]
)

api_router.include_router(
    personal_page.router,
    prefix="/users",
    tags=["个人主页"]
)

# 徽章相关路由
api_router.include_router(
    badges.router,
    prefix="/badges",
    tags=["徽章系统"]
)

# 学习方法相关路由
api_router.include_router(
    methods.router,
    prefix="/methods",
    tags=["学习方法"]
)

api_router.include_router(
    checkins.router,
    prefix="/methods",
    tags=["方法打卡"]
)

# 动态相关路由
api_router.include_router(
    moments.router,
    prefix="/moments",
    tags=["动态管理"]
)

api_router.include_router(
    moment_interactions.router,
    prefix="/moments",
    tags=["动态互动"]
)

# 成功案例相关路由
api_router.include_router(
    cases.router,
    prefix="/cases",
    tags=["成功案例"]
)

api_router.include_router(
    case_details.router,
    prefix="/cases",
    tags=["案例详情"]
)

api_router.include_router(
    case_permissions.router,
    prefix="/cases",
    tags=["案例权限"]
)

# 导师相关路由
api_router.include_router(
    tutors.router,
    prefix="/tutors",
    tags=["导师管理"]
)

api_router.include_router(
    tutor_details.router,
    prefix="/tutors",
    tags=["导师详情"]
) 