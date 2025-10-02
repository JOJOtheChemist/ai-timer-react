#!/usr/bin/env python3
"""
添加层级任务数据（项目-子任务结构）
"""
import sys
from pathlib import Path
from datetime import date, timedelta

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from models.task import Task, Subtask, TimeSlot, MoodRecord

def add_hierarchical_tasks():
    """添加带子任务的项目结构"""
    db = SessionLocal()
    
    try:
        user_id = 1
        today = date.today()
        
        print("🚀 开始添加层级任务数据...")
        print(f"📅 日期: {today}")
        print(f"👤 用户ID: {user_id}\n")
        
        # 清空现有任务（避免重复）
        print("🗑️  清空现有任务...")
        db.query(MoodRecord).filter(MoodRecord.user_id == user_id).delete()
        db.query(TimeSlot).filter(TimeSlot.user_id == user_id).delete()
        db.query(Subtask).filter(Subtask.user_id == user_id).delete()
        db.query(Task).filter(Task.user_id == user_id).delete()
        db.commit()
        print("✅ 已清空\n")
        
        # 1. 创建项目（一级任务）和子任务
        print("1️⃣ 创建项目和子任务...")
        
        # 项目1: 考研复习（学习类）
        project1 = Task(
            user_id=user_id,
            name="考研复习",
            type="study",
            category="学习",
            weekly_hours=20.0,
            is_high_frequency=1,
            is_overcome=0
        )
        db.add(project1)
        db.flush()
        print(f"✅ 创建项目: {project1.name}")
        
        subtasks1 = [
            {"name": "英语阅读训练", "hours": 5.0, "is_high_frequency": 1, "is_overcome": 0},
            {"name": "英语听写练习", "hours": 3.0, "is_high_frequency": 1, "is_overcome": 0},
            {"name": "数学公式背诵", "hours": 4.0, "is_high_frequency": 0, "is_overcome": 1},
            {"name": "数学习题练习", "hours": 4.0, "is_high_frequency": 0, "is_overcome": 0},
            {"name": "专业课复习", "hours": 4.0, "is_high_frequency": 0, "is_overcome": 0}
        ]
        
        created_subtasks1 = []
        for sub_data in subtasks1:
            subtask = Subtask(
                task_id=project1.id,
                user_id=user_id,
                **sub_data
            )
            db.add(subtask)
            db.flush()
            created_subtasks1.append(subtask)
            print(f"   └─ {subtask.name} ({subtask.hours}h)")
        
        # 项目2: 编程学习（学习类）
        project2 = Task(
            user_id=user_id,
            name="编程学习",
            type="study",
            category="编程",
            weekly_hours=15.0,
            is_high_frequency=1,
            is_overcome=0
        )
        db.add(project2)
        db.flush()
        print(f"\n✅ 创建项目: {project2.name}")
        
        subtasks2 = [
            {"name": "算法刷题", "hours": 6.0, "is_high_frequency": 1, "is_overcome": 0},
            {"name": "项目开发", "hours": 5.0, "is_high_frequency": 1, "is_overcome": 0},
            {"name": "技术文档阅读", "hours": 4.0, "is_high_frequency": 0, "is_overcome": 0}
        ]
        
        created_subtasks2 = []
        for sub_data in subtasks2:
            subtask = Subtask(
                task_id=project2.id,
                user_id=user_id,
                **sub_data
            )
            db.add(subtask)
            db.flush()
            created_subtasks2.append(subtask)
            print(f"   └─ {subtask.name} ({subtask.hours}h)")
        
        # 项目3: 健康管理（生活类）
        project3 = Task(
            user_id=user_id,
            name="健康管理",
            type="life",
            category="健康",
            weekly_hours=7.0,
            is_high_frequency=0,
            is_overcome=1
        )
        db.add(project3)
        db.flush()
        print(f"\n✅ 创建项目: {project3.name}")
        
        subtasks3 = [
            {"name": "跑步锻炼", "hours": 3.0, "is_high_frequency": 0, "is_overcome": 1},
            {"name": "健身房训练", "hours": 2.5, "is_high_frequency": 0, "is_overcome": 1},
            {"name": "瑜伽拉伸", "hours": 1.5, "is_high_frequency": 0, "is_overcome": 0}
        ]
        
        created_subtasks3 = []
        for sub_data in subtasks3:
            subtask = Subtask(
                task_id=project3.id,
                user_id=user_id,
                **sub_data
            )
            db.add(subtask)
            db.flush()
            created_subtasks3.append(subtask)
            print(f"   └─ {subtask.name} ({subtask.hours}h)")
        
        # 项目4: 兼职工作（工作类）
        project4 = Task(
            user_id=user_id,
            name="兼职工作",
            type="work",
            category="工作",
            weekly_hours=8.0,
            is_high_frequency=0,
            is_overcome=0
        )
        db.add(project4)
        db.flush()
        print(f"\n✅ 创建项目: {project4.name}")
        
        subtasks4 = [
            {"name": "撰写报告", "hours": 4.0, "is_high_frequency": 0, "is_overcome": 1},
            {"name": "数据整理", "hours": 2.0, "is_high_frequency": 1, "is_overcome": 0},
            {"name": "会议参与", "hours": 2.0, "is_high_frequency": 0, "is_overcome": 0}
        ]
        
        created_subtasks4 = []
        for sub_data in subtasks4:
            subtask = Subtask(
                task_id=project4.id,
                user_id=user_id,
                **sub_data
            )
            db.add(subtask)
            db.flush()
            created_subtasks4.append(subtask)
            print(f"   └─ {subtask.name} ({subtask.hours}h)")
        
        db.commit()
        print(f"\n✅ 共创建 4 个项目，15 个子任务\n")
        
        # 2. 创建今日时间表（包含子任务）
        print("2️⃣ 创建今日时间表...")
        
        all_subtasks = created_subtasks1 + created_subtasks2 + created_subtasks3 + created_subtasks4
        
        time_slots_data = [
            {"time_range": "07:30-08:30", "task": project1, "subtask": created_subtasks1[0], "status": "completed"},  # 英语阅读
            {"time_range": "08:30-09:30", "task": project1, "subtask": created_subtasks1[1], "status": "completed"},  # 英语听写
            {"time_range": "09:30-10:30", "task": project2, "subtask": created_subtasks2[0], "status": "completed"},  # 算法刷题
            {"time_range": "10:30-11:30", "task": project2, "subtask": created_subtasks2[1], "status": "in-progress"},  # 项目开发
            {"time_range": "11:30-12:30", "task": None, "subtask": None, "status": "pending"},  # 午餐
            {"time_range": "12:30-13:30", "task": None, "subtask": None, "status": "pending"},  # 午休
            {"time_range": "13:30-14:30", "task": project1, "subtask": created_subtasks1[2], "status": "pending"},  # 数学公式
            {"time_range": "14:30-15:30", "task": project1, "subtask": created_subtasks1[3], "status": "pending"},  # 数学习题
            {"time_range": "15:30-16:30", "task": project1, "subtask": created_subtasks1[4], "status": "pending"},  # 专业课
            {"time_range": "16:30-17:30", "task": project3, "subtask": created_subtasks3[0], "status": "pending"},  # 跑步
            {"time_range": "17:30-18:30", "task": None, "subtask": None, "status": "pending"},  # 晚餐
            {"time_range": "18:30-19:30", "task": project4, "subtask": created_subtasks4[0], "status": "pending"},  # 撰写报告
            {"time_range": "19:30-20:30", "task": project2, "subtask": created_subtasks2[2], "status": "pending"},  # 技术文档
            {"time_range": "20:30-21:30", "task": project1, "subtask": created_subtasks1[0], "status": "pending"},  # 英语阅读
        ]
        
        created_slots = []
        for slot_data in time_slots_data:
            task = slot_data["task"]
            subtask = slot_data["subtask"]
            
            time_slot = TimeSlot(
                user_id=user_id,
                date=today,
                time_range=slot_data["time_range"],
                task_id=task.id if task else None,
                subtask_id=subtask.id if subtask else None,
                status=slot_data["status"],
                is_ai_recommended=1 if task in [project1, project2] else 0,
                ai_tip="专注力黄金时段！" if slot_data["time_range"].startswith("07") else None
            )
            db.add(time_slot)
            db.flush()
            created_slots.append(time_slot)
            
            task_name = f"{task.name} - {subtask.name}" if task and subtask else "空闲"
            print(f"   ✓ {slot_data['time_range']} - {task_name} ({slot_data['status']})")
        
        db.commit()
        print(f"✅ 共创建 {len(created_slots)} 个时间段\n")
        
        # 3. 添加心情记录
        print("3️⃣ 添加心情记录...")
        
        moods = ["happy", "focused", "happy"]
        for i, slot in enumerate(created_slots[:3]):
            mood_record = MoodRecord(
                user_id=user_id,
                time_slot_id=slot.id,
                mood=moods[i]
            )
            db.add(mood_record)
            print(f"   ✓ {slot.time_range} - {moods[i]}")
        
        db.commit()
        print(f"✅ 共添加 {len(moods)} 条心情记录\n")
        
        # 4. 添加历史数据
        print("4️⃣ 添加历史数据...")
        
        for days_ago in range(1, 4):
            past_date = today - timedelta(days=days_ago)
            
            # 每天添加一些已完成的时间段
            for i, subtask in enumerate(all_subtasks[:4]):
                time_slot = TimeSlot(
                    user_id=user_id,
                    date=past_date,
                    time_range=f"{8+i:02d}:00-{9+i:02d}:00",
                    task_id=subtask.task_id,
                    subtask_id=subtask.id,
                    status="completed",
                    is_ai_recommended=0
                )
                db.add(time_slot)
            
            print(f"   ✓ {past_date} - 添加4个已完成时间段")
        
        db.commit()
        print(f"✅ 历史数据添加完成\n")
        
        # 5. 统计
        print("📊 数据统计:")
        total_projects = db.query(Task).filter(Task.user_id == user_id).count()
        total_subtasks = db.query(Subtask).filter(Subtask.user_id == user_id).count()
        total_slots = db.query(TimeSlot).filter(TimeSlot.user_id == user_id).count()
        
        print(f"   • 项目数: {total_projects}")
        print(f"   • 子任务数: {total_subtasks}")
        print(f"   • 总时间段: {total_slots}")
        print(f"   • 今日时间段: {len(created_slots)}")
        
        print("\n✅ 层级任务数据添加成功！")
        print("\n🌐 现在刷新前端页面查看:")
        print("   • 项目会显示在任务库顶层")
        print("   • 点击项目可展开查看子任务")
        print("   • 时间表显示：项目 - 子任务\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_hierarchical_tasks() 