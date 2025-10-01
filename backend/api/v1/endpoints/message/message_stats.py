from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.message import UnreadStatsResponse
from services.message.message_stat_service import message_stat_service

router = APIRouter()

@router.get("/unread-stats", response_model=UnreadStatsResponse)
async def get_unread_stats(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取各类型消息的未读数量（用于标签页徽章显示）"""
    try:
        unread_stats = message_stat_service.calculate_unread_stats(db, current_user_id)
        return unread_stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取未读统计失败: {str(e)}")

@router.get("/overview")
async def get_message_overview(
    days: int = Query(7, ge=1, le=90, description="统计天数"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息概览统计"""
    try:
        overview = message_stat_service.get_message_overview(db, current_user_id, days)
        return overview
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息概览失败: {str(e)}")

@router.get("/activity-analysis")
async def get_activity_analysis(
    days: int = Query(30, ge=7, le=90, description="分析天数"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息活动分析"""
    try:
        analysis = message_stat_service.get_message_activity_analysis(db, current_user_id, days)
        return analysis
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取活动分析失败: {str(e)}")

@router.get("/type-stats")
async def get_type_stats(
    days: int = Query(30, ge=1, le=90, description="统计天数"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取详细的消息类型统计"""
    try:
        type_stats = message_stat_service.get_detailed_type_stats(db, current_user_id, days)
        return type_stats
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取类型统计失败: {str(e)}")

@router.get("/dashboard")
async def get_message_dashboard(
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息仪表板数据（综合统计）"""
    try:
        # 获取未读统计
        unread_stats = message_stat_service.calculate_unread_stats(db, current_user_id)
        
        # 获取7天概览
        weekly_overview = message_stat_service.get_message_overview(db, current_user_id, days=7)
        
        # 获取30天类型统计
        type_stats = message_stat_service.get_detailed_type_stats(db, current_user_id, days=30)
        
        # 获取活动分析
        activity_analysis = message_stat_service.get_message_activity_analysis(db, current_user_id, days=30)
        
        return {
            "user_id": current_user_id,
            "unread_stats": unread_stats.dict(),
            "weekly_overview": weekly_overview,
            "monthly_type_stats": type_stats,
            "activity_analysis": {
                "peak_hours": activity_analysis["peak_hours"],
                "trend_analysis": activity_analysis["trend_analysis"],
                "recommendations": activity_analysis["recommendations"]
            },
            "summary": {
                "total_unread": unread_stats.total_count,
                "weekly_total": weekly_overview["period_stats"]["total_messages"],
                "read_rate": weekly_overview["period_stats"]["read_rate"],
                "response_rate": weekly_overview["response_stats"]["response_rate"],
                "most_active_type": weekly_overview["summary"]["most_active_type"],
                "peak_activity_hour": activity_analysis["peak_hours"]["peak_hour"]
            }
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息仪表板失败: {str(e)}")

@router.get("/trends")
async def get_message_trends(
    period: str = Query("week", description="趋势周期：week/month"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取消息趋势数据"""
    try:
        days = 30 if period == "month" else 7
        
        # 获取活动趋势
        activity_analysis = message_stat_service.get_message_activity_analysis(db, current_user_id, days)
        
        # 获取类型统计趋势
        type_stats = message_stat_service.get_detailed_type_stats(db, current_user_id, days)
        
        return {
            "period": period,
            "days": days,
            "activity_trend": activity_analysis["activity_trend"],
            "trend_analysis": activity_analysis["trend_analysis"],
            "type_distribution": type_stats["type_percentages"],
            "recommendations": activity_analysis["recommendations"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取消息趋势失败: {str(e)}")

@router.get("/health")
async def health_check():
    """消息统计服务健康检查"""
    return {"status": "healthy", "service": "message_stat_service"} 