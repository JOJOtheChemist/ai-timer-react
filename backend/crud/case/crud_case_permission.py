from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from datetime import datetime

# 注意：这里假设有对应的数据库模型，实际使用时需要根据具体的模型进行调整
# from models.case import CasePermission, CasePurchaseRecord, SuccessCase

class CRUDCasePermission:
    def __init__(self):
        pass

    async def get_permission_info(self, db: Session, case_id: int) -> Optional[Any]:
        """查询案例的权限配置（预览天数、价格等）"""
        try:
            permission_info = db.query(CasePermission).filter(
                CasePermission.case_id == case_id
            ).first()
            
            return permission_info
        except Exception as e:
            raise Exception(f"查询案例权限配置失败: {str(e)}")

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

    async def check_is_author(self, db: Session, case_id: int, user_id: int) -> bool:
        """检查用户是否为案例作者"""
        try:
            case = db.query(SuccessCase).filter(
                and_(
                    SuccessCase.id == case_id,
                    SuccessCase.author_id == user_id
                )
            ).first()
            
            return case is not None
        except Exception as e:
            raise Exception(f"检查作者身份失败: {str(e)}")

    async def create_purchase_record(
        self,
        db: Session,
        case_id: int,
        user_id: int,
        price: float,
        currency: str,
        payment_method: str,
        purchase_time: datetime
    ) -> str:
        """创建购买记录"""
        try:
            # 生成订单ID
            order_id = f"CASE_{case_id}_{user_id}_{int(purchase_time.timestamp())}"
            
            purchase_record = CasePurchaseRecord(
                order_id=order_id,
                case_id=case_id,
                user_id=user_id,
                price=price,
                currency=currency,
                payment_method=payment_method,
                status='completed',
                purchase_time=purchase_time,
                created_at=purchase_time
            )
            
            db.add(purchase_record)
            db.commit()
            
            return order_id
        except Exception as e:
            db.rollback()
            raise Exception(f"创建购买记录失败: {str(e)}")

    async def get_user_purchased_cases(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        """获取用户已购买的案例列表"""
        try:
            purchased_cases = db.query(CasePurchaseRecord).join(
                SuccessCase, CasePurchaseRecord.case_id == SuccessCase.id
            ).filter(
                and_(
                    CasePurchaseRecord.user_id == user_id,
                    CasePurchaseRecord.status == 'completed',
                    SuccessCase.is_active == True
                )
            ).order_by(desc(CasePurchaseRecord.purchase_time)).offset(skip).limit(limit).all()
            
            return purchased_cases
        except Exception as e:
            raise Exception(f"获取已购买案例失败: {str(e)}")

    async def count_user_purchased_cases(self, db: Session, user_id: int) -> int:
        """统计用户已购买的案例数量"""
        try:
            count = db.query(CasePurchaseRecord).filter(
                and_(
                    CasePurchaseRecord.user_id == user_id,
                    CasePurchaseRecord.status == 'completed'
                )
            ).count()
            
            return count
        except Exception as e:
            raise Exception(f"统计已购买案例数量失败: {str(e)}")

    async def get_purchase_record_by_order_id(self, db: Session, order_id: str) -> Optional[Any]:
        """根据订单ID获取购买记录"""
        try:
            purchase_record = db.query(CasePurchaseRecord).filter(
                CasePurchaseRecord.order_id == order_id
            ).first()
            
            return purchase_record
        except Exception as e:
            raise Exception(f"查询购买记录失败: {str(e)}")

    async def update_purchase_status(
        self,
        db: Session,
        order_id: str,
        status: str,
        payment_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """更新购买记录状态"""
        try:
            purchase_record = db.query(CasePurchaseRecord).filter(
                CasePurchaseRecord.order_id == order_id
            ).first()
            
            if not purchase_record:
                return False
            
            purchase_record.status = status
            purchase_record.updated_at = datetime.now()
            
            if payment_info:
                purchase_record.payment_info = str(payment_info)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新购买状态失败: {str(e)}")

    async def create_permission_config(
        self,
        db: Session,
        case_id: int,
        preview_days: int,
        price: float,
        currency: str = "CNY",
        preview_content_ratio: float = 0.3
    ) -> Any:
        """创建案例权限配置"""
        try:
            permission_config = CasePermission(
                case_id=case_id,
                preview_days=preview_days,
                price=price,
                currency=currency,
                preview_content_ratio=preview_content_ratio,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )
            
            db.add(permission_config)
            db.commit()
            db.refresh(permission_config)
            
            return permission_config
        except Exception as e:
            db.rollback()
            raise Exception(f"创建权限配置失败: {str(e)}")

    async def update_permission_config(
        self,
        db: Session,
        case_id: int,
        update_data: Dict[str, Any]
    ) -> bool:
        """更新案例权限配置"""
        try:
            permission_config = db.query(CasePermission).filter(
                CasePermission.case_id == case_id
            ).first()
            
            if not permission_config:
                return False
            
            for key, value in update_data.items():
                if hasattr(permission_config, key):
                    setattr(permission_config, key, value)
            
            permission_config.updated_at = datetime.now()
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新权限配置失败: {str(e)}")

    async def get_case_revenue_stats(self, db: Session, case_id: int) -> Dict[str, Any]:
        """获取案例收益统计"""
        try:
            # 总销售额
            total_revenue = db.query(
                db.func.sum(CasePurchaseRecord.price)
            ).filter(
                and_(
                    CasePurchaseRecord.case_id == case_id,
                    CasePurchaseRecord.status == 'completed'
                )
            ).scalar() or 0
            
            # 购买人数
            purchase_count = db.query(CasePurchaseRecord).filter(
                and_(
                    CasePurchaseRecord.case_id == case_id,
                    CasePurchaseRecord.status == 'completed'
                )
            ).count()
            
            # 最近30天销售额
            from datetime import timedelta
            thirty_days_ago = datetime.now() - timedelta(days=30)
            recent_revenue = db.query(
                db.func.sum(CasePurchaseRecord.price)
            ).filter(
                and_(
                    CasePurchaseRecord.case_id == case_id,
                    CasePurchaseRecord.status == 'completed',
                    CasePurchaseRecord.purchase_time >= thirty_days_ago
                )
            ).scalar() or 0
            
            return {
                "total_revenue": float(total_revenue),
                "purchase_count": purchase_count,
                "recent_revenue_30d": float(recent_revenue),
                "average_price": float(total_revenue / purchase_count) if purchase_count > 0 else 0
            }
        except Exception as e:
            raise Exception(f"获取收益统计失败: {str(e)}") 