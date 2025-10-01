from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime, date

from models.case import SuccessCase, CaseInteraction, CasePurchase

class CRUDCaseDetail:
    def __init__(self):
        pass

    async def get_by_id(self, db: Session, case_id: int) -> Optional[Any]:
        """查询案例详情数据"""
        try:
            case_detail = db.query(SuccessCase).filter(
                and_(
                    SuccessCase.id == case_id,
                    SuccessCase.status == 1
                )
            ).first()
            
            return case_detail
        except Exception as e:
            raise Exception(f"查询案例详情失败: {str(e)}")

    async def check_user_viewed_today(self, db: Session, case_id: int, user_id: int) -> bool:
        """检查用户今天是否已浏览过此案例"""
        try:
            today = date.today()
            view_record = db.query(CaseInteraction).filter(
                and_(
                    CaseInteraction.case_id == case_id,
                    CaseInteraction.user_id == user_id,
                    CaseInteraction.view_date == today
                )
            ).first()
            
            return view_record is not None
        except Exception as e:
            raise Exception(f"检查浏览记录失败: {str(e)}")

    async def create_view_record(self, db: Session, case_id: int, user_id: int) -> bool:
        """创建用户浏览记录"""
        try:
            view_record = CaseInteraction(
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
            purchase_record = db.query(CasePurchase).filter(
                and_(
                    CasePurchase.case_id == case_id,
                    CasePurchase.user_id == user_id,
                    CasePurchase.status == 'completed'
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
            view_records = db.query(CaseInteraction).filter(
                CaseInteraction.user_id == user_id
            ).order_by(desc(CaseInteraction.view_time)).offset(skip).limit(limit).all()
            
            return view_records
        except Exception as e:
            raise Exception(f"获取浏览历史失败: {str(e)}")

    async def get_case_view_stats(self, db: Session, case_id: int) -> Dict[str, Any]:
        """获取案例浏览统计"""
        try:
            # 总浏览次数
            total.view_count = db.query(CaseInteraction).filter(
                CaseInteraction.case_id == case_id
            ).count()
            
            # 独立访客数
            unique_visitors = db.query(CaseInteraction.user_id).filter(
                CaseInteraction.case_id == case_id
            ).distinct().count()
            
            # 今日浏览次数
            today = date.today()
            today.view_count = db.query(CaseInteraction).filter(
                and_(
                    CaseInteraction.case_id == case_id,
                    CaseInteraction.view_date == today
                )
            ).count()
            
            return {
                "total.view_count": total.view_count,
                "unique_visitors": unique_visitors,
                "today.view_count": today.view_count
            }
        except Exception as e:
            raise Exception(f"获取浏览统计失败: {str(e)}")

    async def create_case_detail(self, db: Session, detail_data: Dict[str, Any]) -> Any:
        """创建案例详情"""
        try:
            case_detail = SuccessCase(**detail_data)
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
            case_detail = db.query(SuccessCase).filter(
                SuccessCase.id == case_id
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
            case_detail = db.query(SuccessCase).filter(
                SuccessCase.id == case_id
            ).first()
            
            if not case_detail:
                return False
            
            case_detail.status = False
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
                CaseInteraction.case_id,
                db.func.count(CaseInteraction.id).label('view_count')
            ).filter(
                CaseInteraction.view_date >= start_date
            ).group_by(CaseInteraction.case_id).order_by(
                desc('view_count')
            ).limit(limit).all()
            
            return popular_cases
        except Exception as e:
            raise Exception(f"获取热门案例失败: {str(e)}") 