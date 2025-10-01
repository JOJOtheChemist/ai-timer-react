from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas.case import CasePermissionResponse, CasePurchaseRequest, CasePurchaseResponse
from services.case.case_permission_service import CasePermissionService

router = APIRouter()

@router.get("/{case_id}/permission", response_model=CasePermissionResponse)
async def get_case_permission(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取案例的预览权限和价格信息（含preview_days、price、currency等）"""
    try:
        permission_service = CasePermissionService(db)
        permission_info = await permission_service.get_case_permission(
            case_id=case_id,
            user_id=current_user["id"]
        )
        
        if not permission_info:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="案例不存在"
            )
        
        return permission_info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取案例权限信息失败: {str(e)}"
        )

@router.post("/{case_id}/purchase", response_model=CasePurchaseResponse)
async def purchase_case_access(
    case_id: int,
    purchase_data: CasePurchaseRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """购买案例完整访问权限"""
    try:
        permission_service = CasePermissionService(db)
        purchase_result = await permission_service.purchase_case_access(
            case_id=case_id,
            user_id=current_user["id"],
            purchase_data=purchase_data
        )
        
        return purchase_result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"购买案例访问权限失败: {str(e)}"
        )

@router.get("/{case_id}/access-status")
async def check_case_access_status(
    case_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """检查用户对案例的访问状态（免费预览/已购买/需购买）"""
    try:
        permission_service = CasePermissionService(db)
        access_status = await permission_service.check_case_access_status(
            case_id=case_id,
            user_id=current_user["id"]
        )
        
        return access_status
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检查访问状态失败: {str(e)}"
        )

@router.get("/my-purchased")
async def get_my_purchased_cases(
    page: int = 1,
    page_size: int = 20,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户已购买的案例列表"""
    try:
        permission_service = CasePermissionService(db)
        purchased_cases = await permission_service.get_user_purchased_cases(
            user_id=current_user["id"],
            page=page,
            page_size=page_size
        )
        
        return purchased_cases
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取已购买案例失败: {str(e)}"
        ) 