#!/usr/bin/env python3
"""
添加测试数据脚本
为user_id=1添加任务和时间表数据
"""
import sys
from pathlib import Path
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from models.task import Task, TimeSlot, MoodRecord

def add_test_data():
    """添加测试数据"""
    db = SessionLocal()
    
    try:
        user_id = 1
        today = date.today()
        
        print("🚀 开始添加测试数据...")
        print(f"📅 目标日期: {today}")
        print(f"👤 用户ID: {user_id}\n")
        
        # 1. 创建任务
        print("1️⃣ 创建任务...")
        
        tasks_data = [
            {
                "name": "算法学习",
                "type": "study",
                "category": "编程",
                "weekly_hours": 10.0,
                "is_high_frequency": 1,
                "is_overcome": 0
            },
            {
                "name": "英语阅读",
                "type": "study",
                "category": "语言",
                "weekly_hours": 5.0,
                "is_high_frequency": 1,
                "is_overcome": 0
            },
            {
                "name": "健身锻炼",
                "type": "life",
                "category": "健康",
                "weekly_hours": 3.0,
                "is_high_frequency": 0,
                "is_overcome": 1
            },
            {
                "name": "项目开发",
                "type": "work",
                "category": "工作",
                "weekly_hours": 15.0,
                "is_high_frequency": 1,
                "is_overcome": 0
            },
            {
                "name": "读书笔记",
                "type": "study",
                "category": "阅读",
                "weekly_hours": 4.0,
                "is_high_frequency": 0,
                "is_overcome": 0
            }
        ]
        
        created_tasks = []
        for task_data in tasks_data:
            # 检查是否已存在
            existing = db.query(Task).filter(
                Task.user_id == user_id,
                Task.name == task_data["name"]
            ).first()
            
            if existing:
                print(f"   ✓ 任务已存在: {task_data['name']}")
                created_tasks.append(existing)
            else:
                task = Task(user_id=user_id, **task_data)
                db.add(task)
                db.flush()
                created_tasks.append(task)
                print(f"   ✓ 创建任务: {task_data['name']}")
        
        db.commit()
        print(f"✅ 共创建 {len(created_tasks)} 个任务\n")
        
        # 2. 创建今日时间表
        print("2️⃣ 创建今日时间表...")
        
        # 删除今日已有的时间表（避免重复）
        db.query(TimeSlot).filter(
            TimeSlot.user_id == user_id,
            TimeSlot.date == today
        ).delete()
        db.commit()
        
        time_slots_data = [
            {"time_range": "07:30-08:30", "task_idx": 0, "status": "completed"},  # 算法学习
            {"time_range": "08:30-09:30", "task_idx": 0, "status": "completed"},  # 算法学习
            {"time_range": "09:30-10:30", "task_idx": 1, "status": "completed"},  # 英语阅读
            {"time_range": "10:30-11:30", "task_idx": 3, "status": "in-progress"},  # 项目开发
            {"time_range": "11:30-12:30", "task_idx": None, "status": "pending"},  # 午餐休息
            {"time_range": "12:30-13:30", "task_idx": None, "status": "pending"},  # 午休
            {"time_range": "13:30-14:30", "task_idx": 3, "status": "pending"},  # 项目开发
            {"time_range": "14:30-15:30", "task_idx": 3, "status": "pending"},  # 项目开发
            {"time_range": "15:30-16:30", "task_idx": 4, "status": "pending"},  # 读书笔记
            {"time_range": "16:30-17:30", "task_idx": 2, "status": "pending"},  # 健身锻炼
            {"time_range": "17:30-18:30", "task_idx": None, "status": "pending"},  # 晚餐
            {"time_range": "18:30-19:30", "task_idx": 1, "status": "pending"},  # 英语阅读
            {"time_range": "19:30-20:30", "task_idx": 0, "status": "pending"},  # 算法学习
            {"time_range": "20:30-21:30", "task_idx": 4, "status": "pending"},  # 读书笔记
        ]
        
        created_slots = []
        for slot_data in time_slots_data:
            task_idx = slot_data["task_idx"]
            time_slot = TimeSlot(
                user_id=user_id,
                date=today,
                time_range=slot_data["time_range"],
                task_id=created_tasks[task_idx].id if task_idx is not None else None,
                status=slot_data["status"],
                is_ai_recommended=1 if task_idx in [0, 3] else 0,  # 算法和项目是AI推荐
                ai_tip="专注力黄金时段，适合深度学习！" if slot_data["time_range"].startswith("07") else None
            )
            db.add(time_slot)
            db.flush()
            created_slots.append(time_slot)
            
            task_name = created_tasks[task_idx].name if task_idx is not None else "空闲"
            print(f"   ✓ {slot_data['time_range']} - {task_name} ({slot_data['status']})")
        
        db.commit()
        print(f"✅ 共创建 {len(created_slots)} 个时间段\n")
        
        # 3. 添加心情记录
        print("3️⃣ 添加心情记录...")
        
        moods = ["happy", "focused", "happy"]
        for i, slot in enumerate(created_slots[:3]):  # 只为已完成的时间段添加心情
            mood_record = MoodRecord(
                user_id=user_id,
                time_slot_id=slot.id,
                mood=moods[i]
            )
            db.add(mood_record)
            print(f"   ✓ {slot.time_range} - {moods[i]}")
        
        db.commit()
        print(f"✅ 共添加 {len(moods)} 条心情记录\n")
        
        # 4. 添加上周的一些历史数据（用于统计）
        print("4️⃣ 添加历史数据（本周其他日期）...")
        
        for days_ago in range(1, 4):  # 过去3天
            past_date = today - timedelta(days=days_ago)
            
            # 为每天添加几个已完成的时间段
            for hour in range(8, 12):  # 8:00-12:00
                time_slot = TimeSlot(
                    user_id=user_id,
                    date=past_date,
                    time_range=f"{hour:02d}:00-{hour+1:02d}:00",
                    task_id=created_tasks[hour % len(created_tasks)].id,
                    status="completed",
                    is_ai_recommended=0
                )
                db.add(time_slot)
            
            print(f"   ✓ {past_date} - 添加4个已完成时间段")
        
        db.commit()
        print(f"✅ 历史数据添加完成\n")
        
        # 5. 统计信息
        print("📊 数据统计:")
        total_tasks = db.query(Task).filter(Task.user_id == user_id).count()
        total_slots = db.query(TimeSlot).filter(TimeSlot.user_id == user_id).count()
        completed_slots = db.query(TimeSlot).filter(
            TimeSlot.user_id == user_id,
            TimeSlot.status == "completed"
        ).count()
        
        print(f"   • 总任务数: {total_tasks}")
        print(f"   • 总时间段: {total_slots}")
        print(f"   • 已完成时间段: {completed_slots}")
        print(f"   • 今日时间段: {len(created_slots)}")
        
        print("\n✅ 测试数据添加成功！")
        print("\n🌐 现在可以在前端查看:")
        print("   • 打开 http://localhost:3000")
        print("   • 查看首页时间表")
        print("   • 查看任务列表")
        print("   • 查看统计数据\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_test_data() 