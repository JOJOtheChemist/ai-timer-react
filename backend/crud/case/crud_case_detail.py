from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, date

# 注意：这里假设有对应的数据库模型，实际使用时需要根据具体的模型进行调整
# from models.case import SuccessCaseDetail, CaseViewRecord, CasePurchaseRecord

class CRUDCaseDetail:
    def __init__(self):
        pass

    async def get_by_id(self, db: Session, case_id: int) -> Optional[Any]:
        """查询案例详情数据"""
        try:
            case_detail = db.query(SuccessCaseDetail).filter(
                and_(
                    SuccessCaseDetail.id == case_id,
                    SuccessCaseDetail.is_active == True
                )
            ).first()
            
            return case_detail
        except Exception as e:
            raise Exception(f"查询案例详情失败: {str(e)}")

    async def check_user_viewed_today(self, db: Session, case_id: int, user_id: int) -> bool:
        """检查用户今天是否已浏览过此案例"""
        try:
            today = date.today()
            view_record = db.query(CaseViewRecord).filter(
                and_(
                    CaseViewRecord.case_id == case_id,
                    CaseViewRecord.user_id == user_id,
                    CaseViewRecord.view_date == today
                )
            ).first()
            
            return view_record is not None
        except Exception as e:
            raise Exception(f"检查浏览记录失败: {str(e)}")

    async def create_view_record(self, db: Session, case_id: int, user_id: int) -> bool:
        """创建用户浏览记录"""
        try:
            view_record = CaseViewRecord(
                case_id=case_id,
                user_id=user_id,
                view_date=date.today(),
                view_time=datetime.now()
            )
            
            db.add(view_record)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"创建浏览记录失败: {str(e)}")

    async def check_user_purchased(self, db: Session, case_id: int, user_id: int) -> bool:
        """检查用户是否已购买此案例"""
        try:
            purchase_record = db.query(CasePurchaseRecord).filter(
                and_(
                    CasePurchaseRecord.case_id == case_id,
                    CasePurchaseRecord.user_id == user_id,
                    CasePurchaseRecord.status == 'completed'
                )
            ).first()
            
            return purchase_record is not None
        except Exception as e:
            raise Exception(f"检查购买记录失败: {str(e)}")

    async def get_user_view_history(
        self, 
        db: Session, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[Any]:
        """获取用户浏览历史"""
        try:
            view_records = db.query(CaseViewRecord).filter(
                CaseViewRecord.user_id == user_id
            ).order_by(desc(CaseViewRecord.view_time)).offset(skip).limit(limit).all()
            
            return view_records
        except Exception as e:
            raise Exception(f"获取浏览历史失败: {str(e)}")

    async def get_case_view_stats(self, db: Session, case_id: int) -> Dict[str, Any]:
        """获取案例浏览统计"""
        try:
            # 总浏览次数
            total_views = db.query(CaseViewRecord).filter(
                CaseViewRecord.case_id == case_id
            ).count()
            
            # 独立访客数
            unique_visitors = db.query(CaseViewRecord.user_id).filter(
                CaseViewRecord.case_id == case_id
            ).distinct().count()
            
            # 今日浏览次数
            today = date.today()
            today_views = db.query(CaseViewRecord).filter(
                and_(
                    CaseViewRecord.case_id == case_id,
                    CaseViewRecord.view_date == today
                )
            ).count()
            
            return {
                "total_views": total_views,
                "unique_visitors": unique_visitors,
                "today_views": today_views
            }
        except Exception as e:
            raise Exception(f"获取浏览统计失败: {str(e)}")

    async def create_case_detail(self, db: Session, detail_data: Dict[str, Any]) -> Any:
        """创建案例详情"""
        try:
            case_detail = SuccessCaseDetail(**detail_data)
            db.add(case_detail)
            db.commit()
            db.refresh(case_detail)
            return case_detail
        except Exception as e:
            db.rollback()
            raise Exception(f"创建案例详情失败: {str(e)}")

    async def update_case_detail(
        self, 
        db: Session, 
        case_id: int, 
        update_data: Dict[str, Any]
    ) -> bool:
        """更新案例详情"""
        try:
            case_detail = db.query(SuccessCaseDetail).filter(
                SuccessCaseDetail.id == case_id
            ).first()
            
            if not case_detail:
                return False
            
            for key, value in update_data.items():
                if hasattr(case_detail, key):
                    setattr(case_detail, key, value)
            
            case_detail.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新案例详情失败: {str(e)}")

    async def delete_case_detail(self, db: Session, case_id: int) -> bool:
        """软删除案例详情"""
        try:
            case_detail = db.query(SuccessCaseDetail).filter(
                SuccessCaseDetail.id == case_id
            ).first()
            
            if not case_detail:
                return False
            
            case_detail.is_active = False
            case_detail.deleted_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"删除案例详情失败: {str(e)}")

    async def get_popular_cases_by_views(
        self, 
        db: Session, 
        days: int = 7, 
        limit: int = 10
    ) -> List[Any]:
        """获取指定天数内最受欢迎的案例"""
        try:
            from datetime import timedelta
            start_date = date.today() - timedelta(days=days)
            
            # 统计指定时间内的浏览量
            popular_cases = db.query(
                CaseViewRecord.case_id,
                db.func.count(CaseViewRecord.id).label('view_count')
            ).filter(
                CaseViewRecord.view_date >= start_date
            ).group_by(CaseViewRecord.case_id).order_by(
                desc('view_count')
            ).limit(limit).all()
            
            return popular_cases
        except Exception as e:
            raise Exception(f"获取热门案例失败: {str(e)}") 