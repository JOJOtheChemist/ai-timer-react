#!/usr/bin/env python3
"""
添加消息页面测试数据
创建导师用户和各类消息（导师反馈、私信、系统通知）
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import text

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal

def add_message_test_data():
    """添加消息测试数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始添加消息页面测试数据...\n")
        
        # 1. 创建导师用户
        print("1️⃣ 创建导师用户...")
        
        tutors_data = [
            {
                "id": 201,
                "username": "王英语老师",
                "phone": "13800000201",
                "password_hash": "hashed_password_201",
                "avatar": "/avatars/avatar1.png",
                "goal": "帮助学生提高英语成绩",
                "major": "英语教育"
            },
            {
                "id": 202,
                "username": "李会计学姐",
                "phone": "13800000202",
                "password_hash": "hashed_password_202",
                "avatar": "/avatars/avatar2.png",
                "goal": "CPA考试辅导",
                "major": "会计"
            },
            {
                "id": 203,
                "username": "张编程导师",
                "phone": "13800000203",
                "password_hash": "hashed_password_203",
                "avatar": "/avatars/avatar3.png",
                "goal": "编程技能培训",
                "major": "计算机科学"
            }
        ]
        
        for tutor_data in tutors_data:
            # 检查用户是否已存在
            check_query = text("SELECT id FROM \"user\" WHERE id = :user_id")
            result = db.execute(check_query, {"user_id": tutor_data["id"]}).fetchone()
            
            if result:
                # 更新用户信息
                update_query = text("""
                    UPDATE "user" 
                    SET username = :username, avatar = :avatar, goal = :goal, major = :major
                    WHERE id = :user_id
                """)
                db.execute(update_query, {
                    "user_id": tutor_data["id"],
                    "username": tutor_data["username"],
                    "avatar": tutor_data["avatar"],
                    "goal": tutor_data["goal"],
                    "major": tutor_data["major"]
                })
                print(f"   ✓ 更新导师: {tutor_data['username']} (ID: {tutor_data['id']})")
            else:
                # 创建新用户
                insert_query = text("""
                    INSERT INTO "user" (id, username, phone, password_hash, avatar, goal, major)
                    VALUES (:id, :username, :phone, :password_hash, :avatar, :goal, :major)
                """)
                db.execute(insert_query, tutor_data)
                print(f"   ✓ 创建导师: {tutor_data['username']} (ID: {tutor_data['id']})")
        
        db.commit()
        print(f"✅ 共处理 {len(tutors_data)} 个导师用户\n")
        
        # 2. 创建消息数据
        print("2️⃣ 创建消息数据...")
        
        # 删除已有的测试消息
        delete_query = text("DELETE FROM message WHERE sender_id >= 100 OR receiver_id = 101")
        db.execute(delete_query)
        db.commit()
        
        now = datetime.now()
        messages_data = [
            # 导师反馈消息（type=0）
            {
                "sender_id": 201,
                "receiver_id": 101,
                "type": 0,  # 导师反馈
                "title": "英语时间表优化建议",
                "content": "你好！查看了你的英语时间表，发现几个可以优化的点：\n1. 阅读时长过长：每天2.5h远超建议的1.5h，效率会下降，建议拆分1h精读+0.5h泛读；\n2. 复习缺失：近3天未安排单词复习，推荐用艾宾浩斯法嵌入碎片时间；\n3. 时段适配：你早上记忆力最佳，可将单词复习调整至7:00-7:30。",
                "is_unread": 1,
                "related_id": 1,  # 关联时间表ID
                "related_type": "schedule",
                "create_time": now - timedelta(hours=2)
            },
            {
                "sender_id": 201,
                "receiver_id": 101,
                "type": 0,
                "title": "作文模板分享",
                "content": "作文模板已发送至你的私信，记得结合每日练习套用，重点关注三段式结构~",
                "is_unread": 0,
                "related_id": None,
                "related_type": None,
                "create_time": now - timedelta(days=1, hours=7)
            },
            {
                "sender_id": 202,
                "receiver_id": 101,
                "type": 0,
                "title": "CPA税法考点整理",
                "content": "CPA税法高频考点整理好了，结合你的时间表看，建议在第三周重点突破增值税章节。附件已发送~",
                "is_unread": 1,
                "related_id": None,
                "related_type": None,
                "create_time": now - timedelta(days=1, hours=5)
            },
            {
                "sender_id": 203,
                "receiver_id": 101,
                "type": 0,
                "title": "Python学习计划反馈",
                "content": "你的Python学习计划很合理，坚持每日代码练习即可~记得多做项目实战。",
                "is_unread": 0,
                "related_id": None,
                "related_type": None,
                "create_time": now - timedelta(days=3)
            },
            # 私信（type=1）
            {
                "sender_id": 102,
                "receiver_id": 101,
                "type": 1,  # 私信
                "title": None,
                "content": "你用的艾宾浩斯复习法真的好用！求打卡模板~",
                "is_unread": 1,
                "related_id": None,
                "related_type": None,
                "create_time": now - timedelta(hours=1)
            },
            {
                "sender_id": 105,
                "receiver_id": 101,
                "type": 1,
                "title": None,
                "content": "分享给你一个Python刷题网站，亲测有效！",
                "is_unread": 0,
                "related_id": None,
                "related_type": None,
                "create_time": now - timedelta(days=1, hours=3)
            },
            {
                "sender_id": 106,
                "receiver_id": 101,
                "type": 1,
                "title": None,
                "content": "常识模块的复习时间表整理好啦，发你看看~",
                "is_unread": 0,
                "related_id": None,
                "related_type": None,
                "create_time": now - timedelta(days=4)
            },
            # 系统通知（type=2）
            {
                "sender_id": None,
                "receiver_id": 101,
                "type": 2,  # 系统通知
                "title": "徽章通知",
                "content": "你连续7天打卡复习法，获得「坚持之星」徽章！",
                "is_unread": 0,
                "related_id": None,
                "related_type": "badge",
                "create_time": now - timedelta(hours=16)
            },
            {
                "sender_id": None,
                "receiver_id": 101,
                "type": 2,
                "title": "钻石通知",
                "content": "分享上岸案例获得10钻石奖励，已到账~",
                "is_unread": 0,
                "related_id": None,
                "related_type": "diamond",
                "create_time": now - timedelta(days=1, hours=9)
            },
            {
                "sender_id": None,
                "receiver_id": 101,
                "type": 2,
                "title": "活动通知",
                "content": "「上传时间表赢真皮包」活动剩最后5天，快去参与！",
                "is_unread": 0,
                "related_id": None,
                "related_type": "activity",
                "create_time": now - timedelta(days=3)
            }
        ]
        
        for msg_data in messages_data:
            insert_query = text("""
                INSERT INTO message 
                (sender_id, receiver_id, type, title, content, is_unread, 
                 related_id, related_type, create_time)
                VALUES 
                (:sender_id, :receiver_id, :type, :title, :content, :is_unread,
                 :related_id, :related_type, :create_time)
            """)
            
            db.execute(insert_query, msg_data)
            
            type_name = "导师反馈" if msg_data["type"] == 0 else ("私信" if msg_data["type"] == 1 else "系统通知")
            sender = next((t["username"] for t in tutors_data if t["id"] == msg_data.get("sender_id")), "系统")
            print(f"   ✓ 创建{type_name}: {sender} → {msg_data.get('title') or msg_data['content'][:30]}...")
        
        db.commit()
        print(f"✅ 共创建 {len(messages_data)} 条消息\n")
        
        # 3. 统计信息
        print("📊 数据统计:")
        tutor_count_query = text("SELECT COUNT(*) FROM message WHERE receiver_id = 101 AND type = 0")
        tutor_count = db.execute(tutor_count_query).scalar()
        
        private_count_query = text("SELECT COUNT(*) FROM message WHERE receiver_id = 101 AND type = 1")
        private_count = db.execute(private_count_query).scalar()
        
        system_count_query = text("SELECT COUNT(*) FROM message WHERE receiver_id = 101 AND type = 2")
        system_count = db.execute(system_count_query).scalar()
        
        unread_query = text("SELECT COUNT(*) FROM message WHERE receiver_id = 101 AND is_unread = 1")
        unread_count = db.execute(unread_query).scalar()
        
        print(f"   • 导师反馈: {tutor_count} 条")
        print(f"   • 私信: {private_count} 条")
        print(f"   • 系统通知: {system_count} 条")
        print(f"   • 未读消息: {unread_count} 条")
        
        print("\n✅ 消息页面测试数据添加成功！")
        print("\n🌐 现在可以在前端查看:")
        print("   • 打开 http://localhost:3000/messages")
        print("   • 查看导师反馈、私信和系统通知")
        print("   • 测试未读消息标记和详情查看\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_message_test_data() 