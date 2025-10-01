from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import Optional, List

from core.database import get_db
from core.dependencies import get_current_user_dev
from models.schemas.moment import (
    MomentListResponse, MomentResponse, MomentCreate, MomentUpdate,
    MomentTypeEnum, HotTypeEnum, MomentFilterParams, SearchParams,
    DynamicCreate, DryGoodsCreate, PopularTagsResponse
)
from services.moment.moment_service import moment_service

router = APIRouter()

@router.get("", response_model=MomentListResponse)
async def get_moments(
    moment_type: Optional[MomentTypeEnum] = Query(None, description="内容类型：dynamic/dryGoods"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    # 筛选参数
    tags: Optional[List[str]] = Query(None, description="标签筛选"),
    time_range: Optional[str] = Query(None, description="时间范围：today/week/month/all"),
    hot_type: Optional[HotTypeEnum] = Query(None, description="热度排序类型"),
    user_id: Optional[int] = Query(None, description="用户筛选"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """
    获取内容列表（支持type参数：dynamic/dryGoods，默认dynamic）
    支持分页参数（page、page_size）
    复用GET /api/v1/moments接口，通过query参数传递筛选条件（tags、time_range、hot_type）
    """
    try:
        # 如果没有筛选条件，使用基础列表查询
        if not any([tags, time_range, hot_type, user_id]):
            moment_list = moment_service.get_moment_list(
                db=db,
                moment_type=moment_type,
                page=page,
                page_size=page_size,
                current_user_id=current_user_id
            )
        else:
            # 有筛选条件，使用筛选查询
            filters = MomentFilterParams(
                tags=tags,
                time_range=time_range,
                hot_type=hot_type,
                user_id=user_id
            )
            moment_list = moment_service.get_filtered_moments(
                db=db,
                moment_type=moment_type,
                filters=filters,
                page=page,
                page_size=page_size,
                current_user_id=current_user_id
            )
        
        return moment_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内容列表失败: {str(e)}")

@router.post("", response_model=MomentResponse)
async def create_moment(
    moment_data: MomentCreate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """
    发布内容（支持type参数区分动态/干货，请求体含对应字段）
    动态发布：需content、tags等；干货发布：额外需title、attachments等
    """
    try:
        # 根据类型调用不同的创建方法
        if moment_data.moment_type == MomentTypeEnum.DYNAMIC:
            dynamic_data = DynamicCreate(
                content=moment_data.content,
                tags=moment_data.tags
            )
            moment = moment_service.create_dynamic(db, current_user_id, dynamic_data)
        
        elif moment_data.moment_type == MomentTypeEnum.DRY_GOODS:
            if not moment_data.title:
                raise HTTPException(status_code=400, detail="干货标题不能为空")
            
            dry_goods_data = DryGoodsCreate(
                title=moment_data.title,
                content=moment_data.content,
                tags=moment_data.tags,
                attachments=moment_data.attachments
            )
            moment = moment_service.create_dry_goods(db, current_user_id, dry_goods_data)
        
        else:
            raise HTTPException(status_code=400, detail="不支持的内容类型")
        
        return moment
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"发布内容失败: {str(e)}")

@router.get("/search", response_model=MomentListResponse)
async def search_moments(
    keyword: str = Query(..., min_length=1, description="搜索关键词"),
    moment_type: Optional[MomentTypeEnum] = Query(None, description="内容类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """按关键词搜索内容（支持keyword参数，匹配title、content、tags、user_name）"""
    try:
        moment_list = moment_service.search_moments(
            db=db,
            keyword=keyword,
            moment_type=moment_type,
            page=page,
            page_size=page_size,
            current_user_id=current_user_id
        )
        
        return moment_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"搜索内容失败: {str(e)}")

@router.get("/{moment_id}", response_model=MomentResponse)
async def get_moment_detail(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取单个动态详情"""
    try:
        moment = moment_service.get_moment_by_id(db, moment_id, current_user_id)
        
        if not moment:
            raise HTTPException(status_code=404, detail="内容不存在")
        
        return moment
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取内容详情失败: {str(e)}")

@router.put("/{moment_id}", response_model=MomentResponse)
async def update_moment(
    moment_id: int,
    moment_data: MomentUpdate,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """更新动态"""
    try:
        moment = moment_service.update_moment(db, moment_id, current_user_id, moment_data)
        
        if not moment:
            raise HTTPException(status_code=404, detail="内容不存在或无权限修改")
        
        return moment
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"更新内容失败: {str(e)}")

@router.delete("/{moment_id}")
async def delete_moment(
    moment_id: int,
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """删除动态"""
    try:
        success = moment_service.delete_moment(db, moment_id, current_user_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="内容不存在或无权限删除")
        
        return {"success": True, "message": "内容删除成功"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除内容失败: {str(e)}")

@router.get("/user/{user_id}", response_model=MomentListResponse)
async def get_user_moments(
    user_id: int = Path(..., description="用户ID"),
    moment_type: Optional[MomentTypeEnum] = Query(None, description="内容类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取用户发布的动态"""
    try:
        moment_list = moment_service.get_user_moments(
            db=db,
            user_id=user_id,
            moment_type=moment_type,
            page=page,
            page_size=page_size,
            current_user_id=current_user_id
        )
        
        return moment_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取用户内容失败: {str(e)}")

@router.get("/tags/popular", response_model=PopularTagsResponse)
async def get_popular_tags(
    limit: int = Query(20, ge=1, le=100, description="标签数量限制"),
    db: Session = Depends(get_db)
):
    """获取热门标签"""
    try:
        tags = moment_service.get_popular_tags(db, limit)
        
        return PopularTagsResponse(
            tags=[
                {
                    "tag_name": tag["tag_name"],
                    "use_count": tag["use_count"],
                    "tag_type": tag["tag_type"]
                }
                for tag in tags
            ],
            total=len(tags)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门标签失败: {str(e)}")

@router.get("/me/published", response_model=MomentListResponse)
async def get_my_moments(
    moment_type: Optional[MomentTypeEnum] = Query(None, description="内容类型筛选"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(10, ge=1, le=50, description="每页大小"),
    db: Session = Depends(get_db),
    current_user_id: int = Depends(get_current_user_dev)
):
    """获取我发布的动态"""
    try:
        moment_list = moment_service.get_user_moments(
            db=db,
            user_id=current_user_id,
            moment_type=moment_type,
            page=page,
            page_size=page_size,
            current_user_id=current_user_id
        )
        
        return moment_list
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取我的内容失败: {str(e)}")

@router.get("/health")
async def health_check():
    """动态服务健康检查"""
    return {"status": "healthy", "service": "moment_service"} 