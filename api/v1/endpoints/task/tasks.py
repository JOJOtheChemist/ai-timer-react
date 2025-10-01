from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List

from core.dependencies import get_db_and_user
from services.task.task_service import task_service
from models.schemas.task import (
    TaskCreate, TaskUpdate, TaskQuickCreate, TaskListResponse,
    TaskResponse, TaskOperationResponse, TaskType
)

router = APIRouter()

@router.get("", response_model=TaskListResponse)
async def get_tasks(
    category: Optional[str] = Query(None, description="任务分类筛选"),
    task_type: Optional[TaskType] = Query(None, description="任务类型筛选"),
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(20, ge=1, le=100, description="每页大小"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取任务列表
    
    - **category**: 任务分类筛选（可选）
    - **task_type**: 任务类型筛选（可选）
    - **skip**: 跳过数量
    - **limit**: 每页大小
    """
    db, user_id = db_and_user
    
    try:
        return task_service.get_task_list(
            db=db,
            user_id=user_id,
            category=category,
            task_type=task_type,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务列表失败: {str(e)}")

@router.post("", response_model=TaskResponse)
async def create_task(
    task_data: TaskCreate,
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    创建新任务
    
    - **task_data**: 任务创建数据
    """
    db, user_id = db_and_user
    
    try:
        return task_service.create_task(db=db, user_id=user_id, task_data=task_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建任务失败: {str(e)}")

@router.post("/quick-add", response_model=TaskResponse)
async def quick_add_task(
    task_data: TaskQuickCreate,
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    快捷创建任务
    
    - **task_data**: 快捷任务创建数据
    """
    db, user_id = db_and_user
    
    try:
        return task_service.quick_create_task(
            db=db, 
            user_id=user_id, 
            task_name=task_data.name,
            task_type=task_data.type
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"快捷创建任务失败: {str(e)}")

@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: int = Path(..., description="任务ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    根据ID获取任务详情
    
    - **task_id**: 任务ID
    """
    db, user_id = db_and_user
    
    task = task_service.get_task_by_id(db=db, task_id=task_id, user_id=user_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task

@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_data: TaskUpdate,
    task_id: int = Path(..., description="任务ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    更新任务
    
    - **task_id**: 任务ID
    - **task_data**: 任务更新数据
    """
    db, user_id = db_and_user
    
    task = task_service.update_task(db=db, task_id=task_id, user_id=user_id, task_data=task_data)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task

@router.patch("/{task_id}/expand", response_model=TaskResponse)
async def update_task_expand_status(
    task_id: int = Path(..., description="任务ID"),
    is_expand: bool = Query(..., description="是否展开子任务"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    更新任务展开状态
    
    - **task_id**: 任务ID
    - **is_expand**: 是否展开子任务
    """
    db, user_id = db_and_user
    
    task = task_service.update_task_expand_status(
        db=db, user_id=user_id, task_id=task_id, is_expand=is_expand
    )
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return task

@router.delete("/{task_id}", response_model=TaskOperationResponse)
async def delete_task(
    task_id: int = Path(..., description="任务ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    删除任务
    
    - **task_id**: 任务ID
    """
    db, user_id = db_and_user
    
    success = task_service.delete_task(db=db, task_id=task_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return TaskOperationResponse(
        success=True,
        message="任务删除成功",
        data={"task_id": task_id}
    )

@router.get("/high-frequency/list", response_model=List[TaskResponse])
async def get_high_frequency_tasks(
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取高频任务列表
    """
    db, user_id = db_and_user
    
    try:
        return task_service.get_high_frequency_tasks(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取高频任务失败: {str(e)}")

@router.get("/overcome/list", response_model=List[TaskResponse])
async def get_overcome_tasks(
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取待克服任务列表
    """
    db, user_id = db_and_user
    
    try:
        return task_service.get_overcome_tasks(db=db, user_id=user_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取待克服任务失败: {str(e)}")

@router.get("/statistics/overview")
async def get_task_statistics(
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取任务统计概览
    """
    db, user_id = db_and_user
    
    try:
        stats = task_service.get_task_statistics(db=db, user_id=user_id)
        return TaskOperationResponse(
            success=True,
            message="获取统计信息成功",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

# 健康检查
@router.get("/health/check")
async def task_health_check():
    """任务服务健康检查"""
    return TaskOperationResponse(
        success=True,
        message="任务服务正常运行",
        data={
            "service": "task",
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    ) 