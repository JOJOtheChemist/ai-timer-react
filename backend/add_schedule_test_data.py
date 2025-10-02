#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
为用户101添加任务和时间表测试数据
"""

from sqlalchemy import text
from core.database import SessionLocal
from datetime import datetime, time

def add_schedule_data():
    db = SessionLocal()
    
    try:
        print("=" * 50)
        print("开始为用户101创建任务和时间表数据...")
        print("=" * 50)
        
        # 1. 创建任务（主任务）
        print("\n📝 1. 创建主任务...")
        
        tasks_data = [
            {
                'user_id': 101,
                'name': '英语学习',
                'type': 'study',
                'category': '学习',
                'weekly_hours': 14.0,
                'is_high_frequency': 1,
                'is_overcome': 0
            },
            {
                'user_id': 101,
                'name': '数学学习',
                'type': 'study',
                'category': '学习',
                'weekly_hours': 12.0,
                'is_high_frequency': 0,
                'is_overcome': 0
            },
            {
                'user_id': 101,
                'name': '专业课',
                'type': 'study',
                'category': '学习',
                'weekly_hours': 10.0,
                'is_high_frequency': 0,
                'is_overcome': 0
            }
        ]
        
        task_ids = []
        for task in tasks_data:
            query = text("""
                INSERT INTO task (user_id, name, type, category, weekly_hours, is_high_frequency, is_overcome, create_time, update_time)
                VALUES (:user_id, :name, :type, :category, :weekly_hours, :is_high_frequency, :is_overcome, NOW(), NOW())
                RETURNING id
            """)
            result = db.execute(query, task)
            task_id = result.fetchone()[0]
            task_ids.append(task_id)
            print(f"  ✓ 创建任务: {task['name']} (ID: {task_id})")
        
        db.commit()
        
        # 2. 创建子任务
        print("\n📋 2. 创建子任务...")
        
        subtasks_data = [
            # 英语学习的子任务
            {'task_id': task_ids[0], 'user_id': 101, 'name': '单词记忆', 'hours': 7.0, 'is_high_frequency': 1, 'is_overcome': 0},
            {'task_id': task_ids[0], 'user_id': 101, 'name': '阅读理解', 'hours': 5.0, 'is_high_frequency': 0, 'is_overcome': 0},
            {'task_id': task_ids[0], 'user_id': 101, 'name': '写作练习', 'hours': 2.0, 'is_high_frequency': 0, 'is_overcome': 1},
            # 数学学习的子任务
            {'task_id': task_ids[1], 'user_id': 101, 'name': '高数刷题', 'hours': 6.0, 'is_high_frequency': 0, 'is_overcome': 0},
            {'task_id': task_ids[1], 'user_id': 101, 'name': '线代复习', 'hours': 4.0, 'is_high_frequency': 0, 'is_overcome': 0},
            {'task_id': task_ids[1], 'user_id': 101, 'name': '概率统计', 'hours': 2.0, 'is_high_frequency': 0, 'is_overcome': 1},
            # 专业课的子任务
            {'task_id': task_ids[2], 'user_id': 101, 'name': '教材通读', 'hours': 5.0, 'is_high_frequency': 0, 'is_overcome': 0},
            {'task_id': task_ids[2], 'user_id': 101, 'name': '真题练习', 'hours': 3.0, 'is_high_frequency': 0, 'is_overcome': 0},
            {'task_id': task_ids[2], 'user_id': 101, 'name': '笔记整理', 'hours': 2.0, 'is_high_frequency': 0, 'is_overcome': 0}
        ]
        
        subtask_ids = []
        for subtask in subtasks_data:
            query = text("""
                INSERT INTO subtask (task_id, user_id, name, hours, is_high_frequency, is_overcome, create_time, update_time)
                VALUES (:task_id, :user_id, :name, :hours, :is_high_frequency, :is_overcome, NOW(), NOW())
                RETURNING id
            """)
            result = db.execute(query, subtask)
            subtask_id = result.fetchone()[0]
            subtask_ids.append(subtask_id)
            print(f"  ✓ 创建子任务: {subtask['name']} (ID: {subtask_id})")
        
        db.commit()
        
        # 3. 创建今日时间表
        print("\n⏰ 3. 创建今日时间表...")
        
        time_slots_data = [
            {'time_range': '06:00-07:00', 'task_id': task_ids[0], 'subtask_id': subtask_ids[0], 'status': 'completed'},
            {'time_range': '07:00-08:00', 'task_id': None, 'subtask_id': None, 'status': 'completed', 'note': '早餐+晨练'},
            {'time_range': '08:00-09:30', 'task_id': task_ids[1], 'subtask_id': subtask_ids[3], 'status': 'in_progress', 'ai_tip': '建议先复习昨天错题，再做新题', 'is_ai_recommended': 1},
            {'time_range': '09:30-10:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '休息'},
            {'time_range': '10:00-12:00', 'task_id': task_ids[2], 'subtask_id': subtask_ids[6], 'status': 'pending'},
            {'time_range': '12:00-13:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '午餐+午休'},
            {'time_range': '13:00-14:30', 'task_id': task_ids[0], 'subtask_id': subtask_ids[1], 'status': 'pending'},
            {'time_range': '14:30-15:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '休息'},
            {'time_range': '15:00-17:00', 'task_id': task_ids[1], 'subtask_id': subtask_ids[4], 'status': 'pending'},
            {'time_range': '17:00-18:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '晚餐+散步'},
            {'time_range': '18:00-19:30', 'task_id': task_ids[2], 'subtask_id': subtask_ids[7], 'status': 'pending'},
            {'time_range': '19:30-20:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '休息'},
            {'time_range': '20:00-21:00', 'task_id': task_ids[0], 'subtask_id': subtask_ids[0], 'status': 'pending'},
            {'time_range': '21:00-22:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '复习总结'},
            {'time_range': '22:00-23:00', 'task_id': None, 'subtask_id': None, 'status': 'pending', 'note': '洗漱+放松'}
        ]
        
        today = datetime.now().date()
        for slot in time_slots_data:
            query = text("""
                INSERT INTO time_slot (
                    user_id, date, time_range, task_id, subtask_id, 
                    status, note, ai_tip, is_ai_recommended, 
                    create_time, update_time
                )
                VALUES (
                    :user_id, :date, :time_range, :task_id, :subtask_id,
                    :status, :note, :ai_tip, :is_ai_recommended,
                    NOW(), NOW()
                )
            """)
            db.execute(query, {
                'user_id': 101,
                'date': today,
                'time_range': slot['time_range'],
                'task_id': slot.get('task_id'),
                'subtask_id': slot.get('subtask_id'),
                'status': slot['status'],
                'note': slot.get('note'),
                'ai_tip': slot.get('ai_tip'),
                'is_ai_recommended': slot.get('is_ai_recommended', 0)
            })
            print(f"  ✓ 创建时间段: {slot['time_range']} - {slot.get('note', '学习任务')}")
        
        db.commit()
        
        print("\n" + "=" * 50)
        print("✅ 任务和时间表数据创建成功！")
        print("=" * 50)
        print(f"\n📊 统计信息:")
        print(f"  • 主任务数: {len(tasks_data)}")
        print(f"  • 子任务数: {len(subtasks_data)}")
        print(f"  • 时间段数: {len(time_slots_data)}")
        print(f"  • 用户ID: 101 (考研的小艾)")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_schedule_data() 