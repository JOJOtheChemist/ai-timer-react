from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, text
from datetime import datetime
import uuid

from models.tutor import TutorServiceOrder

class CRUDTutorServiceOrder:
    def __init__(self):
        pass

    async def create_order(
        self,
        db: Session,
        user_id: int,
        tutor_id: int,
        service_id: int,
        amount: float,
        currency: str = "diamonds",
        service_name: str = ""
    ) -> str:
        """创建导师服务订单（记录订单状态、金额、时间）"""
        try:
            # 生成订单号
            order_no = f"TUTOR{int(datetime.now().timestamp())}{user_id:04d}"
            
            # 使用raw SQL插入
            insert_query = text("""
            INSERT INTO tutor_service_order (
                user_id, tutor_id, service_id, order_no, amount, status, create_time, update_time
            ) VALUES (
                :user_id, :tutor_id, :service_id, :order_no, :amount, :status, :create_time, :update_time
            )
            """)
            
            db.execute(insert_query, {
                "user_id": user_id,
                "tutor_id": tutor_id,
                "service_id": service_id,
                "order_no": order_no,
                "amount": int(amount),
                "status": 1,  # 1=已支付
                "create_time": datetime.now(),
                "update_time": datetime.now()
            })
            
            db.commit()
            
            return order_no
        except Exception as e:
            db.rollback()
            raise Exception(f"创建订单失败: {str(e)}")

    async def get_by_order_no(self, db: Session, order_no: str) -> Optional[Any]:
        """根据订单号获取订单详情"""
        try:
            query = text("""
            SELECT * FROM tutor_service_order WHERE order_no = :order_no
            """)
            
            result = db.execute(query, {"order_no": order_no}).fetchone()
            
            return result
        except Exception as e:
            raise Exception(f"查询订单失败: {str(e)}")

    async def get_orders_by_user(
        self,
        db: Session,
        user_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        """获取用户的导师服务订单列表"""
        try:
            query = text("""
            SELECT 
                tso.id,
                tso.user_id,
                tso.tutor_id,
                tso.service_id,
                tso.order_no,
                tso.amount,
                tso.status,
                tso.create_time,
                ts.name as service_name
            FROM tutor_service_order tso
            LEFT JOIN tutor_service ts ON tso.service_id = ts.id
            WHERE tso.user_id = :user_id
            ORDER BY tso.create_time DESC
            LIMIT :limit OFFSET :skip
            """)
            
            results = db.execute(query, {
                "user_id": user_id,
                "skip": skip,
                "limit": limit
            }).fetchall()
            
            return results
        except Exception as e:
            raise Exception(f"获取用户订单失败: {str(e)}")

    async def get_orders_by_tutor(
        self,
        db: Session,
        tutor_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> List[Any]:
        """获取导师的服务订单列表"""
        try:
            orders = db.query(TutorServiceOrder).filter(
                TutorServiceOrder.tutor_id == tutor_id
            ).order_by(desc(TutorServiceOrder.created_at)).offset(skip).limit(limit).all()
            
            return orders
        except Exception as e:
            raise Exception(f"获取导师订单失败: {str(e)}")

    async def update_order_status(
        self,
        db: Session,
        order_id: str,
        status: str,
        update_info: Optional[Dict[str, Any]] = None
    ) -> bool:
        """更新订单状态"""
        try:
            order = db.query(TutorServiceOrder).filter(
                TutorServiceOrder.order_id == order_id
            ).first()
            
            if not order:
                return False
            
            order.status = status
            order.updated_at = datetime.now()
            
            if update_info:
                for key, value in update_info.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise Exception(f"更新订单状态失败: {str(e)}")

    async def get_order_stats(self, db: Session, tutor_id: int) -> Dict[str, Any]:
        """获取导师的订单统计"""
        try:
            from sqlalchemy import func
            
            # 总订单数
            total_orders = db.query(TutorServiceOrder).filter(
                TutorServiceOrder.tutor_id == tutor_id
            ).count()
            
            # 已完成订单数
            completed_orders = db.query(TutorServiceOrder).filter(
                and_(
                    TutorServiceOrder.tutor_id == tutor_id,
                    TutorServiceOrder.status == "completed"
                )
            ).count()
            
            # 总收入
            total_revenue = db.query(func.sum(TutorServiceOrder.amount)).filter(
                and_(
                    TutorServiceOrder.tutor_id == tutor_id,
                    TutorServiceOrder.status == "completed"
                )
            ).scalar() or 0.0
            
            # 本月订单数
            from datetime import date
            current_month_start = date.today().replace(day=1)
            monthly_orders = db.query(TutorServiceOrder).filter(
                and_(
                    TutorServiceOrder.tutor_id == tutor_id,
                    TutorServiceOrder.created_at >= current_month_start
                )
            ).count()
            
            return {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "total_revenue": float(total_revenue),
                "monthly_orders": monthly_orders,
                "completion_rate": completed_orders / total_orders if total_orders > 0 else 0.0
            }
        except Exception as e:
            raise Exception(f"获取订单统计失败: {str(e)}")

    async def get_recent_orders(
        self,
        db: Session,
        tutor_id: int,
        days: int = 7,
        limit: int = 10
    ) -> List[Any]:
        """获取导师最近的订单"""
        try:
            from datetime import timedelta
            since_date = datetime.now() - timedelta(days=days)
            
            orders = db.query(TutorServiceOrder).filter(
                and_(
                    TutorServiceOrder.tutor_id == tutor_id,
                    TutorServiceOrder.created_at >= since_date
                )
            ).order_by(desc(TutorServiceOrder.created_at)).limit(limit).all()
            
            return orders
        except Exception as e:
            raise Exception(f"获取最近订单失败: {str(e)}")

    async def count_user_orders(self, db: Session, user_id: int) -> int:
        """统计用户的订单总数"""
        try:
            count = db.query(TutorServiceOrder).filter(
                TutorServiceOrder.user_id == user_id
            ).count()
            
            return count
        except Exception as e:
            raise Exception(f"统计用户订单数失败: {str(e)}")

    async def check_user_purchased_service(
        self,
        db: Session,
        user_id: int,
        tutor_id: int,
        service_id: int
    ) -> bool:
        """检查用户是否已购买过此服务"""
        try:
            order = db.query(TutorServiceOrder).filter(
                and_(
                    TutorServiceOrder.user_id == user_id,
                    TutorServiceOrder.tutor_id == tutor_id,
                    TutorServiceOrder.service_id == service_id,
                    TutorServiceOrder.status == "completed"
                )
            ).first()
            
            return order is not None
        except Exception as e:
            raise Exception(f"检查购买状态失败: {str(e)}")

    async def get_service_purchase_stats(self, db: Session, service_id: int) -> Dict[str, Any]:
        """获取服务的购买统计"""
        try:
            from sqlalchemy import func
            
            # 购买次数
            purchase_count = db.query(TutorServiceOrder).filter(
                and_(
                    TutorServiceOrder.service_id == service_id,
                    TutorServiceOrder.status == "completed"
                )
            ).count()
            
            # 总收入
            total_revenue = db.query(func.sum(TutorServiceOrder.amount)).filter(
                and_(
                    TutorServiceOrder.service_id == service_id,
                    TutorServiceOrder.status == "completed"
                )
            ).scalar() or 0.0
            
            # 独立购买用户数
            unique_buyers = db.query(TutorServiceOrder.user_id).filter(
                and_(
                    TutorServiceOrder.service_id == service_id,
                    TutorServiceOrder.status == "completed"
                )
            ).distinct().count()
            
            return {
                "purchase_count": purchase_count,
                "total_revenue": float(total_revenue),
                "unique_buyers": unique_buyers,
                "average_price": float(total_revenue / purchase_count) if purchase_count > 0 else 0.0
            }
        except Exception as e:
            raise Exception(f"获取服务购买统计失败: {str(e)}") 