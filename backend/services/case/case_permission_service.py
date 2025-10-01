from typing import List, Optional
from sqlalchemy.orm import Session
from datetime import datetime

from crud.case.crud_case_permission import CRUDCasePermission
from crud.user.crud_user_asset import CRUDUserAsset
from models.schemas.case import (
    CasePermissionResponse,
    CasePurchaseRequest,
    CasePurchaseResponse
)

class CasePermissionService:
    def __init__(self, db: Session):
        self.db = db
        self.crud_permission = CRUDCasePermission()
        self.crud_user_asset = CRUDUserAsset()

    async def get_case_permission(self, case_id: int, user_id: int) -> Optional[CasePermissionResponse]:
        """获取案例的预览权限和价格信息"""
        try:
            # 获取案例权限配置
            permission_info = await self.crud_permission.get_permission_info(self.db, case_id)
            
            if not permission_info:
                return None
            
            # 检查用户是否已购买
            has_purchased = await self.crud_permission.check_user_purchased(
                self.db, case_id, user_id
            )
            
            # 检查是否为案例作者
            is_author = await self.crud_permission.check_is_author(
                self.db, case_id, user_id
            )
            
            return CasePermissionResponse(
                case_id=case_id,
                preview_days=permission_info.preview_days,
                price=permission_info.price,
                currency=permission_info.currency,
                has_purchased=has_purchased,
                is_author=is_author,
                can_preview=True,  # 所有用户都可以预览
                purchase_required=not (has_purchased or is_author),
                preview_content_ratio=permission_info.preview_content_ratio,
                created_at=permission_info.created_at,
                updated_at=permission_info.updated_at
            )
        except Exception as e:
            raise Exception(f"获取案例权限信息失败: {str(e)}")

    async def purchase_case_access(
        self, 
        case_id: int, 
        user_id: int, 
        purchase_data: CasePurchaseRequest
    ) -> CasePurchaseResponse:
        """购买案例完整访问权限"""
        try:
            # 检查是否已购买
            has_purchased = await self.crud_permission.check_user_purchased(
                self.db, case_id, user_id
            )
            
            if has_purchased:
                return CasePurchaseResponse(
                    success=False,
                    message="您已购买过此案例",
                    order_id=None,
                    purchase_time=None
                )
            
            # 获取案例价格信息
            permission_info = await self.crud_permission.get_permission_info(self.db, case_id)
            
            if not permission_info:
                return CasePurchaseResponse(
                    success=False,
                    message="案例不存在",
                    order_id=None,
                    purchase_time=None
                )
            
            # 检查用户余额
            user_asset = await self.crud_user_asset.get_asset_by_user_id(self.db, user_id)
            
            if not user_asset or user_asset.diamonds < permission_info.price:
                return CasePurchaseResponse(
                    success=False,
                    message="钻石余额不足",
                    order_id=None,
                    purchase_time=None
                )
            
            # 执行购买
            purchase_time = datetime.now()
            order_id = await self.crud_permission.create_purchase_record(
                self.db,
                case_id=case_id,
                user_id=user_id,
                price=permission_info.price,
                currency=permission_info.currency,
                payment_method=purchase_data.payment_method,
                purchase_time=purchase_time
            )
            
            # 扣除钻石
            await self.crud_user_asset.deduct_diamonds(
                self.db, user_id, permission_info.price
            )
            
            return CasePurchaseResponse(
                success=True,
                message="购买成功",
                order_id=order_id,
                purchase_time=purchase_time
            )
        except Exception as e:
            raise Exception(f"购买案例访问权限失败: {str(e)}")

    async def check_case_access_status(self, case_id: int, user_id: int) -> dict:
        """检查用户对案例的访问状态"""
        try:
            # 检查是否为作者
            is_author = await self.crud_permission.check_is_author(
                self.db, case_id, user_id
            )
            
            if is_author:
                return {
                    "access_type": "author",
                    "can_view_full": True,
                    "message": "您是此案例的作者"
                }
            
            # 检查是否已购买
            has_purchased = await self.crud_permission.check_user_purchased(
                self.db, case_id, user_id
            )
            
            if has_purchased:
                return {
                    "access_type": "purchased",
                    "can_view_full": True,
                    "message": "您已购买此案例"
                }
            
            # 只能预览
            return {
                "access_type": "preview",
                "can_view_full": False,
                "message": "仅可预览，需购买查看完整内容"
            }
        except Exception as e:
            raise Exception(f"检查访问状态失败: {str(e)}")

    async def get_user_purchased_cases(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 20
    ) -> dict:
        """获取用户已购买的案例列表"""
        try:
            # 获取购买记录
            purchased_cases = await self.crud_permission.get_user_purchased_cases(
                self.db,
                user_id=user_id,
                skip=(page - 1) * page_size,
                limit=page_size
            )
            
            # 获取总数
            total_count = await self.crud_permission.count_user_purchased_cases(
                self.db, user_id
            )
            
            return {
                "cases": purchased_cases,
                "total": total_count,
                "page": page,
                "page_size": page_size,
                "total_pages": (total_count + page_size - 1) // page_size
            }
        except Exception as e:
            raise Exception(f"获取已购买案例失败: {str(e)}") 