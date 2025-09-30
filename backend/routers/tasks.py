from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from datetime import datetime, date

router = APIRouter()

# 模拟数据库数据
mock_tasks = [
    {
        "id": 1,
        "title": "数学复习",
        "description": "复习高等数学第一章",
        "status": "completed",
        "category": "学习",
        "duration": 120,
        "priority": "high",
        "tags": ["数学", "复习"],
        "user_id": 1,
        "date": "2023-12-01",
        "created_at": "2023-12-01T10:00:00"
    },
    {
        "id": 2,
        "title": "英语阅读",
        "description": "阅读英语文章并做笔记",
        "status": "in-progress",
        "category": "学习",
        "duration": 60,
        "priority": "medium",
        "tags": ["英语", "阅读"],
        "user_id": 1,
        "date": "2023-12-01",
        "created_at": "2023-12-01T14:00:00"
    }
]

@router.get("/{user_id}")
async def get_tasks(user_id: int):
    """获取用户的任务列表"""
    user_tasks = [task for task in mock_tasks if task["user_id"] == user_id]
    return {"tasks": user_tasks, "total": len(user_tasks)}

@router.post("/")
async def create_task(task_data: dict):
    """创建新任务"""
    new_task = {
        "id": len(mock_tasks) + 1,
        "created_at": datetime.now().isoformat(),
        "user_id": task_data.get("user_id", 1),
        **task_data
    }
    mock_tasks.append(new_task)
    return {"message": "任务创建成功", "task": new_task}

@router.put("/{task_id}/status")
async def update_task_status(task_id: int, status_data: dict):
    """更新任务状态"""
    for task in mock_tasks:
        if task["id"] == task_id:
            task["status"] = status_data["status"]
            return {"message": "任务状态更新成功", "task": task}
    
    raise HTTPException(status_code=404, detail="任务不存在")

@router.get("/stats/{user_id}")
async def get_task_stats(user_id: int, range: str = "week"):
    """获取任务统计数据"""
    user_tasks = [task for task in mock_tasks if task["user_id"] == user_id]
    
    completed_tasks = len([task for task in user_tasks if task["status"] == "completed"])
    total_duration = sum(task.get("duration", 0) for task in user_tasks if task["status"] == "completed")
    
    return {
        "completed_tasks": completed_tasks,
        "total_duration": total_duration,
        "average_duration": total_duration / max(completed_tasks, 1),
        "range": range
    }

@router.get("/heatmap/{user_id}")
async def get_heatmap_data(user_id: int, start: str, end: str):
    """获取热力图数据"""
    # 模拟热力图数据
    heatmap_data = []
    start_date = datetime.strptime(start, "%Y-%m-%d")
    end_date = datetime.strptime(end, "%Y-%m-%d")
    
    current_date = start_date
    while current_date <= end_date:
        # 模拟每日学习强度数据
        intensity = min(4, len([task for task in mock_tasks 
                               if task["user_id"] == user_id and 
                               task["date"] == current_date.strftime("%Y-%m-%d")]))
        
        heatmap_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "intensity": intensity,
            "tasks_completed": intensity
        })
        
        current_date = current_date.replace(day=current_date.day + 1)
    
    return {"heatmap_data": heatmap_data} 