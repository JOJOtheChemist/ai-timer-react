from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from core.dependencies import get_db_and_user
from services.statistic.statistic_service import statistic_service
from models.schemas.statistic import (
    WeeklyOverviewResponse, WeeklyChartResponse
)
from models.schemas.task import TaskOperationResponse

router = APIRouter()

@router.get("/weekly-overview", response_model=WeeklyOverviewResponse)
async def get_weekly_overview(
    year_week: Optional[str] = Query(None, description="年周，如'2025-01'，默认为当前周"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取本周统计概览
    
    - **year_week**: 年周，如'2025-01'，默认为当前周
    """
    db, user_id = db_and_user
    
    try:
        return statistic_service.calculate_weekly_overview(
            db=db, user_id=user_id, year_week=year_week
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取周统计失败: {str(e)}")

@router.get("/weekly-chart", response_model=WeeklyChartResponse)
async def get_weekly_chart(
    year_week: Optional[str] = Query(None, description="年周，如'2025-01'，默认为当前周"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取本周时间分布图表数据
    
    - **year_week**: 年周，如'2025-01'，默认为当前周
    """
    db, user_id = db_and_user
    
    try:
        return statistic_service.generate_weekly_chart_data(
            db=db, user_id=user_id, year_week=year_week
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取图表数据失败: {str(e)}")

@router.get("/weekly-task-hours")
async def get_weekly_task_hours(
    year_week: Optional[str] = Query(None, description="年周，如'2025-01'，默认为当前周"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取本周各任务时长统计
    
    - **year_week**: 年周，如'2025-01'，默认为当前周
    """
    db, user_id = db_and_user
    
    try:
        task_hours = statistic_service.get_weekly_task_hours(
            db=db, user_id=user_id, year_week=year_week
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取任务时长统计成功",
            data=task_hours
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取任务时长统计失败: {str(e)}")

@router.get("/weekly-category-hours")
async def get_weekly_category_hours(
    year_week: Optional[str] = Query(None, description="年周，如'2025-01'，默认为当前周"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取本周各类型任务时长统计
    
    - **year_week**: 年周，如'2025-01'，默认为当前周
    """
    db, user_id = db_and_user
    
    try:
        category_hours = statistic_service.get_weekly_category_hours(
            db=db, user_id=user_id, year_week=year_week
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取分类时长统计成功",
            data=category_hours
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分类时长统计失败: {str(e)}")

@router.get("/efficiency-analysis")
async def get_efficiency_analysis(
    days: int = Query(7, ge=1, le=30, description="分析天数"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取效率分析
    
    - **days**: 分析天数，默认7天
    """
    db, user_id = db_and_user
    
    try:
        analysis = statistic_service.get_efficiency_analysis(
            db=db, user_id=user_id, days=days
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取效率分析成功",
            data=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取效率分析失败: {str(e)}")

@router.get("/mood-trend")
async def get_mood_trend_analysis(
    days: int = Query(7, ge=1, le=30, description="分析天数"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取心情趋势分析
    
    - **days**: 分析天数，默认7天
    """
    db, user_id = db_and_user
    
    try:
        analysis = statistic_service.get_mood_trend_analysis(
            db=db, user_id=user_id, days=days
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取心情趋势分析成功",
            data=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取心情趋势分析失败: {str(e)}")

@router.get("/comparison")
async def get_comparison_analysis(
    current_week: str = Query(..., description="当前周，如'2025-01'"),
    previous_week: str = Query(..., description="对比周，如'2024-52'"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取周对比分析
    
    - **current_week**: 当前周，如'2025-01'
    - **previous_week**: 对比周，如'2024-52'
    """
    db, user_id = db_and_user
    
    try:
        analysis = statistic_service.get_comparison_analysis(
            db=db, user_id=user_id, current_week=current_week, previous_week=previous_week
        )
        
        return TaskOperationResponse(
            success=True,
            message="获取对比分析成功",
            data=analysis
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取对比分析失败: {str(e)}")

@router.get("/dashboard")
async def get_dashboard_data(
    year_week: Optional[str] = Query(None, description="年周，如'2025-01'，默认为当前周"),
    db_and_user: tuple[Session, int] = Depends(get_db_and_user)
):
    """
    获取首页仪表盘数据（综合统计）
    
    - **year_week**: 年周，如'2025-01'，默认为当前周
    """
    db, user_id = db_and_user
    
    try:
        # 获取周概览
        overview = statistic_service.calculate_weekly_overview(
            db=db, user_id=user_id, year_week=year_week
        )
        
        # 获取图表数据
        chart_data = statistic_service.generate_weekly_chart_data(
            db=db, user_id=user_id, year_week=year_week
        )
        
        # 获取效率分析
        efficiency = statistic_service.get_efficiency_analysis(
            db=db, user_id=user_id, days=7
        )
        
        # 获取心情趋势
        mood_trend = statistic_service.get_mood_trend_analysis(
            db=db, user_id=user_id, days=7
        )
        
        dashboard_data = {
            "overview": overview,
            "charts": chart_data,
            "efficiency": efficiency,
            "mood_trend": mood_trend,
            "last_updated": "2025-01-01T00:00:00Z"
        }
        
        return TaskOperationResponse(
            success=True,
            message="获取仪表盘数据成功",
            data=dashboard_data
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取仪表盘数据失败: {str(e)}")

# 健康检查
@router.get("/health/check")
async def statistics_health_check():
    """统计服务健康检查"""
    return TaskOperationResponse(
        success=True,
        message="统计服务正常运行",
        data={
            "service": "statistics",
            "status": "healthy",
            "timestamp": "2025-01-01T00:00:00Z"
        }
    ) 