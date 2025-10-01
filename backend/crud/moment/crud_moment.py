from sqlalchemy.orm import Session
from sqlalchemy import and_, desc, func, or_, cast, Text
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime, timedelta

from models.moment import Moment, MomentAttachment
from models.schemas.moment import MomentCreate, MomentUpdate, MomentTypeEnum, HotTypeEnum

class CRUDMoment:
    """动态CRUD操作"""
    
    def create(self, db: Session, user_id: int, moment_data: MomentCreate) -> Moment:
        """
        创建动态/干货
        将枚举类型转换为数据库整数值
        """
        db_moment = Moment(
            user_id=user_id,
            type=MomentTypeEnum.to_db_value(moment_data.moment_type),  # 枚举 → 整数
            title=moment_data.title,
            content=moment_data.content,
            image_url=moment_data.image_url,
            tags=moment_data.tags,
            status=1  # 默认已发布
        )
        db.add(db_moment)
        db.commit()
        db.refresh(db_moment)
        
        # 保存附件关联（干货专用）
        if moment_data.attachments:
            self.save_attachments(db, db_moment.id, moment_data.attachments)
        
        return db_moment
    
    def get_multi_by_type(
        self,
        db: Session,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Moment], int]:
        """按类型查询动态列表"""
        query = db.query(Moment).filter(Moment.status == 1)  # status=1 表示已发布
        
        if moment_type:
            type_value = MomentTypeEnum.to_db_value(moment_type)
            query = query.filter(Moment.type == type_value)
        
        # 获取总数
        total = query.count()
        
        # 分页查询，置顶内容优先，然后按时间倒序
        moments = query.order_by(
            desc(Moment.is_top),
            desc(Moment.create_time)
        ).offset((page - 1) * page_size).limit(page_size).all()
        
        return moments, total
    
    def get_multi_by_filters(
        self,
        db: Session,
        moment_type: Optional[MomentTypeEnum] = None,
        filters: Optional[Dict[str, Any]] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Moment], int]:
        """按筛选条件查询（标签、时间范围、热度排序）"""
        query = db.query(Moment).filter(Moment.status == 1)
        
        if moment_type:
            type_value = MomentTypeEnum.to_db_value(moment_type)
            query = query.filter(Moment.type == type_value)
        
        if filters:
            # 标签筛选（JSONB数组包含查询）
            if filters.get('tags'):
                for tag in filters['tags']:
                    # PostgreSQL JSONB 包含查询
                    query = query.filter(Moment.tags.contains([tag]))
            
            # 时间范围筛选
            if filters.get('time_range'):
                time_range = filters['time_range']
                now = datetime.now()
                
                if time_range == 'today':
                    start_time = now.replace(hour=0, minute=0, second=0, microsecond=0)
                    query = query.filter(Moment.create_time >= start_time)
                elif time_range == 'week':
                    start_time = now - timedelta(days=7)
                    query = query.filter(Moment.create_time >= start_time)
                elif time_range == 'month':
                    start_time = now - timedelta(days=30)
                    query = query.filter(Moment.create_time >= start_time)
            
            # 用户筛选
            if filters.get('user_id'):
                query = query.filter(Moment.user_id == filters['user_id'])
            
            # 热度排序
            hot_type = filters.get('hot_type', HotTypeEnum.LATEST)
            if hot_type == HotTypeEnum.HOT:
                # 综合热度：点赞数 * 2 + 评论数 * 3 + 分享数 * 1.5
                query = query.order_by(
                    desc(Moment.like_count * 2 + Moment.comment_count * 3 + Moment.share_count * 1.5),
                    desc(Moment.create_time)
                )
            elif hot_type == HotTypeEnum.MOST_LIKED:
                query = query.order_by(desc(Moment.like_count), desc(Moment.create_time))
            elif hot_type == HotTypeEnum.MOST_COMMENTED:
                query = query.order_by(desc(Moment.comment_count), desc(Moment.create_time))
            else:  # LATEST
                query = query.order_by(desc(Moment.is_top), desc(Moment.create_time))
        else:
            # 默认排序
            query = query.order_by(desc(Moment.is_top), desc(Moment.create_time))
        
        # 获取总数
        total = query.count()
        
        # 分页
        moments = query.offset((page - 1) * page_size).limit(page_size).all()
        
        return moments, total
    
    def search_by_keyword(
        self,
        db: Session,
        keyword: str,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Moment], int]:
        """关键词搜索（标题、内容、标签）"""
        query = db.query(Moment).filter(Moment.status == 1)
        
        if moment_type:
            type_value = MomentTypeEnum.to_db_value(moment_type)
            query = query.filter(Moment.type == type_value)
        
        # 关键词搜索：标题、内容
        search_conditions = [
            Moment.content.contains(keyword)
        ]
        
        # 搜索标题（可能为NULL）
        if keyword:
            search_conditions.append(Moment.title.contains(keyword))
        
        # 标签搜索（JSONB转文本后搜索）
        search_conditions.append(
            cast(Moment.tags, Text).contains(keyword)
        )
        
        query = query.filter(or_(*search_conditions))
        
        # 获取总数
        total = query.count()
        
        # 按相关性排序（这里简化为按时间排序）
        moments = query.order_by(desc(Moment.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size).all()
        
        return moments, total
    
    def get_top_ad(self, db: Session) -> Optional[Moment]:
        """查询置顶广告内容"""
        return db.query(Moment).filter(
            and_(
                Moment.type == 2,  # type=2 表示广告
                Moment.is_top == 1,
                Moment.status == 1
            )
        ).first()
    
    def get_by_id(self, db: Session, moment_id: int) -> Optional[Moment]:
        """根据ID获取动态"""
        return db.query(Moment).filter(
            and_(
                Moment.id == moment_id,
                Moment.status == 1
            )
        ).first()
    
    def update(self, db: Session, moment_id: int, user_id: int, moment_data: MomentUpdate) -> Optional[Moment]:
        """更新动态"""
        db_moment = db.query(Moment).filter(
            and_(
                Moment.id == moment_id,
                Moment.user_id == user_id,
                Moment.status == 1
            )
        ).first()
        
        if not db_moment:
            return None
        
        update_data = moment_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_moment, field) and value is not None:
                setattr(db_moment, field, value)
        
        # 更新附件
        if 'attachments' in update_data and update_data['attachments'] is not None:
            self.update_attachments(db, moment_id, update_data['attachments'])
        
        db.commit()
        db.refresh(db_moment)
        return db_moment
    
    def delete(self, db: Session, moment_id: int, user_id: int) -> bool:
        """删除动态（软删除）"""
        db_moment = db.query(Moment).filter(
            and_(
                Moment.id == moment_id,
                Moment.user_id == user_id,
                Moment.status == 1
            )
        ).first()
        
        if not db_moment:
            return False
        
        db_moment.status = 2  # status=2 表示已删除
        db.commit()
        return True
    
    def save_attachments(self, db: Session, moment_id: int, attachments: List[Dict[str, Any]]):
        """保存干货的附件关联（如时间表ID、文件ID）"""
        for attachment_data in attachments:
            db_attachment = MomentAttachment(
                moment_id=moment_id,
                attachment_type=attachment_data.get('type', 'file'),
                attachment_id=attachment_data.get('id'),
                attachment_url=attachment_data.get('url'),
                attachment_name=attachment_data.get('name'),
                attachment_size=attachment_data.get('size')
            )
            db.add(db_attachment)
        
        db.commit()
    
    def update_attachments(self, db: Session, moment_id: int, attachments: List[Dict[str, Any]]):
        """更新附件"""
        # 删除旧附件
        db.query(MomentAttachment).filter(MomentAttachment.moment_id == moment_id).delete()
        
        # 保存新附件
        if attachments:
            self.save_attachments(db, moment_id, attachments)
    
    def get_user_moments(
        self,
        db: Session,
        user_id: int,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Moment], int]:
        """获取用户发布的动态"""
        query = db.query(Moment).filter(
            and_(
                Moment.user_id == user_id,
                Moment.status == 1
            )
        )
        
        if moment_type:
            type_value = MomentTypeEnum.to_db_value(moment_type)
            query = query.filter(Moment.type == type_value)
        
        total = query.count()
        
        moments = query.order_by(desc(Moment.create_time))\
                      .offset((page - 1) * page_size)\
                      .limit(page_size).all()
        
        return moments, total
    
    def increment_view_count(self, db: Session, moment_id: int):
        """增加浏览次数"""
        db.query(Moment).filter(Moment.id == moment_id).update({
            "view_count": Moment.view_count + 1
        })
        db.commit()

# 创建CRUD实例
crud_moment = CRUDMoment() 