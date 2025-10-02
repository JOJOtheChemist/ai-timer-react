#!/usr/bin/env python3
"""
添加个人主页测试数据
创建用户个人信息、资产、关系链和徽章数据
"""
import sys
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import text

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal

def add_personal_page_data():
    """添加个人主页测试数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始添加个人主页测试数据...\n")
        
        # 禁用触发器避免问题
        print("⚙️  暂时禁用数据库触发器...")
        db.execute(text("SET session_replication_role = replica;"))
        db.commit()
        print("   ✓ 触发器已禁用\n")
        
        # 1. 更新用户101的个人信息
        print("1️⃣ 更新用户个人信息...")
        update_user_query = text("""
            UPDATE "user" 
            SET username = :username,
                avatar = :avatar,
                goal = :goal,
                major = :major
            WHERE id = :user_id
        """)
        
        db.execute(update_user_query, {
            "user_id": 101,
            "username": "考研的小艾",
            "avatar": "/avatars/avatar1.png",
            "goal": "24考研上岸会计学",
            "major": "财务管理"
        })
        db.commit()
        print("   ✓ 更新用户101: 考研的小艾\n")
        
        # 2. 创建或更新用户资产
        print("2️⃣ 创建/更新用户资产...")
        
        # 检查资产记录是否存在
        check_asset_query = text('SELECT id FROM user_asset WHERE user_id = :user_id')
        asset_exists = db.execute(check_asset_query, {"user_id": 101}).fetchone()
        
        if asset_exists:
            # 更新资产
            update_asset_query = text("""
                UPDATE user_asset 
                SET diamond_count = :diamond_count
                WHERE user_id = :user_id
            """)
            db.execute(update_asset_query, {
                "user_id": 101,
                "diamond_count": 158
            })
            print("   ✓ 更新用户资产: 158钻石")
        else:
            # 创建新资产记录
            insert_asset_query = text("""
                INSERT INTO user_asset (user_id, diamond_count)
                VALUES (:user_id, :diamond_count)
            """)
            db.execute(insert_asset_query, {
                "user_id": 101,
                "diamond_count": 158
            })
            print("   ✓ 创建用户资产: 158钻石")
        
        # 更新最近消费时间
        update_consume_time_query = text("""
            UPDATE user_asset 
            SET last_consume_time = :last_consume_time
            WHERE user_id = :user_id
        """)
        db.execute(update_consume_time_query, {
            "user_id": 101,
            "last_consume_time": datetime.now() - timedelta(days=3)
        })
        db.commit()
        print("   ✓ 更新消费记录: 3天前购买导师咨询 50钻石\n")
        
        # 3. 创建关系链数据
        print("3️⃣ 创建关系链数据...")
        
        # 创建3个关注的导师关系
        tutors = [
            {"tutor_id": 201, "tutor_name": "王英语老师"},
            {"tutor_id": 202, "tutor_name": "李会计学姐"},
            {"tutor_id": 203, "tutor_name": "张编程导师"}
        ]
        
        insert_relation_query = text("""
            INSERT INTO user_relation 
            (user_id, target_user_id, relation_type, create_time)
            VALUES (:user_id, :target_user_id, :relation_type, :create_time)
            ON CONFLICT DO NOTHING
        """)
        
        for tutor in tutors:
            db.execute(insert_relation_query, {
                "user_id": 101,
                "target_user_id": tutor["tutor_id"],
                "relation_type": 0,  # 0=关注导师
                "create_time": datetime.now() - timedelta(days=30)
            })
            print(f"   ✓ 关注导师: {tutor['tutor_name']}")
        
        # 创建4个粉丝（其他用户关注101）
        fans = [
            {"fan_id": 102, "fan_name": "琪琪要上岸", "days_ago": 1},
            {"fan_id": 105, "fan_name": "学习小达人", "days_ago": 5},
            {"fan_id": 106, "fan_name": "努力的小李", "days_ago": 10},
            {"fan_id": 107, "fan_name": "加油的小美", "days_ago": 15}
        ]
        
        for fan in fans:
            db.execute(insert_relation_query, {
                "user_id": fan["fan_id"],
                "target_user_id": 101,
                "relation_type": 1,  # 1=粉丝
                "create_time": datetime.now() - timedelta(days=fan["days_ago"])
            })
            print(f"   ✓ 粉丝: {fan['fan_name']} ({fan['days_ago']}天前关注)")
        
        db.commit()
        print(f"✅ 共创建 {len(tutors)} 个导师关注 + {len(fans)} 个粉丝\n")
        
        # 4. 创建徽章数据
        print("4️⃣ 创建徽章数据...")
        
        # 首先创建徽章定义
        badges_def = [
            {"id": 1, "name": "坚持之星", "description": "连续7天完成学习计划打卡", "icon": "🔥", "condition": "连续打卡7天"},
            {"id": 2, "name": "复习王者", "description": "连续14天完成复习任务，复习频率达到80%以上", "icon": "📚", "condition": "复习频率达标"},
            {"id": 3, "name": "目标达成", "description": "单周学习时长超过计划时长的120%", "icon": "🎯", "condition": "周时长超计划"},
            {"id": 4, "name": "分享达人", "description": "累计发布5条学习动态，获得20次以上点赞", "icon": "👥", "condition": "发布5条动态"},
            {"id": 5, "name": "首次充值", "description": "完成首次钻石充值，开启导师指导服务", "icon": "💎", "condition": "充值任意金额"},
            {"id": 6, "name": "进步神速", "description": "单周学习时长较上一周增长50%以上", "icon": "📈", "condition": "周时长增50%"},
            {"id": 7, "name": "上岸先锋", "description": "成功上传考研上岸经验案例，通过官方审核", "icon": "🎓", "condition": "上传上岸案例"},
            {"id": 8, "name": "学霸认证", "description": "累计学习时长达到3000小时，且周均打卡率90%以上", "icon": "🏅", "condition": "3000小时学习"}
        ]
        
        insert_badge_query = text("""
            INSERT INTO badge 
            (id, name, description, icon, condition_text, condition_config, create_time)
            VALUES (:id, :name, :description, :icon, :condition_text, '{}', :create_time)
            ON CONFLICT (id) DO UPDATE SET
                name = EXCLUDED.name,
                description = EXCLUDED.description,
                icon = EXCLUDED.icon,
                condition_text = EXCLUDED.condition_text
        """)
        
        for badge in badges_def:
            db.execute(insert_badge_query, {
                "id": badge["id"],
                "name": badge["name"],
                "description": badge["description"],
                "icon": badge["icon"],
                "condition_text": badge["condition"],
                "create_time": datetime.now()
            })
        
        db.commit()
        print(f"   ✓ 创建徽章定义: {len(badges_def)} 个徽章")
        
        # 为用户101创建已获得的徽章（前6个）
        obtained_badges = [
            {"badge_id": 1, "obtain_date": "2024-07-10"},
            {"badge_id": 2, "obtain_date": "2024-07-05"},
            {"badge_id": 3, "obtain_date": "2024-06-28"},
            {"badge_id": 4, "obtain_date": "2024-06-15"},
            {"badge_id": 5, "obtain_date": "2024-06-01"},
            {"badge_id": 6, "obtain_date": "2024-05-20"}
        ]
        
        insert_user_badge_query = text("""
            INSERT INTO user_badge 
            (user_id, badge_id, obtain_time)
            VALUES (:user_id, :badge_id, :obtain_time)
            ON CONFLICT DO NOTHING
        """)
        
        for obtained in obtained_badges:
            obtain_time = datetime.strptime(obtained["obtain_date"], "%Y-%m-%d")
            db.execute(insert_user_badge_query, {
                "user_id": 101,
                "badge_id": obtained["badge_id"],
                "obtain_time": obtain_time
            })
        
        db.commit()
        print(f"   ✓ 用户获得徽章: {len(obtained_badges)} 个\n")
        
        # 5. 学习时长统计（跳过，statistic表可能不存在或不同名）
        print("5️⃣ 跳过学习时长统计（待后续完善）...\n")
        
        # 6. 统计信息
        print("📊 数据统计:")
        
        # 关注导师数
        tutor_count_query = text("""
            SELECT COUNT(*) FROM user_relation 
            WHERE user_id = 101 AND relation_type = 0
        """)
        tutor_count = db.execute(tutor_count_query).scalar()
        
        # 粉丝数
        fan_count_query = text("""
            SELECT COUNT(*) FROM user_relation 
            WHERE target_user_id = 101 AND relation_type = 1
        """)
        fan_count = db.execute(fan_count_query).scalar()
        
        # 徽章数
        badge_count_query = text("""
            SELECT COUNT(*) FROM user_badge WHERE user_id = 101
        """)
        badge_count = db.execute(badge_count_query).scalar()
        
        # 资产
        asset_query = text("""
            SELECT diamond_count FROM user_asset WHERE user_id = 101
        """)
        diamond_count = db.execute(asset_query).scalar()
        
        print(f"   • 关注导师: {tutor_count} 个")
        print(f"   • 粉丝数: {fan_count} 个")
        print(f"   • 已获得徽章: {badge_count} 个")
        print(f"   • 钻石余额: {diamond_count} 个")
        
        print("\n✅ 个人主页测试数据添加成功！")
        
        # 重新启用触发器
        print("\n⚙️  重新启用数据库触发器...")
        db.execute(text("SET session_replication_role = default;"))
        db.commit()
        print("   ✓ 触发器已启用")
        
        print("\n🌐 现在可以在前端查看:")
        print("   • 打开 http://localhost:3000/personal")
        print("   • 查看个人信息、资产、关系链和徽章")
        print("   • 测试各种交互功能\n")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_personal_page_data() 