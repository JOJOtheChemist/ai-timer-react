from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, desc, func
from typing import List, Optional
from datetime import datetime

from models.task import Task, Subtask
from models.schemas.task import TaskCreate, TaskUpdate, TaskQuickCreate, TaskType

class CRUDTask:
    """任务CRUD操作"""
    
    def create(self, db: Session, user_id: int, task_data: TaskCreate) -> Task:
        """创建任务"""
        # 创建主任务
        db_task = Task(
            user_id=user_id,
            name=task_data.name,
            type=task_data.type.value,
            category=task_data.category,
            weekly_hours=task_data.weekly_hours,
            is_high_frequency=1 if task_data.is_high_frequency else 0,
            is_overcome=1 if task_data.is_overcome else 0
        )
        db.add(db_task)
        db.flush()  # 获取task_id
        
        # 创建子任务
        for subtask_data in task_data.subtasks:
            db_subtask = Subtask(
                task_id=db_task.id,
                user_id=user_id,
                name=subtask_data.name,
                hours=subtask_data.hours,
                is_high_frequency=1 if subtask_data.is_high_frequency else 0,
                is_overcome=1 if subtask_data.is_overcome else 0
            )
            db.add(db_subtask)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def quick_create(self, db: Session, user_id: int, task_data: TaskQuickCreate) -> Task:
        """快捷创建任务"""
        db_task = Task(
            user_id=user_id,
            name=task_data.name,
            type=task_data.type.value if task_data.type else TaskType.STUDY.value,
            category=task_data.category,
            weekly_hours=0.0,
            is_high_frequency=0,
            is_overcome=0
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def get_multi_by_user(
        self, 
        db: Session, 
        user_id: int, 
        category: Optional[str] = None,
        task_type: Optional[TaskType] = None,
        skip: int = 0, 
        limit: int = 100
    ) -> tuple[List[Task], int]:
        """获取用户任务列表"""
        query = db.query(Task).filter(Task.user_id == user_id)
        
        if category:
            query = query.filter(Task.category == category)
        
        if task_type:
            query = query.filter(Task.type == task_type.value)
        
        # 获取总数
        total = query.count()
        
        # 分页查询，包含子任务
        tasks = query.options(joinedload(Task.subtasks))\
                    .order_by(desc(Task.update_time))\
                    .offset(skip)\
                    .limit(limit)\
                    .all()
        
        return tasks, total
    
    def get_multi_by_category(
        self, 
        db: Session, 
        user_id: int, 
        category: str
    ) -> List[Task]:
        """按分类获取任务"""
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.category == category
            )
        ).options(joinedload(Task.subtasks)).all()
    
    def get_by_id(self, db: Session, task_id: int, user_id: int) -> Optional[Task]:
        """根据ID获取任务"""
        return db.query(Task).filter(
            and_(
                Task.id == task_id,
                Task.user_id == user_id
            )
        ).options(joinedload(Task.subtasks)).first()
    
    def update(self, db: Session, task_id: int, user_id: int, task_data: TaskUpdate) -> Optional[Task]:
        """更新任务"""
        db_task = self.get_by_id(db, task_id, user_id)
        if not db_task:
            return None
        
        update_data = task_data.dict(exclude_unset=True)
        
        # 处理枚举类型
        if 'type' in update_data and update_data['type']:
            update_data['type'] = update_data['type'].value
        
        # 处理布尔类型转换
        if 'is_high_frequency' in update_data:
            update_data['is_high_frequency'] = 1 if update_data['is_high_frequency'] else 0
        if 'is_overcome' in update_data:
            update_data['is_overcome'] = 1 if update_data['is_overcome'] else 0
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def update_expand_status(self, db: Session, task_id: int, is_expand: bool) -> Optional[Task]:
        """更新任务展开状态（这里可以添加一个字段来记录展开状态）"""
        # 注意：数据库模型中需要添加is_expanded字段，这里先简单返回任务
        return self.get_by_id(db, task_id, 0)  # 这里需要传入正确的user_id
    
    def delete(self, db: Session, task_id: int, user_id: int) -> bool:
        """删除任务"""
        db_task = self.get_by_id(db, task_id, user_id)
        if not db_task:
            return False
        
        db.delete(db_task)
        db.commit()
        return True
    
    def get_high_frequency_tasks(self, db: Session, user_id: int) -> List[Task]:
        """获取高频任务"""
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.is_high_frequency == 1
            )
        ).options(joinedload(Task.subtasks)).all()
    
    def get_overcome_tasks(self, db: Session, user_id: int) -> List[Task]:
        """获取待克服任务"""
        return db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.is_overcome == 1
            )
        ).options(joinedload(Task.subtasks)).all()
    
    def get_task_statistics(self, db: Session, user_id: int) -> dict:
        """获取任务统计信息"""
        total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
        high_freq_count = db.query(Task).filter(
            and_(Task.user_id == user_id, Task.is_high_frequency == 1)
        ).count()
        overcome_count = db.query(Task).filter(
            and_(Task.user_id == user_id, Task.is_overcome == 1)
        ).count()
        
        # 按类型统计
        type_stats = db.query(
            Task.type,
            func.count(Task.id).label('count'),
            func.sum(Task.weekly_hours).label('total_hours')
        ).filter(Task.user_id == user_id)\
         .group_by(Task.type)\
         .all()
        
        return {
            "total_tasks": total_tasks,
            "high_frequency_count": high_freq_count,
            "overcome_count": overcome_count,
            "type_statistics": [
                {
                    "type": stat.type,
                    "count": stat.count,
                    "total_hours": float(stat.total_hours) if stat.total_hours else 0.0
                }
                for stat in type_stats
            ]
        }

class CRUDSubtask:
    """子任务CRUD操作"""
    
    def create(self, db: Session, task_id: int, user_id: int, subtask_data: dict) -> Subtask:
        """创建子任务"""
        db_subtask = Subtask(
            task_id=task_id,
            user_id=user_id,
            **subtask_data
        )
        db.add(db_subtask)
        db.commit()
        db.refresh(db_subtask)
        return db_subtask
    
    def get_by_task(self, db: Session, task_id: int, user_id: int) -> List[Subtask]:
        """获取任务的所有子任务"""
        return db.query(Subtask).filter(
            and_(
                Subtask.task_id == task_id,
                Subtask.user_id == user_id
            )
        ).all()
    
    def update(self, db: Session, subtask_id: int, user_id: int, subtask_data: dict) -> Optional[Subtask]:
        """更新子任务"""
        db_subtask = db.query(Subtask).filter(
            and_(
                Subtask.id == subtask_id,
                Subtask.user_id == user_id
            )
        ).first()
        
        if not db_subtask:
            return None
        
        for field, value in subtask_data.items():
            if hasattr(db_subtask, field):
                setattr(db_subtask, field, value)
        
        db.commit()
        db.refresh(db_subtask)
        return db_subtask
    
    def delete(self, db: Session, subtask_id: int, user_id: int) -> bool:
        """删除子任务"""
        db_subtask = db.query(Subtask).filter(
            and_(
                Subtask.id == subtask_id,
                Subtask.user_id == user_id
            )
        ).first()
        
        if not db_subtask:
            return False
        
        db.delete(db_subtask)
        db.commit()
        return True

# 创建CRUD实例
crud_task = CRUDTask()
crud_subtask = CRUDSubtask() 