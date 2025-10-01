from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
from models.schemas.method import CheckinCreate

class CRUDCheckin:
    def create(self, db: Session, user_id: int, method_id: int, checkin_data: CheckinCreate):
        """保存打卡记录到CheckinRecord表"""
        try:
            query = """
            INSERT INTO checkin_records (
                user_id, method_id, checkin_type, progress, note, rating, 
                checkin_time, create_time
            ) VALUES (
                :user_id, :method_id, :checkin_type, :progress, :note, :rating,
                :checkin_time, :create_time
            )
            """
            
            params = {
                "user_id": user_id,
                "method_id": method_id,
                "checkin_type": checkin_data.checkin_type,
                "progress": checkin_data.progress,
                "note": checkin_data.note,
                "rating": checkin_data.rating,
                "checkin_time": datetime.now(),
                "create_time": datetime.now()
            }
            
            result = db.execute(query, params)
            db.commit()
            
            # 获取创建的记录ID
            checkin_id = result.lastrowid
            
            # 返回创建的记录
            return self.get_by_id(db, checkin_id)
        except Exception as e:
            print(f"创建打卡记录失败: {e}")
            db.rollback()
            return None
    
    def get_by_id(self, db: Session, checkin_id: int):
        """根据ID获取打卡记录"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                method_id,
                checkin_type,
                progress,
                note,
                rating,
                checkin_time,
                create_time
            FROM checkin_records 
            WHERE id = :checkin_id
            """
            
            result = db.execute(query, {"checkin_id": checkin_id}).fetchone()
            
            if result:
                return CheckinRecordData(
                    id=result.id,
                    user_id=result.user_id,
                    method_id=result.method_id,
                    checkin_type=result.checkin_type,
                    progress=result.progress,
                    note=result.note,
                    rating=result.rating,
                    checkin_time=result.checkin_time,
                    create_time=result.create_time
                )
            return None
        except Exception as e:
            print(f"获取打卡记录失败: {e}")
            return None
    
    def get_multi_by_user_method(
        self, 
        db: Session, 
        user_id: int, 
        method_id: int,
        page: int = 1,
        page_size: int = 20
    ):
        """查询用户-方法的打卡历史"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                method_id,
                checkin_type,
                progress,
                note,
                rating,
                checkin_time,
                create_time
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id
            ORDER BY checkin_time DESC
            LIMIT :limit OFFSET :offset
            """
            
            params = {
                "user_id": user_id,
                "method_id": method_id,
                "limit": page_size,
                "offset": (page - 1) * page_size
            }
            
            results = db.execute(query, params).fetchall()
            
            records = []
            for result in results:
                records.append(CheckinRecordData(
                    id=result.id,
                    user_id=result.user_id,
                    method_id=result.method_id,
                    checkin_type=result.checkin_type,
                    progress=result.progress,
                    note=result.note,
                    rating=result.rating,
                    checkin_time=result.checkin_time,
                    create_time=result.create_time
                ))
            
            return records
        except Exception as e:
            print(f"查询打卡历史失败: {e}")
            return []
    
    def get_by_user_method_date(
        self, 
        db: Session, 
        user_id: int, 
        method_id: int, 
        checkin_date: date
    ):
        """获取用户在指定日期的打卡记录"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                method_id,
                checkin_type,
                progress,
                note,
                rating,
                checkin_time,
                create_time
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id 
            AND DATE(checkin_time) = :checkin_date
            """
            
            result = db.execute(query, {
                "user_id": user_id,
                "method_id": method_id,
                "checkin_date": checkin_date
            }).fetchone()
            
            if result:
                return CheckinRecordData(
                    id=result.id,
                    user_id=result.user_id,
                    method_id=result.method_id,
                    checkin_type=result.checkin_type,
                    progress=result.progress,
                    note=result.note,
                    rating=result.rating,
                    checkin_time=result.checkin_time,
                    create_time=result.create_time
                )
            return None
        except Exception as e:
            print(f"获取指定日期打卡记录失败: {e}")
            return None
    
    def count_user_method_checkins(self, db: Session, user_id: int, method_id: int) -> int:
        """统计用户对某方法的总打卡次数"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id
            """
            
            result = db.execute(query, {
                "user_id": user_id,
                "method_id": method_id
            }).fetchone()
            
            return result.count if result else 0
        except Exception as e:
            print(f"统计打卡次数失败: {e}")
            return 0
    
    def get_latest_by_user_method(self, db: Session, user_id: int, method_id: int):
        """获取用户对某方法的最新打卡记录"""
        try:
            query = """
            SELECT 
                id,
                user_id,
                method_id,
                checkin_type,
                progress,
                note,
                rating,
                checkin_time,
                create_time
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id
            ORDER BY checkin_time DESC
            LIMIT 1
            """
            
            result = db.execute(query, {
                "user_id": user_id,
                "method_id": method_id
            }).fetchone()
            
            if result:
                return CheckinRecordData(
                    id=result.id,
                    user_id=result.user_id,
                    method_id=result.method_id,
                    checkin_type=result.checkin_type,
                    progress=result.progress,
                    note=result.note,
                    rating=result.rating,
                    checkin_time=result.checkin_time,
                    create_time=result.create_time
                )
            return None
        except Exception as e:
            print(f"获取最新打卡记录失败: {e}")
            return None
    
    def get_average_progress(self, db: Session, user_id: int, method_id: int) -> Optional[float]:
        """获取用户对某方法的平均进度"""
        try:
            query = """
            SELECT AVG(progress) as avg_progress
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id
            """
            
            result = db.execute(query, {
                "user_id": user_id,
                "method_id": method_id
            }).fetchone()
            
            return result.avg_progress if result and result.avg_progress else None
        except Exception as e:
            print(f"获取平均进度失败: {e}")
            return None
    
    def count_user_method_checkins_by_month(
        self, 
        db: Session, 
        user_id: int, 
        method_id: int,
        year: int,
        month: int
    ) -> int:
        """统计用户某月对某方法的打卡次数"""
        try:
            query = """
            SELECT COUNT(*) as count
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id
            AND YEAR(checkin_time) = :year AND MONTH(checkin_time) = :month
            """
            
            result = db.execute(query, {
                "user_id": user_id,
                "method_id": method_id,
                "year": year,
                "month": month
            }).fetchone()
            
            return result.count if result else 0
        except Exception as e:
            print(f"统计月度打卡次数失败: {e}")
            return 0
    
    def get_user_checkins_by_month(
        self, 
        db: Session, 
        user_id: int, 
        year: int, 
        month: int
    ):
        """获取用户某月的所有打卡记录"""
        try:
            query = """
            SELECT 
                cr.id,
                cr.user_id,
                cr.method_id,
                cr.checkin_type,
                cr.progress,
                cr.note,
                cr.rating,
                cr.checkin_time,
                cr.create_time,
                sm.name as method_name
            FROM checkin_records cr
            LEFT JOIN study_methods sm ON cr.method_id = sm.id
            WHERE cr.user_id = :user_id
            AND YEAR(cr.checkin_time) = :year AND MONTH(cr.checkin_time) = :month
            ORDER BY cr.checkin_time DESC
            """
            
            results = db.execute(query, {
                "user_id": user_id,
                "year": year,
                "month": month
            }).fetchall()
            
            records = []
            for result in results:
                record = CheckinRecordData(
                    id=result.id,
                    user_id=result.user_id,
                    method_id=result.method_id,
                    checkin_type=result.checkin_type,
                    progress=result.progress,
                    note=result.note,
                    rating=result.rating,
                    checkin_time=result.checkin_time,
                    create_time=result.create_time
                )
                # 添加方法信息
                record.method = type('Method', (), {'name': result.method_name})()
                records.append(record)
            
            return records
        except Exception as e:
            print(f"获取月度打卡记录失败: {e}")
            return []
    
    def count_checkin_days_in_range(
        self, 
        db: Session, 
        user_id: int, 
        method_id: int,
        start_date: date,
        end_date: date
    ) -> int:
        """统计指定时间范围内的打卡天数"""
        try:
            query = """
            SELECT COUNT(DISTINCT DATE(checkin_time)) as count
            FROM checkin_records 
            WHERE user_id = :user_id AND method_id = :method_id
            AND DATE(checkin_time) BETWEEN :start_date AND :end_date
            """
            
            result = db.execute(query, {
                "user_id": user_id,
                "method_id": method_id,
                "start_date": start_date,
                "end_date": end_date
            }).fetchone()
            
            return result.count if result else 0
        except Exception as e:
            print(f"统计打卡天数失败: {e}")
            return 0
    
    def delete(self, db: Session, checkin_id: int) -> bool:
        """删除打卡记录"""
        try:
            query = """
            DELETE FROM checkin_records 
            WHERE id = :checkin_id
            """
            
            result = db.execute(query, {"checkin_id": checkin_id})
            db.commit()
            
            return result.rowcount > 0
        except Exception as e:
            print(f"删除打卡记录失败: {e}")
            db.rollback()
            return False
    
    def update(self, db: Session, checkin_id: int, checkin_data: CheckinCreate):
        """更新打卡记录"""
        try:
            query = """
            UPDATE checkin_records 
            SET checkin_type = :checkin_type,
                progress = :progress,
                note = :note,
                rating = :rating
            WHERE id = :checkin_id
            """
            
            params = {
                "checkin_id": checkin_id,
                "checkin_type": checkin_data.checkin_type,
                "progress": checkin_data.progress,
                "note": checkin_data.note,
                "rating": checkin_data.rating
            }
            
            result = db.execute(query, params)
            db.commit()
            
            if result.rowcount > 0:
                return self.get_by_id(db, checkin_id)
            return None
        except Exception as e:
            print(f"更新打卡记录失败: {e}")
            db.rollback()
            return None

class CheckinRecordData:
    """打卡记录数据类"""
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.user_id = kwargs.get('user_id')
        self.method_id = kwargs.get('method_id')
        self.checkin_type = kwargs.get('checkin_type')
        self.progress = kwargs.get('progress')
        self.note = kwargs.get('note')
        self.rating = kwargs.get('rating')
        self.checkin_time = kwargs.get('checkin_time')
        self.create_time = kwargs.get('create_time') 