from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime

from models.schemas.moment import (
    MomentListResponse, MomentResponse, MomentCreate, MomentUpdate,
    MomentTypeEnum, HotTypeEnum, MomentFilterParams, UserInfo,
    AttachmentInfo, MomentStats, DynamicCreate, DryGoodsCreate
)
from crud.moment.crud_moment import crud_moment
from crud.moment.crud_moment_interaction import crud_moment_interaction

class MomentService:
    """动态服务层"""
    
    def get_moment_list(
        self,
        db: Session,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_id: Optional[int] = None
    ) -> MomentListResponse:
        """按类型查询内容列表（动态/干货），包含置顶广告"""
        # 获取动态列表
        moments, total = crud_moment.get_multi_by_type(db, moment_type, page, page_size)
        
        # 如果是第一页且类型为动态，添加置顶广告
        if page == 1 and (moment_type is None or moment_type == MomentTypeEnum.DYNAMIC):
            top_ad = crud_moment.get_top_ad(db)
            if top_ad:
                moments.insert(0, top_ad)
        
        # 转换为响应模型
        moment_responses = []
        for moment in moments:
            moment_response = self._convert_to_response(db, moment, current_user_id)
            moment_responses.append(moment_response)
        
        return MomentListResponse(
            moments=moment_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def get_filtered_moments(
        self,
        db: Session,
        moment_type: Optional[MomentTypeEnum] = None,
        filters: Optional[MomentFilterParams] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_id: Optional[int] = None
    ) -> MomentListResponse:
        """按筛选条件查询内容"""
        # 解析筛选参数
        filter_dict = self.parse_filter_params(filters) if filters else {}
        
        # 获取筛选后的动态列表
        moments, total = crud_moment.get_multi_by_filters(
            db, moment_type, filter_dict, page, page_size
        )
        
        # 转换为响应模型
        moment_responses = []
        for moment in moments:
            moment_response = self._convert_to_response(db, moment, current_user_id)
            moment_responses.append(moment_response)
        
        return MomentListResponse(
            moments=moment_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def search_moments(
        self,
        db: Session,
        keyword: str,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_id: Optional[int] = None
    ) -> MomentListResponse:
        """处理搜索逻辑（多字段模糊匹配，去重）"""
        # 执行搜索
        moments, total = crud_moment.search_by_keyword(db, keyword, moment_type, page, page_size)
        
        # 转换为响应模型
        moment_responses = []
        for moment in moments:
            moment_response = self._convert_to_response(db, moment, current_user_id)
            moment_responses.append(moment_response)
        
        return MomentListResponse(
            moments=moment_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def create_dynamic(self, db: Session, user_id: int, dynamic_data: DynamicCreate) -> MomentResponse:
        """发布动态（校验内容长度、标签格式）"""
        # 校验内容长度
        if len(dynamic_data.content) > 5000:
            raise ValueError("动态内容不能超过5000字符")
        
        # 校验标签格式
        if len(dynamic_data.tags) > 10:
            raise ValueError("标签数量不能超过10个")
        
        for tag in dynamic_data.tags:
            if len(tag) > 20:
                raise ValueError("单个标签长度不能超过20字符")
        
        # 创建动态数据
        moment_create = MomentCreate(
            moment_type=MomentTypeEnum.DYNAMIC,
            content=dynamic_data.content,
            tags=dynamic_data.tags
        )
        
        # 保存到数据库
        db_moment = crud_moment.create(db, user_id, moment_create)
        
        # 转换为响应模型
        return self._convert_to_response(db, db_moment, user_id)
    
    def create_dry_goods(self, db: Session, user_id: int, dry_goods_data: DryGoodsCreate) -> MomentResponse:
        """发布干货（校验标题、附件关联合法性）"""
        # 校验标题
        if not dry_goods_data.title or len(dry_goods_data.title.strip()) == 0:
            raise ValueError("干货标题不能为空")
        
        if len(dry_goods_data.title) > 200:
            raise ValueError("干货标题不能超过200字符")
        
        # 校验内容长度
        if len(dry_goods_data.content) > 5000:
            raise ValueError("干货内容不能超过5000字符")
        
        # 校验附件
        if len(dry_goods_data.attachments) > 20:
            raise ValueError("附件数量不能超过20个")
        
        # 校验附件关联合法性
        for attachment in dry_goods_data.attachments:
            if not self._validate_attachment(attachment):
                raise ValueError(f"附件格式不正确: {attachment}")
        
        # 创建干货数据
        moment_create = MomentCreate(
            moment_type=MomentTypeEnum.DRY_GOODS,
            title=dry_goods_data.title,
            content=dry_goods_data.content,
            tags=dry_goods_data.tags,
            attachments=dry_goods_data.attachments
        )
        
        # 保存到数据库
        db_moment = crud_moment.create(db, user_id, moment_create)
        
        # 转换为响应模型
        return self._convert_to_response(db, db_moment, user_id)
    
    def get_moment_by_id(
        self, 
        db: Session, 
        moment_id: int, 
        current_user_id: Optional[int] = None
    ) -> Optional[MomentResponse]:
        """获取单个动态详情"""
        db_moment = crud_moment.get_by_id(db, moment_id)
        if not db_moment:
            return None
        
        # 记录浏览
        if current_user_id:
            crud_moment_interaction.record_view(db, moment_id, current_user_id)
        
        return self._convert_to_response(db, db_moment, current_user_id)
    
    def update_moment(
        self, 
        db: Session, 
        moment_id: int, 
        user_id: int, 
        moment_data: MomentUpdate
    ) -> Optional[MomentResponse]:
        """更新动态"""
        # 校验更新数据
        if moment_data.content and len(moment_data.content) > 5000:
            raise ValueError("内容不能超过5000字符")
        
        if moment_data.title and len(moment_data.title) > 200:
            raise ValueError("标题不能超过200字符")
        
        if moment_data.tags and len(moment_data.tags) > 10:
            raise ValueError("标签数量不能超过10个")
        
        # 更新动态
        db_moment = crud_moment.update(db, moment_id, user_id, moment_data)
        if not db_moment:
            return None
        
        return self._convert_to_response(db, db_moment, user_id)
    
    def delete_moment(self, db: Session, moment_id: int, user_id: int) -> bool:
        """删除动态"""
        return crud_moment.delete(db, moment_id, user_id)
    
    def get_user_moments(
        self,
        db: Session,
        user_id: int,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10,
        current_user_id: Optional[int] = None
    ) -> MomentListResponse:
        """获取用户发布的动态"""
        moments, total = crud_moment.get_user_moments(db, user_id, moment_type, page, page_size)
        
        # 转换为响应模型
        moment_responses = []
        for moment in moments:
            moment_response = self._convert_to_response(db, moment, current_user_id)
            moment_responses.append(moment_response)
        
        return MomentListResponse(
            moments=moment_responses,
            total=total,
            page=page,
            page_size=page_size,
            has_next=page * page_size < total
        )
    
    def get_popular_tags(self, db: Session, limit: int = 20) -> List[Dict[str, Any]]:
        """获取热门标签"""
        tags = crud_moment.get_popular_tags(db, limit)
        
        return [
            {
                "tag_name": tag.tag_name,
                "use_count": tag.use_count,
                "tag_type": tag.tag_type
            }
            for tag in tags
        ]
    
    def parse_filter_params(self, filter_params: MomentFilterParams) -> Dict[str, Any]:
        """解析筛选参数（如time_range转换为数据库时间条件，hot_type转换为排序规则）"""
        filters = {}
        
        if filter_params.tags:
            filters['tags'] = filter_params.tags
        
        if filter_params.time_range:
            filters['time_range'] = filter_params.time_range
        
        if filter_params.hot_type:
            filters['hot_type'] = filter_params.hot_type
        
        if filter_params.user_id:
            filters['user_id'] = filter_params.user_id
        
        return filters
    
    def _convert_to_response(
        self, 
        db: Session, 
        moment, 
        current_user_id: Optional[int] = None
    ) -> MomentResponse:
        """转换数据库模型为响应模型"""
        # 获取用户信息
        user_info = self._get_user_info(db, moment.user_id)
        
        # 获取附件信息
        attachments = self._get_attachment_info(moment.attachments)
        
        # 获取统计信息
        stats = MomentStats(
            like_count=moment.like_count,
            comment_count=moment.comment_count,
            share_count=moment.share_count,
            bookmark_count=moment.bookmark_count,
            view_count=moment.view_count
        )
        
        # 获取用户互动状态
        is_liked = False
        is_bookmarked = False
        if current_user_id:
            interaction_status = crud_moment_interaction.get_user_interaction_status(
                db, current_user_id, moment.id
            )
            is_liked = interaction_status.get('is_liked', False)
            is_bookmarked = interaction_status.get('is_bookmarked', False)
        
        return MomentResponse(
            id=moment.id,
            user=user_info,
            moment_type=MomentTypeEnum(moment.moment_type),
            title=moment.title,
            content=moment.content,
            tags=moment.tags or [],
            attachments=attachments,
            stats=stats,
            is_top=bool(moment.is_top),
            create_time=moment.create_time,
            update_time=moment.update_time,
            is_liked=is_liked,
            is_bookmarked=is_bookmarked
        )
    
    def _get_user_info(self, db: Session, user_id: int) -> UserInfo:
        """自动拼接用户基础信息（头像、名称）"""
        # 这里应该调用用户服务获取用户信息
        # 目前返回模拟数据
        return UserInfo(
            user_id=user_id,
            username=f"user_{user_id}",
            nickname=f"用户{user_id}",
            avatar=f"/avatars/user_{user_id}.png"
        )
    
    def _get_attachment_info(self, attachments: List[Dict[str, Any]]) -> List[AttachmentInfo]:
        """获取附件信息"""
        if not attachments:
            return []
        
        attachment_list = []
        for attachment in attachments:
            attachment_info = AttachmentInfo(
                attachment_type=attachment.get('type', 'file'),
                attachment_id=attachment.get('id'),
                attachment_url=attachment.get('url'),
                attachment_name=attachment.get('name'),
                attachment_size=attachment.get('size')
            )
            attachment_list.append(attachment_info)
        
        return attachment_list
    
    def _validate_attachment(self, attachment: Dict[str, Any]) -> bool:
        """校验附件格式"""
        required_fields = ['type']
        
        # 检查必需字段
        for field in required_fields:
            if field not in attachment:
                return False
        
        # 检查附件类型
        valid_types = ['schedule', 'file', 'image', 'link']
        if attachment['type'] not in valid_types:
            return False
        
        # 根据类型检查特定字段
        if attachment['type'] in ['schedule'] and not attachment.get('id'):
            return False
        
        if attachment['type'] in ['file', 'image'] and not attachment.get('url'):
            return False
        
        if attachment['type'] == 'link' and not attachment.get('url'):
            return False
        
        return True

# 创建服务实例
moment_service = MomentService() 