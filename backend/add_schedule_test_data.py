#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
向数据库添加时间表测试数据
"""

import psycopg2
from datetime import datetime, date

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'ai_time_management',
    'user': 'yeya',
    'password': ''
}

def add_schedule_test_data():
    """添加时间表测试数据"""
    conn = None
    try:
        # 连接数据库
        print("正在连接数据库...")
        conn = psycopg2.connect(**DB_CONFIG)
        conn.autocommit = False
        cur = conn.cursor()
        
        # 确保用户ID=1存在
        cur.execute('SELECT id FROM "user" WHERE id = 1')
        if not cur.fetchone():
            print("创建测试用户 (ID=1)...")
            cur.execute('''
                INSERT INTO "user" (id, username, email, phone, password_hash, created_at)
                VALUES (1, '测试用户', 'test@example.com', '13800138000', 'test_hash', NOW())
                ON CONFLICT (id) DO NOTHING
            ''')
            conn.commit()
        
        # 创建一些任务
        print("\n创建测试任务...")
        tasks_data = [
            (1, 1, '英语学习', 'study', '学习', 1, 0, 14.0),
            (2, 1, '数学学习', 'study', '学习', 0, 0, 12.0),
            (3, 1, '专业课', 'study', '学习', 0, 0, 10.0),
            (4, 1, '休息放松', 'life', '休息', 0, 0, 3.0),
            (5, 1, '日常生活', 'life', '生活', 0, 0, 5.0),
        ]
        
        for task in tasks_data:
            cur.execute('''
                INSERT INTO task (id, user_id, name, type, category, is_high_frequency, is_overcome, weekly_hours, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    type = EXCLUDED.type,
                    category = EXCLUDED.category,
                    is_high_frequency = EXCLUDED.is_high_frequency,
                    is_overcome = EXCLUDED.is_overcome,
                    weekly_hours = EXCLUDED.weekly_hours
            ''', task)
        conn.commit()
        print(f"✅ 创建了 {len(tasks_data)} 个任务")
        
        # 创建子任务
        print("\n创建子任务...")
        subtasks_data = [
            (11, 1, 1, '单词记忆', 7.0, 1, 0),
            (12, 1, 1, '阅读理解', 5.0, 0, 0),
            (13, 1, 1, '写作练习', 2.0, 0, 1),
            (21, 2, 1, '高数刷题', 6.0, 0, 0),
            (22, 2, 1, '线代复习', 4.0, 0, 0),
            (23, 2, 1, '概率统计', 2.0, 0, 1),
            (31, 3, 1, '教材通读', 5.0, 0, 0),
            (32, 3, 1, '真题练习', 3.0, 0, 0),
            (33, 3, 1, '笔记整理', 2.0, 0, 0),
        ]
        
        for subtask in subtasks_data:
            cur.execute('''
                INSERT INTO subtask (id, task_id, user_id, name, hours, is_high_frequency, is_overcome, create_time, update_time)
                VALUES (%s, %s, %s, %s, %s, %s, %s, NOW(), NOW())
                ON CONFLICT (id) DO UPDATE SET
                    name = EXCLUDED.name,
                    hours = EXCLUDED.hours,
                    is_high_frequency = EXCLUDED.is_high_frequency,
                    is_overcome = EXCLUDED.is_overcome
            ''', subtask)
        conn.commit()
        print(f"✅ 创建了 {len(subtasks_data)} 个子任务")
        
        # 获取今天的日期
        today = date.today()
        print(f"\n为日期 {today} 创建时间槽...")
        
        # 先删除今天的旧数据
        cur.execute('DELETE FROM time_slot WHERE user_id = 1 AND date = %s', (today,))
        
        # 创建时间槽
        time_slots_data = [
            (today, '06:00-07:00', 1, 11, 'completed', 0, '完成了200个单词记忆', None),
            (today, '07:00-08:00', 5, None, 'completed', 0, '早餐+晨练', None),
            (today, '08:00-09:30', 2, 21, 'in-progress', 1, '正在刷高数题', '建议先复习昨天错题，再做新题'),
            (today, '09:30-10:00', 4, None, 'pending', 0, '休息', None),
            (today, '10:00-12:00', 3, 31, 'pending', 0, None, None),
            (today, '12:00-13:00', 5, None, 'pending', 0, '午餐+午休', None),
            (today, '13:00-14:30', 1, 12, 'pending', 0, None, None),
            (today, '14:30-15:00', 4, None, 'pending', 0, '休息', None),
            (today, '15:00-17:00', 2, 22, 'pending', 0, None, None),
            (today, '17:00-18:00', 5, None, 'pending', 0, '晚餐+散步', None),
            (today, '18:00-19:30', 3, 32, 'pending', 1, None, '建议先复习知识点，再做真题'),
            (today, '19:30-20:00', 4, None, 'pending', 0, '休息', None),
            (today, '20:00-21:00', 1, 11, 'pending', 0, None, None),
            (today, '21:00-22:00', 3, 33, 'pending', 0, '复习总结', None),
            (today, '22:00-23:00', 5, None, 'pending', 0, '洗漱+放松', None),
        ]
        
        for slot_data in time_slots_data:
            cur.execute('''
                INSERT INTO time_slot (
                    user_id, date, time_range, task_id, subtask_id,
                    status, is_ai_recommended, note, ai_tip, create_time, update_time
                ) VALUES (
                    1, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW()
                )
            ''', slot_data)
        
        conn.commit()
        print(f"✅ 创建了 {len(time_slots_data)} 个时间槽")
        
        # 验证数据
        cur.execute('''
            SELECT COUNT(*) FROM time_slot 
            WHERE user_id = 1 AND date = %s
        ''', (today,))
        count = cur.fetchone()[0]
        
        print(f"\n🎉 成功！数据库中现在有 {count} 个时间槽")
        print(f"📅 日期: {today}")
        print(f"👤 用户ID: 1")
        
        # 显示部分数据
        cur.execute('''
            SELECT 
                ts.time_range,
                t.name as task_name,
                st.name as subtask_name,
                ts.status,
                ts.note
            FROM time_slot ts
            LEFT JOIN task t ON ts.task_id = t.id
            LEFT JOIN subtask st ON ts.subtask_id = st.id
            WHERE ts.user_id = 1 AND ts.date = %s
            ORDER BY ts.time_range
            LIMIT 5
        ''', (today,))
        
        print("\n前5个时间槽示例:")
        print("-" * 80)
        for row in cur.fetchall():
            time_range, task_name, subtask_name, status, note = row
            task_display = f"{task_name} - {subtask_name}" if subtask_name else (task_name or note or '空闲')
            print(f"⏰ {time_range:15} | {task_display:30} | {status:12}")
        print("-" * 80)
        
        cur.close()
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if conn:
            conn.close()
            print("\n数据库连接已关闭")

if __name__ == '__main__':
    print("=" * 80)
    print("  📊 向数据库添加时间表测试数据")
    print("=" * 80)
    add_schedule_test_data()
    print("\n✅ 完成！现在可以刷新前端页面查看数据") 