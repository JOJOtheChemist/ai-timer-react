from fastapi import APIRouter, HTTPException
from datetime import datetime

router = APIRouter()

# 模拟用户数据
mock_users = [
    {
        "id": 1,
        "username": "学习者001",
        "email": "user1@example.com",
        "level": 5,
        "total_study_hours": 128,
        "completed_tasks": 256,
        "streak_days": 15,
        "ranking": 23,
        "created_at": "2023-11-01T00:00:00"
    }
]

@router.post("/auth/login")
async def login(credentials: dict):
    """用户登录"""
    # 简化的登录逻辑
    email = credentials.get("email")
    password = credentials.get("password")
    
    # 模拟验证
    if email and password:
        user = mock_users[0]  # 返回第一个用户
        return {
            "token": "mock_jwt_token_12345",
            "user": user,
            "message": "登录成功"
        }
    
    raise HTTPException(status_code=401, detail="用户名或密码错误")

@router.post("/auth/register")
async def register(user_data: dict):
    """用户注册"""
    new_user = {
        "id": len(mock_users) + 1,
        "username": user_data.get("username"),
        "email": user_data.get("email"),
        "level": 1,
        "total_study_hours": 0,
        "completed_tasks": 0,
        "streak_days": 0,
        "ranking": 999,
        "created_at": datetime.now().isoformat()
    }
    
    mock_users.append(new_user)
    return {"message": "注册成功", "user": new_user}

@router.get("/{user_id}")
async def get_user_profile(user_id: int):
    """获取用户详细信息"""
    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {"user": user}

@router.get("/{user_id}/stats")
async def get_user_stats(user_id: int):
    """获取用户学习统计"""
    user = next((u for u in mock_users if u["id"] == user_id), None)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    
    return {
        "total_study_hours": user["total_study_hours"],
        "completed_tasks": user["completed_tasks"],
        "streak_days": user["streak_days"],
        "level": user["level"],
        "ranking": user["ranking"],
        "weekly_hours": 25,  # 模拟数据
        "monthly_hours": 98,
        "achievements": ["坚持学习", "高效学习者", "时间管理大师"]
    }

@router.get("/leaderboard")
async def get_leaderboard(type: str = "weekly", limit: int = 100):
    """获取排行榜数据"""
    # 模拟排行榜数据
    leaderboard = [
        {"rank": 1, "username": "学习达人", "score": 1250, "avatar": "👨‍🎓"},
        {"rank": 2, "username": "时间管理者", "score": 1180, "avatar": "👩‍💼"},
        {"rank": 3, "username": "效率专家", "score": 1120, "avatar": "🧑‍💻"},
        {"rank": 23, "username": "学习者001", "score": 890, "avatar": "👤"},
    ]
    
    return {
        "leaderboard": leaderboard[:limit],
        "type": type,
        "total": len(leaderboard)
    } 