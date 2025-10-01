from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func, or_, text
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta

from models.moment import Moment, MomentAttachment, MomentTag
from models.schemas.moment import MomentCreate, MomentUpdate, MomentTypeEnum, HotTypeEnum

class CRUDMoment:
    """动态CRUD操作"""
    
    def create(self, db: Session, user_id: int, moment_data: MomentCreate) -> Moment:
        """保存内容到数据库（自动填充发布时间、用户ID）"""
        db_moment = Moment(
            user_id=user_id,
            moment_type=moment_data.moment_type.value,
            title=moment_data.title,
            content=moment_data.content,
            tags=moment_data.tags,
            attachments=moment_data.attachments
        )
        db.add(db_moment)
        db.commit()
        db.refresh(db_moment)
        
        # 保存附件关联
        if moment_data.attachments:
            self.save_attachments(db, db_moment.id, moment_data.attachments)
        
        # 更新标签使用次数
        if moment_data.tags:
            self.update_tag_usage(db, moment_data.tags)
        
        return db_moment
    
    def get_multi_by_type(
        self,
        db: Session,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[Moment], int]:
        """按类型从数据库查询内容"""
        query = db.query(Moment).filter(Moment.status == 'published')
        
        if moment_type:
            query = query.filter(Moment.moment_type == moment_type.value)
        
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
    ) -> tuple[List[Moment], int]:
        """按筛选条件执行数据库查询（标签匹配、时间范围、热度排序）"""
        query = db.query(Moment).filter(Moment.status == 'published')
        
        if moment_type:
            query = query.filter(Moment.moment_type == moment_type.value)
        
        if filters:
            # 标签筛选
            if filters.get('tags'):
                tags = filters['tags']
                # 使用JSON_CONTAINS或类似功能进行标签匹配
                for tag in tags:
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
    ) -> tuple[List[Moment], int]:
        """执行数据库模糊查询（关联用户表匹配用户名）"""
        # 基础查询
        query = db.query(Moment).filter(Moment.status == 'published')
        
        if moment_type:
            query = query.filter(Moment.moment_type == moment_type.value)
        
        # 关键词搜索：标题、内容、标签
        search_conditions = [
            Moment.content.contains(keyword)
        ]
        
        # 如果有标题，也搜索标题
        if keyword:
            search_conditions.append(Moment.title.contains(keyword))
        
        # 标签搜索（JSON数组中包含关键词）
        # 注意：这里的实现可能需要根据具体数据库调整
        try:
            search_conditions.append(
                func.json_search(Moment.tags, 'one', f'%{keyword}%').isnot(None)
            )
        except:
            # 如果数据库不支持json_search，使用简单的文本搜索
            search_conditions.append(
                func.cast(Moment.tags, text('TEXT')).contains(keyword)
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
                Moment.moment_type == 'ad',
                Moment.is_top == 1,
                Moment.status == 'published'
            )
        ).first()
    
    def get_by_id(self, db: Session, moment_id: int) -> Optional[Moment]:
        """根据ID获取动态"""
        return db.query(Moment).filter(
            and_(
                Moment.id == moment_id,
                Moment.status == 'published'
            )
        ).first()
    
    def update(self, db: Session, moment_id: int, user_id: int, moment_data: MomentUpdate) -> Optional[Moment]:
        """更新动态"""
        db_moment = db.query(Moment).filter(
            and_(
                Moment.id == moment_id,
                Moment.user_id == user_id
            )
        ).first()
        
        if not db_moment:
            return None
        
        update_data = moment_data.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            if hasattr(db_moment, field):
                setattr(db_moment, field, value)
        
        # 更新附件
        if 'attachments' in update_data:
            self.update_attachments(db, moment_id, update_data['attachments'])
        
        # 更新标签使用次数
        if 'tags' in update_data:
            self.update_tag_usage(db, update_data['tags'])
        
        db.commit()
        db.refresh(db_moment)
        return db_moment
    
    def delete(self, db: Session, moment_id: int, user_id: int) -> bool:
        """删除动态（软删除）"""
        db_moment = db.query(Moment).filter(
            and_(
                Moment.id == moment_id,
                Moment.user_id == user_id
            )
        ).first()
        
        if not db_moment:
            return False
        
        db_moment.status = 'deleted'
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
        self.save_attachments(db, moment_id, attachments)
    
    def update_tag_usage(self, db: Session, tags: List[str]):
        """更新标签使用次数"""
        for tag_name in tags:
            # 查找或创建标签
            db_tag = db.query(MomentTag).filter(MomentTag.tag_name == tag_name).first()
            
            if db_tag:
                db_tag.use_count += 1
            else:
                db_tag = MomentTag(tag_name=tag_name, use_count=1)
                db.add(db_tag)
        
        db.commit()
    
    def get_popular_tags(self, db: Session, limit: int = 20) -> List[MomentTag]:
        """获取热门标签"""
        return db.query(MomentTag).order_by(desc(MomentTag.use_count)).limit(limit).all()
    
    def get_user_moments(
        self,
        db: Session,
        user_id: int,
        moment_type: Optional[MomentTypeEnum] = None,
        page: int = 1,
        page_size: int = 10
    ) -> tuple[List[Moment], int]:
        """获取用户发布的动态"""
        query = db.query(Moment).filter(
            and_(
                Moment.user_id == user_id,
                Moment.status == 'published'
            )
        )
        
        if moment_type:
            query = query.filter(Moment.moment_type == moment_type.value)
        
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
    
    def get_moment_stats(self, db: Session) -> Dict[str, int]:
        """获取动态统计信息"""
        total_moments = db.query(func.count(Moment.id)).filter(Moment.status == 'published').scalar() or 0
        
        total_dynamics = db.query(func.count(Moment.id)).filter(
            and_(Moment.moment_type == 'dynamic', Moment.status == 'published')
        ).scalar() or 0
        
        total_dry_goods = db.query(func.count(Moment.id)).filter(
            and_(Moment.moment_type == 'dryGoods', Moment.status == 'published')
        ).scalar() or 0
        
        total_likes = db.query(func.sum(Moment.like_count)).filter(Moment.status == 'published').scalar() or 0
        total_comments = db.query(func.sum(Moment.comment_count)).filter(Moment.status == 'published').scalar() or 0
        total_shares = db.query(func.sum(Moment.share_count)).filter(Moment.status == 'published').scalar() or 0
        total_bookmarks = db.query(func.sum(Moment.bookmark_count)).filter(Moment.status == 'published').scalar() or 0
        
        return {
            "total_moments": total_moments,
            "total_dynamics": total_dynamics,
            "total_dry_goods": total_dry_goods,
            "total_likes": total_likes,
            "total_comments": total_comments,
            "total_shares": total_shares,
            "total_bookmarks": total_bookmarks
        }

# 创建CRUD实例
crud_moment = CRUDMoment() 