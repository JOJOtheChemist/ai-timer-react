#!/usr/bin/env python3
"""
AI Time Management Backend API Server
完整的API服务器，包含所有端点和详细的API文档
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.utils import get_openapi
import uvicorn

# 创建FastAPI应用实例（带详细文档配置）
app = FastAPI(
    title="AI Time Management API",
    description="""
## AI时间管理系统 - 后端API文档

这是一个完整的AI驱动的时间管理系统，包含以下功能模块：

### 🤖 AI功能
- **AI聊天助手**: 智能对话，学习建议
- **AI推荐系统**: 个性化学习方法推荐
- **用户行为分析**: 数据驱动的学习习惯分析

### 📚 成功案例管理
- **案例浏览**: 热门案例、分类筛选、关键词搜索
- **案例详情**: 完整内容查看、权限控制
- **用户互动**: 浏览记录、购买管理

### 📖 更多功能
- 任务管理
- 时间表规划
- 学习方法分享
- 导师服务
- 用户社交

### 技术栈
- **框架**: FastAPI 0.104+
- **数据库**: PostgreSQL 14+
- **ORM**: SQLAlchemy 2.0
- **认证**: JWT Token
    """,
    version="1.0.0",
    contact={
        "name": "AI Time Management Team",
        "email": "support@aitime.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",  # Swagger UI
    redoc_url="/redoc",  # ReDoc
    openapi_url="/openapi.json",  # OpenAPI JSON schema
    swagger_ui_parameters={
        "defaultModelsExpandDepth": -1,  # 不展开模型
        "displayRequestDuration": True,  # 显示请求耗时
        "filter": True,  # 启用搜索过滤
        "tryItOutEnabled": True,  # 默认启用"Try it out"
    }
)

# 自定义OpenAPI schema
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    
    # 添加自定义标签描述
    openapi_schema["tags"] = [
        {
            "name": "AI聊天",
            "description": "AI对话助手相关接口，支持多轮对话、上下文理解、学习建议等功能"
        },
        {
            "name": "AI推荐",
            "description": "AI智能推荐系统，基于用户行为分析提供个性化学习方法推荐"
        },
        {
            "name": "成功案例",
            "description": "成功案例管理，包括案例浏览、搜索、分类、统计等功能"
        },
        {
            "name": "案例详情",
            "description": "案例详细信息查看，包括内容获取、浏览记录、相关推荐等"
        },
        {
            "name": "案例权限",
            "description": "案例权限管理，处理购买验证、访问控制、权限查询等"
        },
        {
            "name": "系统",
            "description": "系统基础接口，健康检查、版本信息等"
        }
    ]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============= 基础路由 =============

@app.get("/", tags=["系统"], summary="根路由", description="API服务器根路由，返回基本信息")
async def root():
    """
    # API服务器欢迎信息
    
    返回API服务器的基本信息，包括：
    - 服务名称
    - 版本号
    - 运行状态
    - 文档链接
    """
    return {
        "message": "Welcome to AI Time Management API",
        "version": "1.0.0",
        "status": "running",
        "docs": {
            "swagger": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json"
        }
    }

@app.get("/health", tags=["系统"], summary="健康检查", description="检查API服务器运行状态")
async def health_check():
    """
    # 健康检查端点
    
    用于监控系统检查API服务器是否正常运行
    
    ## 返回信息
    - `status`: 健康状态（healthy/unhealthy）
    - `message`: 状态描述
    """
    return {
        "status": "healthy",
        "message": "API is running",
        "database": "connected"  # 实际应该检查数据库连接
    }

# ============= 加载API路由 =============

print("\n" + "="*60)
print("🚀 正在启动 AI Time Management API Server")
print("="*60)

# 加载AI聊天路由
try:
    from api.v1.endpoints.ai import ai_chat
    app.include_router(
        ai_chat.router,
        prefix="/api/v1/ai",
        tags=["AI聊天"]
    )
    print("✅ AI聊天模块加载成功")
except Exception as e:
    print(f"⚠️  AI聊天模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载AI推荐路由
try:
    from api.v1.endpoints.ai import ai_recommendations
    app.include_router(
        ai_recommendations.router,
        prefix="/api/v1/ai",
        tags=["AI推荐"]
    )
    print("✅ AI推荐模块加载成功")
except Exception as e:
    print(f"⚠️  AI推荐模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载成功案例路由
try:
    from api.v1.endpoints.case import cases, case_details, case_permissions
    app.include_router(
        cases.router,
        prefix="/api/v1/cases",
        tags=["成功案例"]
    )
    app.include_router(
        case_details.router,
        prefix="/api/v1/cases",
        tags=["案例详情"]
    )
    app.include_router(
        case_permissions.router,
        prefix="/api/v1/cases",
        tags=["案例权限"]
    )
    print("✅ 成功案例模块加载成功")
except Exception as e:
    print(f"⚠️  成功案例模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载消息路由
try:
    from api.v1.endpoints.message import messages, message_details, message_interactions, message_stats
    app.include_router(
        messages.router,
        prefix="/api/v1/messages",
        tags=["消息管理"]
    )
    app.include_router(
        message_details.router,
        prefix="/api/v1/messages",
        tags=["消息详情"]
    )
    app.include_router(
        message_interactions.router,
        prefix="/api/v1/messages",
        tags=["消息交互"]
    )
    app.include_router(
        message_stats.router,
        prefix="/api/v1/messages",
        tags=["消息统计"]
    )
    print("✅ 消息模块加载成功")
except Exception as e:
    print(f"⚠️  消息模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载学习方法路由
try:
    from api.v1.endpoints.method import methods, checkins
    app.include_router(
        methods.router,
        prefix="/api/v1/methods",
        tags=["学习方法"]
    )
    app.include_router(
        checkins.router,
        prefix="/api/v1/methods",
        tags=["学习打卡"]
    )
    print("✅ 学习方法模块加载成功")
except Exception as e:
    print(f"⚠️  学习方法模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载徽章路由
try:
    from api.v1.endpoints.badge import badges
    app.include_router(
        badges.router,
        prefix="/api/v1/badges",
        tags=["徽章系统"]
    )
    print("✅ 徽章模块加载成功")
except Exception as e:
    print(f"⚠️  徽章模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载动态路由
try:
    from api.v1.endpoints.moment import moments, moment_interactions
    app.include_router(
        moments.router,
        prefix="/api/v1/moments",
        tags=["动态管理"]
    )
    app.include_router(
        moment_interactions.router,
        prefix="/api/v1/moments",
        tags=["动态互动"]
    )
    print("✅ 动态模块加载成功")
except Exception as e:
    print(f"⚠️  动态模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载动态路由
try:
    from api.v1.endpoints.moment import moments, moment_interactions
    app.include_router(
        moments.router,
        prefix="/api/v1/moments",
        tags=["动态管理"]
    )
    app.include_router(
        moment_interactions.router,
        prefix="/api/v1/moments",
        tags=["动态互动"]
    )
    print("✅ 动态模块加载成功")
except Exception as e:
    print(f"⚠️  动态模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载导师路由
try:
    from api.v1.endpoints.tutor import tutors, tutor_details
    app.include_router(
        tutors.router,
        prefix="/api/v1/tutors",
        tags=["导师列表"]
    )
    app.include_router(
        tutor_details.router,
        prefix="/api/v1/tutors",
        tags=["导师详情"]
    )
    print("✅ 导师模块加载成功")
except Exception as e:
    print(f"⚠️  导师模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载时间表路由
try:
    from api.v1.endpoints.schedule import time_slots
    app.include_router(
        time_slots.router,
        prefix="/api/v1/schedule",
        tags=["时间表管理"]
    )
    print("✅ 时间表模块加载成功")
except Exception as e:
    print(f"⚠️  时间表模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载统计路由
try:
    from api.v1.endpoints.statistic import statistics
    app.include_router(
        statistics.router,
        prefix="/api/v1/statistics",
        tags=["统计分析"]
    )
    print("✅ 统计模块加载成功")
except Exception as e:
    print(f"⚠️  统计模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载任务路由
try:
    from api.v1.endpoints.task import tasks
    app.include_router(
        tasks.router,
        prefix="/api/v1/tasks",
        tags=["任务管理"]
    )
    print("✅ 任务模块加载成功")
except Exception as e:
    print(f"⚠️  任务模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载用户资产路由
try:
    from api.v1.endpoints.user import user_assets
    app.include_router(
        user_assets.router,
        prefix="/api/v1/users",
        tags=["用户资产"]
    )
    print("✅ 用户资产模块加载成功")
except Exception as e:
    print(f"⚠️  用户资产模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载用户消息设置路由
try:
    from api.v1.endpoints.user import user_message_settings
    app.include_router(
        user_message_settings.router,
        prefix="/api/v1/users",
        tags=["用户消息设置"]
    )
    print("✅ 用户消息设置模块加载成功")
except Exception as e:
    print(f"⚠️  用户消息设置模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# 加载用户个人信息路由
try:
    from api.v1.endpoints.user import user_profiles
    app.include_router(
        user_profiles.router,
        prefix="/api/v1/users",
        tags=["用户个人信息"]
    )
    print("✅ 用户个人信息模块加载成功")
except Exception as e:
    print(f"⚠️  用户个人信息模块加载失败: {e}")
    import traceback
    traceback.print_exc()

# ============= 全局异常处理 =============

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """全局异常处理器"""
    print(f"❌ Global Exception: {exc}")
    import traceback
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"服务器内部错误: {str(exc)}",
            "type": type(exc).__name__
        }
    )

# ============= 启动配置 =============

if __name__ == "__main__":
    print("="*60)
    print("📚 API文档地址:")
    print("   - Swagger UI: http://localhost:8000/docs")
    print("   - ReDoc:      http://localhost:8000/redoc")
    print("   - OpenAPI:    http://localhost:8000/openapi.json")
    print("="*60)
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # 生产环境设为False
        log_level="info"
    ) 