from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import calendar

from crud.method.crud_checkin import CRUDCheckin
from crud.method.crud_method import CRUDMethod
from models.schemas.method import (
    CheckinCreate,
    CheckinResponse,
    CheckinHistoryResponse
)

class CheckinService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_checkin = CRUDCheckin()
        self.crud_method = CRUDMethod()
    
    async def create_checkin(
        self, 
        user_id: int, 
        method_id: int, 
        checkin_data: CheckinCreate
    ) -> Optional[CheckinResponse]:
        """处理打卡逻辑（校验method_id合法性、进度范围；保存打卡记录；同步更新方法总打卡数）"""
        try:
            # 校验方法是否存在且有效
            method = self.crud_method.get_by_id(self.db, method_id)
            if not method or not method.is_active:
                return None
            
            # 校验进度范围
            if checkin_data.progress < 0 or checkin_data.progress > 100:
                return None
            
            # 检查今日是否已打卡
            today = date.today()
            existing_checkin = self.crud_checkin.get_by_user_method_date(
                self.db, user_id, method_id, today
            )
            if existing_checkin:
                return None  # 今日已打卡
            
            # 创建打卡记录
            checkin_record = self.crud_checkin.create(
                self.db, user_id, method_id, checkin_data
            )
            
            if not checkin_record:
                return None
            
            # 同步更新方法总打卡数
            await self._update_method_checkin_count(method_id)
            
            # 构建响应数据
            checkin_response = CheckinResponse(
                id=checkin_record.id,
                user_id=checkin_record.user_id,
                method_id=checkin_record.method_id,
                checkin_type=checkin_record.checkin_type,
                progress=checkin_record.progress,
                note=checkin_record.note,
                rating=checkin_record.rating,
                checkin_time=checkin_record.checkin_time,
                create_time=checkin_record.create_time
            )
            
            return checkin_response
        except Exception as e:
            print(f"创建打卡记录失败: {e}")
            return None
    
    async def get_user_checkin_history(
        self, 
        user_id: int, 
        method_id: int,
        page: int = 1,
        page_size: int = 20
    ) -> List[CheckinHistoryResponse]:
        """查询用户对该方法的打卡历史"""
        try:
            # 获取打卡历史记录
            checkin_records = self.crud_checkin.get_multi_by_user_method(
                self.db, user_id, method_id, page=page, page_size=page_size
            )
            
            # 构建历史响应数据
            history_responses = []
            for record in checkin_records:
                history_response = CheckinHistoryResponse(
                    id=record.id,
                    checkin_type=record.checkin_type,
                    progress=record.progress,
                    note=record.note,
                    rating=record.rating,
                    checkin_time=record.checkin_time,
                    create_time=record.create_time,
                    # 添加一些额外的历史信息
                    days_ago=self._calculate_days_ago(record.checkin_time),
                    is_continuous=await self._check_continuous_checkin(
                        user_id, method_id, record.checkin_time
                    )
                )
                history_responses.append(history_response)
            
            return history_responses
        except Exception as e:
            print(f"获取打卡历史失败: {e}")
            return []
    
    async def get_user_checkin_stats(
        self, 
        user_id: int, 
        method_id: int
    ) -> Dict[str, Any]:
        """获取用户在该方法的打卡统计"""
        try:
            # 获取总打卡次数
            total_checkins = self.crud_checkin.count_user_method_checkins(
                self.db, user_id, method_id
            )
            
            # 获取连续打卡天数
            continuous_days = await self._calculate_continuous_days(user_id, method_id)
            
            # 获取最近打卡记录
            recent_checkin = self.crud_checkin.get_latest_by_user_method(
                self.db, user_id, method_id
            )
            
            # 获取平均进度
            avg_progress = self.crud_checkin.get_average_progress(
                self.db, user_id, method_id
            )
            
            # 获取本月打卡次数
            current_month_checkins = self.crud_checkin.count_user_method_checkins_by_month(
                self.db, user_id, method_id, datetime.now().year, datetime.now().month
            )
            
            return {
                "total_checkins": total_checkins,
                "continuous_days": continuous_days,
                "last_checkin_date": recent_checkin.checkin_time.date() if recent_checkin else None,
                "average_progress": round(avg_progress, 2) if avg_progress else 0,
                "current_month_checkins": current_month_checkins,
                "checkin_rate": await self._calculate_checkin_rate(user_id, method_id)
            }
        except Exception as e:
            print(f"获取打卡统计失败: {e}")
            return {}
    
    async def delete_checkin(
        self, 
        user_id: int, 
        method_id: int, 
        checkin_id: int
    ) -> bool:
        """删除打卡记录（仅限当天的记录）"""
        try:
            # 获取打卡记录
            checkin = self.crud_checkin.get_by_id(self.db, checkin_id)
            if not checkin or checkin.user_id != user_id or checkin.method_id != method_id:
                return False
            
            # 检查是否为当天记录
            if checkin.checkin_time.date() != date.today():
                return False
            
            # 删除记录
            success = self.crud_checkin.delete(self.db, checkin_id)
            
            if success:
                # 更新方法打卡数
                await self._update_method_checkin_count(method_id)
            
            return success
        except Exception as e:
            print(f"删除打卡记录失败: {e}")
            return False
    
    async def update_checkin(
        self, 
        user_id: int, 
        method_id: int, 
        checkin_id: int,
        checkin_data: CheckinCreate
    ) -> Optional[CheckinResponse]:
        """更新打卡记录（仅限当天的记录）"""
        try:
            # 获取打卡记录
            checkin = self.crud_checkin.get_by_id(self.db, checkin_id)
            if not checkin or checkin.user_id != user_id or checkin.method_id != method_id:
                return None
            
            # 检查是否为当天记录
            if checkin.checkin_time.date() != date.today():
                return None
            
            # 校验进度范围
            if checkin_data.progress < 0 or checkin_data.progress > 100:
                return None
            
            # 更新记录
            updated_checkin = self.crud_checkin.update(
                self.db, checkin_id, checkin_data
            )
            
            if not updated_checkin:
                return None
            
            # 构建响应数据
            checkin_response = CheckinResponse(
                id=updated_checkin.id,
                user_id=updated_checkin.user_id,
                method_id=updated_checkin.method_id,
                checkin_type=updated_checkin.checkin_type,
                progress=updated_checkin.progress,
                note=updated_checkin.note,
                rating=updated_checkin.rating,
                checkin_time=updated_checkin.checkin_time,
                create_time=updated_checkin.create_time
            )
            
            return checkin_response
        except Exception as e:
            print(f"更新打卡记录失败: {e}")
            return None
    
    async def get_checkin_calendar(
        self, 
        user_id: int, 
        year: int, 
        month: int
    ) -> Dict[str, Any]:
        """获取用户的打卡日历（某月的打卡情况）"""
        try:
            # 获取该月的打卡记录
            checkin_records = self.crud_checkin.get_user_checkins_by_month(
                self.db, user_id, year, month
            )
            
            # 构建日历数据
            calendar_data = {}
            for record in checkin_records:
                day = record.checkin_time.day
                if day not in calendar_data:
                    calendar_data[day] = []
                
                calendar_data[day].append({
                    "method_id": record.method_id,
                    "method_name": record.method.name if record.method else "未知方法",
                    "progress": record.progress,
                    "checkin_type": record.checkin_type,
                    "rating": record.rating
                })
            
            # 获取月份信息
            month_info = {
                "year": year,
                "month": month,
                "days_in_month": calendar.monthrange(year, month)[1],
                "checkin_days": len(calendar_data),
                "total_checkins": len(checkin_records)
            }
            
            return {
                "month_info": month_info,
                "calendar_data": calendar_data,
                "checkin_rate": len(calendar_data) / month_info["days_in_month"]
            }
        except Exception as e:
            print(f"获取打卡日历失败: {e}")
            return {}
    
    async def _update_method_checkin_count(self, method_id: int) -> bool:
        """更新方法的打卡人数统计"""
        try:
            return self.crud_method.update_checkin_count(self.db, method_id)
        except Exception as e:
            print(f"更新方法打卡数失败: {e}")
            return False
    
    def _calculate_days_ago(self, checkin_time: datetime) -> int:
        """计算打卡距今天数"""
        return (datetime.now().date() - checkin_time.date()).days
    
    async def _check_continuous_checkin(
        self, 
        user_id: int, 
        method_id: int, 
        checkin_time: datetime
    ) -> bool:
        """检查是否为连续打卡"""
        try:
            # 获取前一天的打卡记录
            previous_date = checkin_time.date() - timedelta(days=1)
            previous_checkin = self.crud_checkin.get_by_user_method_date(
                self.db, user_id, method_id, previous_date
            )
            return previous_checkin is not None
        except Exception:
            return False
    
    async def _calculate_continuous_days(self, user_id: int, method_id: int) -> int:
        """计算连续打卡天数"""
        try:
            # 从今天开始往前计算连续天数
            current_date = date.today()
            continuous_days = 0
            
            while True:
                checkin = self.crud_checkin.get_by_user_method_date(
                    self.db, user_id, method_id, current_date
                )
                if checkin:
                    continuous_days += 1
                    current_date -= timedelta(days=1)
                else:
                    break
            
            return continuous_days
        except Exception:
            return 0
    
    async def _calculate_checkin_rate(self, user_id: int, method_id: int) -> float:
        """计算打卡率（最近30天）"""
        try:
            # 获取最近30天的打卡记录
            end_date = date.today()
            start_date = end_date - timedelta(days=30)
            
            checkin_days = self.crud_checkin.count_checkin_days_in_range(
                self.db, user_id, method_id, start_date, end_date
            )
            
            return checkin_days / 30.0
        except Exception:
            return 0.0 