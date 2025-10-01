from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date

from core.dependencies import get_db_and_user
from services.schedule.time_slot_service import time_slot_service
from models.schemas.schedule import TodayScheduleResponse
from models.schemas.task import (
    TimeSlotCreate, TimeSlotUpdate, TimeSlotResponse, 
    MoodCreate, MoodResponse, TaskSlotBinding, TaskOperationResponse,
    TaskStatus, MoodType
)

router = APIRouter()

@router.get("/time-slots", response_model=TodayScheduleResponse)
async def get_time_slots(
    target_date: Optional[date] = Query(None, description="目标日期，默认为今天"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取今日时间表
    
    - **target_date**: 目标日期，默认为今天
    """
    db, user_id = db_and_user
    
    try:
        return time_slot_service.get_today_time_slots(
            db=db, user_id=user_id, target_date=target_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取时间表失败: {str(e)}")

@router.post("/time-slots", response_model=TimeSlotResponse)
async def create_time_slot(
    slot_data: TimeSlotCreate,
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    创建时间段
    
    - **slot_data**: 时间段创建数据
    """
    db, user_id = db_and_user
    
    try:
        return time_slot_service.create_time_slot(db=db, user_id=user_id, slot_data=slot_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建时间段失败: {str(e)}")

@router.patch("/time-slots/{slot_id}", response_model=TimeSlotResponse)
async def update_time_slot(
    slot_data: TimeSlotUpdate,
    slot_id: int = Path(..., description="时间段ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    更新时间段
    
    - **slot_id**: 时间段ID
    - **slot_data**: 时间段更新数据
    """
    db, user_id = db_and_user
    
    slot = time_slot_service.update_time_slot(
        db=db, slot_id=slot_id, user_id=user_id, slot_data=slot_data
    )
    if not slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    return slot

@router.post("/time-slots/{slot_id}/mood", response_model=MoodResponse)
async def save_mood_record(
    mood_data: MoodCreate,
    slot_id: int = Path(..., description="时间段ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    提交时段心情记录
    
    - **slot_id**: 时间段ID
    - **mood_data**: 心情数据
    """
    db, user_id = db_and_user
    
    # 验证slot_id是否匹配
    if mood_data.time_slot_id != slot_id:
        raise HTTPException(status_code=400, detail="时间段ID不匹配")
    
    try:
        return time_slot_service.save_mood_record(
            db=db, user_id=user_id, slot_id=slot_id, mood=mood_data.mood
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"保存心情记录失败: {str(e)}")

@router.post("/time-slots/{slot_id}/task", response_model=TimeSlotResponse)
async def add_task_to_slot(
    task_binding: TaskSlotBinding,
    slot_id: int = Path(..., description="时间段ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    为空白时段添加任务
    
    - **slot_id**: 时间段ID
    - **task_binding**: 任务绑定数据
    """
    db, user_id = db_and_user
    
    if not task_binding.task_id:
        raise HTTPException(status_code=400, detail="任务ID不能为空")
    
    try:
        slot = time_slot_service.add_task_to_slot(
            db=db, 
            user_id=user_id, 
            slot_id=slot_id, 
            task_id=task_binding.task_id,
            subtask_id=task_binding.subtask_id
        )
        if not slot:
            raise HTTPException(status_code=404, detail="时间段不存在")
        
        return slot
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"绑定任务失败: {str(e)}")

@router.patch("/time-slots/batch/status", response_model=TaskOperationResponse)
async def batch_update_status(
    slot_ids: List[int] = Query(..., description="时间段ID列表"),
    status: TaskStatus = Query(..., description="目标状态"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    批量更新时间段状态
    
    - **slot_ids**: 时间段ID列表
    - **status**: 目标状态
    """
    db, user_id = db_and_user
    
    try:
        updated_count = time_slot_service.batch_update_status(
            db=db, user_id=user_id, slot_ids=slot_ids, status=status
        )
        
        return TaskOperationResponse(
            success=True,
            message=f"成功更新 {updated_count} 个时间段状态",
            data={
                "updated_count": updated_count,
                "status": status.value
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量更新失败: {str(e)}")

@router.get("/time-slots/completion-stats")
async def get_completion_stats(
    target_date: Optional[date] = Query(None, description="目标日期，默认为今天"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取完成情况统计
    
    - **target_date**: 目标日期，默认为今天
    """
    db, user_id = db_and_user
    
    try:
        stats = time_slot_service.get_completion_stats(
            db=db, user_id=user_id, target_date=target_date
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取完成统计成功",
            data=stats
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计失败: {str(e)}")

@router.get("/time-slots/ai-recommended", response_model=List[TimeSlotResponse])
async def get_ai_recommended_slots(
    target_date: Optional[date] = Query(None, description="目标日期，默认为今天"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取AI推荐的时间段
    
    - **target_date**: 目标日期，默认为今天
    """
    db, user_id = db_and_user
    
    try:
        return time_slot_service.get_ai_recommended_slots(
            db=db, user_id=user_id, target_date=target_date
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取AI推荐失败: {str(e)}")

# 快捷操作接口
@router.patch("/time-slots/{slot_id}/complete", response_model=TimeSlotResponse)
async def complete_time_slot(
    slot_id: int = Path(..., description="时间段ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    快捷完成时间段
    
    - **slot_id**: 时间段ID
    """
    db, user_id = db_and_user
    
    slot_data = TimeSlotUpdate(status=TaskStatus.COMPLETED)
    slot = time_slot_service.update_time_slot(
        db=db, slot_id=slot_id, user_id=user_id, slot_data=slot_data
    )
    if not slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    return slot

@router.patch("/time-slots/{slot_id}/start", response_model=TimeSlotResponse)
async def start_time_slot(
    slot_id: int = Path(..., description="时间段ID"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    开始时间段
    
    - **slot_id**: 时间段ID
    """
    db, user_id = db_and_user
    
    slot_data = TimeSlotUpdate(status=TaskStatus.IN_PROGRESS)
    slot = time_slot_service.update_time_slot(
        db=db, slot_id=slot_id, user_id=user_id, slot_data=slot_data
    )
    if not slot:
        raise HTTPException(status_code=404, detail="时间段不存在")
    
    return slot

# 健康检查
@router.get("/health/check")
async def schedule_health_check():
    """时间表服务健康检查"""
    return TaskOperationResponse(
        success=True,
        message="时间表服务正常运行",
        data={
            "service": "schedule",
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    ) 