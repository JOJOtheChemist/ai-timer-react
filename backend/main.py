from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# 导入路由模块
from routers import tasks, users, ai, tutors

# 创建FastAPI应用实例
app = FastAPI(
    title="AI Time Backend API",
    description="AI时间管理系统后端API",
    version="1.0.0"
)

# 配置CORS中间件，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 根路由
@app.get("/")
async def root():
    return {"message": "AI Time Backend API", "version": "1.0.0"}

# 健康检查路由
@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

# 注册路由模块
app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
app.include_router(tutors.router, prefix="/api/tutors", tags=["tutors"])

# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error", "detail": str(exc)}
    )

# 启动应用
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    ) 