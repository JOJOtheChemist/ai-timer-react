#!/usr/bin/env python3
"""
简化的测试服务器 - 仅用于测试AI相关API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 创建FastAPI应用实例
app = FastAPI(
    title="AI Time Backend API - Test Server",
    description="AI API测试服务器",
    version="1.0.0"
)

# 配置CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路由
@app.get("/")
async def root():
    return {"message": "AI API Test Server", "version": "1.0.0", "status": "running"}

# 健康检查路由
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# 只导入AI相关的路由
try:
    from api.v1.endpoints.ai import ai_chat
    app.include_router(ai_chat.router, prefix="/api/v1/ai", tags=["AI聊天"])
    print("✅ AI Chat router loaded")
except Exception as e:
    print(f"⚠️  Failed to load AI Chat router: {e}")
    import traceback
    traceback.print_exc()

try:
    from api.v1.endpoints.ai import ai_recommendations
    app.include_router(ai_recommendations.router, prefix="/api/v1/ai", tags=["AI推荐"])
    print("✅ AI Recommendations router loaded")
except Exception as e:
    print(f"⚠️  Failed to load AI Recommendations router: {e}")
    import traceback
    traceback.print_exc()

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# 启动应用
if __name__ == "__main__":
    print("=" * 60)
    print("🚀 启动AI API测试服务器")
    print("=" * 60)
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
        log_level="info"
    ) 