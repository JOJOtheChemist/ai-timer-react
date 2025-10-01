from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta
import uuid

from crud.user.crud_user_asset import CRUDUserAsset
from models.schemas.user import (
    UserAssetResponse, 
    RechargeResponse, 
    AssetRecordResponse,
    TutorServiceOrderResponse
)
from crud.tutor.crud_tutor_service_order import CRUDTutorServiceOrder
from services.tutor.tutor_service import TutorService

class UserAssetService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_user_asset = CRUDUserAsset()
        self.crud_tutor_service_order = CRUDTutorServiceOrder()
        self.tutor_service = TutorService(db)
    
    async def get_user_assets(self, user_id: int) -> Optional[UserAssetResponse]:
        """查询用户资产及最近消费记录"""
        try:
            # 获取用户资产信息
            user_asset = self.crud_user_asset.get_asset_by_user_id(self.db, user_id)
            if not user_asset:
                return None
            
            # 获取最近消费记录
            recent_consume = self.crud_user_asset.get_recent_consume(self.db, user_id, limit=1)
            recent_consume_data = None
            if recent_consume:
                consume_record = recent_consume[0]
                recent_consume_data = {
                    "amount": consume_record.amount,
                    "description": consume_record.description,
                    "create_time": consume_record.create_time.isoformat()
                }
            
            asset_response = UserAssetResponse(
                user_id=user_asset.user_id,
                diamond_count=user_asset.diamond_count,
                total_recharge=user_asset.total_recharge,
                total_consume=user_asset.total_consume,
                recent_consume=recent_consume_data
            )
            
            return asset_response
        except Exception as e:
            print(f"获取用户资产失败: {e}")
            return None
    
    async def create_default_assets(self, user_id: int) -> Optional[UserAssetResponse]:
        """为新用户创建默认资产记录"""
        try:
            # 创建默认资产记录
            default_asset = {
                "user_id": user_id,
                "diamond_count": 0,
                "total_recharge": Decimal('0.00'),
                "total_consume": 0
            }
            
            created_asset = self.crud_user_asset.create_asset(self.db, default_asset)
            if not created_asset:
                return None
            
            return UserAssetResponse(
                user_id=created_asset.user_id,
                diamond_count=created_asset.diamond_count,
                total_recharge=created_asset.total_recharge,
                total_consume=created_asset.total_consume,
                recent_consume=None
            )
        except Exception as e:
            print(f"创建默认资产失败: {e}")
            return None
    
    async def create_recharge_order(
        self, 
        user_id: int, 
        amount: Decimal, 
        payment_method: Optional[str] = None
    ) -> Optional[RechargeResponse]:
        """创建钻石充值订单（返回支付链接/订单号）"""
        try:
            # 生成订单号
            order_id = f"RCH{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8].upper()}"
            
            # 计算钻石数量（1元 = 10钻石）
            diamond_count = int(amount * 10)
            
            # 创建充值订单记录
            order_data = {
                "user_id": user_id,
                "order_id": order_id,
                "amount": amount,
                "diamond_count": diamond_count,
                "payment_method": payment_method or "alipay",
                "status": "pending",
                "expire_time": datetime.now() + timedelta(minutes=30)  # 30分钟过期
            }
            
            created_order = self.crud_user_asset.create_recharge_order(self.db, order_data)
            if not created_order:
                return None
            
            # 生成支付链接（这里是模拟，实际需要对接支付平台）
            payment_url = await self._generate_payment_url(order_id, amount, payment_method)
            
            return RechargeResponse(
                order_id=order_id,
                amount=amount,
                diamond_count=diamond_count,
                payment_url=payment_url,
                expire_time=created_order.expire_time
            )
        except Exception as e:
            print(f"创建充值订单失败: {e}")
            return None
    
    async def get_asset_records(
        self, 
        user_id: int, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[AssetRecordResponse]:
        """获取用户资产变动记录"""
        try:
            records = self.crud_user_asset.get_asset_records(
                self.db, 
                user_id, 
                limit=limit, 
                offset=offset
            )
            
            record_responses = []
            for record in records:
                record_response = AssetRecordResponse(
                    id=record.id,
                    record_type=record.record_type,
                    amount=record.amount,
                    balance_after=record.balance_after,
                    description=record.description,
                    create_time=record.create_time
                )
                record_responses.append(record_response)
            
            return record_responses
        except Exception as e:
            print(f"获取资产记录失败: {e}")
            return []
    
    async def _generate_payment_url(
        self, 
        order_id: str, 
        amount: Decimal, 
        payment_method: Optional[str]
    ) -> Optional[str]:
        """生成支付链接（模拟实现）"""
        try:
            # 这里是模拟实现，实际需要对接支付宝、微信等支付平台
            base_url = "https://api.example.com/payment"
            payment_url = f"{base_url}?order_id={order_id}&amount={amount}&method={payment_method}"
            
            return payment_url
        except Exception as e:
            print(f"生成支付链接失败: {e}")
            return None
    
    async def process_payment_callback(self, order_id: str, payment_result: Dict[str, Any]) -> bool:
        """处理支付回调（充值成功后更新用户资产）"""
        try:
            # 验证订单状态
            order = self.crud_user_asset.get_recharge_order_by_id(self.db, order_id)
            if not order or order.status != "pending":
                return False
            
            # 验证支付结果
            if payment_result.get("status") != "success":
                return False
            
            # 更新订单状态
            self.crud_user_asset.update_recharge_order_status(self.db, order_id, "completed")
            
            # 增加用户钻石
            success = self.crud_user_asset.add_diamonds(
                self.db, 
                order.user_id, 
                order.diamond_count,
                f"充值获得，订单号：{order_id}"
            )
            
            return success
        except Exception as e:
            print(f"处理支付回调失败: {e}")
            return False

    async def purchase_tutor_service(
        self, 
        user_id: int, 
        tutor_id: int, 
        service_id: int
    ) -> TutorServiceOrderResponse:
        """处理服务购买逻辑（校验钻石余额、扣减钻石、生成订单）"""
        try:
            # 获取服务价格信息
            service_price = await self.tutor_service.get_tutor_service_price(tutor_id, service_id)
            if not service_price:
                raise Exception("服务不存在或不可用")
            
            # 检查用户钻石余额
            user_asset = self.crud_user_asset.get_asset_by_user_id(self.db, user_id)
            if not user_asset or user_asset.diamond_count < service_price["price"]:
                raise Exception("钻石余额不足")
            
            # 开始数据库事务
            try:
                # 扣减钻石
                deduct_success = self.crud_user_asset.deduct_diamonds(
                    self.db, 
                    user_id, 
                    service_price["price"]
                )
                
                if not deduct_success:
                    raise Exception("钻石扣减失败")
                
                # 创建订单
                order_id = await self.crud_tutor_service_order.create_order(
                    self.db,
                    user_id=user_id,
                    tutor_id=tutor_id,
                    service_id=service_id,
                    amount=service_price["price"],
                    currency="diamonds",
                    service_name=service_price["name"]
                )
                
                # 提交事务
                self.db.commit()
                
                return TutorServiceOrderResponse(
                    order_id=order_id,
                    user_id=user_id,
                    tutor_id=tutor_id,
                    service_id=service_id,
                    service_name=service_price["name"],
                    amount=service_price["price"],
                    currency="diamonds",
                    status="completed",
                    created_at=datetime.now()
                )
                
            except Exception as e:
                # 回滚事务
                self.db.rollback()
                raise e
                
        except Exception as e:
            raise Exception(f"购买导师服务失败: {str(e)}")

    async def get_tutor_service_orders(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> List[TutorServiceOrderResponse]:
        """查询用户的导师服务订单历史"""
        try:
            orders = await self.crud_tutor_service_order.get_orders_by_user(
                self.db,
                user_id=user_id,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            result = []
            for order in orders:
                result.append(TutorServiceOrderResponse(
                    order_id=order.order_id,
                    user_id=order.user_id,
                    tutor_id=order.tutor_id,
                    service_id=order.service_id,
                    service_name=order.service_name,
                    amount=order.amount,
                    currency=order.currency,
                    status=order.status,
                    created_at=order.created_at
                ))
            
            return result
        except Exception as e:
            raise Exception(f"获取导师服务订单失败: {str(e)}") 