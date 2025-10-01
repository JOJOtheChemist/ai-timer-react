from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, cast, Date, extract
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import calendar

from models.statistic import StatisticWeekly, StatisticDaily
from models.task import TimeSlot, Task, MoodRecord
from models.schemas.statistic import WeeklyOverviewResponse, CategoryHours, DailyHours

class CRUDStatistic:
    """统计CRUD操作"""
    
    def get_weekly_task_hours(self, db: Session, user_id: int, year_week: Optional[str] = None) -> Dict[str, float]:
        """获取用户本周各任务时长"""
        if year_week is None:
            # 计算当前周
            today = date.today()
            year, week, _ = today.isocalendar()
            year_week = f"{year}-{week:02d}"
        
        # 计算周的开始和结束日期
        year, week = map(int, year_week.split('-'))
        start_date = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w").date()
        end_date = start_date + timedelta(days=6)
        
        # 查询时间段数据，关联任务信息
        from sqlalchemy import case
        results = db.query(
            Task.name.label('task_name'),
            Task.type.label('task_type'),
            func.count(TimeSlot.id).label('slot_count'),
            func.sum(
                case(
                    (TimeSlot.status == 'completed', 1.0),
                    else_=0.0
                )
            ).label('completed_hours')
        ).join(Task, TimeSlot.task_id == Task.id)\
         .filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date
            )
        ).group_by(Task.name, Task.type).all()
        
        task_hours = {}
        for result in results:
            task_hours[result.task_name] = float(result.completed_hours or 0.0)
        
        return task_hours
    
    def get_weekly_category_hours(self, db: Session, user_id: int, year_week: Optional[str] = None) -> Dict[str, float]:
        """获取用户本周各类型任务总时长"""
        if year_week is None:
            today = date.today()
            year, week, _ = today.isocalendar()
            year_week = f"{year}-{week:02d}"
        
        year, week = map(int, year_week.split('-'))
        start_date = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w").date()
        end_date = start_date + timedelta(days=6)
        
        # 使用case语句来计算完成的时长
        from sqlalchemy import case
        
        results = db.query(
            Task.type.label('task_type'),
            func.sum(
                case(
                    (TimeSlot.status == 'completed', 1.0),
                    else_=0.0
                )
            ).label('total_hours')
        ).join(Task, TimeSlot.task_id == Task.id)\
         .filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date
            )
        ).group_by(Task.type).all()
        
        category_hours = {}
        for result in results:
            category_hours[result.task_type] = float(result.total_hours or 0.0)
        
        return category_hours
    
    def calculate_weekly_overview(self, db: Session, user_id: int, year_week: Optional[str] = None) -> WeeklyOverviewResponse:
        """计算本周统计概览"""
        if year_week is None:
            today = date.today()
            year, week, _ = today.isocalendar()
            year_week = f"{year}-{week:02d}"
        
        year, week = map(int, year_week.split('-'))
        start_date = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w").date()
        end_date = start_date + timedelta(days=6)
        
        # 获取总学习时长
        from sqlalchemy import case
        total_study_hours = db.query(
            func.sum(
                case(
                    (TimeSlot.status == 'completed', 1.0),
                    else_=0.0
                )
            )
        ).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date
            )
        ).scalar() or 0.0
        
        # 获取高频任务完成情况
        high_freq_stats = db.query(
            func.count(TimeSlot.id).label('total'),
            func.sum(
                case(
                    (TimeSlot.status == 'completed', 1),
                    else_=0
                )
            ).label('completed')
        ).join(Task, TimeSlot.task_id == Task.id)\
         .filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date,
                Task.is_high_frequency == 1
            )
        ).first()
        
        high_freq_complete = f"{high_freq_stats.completed or 0}/{high_freq_stats.total or 0}"
        
        # 获取待克服任务完成情况
        overcome_stats = db.query(
            func.count(TimeSlot.id).label('total'),
            func.sum(
                case(
                    (TimeSlot.status == 'completed', 1),
                    else_=0
                )
            ).label('completed')
        ).join(Task, TimeSlot.task_id == Task.id)\
         .filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date,
                Task.is_overcome == 1
            )
        ).first()
        
        overcome_complete = f"{overcome_stats.completed or 0}/{overcome_stats.total or 0}"
        
        # AI推荐采纳率（简化计算）
        ai_recommended_count = db.query(func.count(TimeSlot.id)).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date,
                TimeSlot.is_ai_recommended == 1
            )
        ).scalar() or 0
        
        ai_accepted_count = db.query(func.count(TimeSlot.id)).filter(
            and_(
                TimeSlot.user_id == user_id,
                cast(TimeSlot.date, Date) >= start_date,
                cast(TimeSlot.date, Date) <= end_date,
                TimeSlot.is_ai_recommended == 1,
                TimeSlot.status == 'completed'
            )
        ).scalar() or 0
        
        ai_accept_rate = int((ai_accepted_count / ai_recommended_count * 100)) if ai_recommended_count > 0 else 0
        
        return WeeklyOverviewResponse(
            total_study_hours=float(total_study_hours),
            high_freq_complete=high_freq_complete,
            overcome_complete=overcome_complete,
            ai_accept_rate=ai_accept_rate,
            week_start=start_date,
            week_end=end_date
        )
    
    def generate_weekly_chart_data(self, db: Session, user_id: int, year_week: Optional[str] = None) -> Dict[str, Any]:
        """生成本周图表数据"""
        if year_week is None:
            today = date.today()
            year, week, _ = today.isocalendar()
            year_week = f"{year}-{week:02d}"
        
        year, week = map(int, year_week.split('-'))
        start_date = datetime.strptime(f"{year}-W{week:02d}-1", "%Y-W%W-%w").date()
        end_date = start_date + timedelta(days=6)
        
        # 每日时长数据
        from sqlalchemy import case
        daily_data = []
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            
            daily_hours = db.query(
                func.sum(
                    case(
                        (TimeSlot.status == 'completed', 1.0),
                        else_=0.0
                    )
                )
            ).filter(
                and_(
                    TimeSlot.user_id == user_id,
                    cast(TimeSlot.date, Date) == current_date
                )
            ).scalar() or 0.0
            
            # 获取当日完成率
            total_slots = db.query(func.count(TimeSlot.id)).filter(
                and_(
                    TimeSlot.user_id == user_id,
                    cast(TimeSlot.date, Date) == current_date
                )
            ).scalar() or 0
            
            completed_slots = db.query(func.count(TimeSlot.id)).filter(
                and_(
                    TimeSlot.user_id == user_id,
                    cast(TimeSlot.date, Date) == current_date,
                    TimeSlot.status == 'completed'
                )
            ).scalar() or 0
            
            completion_rate = (completed_slots / total_slots * 100) if total_slots > 0 else 0.0
            
            # 获取主要心情
            dominant_mood = db.query(
                MoodRecord.mood,
                func.count(MoodRecord.id).label('count')
            ).join(TimeSlot, MoodRecord.time_slot_id == TimeSlot.id)\
             .filter(
                and_(
                    MoodRecord.user_id == user_id,
                    cast(TimeSlot.date, Date) == current_date
                )
            ).group_by(MoodRecord.mood)\
             .order_by(desc('count'))\
             .first()
            
            daily_data.append(DailyHours(
                date=current_date,
                hours=float(daily_hours),
                completion_rate=completion_rate,
                mood=dominant_mood.mood if dominant_mood else None
            ))
        
        # 分类时长数据
        category_data = self.get_weekly_category_hours(db, user_id, year_week)
        total_hours = sum(category_data.values())
        
        category_details = []
        colors = ["#3498db", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]
        
        for i, (category, hours) in enumerate(category_data.items()):
            percentage = (hours / total_hours * 100) if total_hours > 0 else 0.0
            category_details.append(CategoryHours(
                category=category,
                hours=hours,
                percentage=percentage,
                color=colors[i % len(colors)]
            ))
        
        # 构建图表数据
        daily_chart = {
            "labels": [d.date.strftime("%m-%d") for d in daily_data],
            "datasets": [{
                "label": "学习时长",
                "data": [d.hours for d in daily_data],
                "backgroundColor": "#3498db",
                "borderColor": "#2980b9",
                "borderWidth": 1
            }]
        }
        
        category_chart = {
            "labels": [c.category for c in category_details],
            "datasets": [{
                "data": [c.hours for c in category_details],
                "backgroundColor": [c.color for c in category_details],
                "borderWidth": 0
            }]
        }
        
        return {
            "daily_chart": daily_chart,
            "category_chart": category_chart,
            "daily_details": daily_data,
            "category_details": category_details
        }
    
    def create_or_update_weekly_stat(self, db: Session, user_id: int, year_week: str, stat_data: Dict[str, Any]) -> StatisticWeekly:
        """创建或更新周统计"""
        existing_stat = db.query(StatisticWeekly).filter(
            and_(
                StatisticWeekly.user_id == user_id,
                StatisticWeekly.year_week == year_week
            )
        ).first()
        
        if existing_stat:
            # 更新现有记录
            for field, value in stat_data.items():
                if hasattr(existing_stat, field):
                    setattr(existing_stat, field, value)
            db.commit()
            db.refresh(existing_stat)
            return existing_stat
        else:
            # 创建新记录
            db_stat = StatisticWeekly(
                user_id=user_id,
                year_week=year_week,
                **stat_data
            )
            db.add(db_stat)
            db.commit()
            db.refresh(db_stat)
            return db_stat
    
    def create_or_update_daily_stat(self, db: Session, user_id: int, target_date: date, stat_data: Dict[str, Any]) -> StatisticDaily:
        """创建或更新日统计"""
        existing_stat = db.query(StatisticDaily).filter(
            and_(
                StatisticDaily.user_id == user_id,
                cast(StatisticDaily.date, Date) == target_date
            )
        ).first()
        
        if existing_stat:
            # 更新现有记录
            for field, value in stat_data.items():
                if hasattr(existing_stat, field):
                    setattr(existing_stat, field, value)
            db.commit()
            db.refresh(existing_stat)
            return existing_stat
        else:
            # 创建新记录
            db_stat = StatisticDaily(
                user_id=user_id,
                date=datetime.combine(target_date, datetime.min.time()),
                **stat_data
            )
            db.add(db_stat)
            db.commit()
            db.refresh(db_stat)
            return db_stat

# 创建CRUD实例
crud_statistic = CRUDStatistic() 