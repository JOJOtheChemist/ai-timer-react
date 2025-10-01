from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_current_user
from models.schemas.user import PersonalPageResponse
from services.user.user_profile_service import UserProfileService
from services.user.user_asset_service import UserAssetService
from services.user.user_relation_service import UserRelationService
from services.badge.badge_service import BadgeService

router = APIRouter()

@router.get("/me/personal-page", response_model=PersonalPageResponse)
async def get_personal_page(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个人主页综合数据（个人信息、资产、关系、统计）"""
    try:
        user_id = current_user["id"]
        
        # 并行获取各种数据
        user_profile_service = UserProfileService(db)
        user_asset_service = UserAssetService(db)
        user_relation_service = UserRelationService(db)
        badge_service = BadgeService(db)
        
        # 获取用户个人信息
        profile = await user_profile_service.get_current_user_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户个人信息不存在"
            )
        
        # 获取用户资产信息
        assets = await user_asset_service.get_user_assets(user_id)
        if not assets:
            assets = await user_asset_service.create_default_assets(user_id)
        
        # 获取用户关系统计
        relations = await user_relation_service.get_relation_stats(user_id)
        
        # 获取用户统计信息（从profile中提取）
        from models.schemas.user import UserStatsResponse
        stats = UserStatsResponse(
            user_id=user_id,
            total_study_hours=profile.total_study_hours,
            total_study_days=0,  # 需要从统计服务获取
            total_moments=profile.total_moments,
            total_badges=profile.total_badges,
            total_likes_received=0,  # 需要从动态服务获取
            total_comments_received=0,  # 需要从动态服务获取
            week_study_hours=0,  # 需要从统计服务获取
            week_study_days=0,  # 需要从统计服务获取
            study_hours_rank=None,  # 需要从排行榜服务获取
            badge_count_rank=None  # 需要从排行榜服务获取
        )
        
        # 构建综合响应
        personal_page = PersonalPageResponse(
            profile=profile,
            assets=assets,
            relations=relations,
            stats=stats
        )
        
        return personal_page
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取个人主页数据失败: {str(e)}"
        )

@router.get("/me/dashboard-summary")
async def get_dashboard_summary(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取个人主页仪表板摘要数据（轻量级）"""
    try:
        user_id = current_user["id"]
        
        user_profile_service = UserProfileService(db)
        user_asset_service = UserAssetService(db)
        user_relation_service = UserRelationService(db)
        badge_service = BadgeService(db)
        
        # 获取基础信息
        profile = await user_profile_service.get_current_user_profile(user_id)
        assets = await user_asset_service.get_user_assets(user_id)
        relations = await user_relation_service.get_relation_stats(user_id)
        
        # 获取最近获得的徽章（前3个）
        user_badges = await badge_service.get_user_badges(user_id)
        recent_badges = [badge for badge in user_badges.badges if badge.is_obtained][:3]
        
        # 构建摘要响应
        summary = {
            "user_info": {
                "username": profile.username if profile else "未知用户",
                "avatar": profile.avatar if profile else None,
                "goal": profile.goal if profile else None
            },
            "quick_stats": {
                "study_hours": float(profile.total_study_hours) if profile else 0,
                "diamond_count": assets.diamond_count if assets else 0,
                "fan_count": relations.fan_count,
                "badge_count": profile.total_badges if profile else 0
            },
            "recent_badges": [
                {
                    "name": badge.name,
                    "icon": badge.icon,
                    "level": badge.level,
                    "obtain_date": badge.obtain_date.isoformat() if badge.obtain_date else None
                }
                for badge in recent_badges
            ],
            "quick_actions": [
                {"name": "学习记录", "icon": "📚", "path": "/schedule"},
                {"name": "发布动态", "icon": "✍️", "path": "/moments/create"},
                {"name": "查看徽章", "icon": "🏆", "path": "/badges"},
                {"name": "充值钻石", "icon": "💎", "path": "/shop"}
            ]
        }
        
        return summary
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取仪表板摘要失败: {str(e)}"
        ) 