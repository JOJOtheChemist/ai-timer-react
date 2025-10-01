from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime, date

from crud.task.crud_task import crud_task, crud_subtask
from models.schemas.task import (
    TaskCreate, TaskUpdate, TaskQuickCreate, TaskListResponse,
    TaskResponse, SubtaskResponse, TaskType
)
from models.task import Task

class TaskService:
    """任务服务"""
    
    def get_task_list(
        self, 
        db: Session, 
        user_id: int, 
        category: Optional[str] = None,
        task_type: Optional[TaskType] = None,
        skip: int = 0,
        limit: int = 100
    ) -> TaskListResponse:
        """获取任务列表"""
        tasks, total = crud_task.get_multi_by_user(
            db=db,
            user_id=user_id,
            category=category,
            task_type=task_type,
            skip=skip,
            limit=limit
        )
        
        # 转换为响应模型
        task_responses = []
        for task in tasks:
            subtasks = [
                SubtaskResponse(
                    id=subtask.id,
                    task_id=subtask.task_id,
                    name=subtask.name,
                    hours=float(subtask.hours),
                    is_high_frequency=bool(subtask.is_high_frequency),
                    is_overcome=bool(subtask.is_overcome),
                    create_time=subtask.create_time,
                    update_time=subtask.update_time
                )
                for subtask in task.subtasks
            ]
            
            task_responses.append(TaskResponse(
                id=task.id,
                user_id=task.user_id,
                name=task.name,
                type=TaskType(task.type),
                category=task.category,
                weekly_hours=float(task.weekly_hours),
                is_high_frequency=bool(task.is_high_frequency),
                is_overcome=bool(task.is_overcome),
                subtasks=subtasks,
                create_time=task.create_time,
                update_time=task.update_time
            ))
        
        # 统计信息
        stats = crud_task.get_task_statistics(db, user_id)
        
        return TaskListResponse(
            tasks=task_responses,
            total=total,
            high_frequency_count=stats["high_frequency_count"],
            overcome_count=stats["overcome_count"]
        )
    
    def create_task(self, db: Session, user_id: int, task_data: TaskCreate) -> TaskResponse:
        """创建任务"""
        db_task = crud_task.create(db=db, user_id=user_id, task_data=task_data)
        
        # 转换为响应模型
        subtasks = [
            SubtaskResponse(
                id=subtask.id,
                task_id=subtask.task_id,
                name=subtask.name,
                hours=float(subtask.hours),
                is_high_frequency=bool(subtask.is_high_frequency),
                is_overcome=bool(subtask.is_overcome),
                create_time=subtask.create_time,
                update_time=subtask.update_time
            )
            for subtask in db_task.subtasks
        ]
        
        return TaskResponse(
            id=db_task.id,
            user_id=db_task.user_id,
            name=db_task.name,
            type=TaskType(db_task.type),
            category=db_task.category,
            weekly_hours=float(db_task.weekly_hours),
            is_high_frequency=bool(db_task.is_high_frequency),
            is_overcome=bool(db_task.is_overcome),
            subtasks=subtasks,
            create_time=db_task.create_time,
            update_time=db_task.update_time
        )
    
    def quick_create_task(self, db: Session, user_id: int, task_name: str, task_type: Optional[TaskType] = None) -> TaskResponse:
        """快捷创建任务"""
        task_data = TaskQuickCreate(
            name=task_name,
            type=task_type or TaskType.STUDY
        )
        
        db_task = crud_task.quick_create(db=db, user_id=user_id, task_data=task_data)
        
        return TaskResponse(
            id=db_task.id,
            user_id=db_task.user_id,
            name=db_task.name,
            type=TaskType(db_task.type),
            category=db_task.category,
            weekly_hours=float(db_task.weekly_hours),
            is_high_frequency=bool(db_task.is_high_frequency),
            is_overcome=bool(db_task.is_overcome),
            subtasks=[],
            create_time=db_task.create_time,
            update_time=db_task.update_time
        )
    
    def update_task(self, db: Session, task_id: int, user_id: int, task_data: TaskUpdate) -> Optional[TaskResponse]:
        """更新任务"""
        db_task = crud_task.update(db=db, task_id=task_id, user_id=user_id, task_data=task_data)
        if not db_task:
            return None
        
        subtasks = [
            SubtaskResponse(
                id=subtask.id,
                task_id=subtask.task_id,
                name=subtask.name,
                hours=float(subtask.hours),
                is_high_frequency=bool(subtask.is_high_frequency),
                is_overcome=bool(subtask.is_overcome),
                create_time=subtask.create_time,
                update_time=subtask.update_time
            )
            for subtask in db_task.subtasks
        ]
        
        return TaskResponse(
            id=db_task.id,
            user_id=db_task.user_id,
            name=db_task.name,
            type=TaskType(db_task.type),
            category=db_task.category,
            weekly_hours=float(db_task.weekly_hours),
            is_high_frequency=bool(db_task.is_high_frequency),
            is_overcome=bool(db_task.is_overcome),
            subtasks=subtasks,
            create_time=db_task.create_time,
            update_time=db_task.update_time
        )
    
    def update_task_expand_status(self, db: Session, user_id: int, task_id: int, is_expand: bool) -> Optional[TaskResponse]:
        """更新任务展开状态"""
        # 这里可以添加展开状态的逻辑，目前先返回任务信息
        db_task = crud_task.get_by_id(db=db, task_id=task_id, user_id=user_id)
        if not db_task:
            return None
        
        subtasks = [
            SubtaskResponse(
                id=subtask.id,
                task_id=subtask.task_id,
                name=subtask.name,
                hours=float(subtask.hours),
                is_high_frequency=bool(subtask.is_high_frequency),
                is_overcome=bool(subtask.is_overcome),
                create_time=subtask.create_time,
                update_time=subtask.update_time
            )
            for subtask in db_task.subtasks
        ]
        
        return TaskResponse(
            id=db_task.id,
            user_id=db_task.user_id,
            name=db_task.name,
            type=TaskType(db_task.type),
            category=db_task.category,
            weekly_hours=float(db_task.weekly_hours),
            is_high_frequency=bool(db_task.is_high_frequency),
            is_overcome=bool(db_task.is_overcome),
            subtasks=subtasks,
            create_time=db_task.create_time,
            update_time=db_task.update_time
        )
    
    def delete_task(self, db: Session, task_id: int, user_id: int) -> bool:
        """删除任务"""
        return crud_task.delete(db=db, task_id=task_id, user_id=user_id)
    
    def get_task_by_id(self, db: Session, task_id: int, user_id: int) -> Optional[TaskResponse]:
        """根据ID获取任务"""
        db_task = crud_task.get_by_id(db=db, task_id=task_id, user_id=user_id)
        if not db_task:
            return None
        
        subtasks = [
            SubtaskResponse(
                id=subtask.id,
                task_id=subtask.task_id,
                name=subtask.name,
                hours=float(subtask.hours),
                is_high_frequency=bool(subtask.is_high_frequency),
                is_overcome=bool(subtask.is_overcome),
                create_time=subtask.create_time,
                update_time=subtask.update_time
            )
            for subtask in db_task.subtasks
        ]
        
        return TaskResponse(
            id=db_task.id,
            user_id=db_task.user_id,
            name=db_task.name,
            type=TaskType(db_task.type),
            category=db_task.category,
            weekly_hours=float(db_task.weekly_hours),
            is_high_frequency=bool(db_task.is_high_frequency),
            is_overcome=bool(db_task.is_overcome),
            subtasks=subtasks,
            create_time=db_task.create_time,
            update_time=db_task.update_time
        )
    
    def get_high_frequency_tasks(self, db: Session, user_id: int) -> List[TaskResponse]:
        """获取高频任务"""
        tasks = crud_task.get_high_frequency_tasks(db=db, user_id=user_id)
        
        return [
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                name=task.name,
                type=TaskType(task.type),
                category=task.category,
                weekly_hours=float(task.weekly_hours),
                is_high_frequency=bool(task.is_high_frequency),
                is_overcome=bool(task.is_overcome),
                subtasks=[
                    SubtaskResponse(
                        id=subtask.id,
                        task_id=subtask.task_id,
                        name=subtask.name,
                        hours=float(subtask.hours),
                        is_high_frequency=bool(subtask.is_high_frequency),
                        is_overcome=bool(subtask.is_overcome),
                        create_time=subtask.create_time,
                        update_time=subtask.update_time
                    )
                    for subtask in task.subtasks
                ],
                create_time=task.create_time,
                update_time=task.update_time
            )
            for task in tasks
        ]
    
    def get_overcome_tasks(self, db: Session, user_id: int) -> List[TaskResponse]:
        """获取待克服任务"""
        tasks = crud_task.get_overcome_tasks(db=db, user_id=user_id)
        
        return [
            TaskResponse(
                id=task.id,
                user_id=task.user_id,
                name=task.name,
                type=TaskType(task.type),
                category=task.category,
                weekly_hours=float(task.weekly_hours),
                is_high_frequency=bool(task.is_high_frequency),
                is_overcome=bool(task.is_overcome),
                subtasks=[
                    SubtaskResponse(
                        id=subtask.id,
                        task_id=subtask.task_id,
                        name=subtask.name,
                        hours=float(subtask.hours),
                        is_high_frequency=bool(subtask.is_high_frequency),
                        is_overcome=bool(subtask.is_overcome),
                        create_time=subtask.create_time,
                        update_time=subtask.update_time
                    )
                    for subtask in task.subtasks
                ],
                create_time=task.create_time,
                update_time=task.update_time
            )
            for task in tasks
        ]
    
    def get_task_statistics(self, db: Session, user_id: int) -> Dict[str, Any]:
        """获取任务统计信息"""
        return crud_task.get_task_statistics(db=db, user_id=user_id)

# 创建服务实例
task_service = TaskService() 