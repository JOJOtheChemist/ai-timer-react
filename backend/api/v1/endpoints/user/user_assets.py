from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from core.dependencies import get_db, get_current_user
from models.schemas.user import (
    UserAssetResponse, 
    RechargeRequest, 
    RechargeResponse,
    AssetRecordResponse,
    UserOperationResponse
)
from services.user.user_asset_service import UserAssetService

router = APIRouter()

@router.get("/me/assets", response_model=UserAssetResponse)
async def get_current_user_assets(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取当前用户的资产信息（钻石数量、消费记录）"""
    try:
        user_asset_service = UserAssetService(db)
        assets = await user_asset_service.get_user_assets(current_user["id"])
        
        if not assets:
            # 如果用户资产不存在，创建默认资产记录
            assets = await user_asset_service.create_default_assets(current_user["id"])
        
        return assets
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资产信息失败: {str(e)}"
        )

@router.post("/me/assets/recharge", response_model=RechargeResponse)
async def create_recharge_order(
    recharge_data: RechargeRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """发起钻石充值请求（生成充值订单/对接支付）"""
    try:
        user_asset_service = UserAssetService(db)
        recharge_order = await user_asset_service.create_recharge_order(
            current_user["id"], 
            recharge_data.amount,
            recharge_data.payment_method
        )
        
        if not recharge_order:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="创建充值订单失败"
            )
        
        return recharge_order
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建充值订单失败: {str(e)}"
        )

@router.get("/me/assets/records", response_model=List[AssetRecordResponse])
async def get_asset_records(
    limit: int = 10,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户资产变动记录"""
    try:
        user_asset_service = UserAssetService(db)
        records = await user_asset_service.get_asset_records(
            current_user["id"], 
            limit=limit, 
            offset=offset
        )
        
        return records
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取资产记录失败: {str(e)}"
        ) 