#!/usr/bin/env python3
"""
添加动态页面测试数据
创建用户并分配本地头像，添加动态和干货内容
"""
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from sqlalchemy import text

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.database import SessionLocal
from models.moment import Moment

def add_moment_users_and_posts():
    """添加用户和动态数据"""
    db = SessionLocal()
    
    try:
        print("🚀 开始添加动态页面测试数据...\n")
        
        # 1. 创建用户（分配本地头像）
        print("1️⃣ 创建用户...")
        
        users_data = [
            {
                "id": 101,
                "username": "考研的小琳",
                "phone": "13800000101",
                "password_hash": "hashed_password_101",
                "avatar": "/avatars/avatar1.png",
                "goal": "考研上岸",
                "major": "英语"
            },
            {
                "id": 102,
                "username": "琪琪要上岸",
                "phone": "13800000102",
                "password_hash": "hashed_password_102",
                "avatar": "/avatars/avatar2.png",
                "goal": "考研上岸",
                "major": "计算机"
            },
            {
                "id": 103,
                "username": "考研的小艾",
                "phone": "13800000103",
                "password_hash": "hashed_password_103",
                "avatar": "/avatars/avatar3.png",
                "goal": "考研上岸",
                "major": "英语"
            },
            {
                "id": 104,
                "username": "张学姐笔记",
                "phone": "13800000104",
                "password_hash": "hashed_password_104",
                "avatar": "/avatars/avatar4.jpg",
                "goal": "研究生在读",
                "major": "会计"
            },
            {
                "id": 105,
                "username": "学习小达人",
                "phone": "13800000105",
                "password_hash": "hashed_password_105",
                "avatar": "/avatars/avatar5.png",
                "goal": "考研上岸",
                "major": "数学"
            },
            {
                "id": 106,
                "username": "努力的小李",
                "phone": "13800000106",
                "password_hash": "hashed_password_106",
                "avatar": "/avatars/avatar1.png",
                "goal": "考研上岸",
                "major": "法律"
            },
            {
                "id": 107,
                "username": "图书馆常客",
                "phone": "13800000107",
                "password_hash": "hashed_password_107",
                "avatar": "/avatars/avatar2.png",
                "goal": "考研上岸",
                "major": "历史"
            },
            {
                "id": 108,
                "username": "平台活动",
                "phone": "13800000108",
                "password_hash": "hashed_password_108",
                "avatar": "/avatars/avatar3.png",
                "goal": "平台运营",
                "major": "运营"
            }
        ]
        
        for user_data in users_data:
            # 检查用户是否已存在
            check_query = text("SELECT id FROM \"user\" WHERE id = :user_id")
            result = db.execute(check_query, {"user_id": user_data["id"]}).fetchone()
            
            if result:
                # 更新头像
                update_query = text("""
                    UPDATE "user" 
                    SET avatar = :avatar, username = :username, goal = :goal, major = :major
                    WHERE id = :user_id
                """)
                db.execute(update_query, {
                    "user_id": user_data["id"],
                    "avatar": user_data["avatar"],
                    "username": user_data["username"],
                    "goal": user_data["goal"],
                    "major": user_data["major"]
                })
                print(f"   ✓ 更新用户: {user_data['username']} (ID: {user_data['id']}) - {user_data['avatar']}")
            else:
                # 创建新用户
                insert_query = text("""
                    INSERT INTO "user" (id, username, phone, password_hash, avatar, goal, major)
                    VALUES (:id, :username, :phone, :password_hash, :avatar, :goal, :major)
                """)
                db.execute(insert_query, user_data)
                print(f"   ✓ 创建用户: {user_data['username']} (ID: {user_data['id']}) - {user_data['avatar']}")
        
        db.commit()
        print(f"✅ 共处理 {len(users_data)} 个用户\n")
        
        # 2. 创建动态内容
        print("2️⃣ 创建动态内容...")
        
        # 先删除已有的测试动态（避免重复）
        delete_query = text("DELETE FROM moment WHERE user_id IN (101, 102, 103, 104, 105, 106, 107, 108)")
        db.execute(delete_query)
        db.commit()
        
        moments_data = [
            {
                "user_id": 108,
                "type": 2,  # 广告
                "title": "上传上岸时间表，赢高奢真皮包！",
                "content": "真实时间表+上岸证明=品牌定制包，已有28人获奖，点击参与→",
                "tags": ["#上传时间表", "#赢奖品"],
                "is_top": 1,
                "ad_info": "奖品：真皮笔记本/珍珠首饰",
                "like_count": 0,
                "comment_count": 0,
                "share_count": 0
            },
            {
                "user_id": 101,
                "type": 0,  # 动态
                "title": None,
                "content": "今天做英语阅读错了5道😩 感觉长难句还是没吃透...",
                "tags": ["#考研英语", "#今日复盘"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 12,
                "comment_count": 3,
                "share_count": 0
            },
            {
                "user_id": 102,
                "type": 0,  # 动态
                "title": None,
                "content": "图书馆学习氛围太好了！专注了4小时💪 推荐大家试试番茄工作法，真的有用！",
                "tags": ["#图书馆打卡", "#学习方法"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 36,
                "comment_count": 12,
                "share_count": 5,
                "image_url": "https://picsum.photos/400/240?random=1"
            },
            {
                "user_id": 105,
                "type": 0,  # 动态
                "title": None,
                "content": "终于把数学真题做完了！这个月进步好大，继续加油！💪📚",
                "tags": ["#考研数学", "#每日打卡"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 28,
                "comment_count": 8,
                "share_count": 2
            },
            {
                "user_id": 106,
                "type": 0,  # 动态
                "title": None,
                "content": "今天状态不太好，但还是坚持学了3小时。慢慢来，不要着急！",
                "tags": ["#自我鼓励", "#考研加油"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 45,
                "comment_count": 15,
                "share_count": 1
            },
            {
                "user_id": 107,
                "type": 0,  # 动态
                "title": None,
                "content": "在图书馆遇到了学习小伙伴，一起学习效率更高！📖",
                "tags": ["#图书馆打卡", "#学习搭子"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 52,
                "comment_count": 20,
                "share_count": 3,
                "image_url": "https://picsum.photos/400/240?random=2"
            },
            # 干货内容
            {
                "user_id": 103,
                "type": 1,  # 干货
                "title": "考研英语3个月提分18分的时间表模板",
                "content": "每天1.5h精读+1h单词，用艾宾浩斯复习法复盘，感谢王英语老师的规划！附上我的详细时间安排和学习方法。",
                "tags": ["#考研英语", "#时间表模板", "#提分经验"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 156,
                "comment_count": 42,
                "share_count": 28,
                "image_url": "https://picsum.photos/400/240?random=3"
            },
            {
                "user_id": 104,
                "type": 1,  # 干货
                "title": "财务管理高频考点整理（附记忆方法）",
                "content": "整理了近5年财务管理考研高频考点，特别是长期股权投资这一章，结合思维导图学习法记忆效率翻倍！",
                "tags": ["#财务管理", "#考点整理", "#记忆方法"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 215,
                "comment_count": 58,
                "share_count": 42
            },
            {
                "user_id": 105,
                "type": 1,  # 干货
                "title": "高等数学错题本整理技巧分享",
                "content": "分享我的错题整理方法：按题型分类、标注易错点、定期复习。这个方法让我数学成绩从70分提升到110+！",
                "tags": ["#考研数学", "#学习方法", "#错题本"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 189,
                "comment_count": 35,
                "share_count": 25
            },
            {
                "user_id": 102,
                "type": 1,  # 干货
                "title": "计算机专业课复习时间规划表",
                "content": "408统考的同学看过来！分享我的复习时间规划，包括数据结构、操作系统、计算机网络和组成原理的时间分配。",
                "tags": ["#计算机考研", "#408统考", "#时间规划"],
                "is_top": 0,
                "ad_info": None,
                "like_count": 278,
                "comment_count": 67,
                "share_count": 55,
                "image_url": "https://picsum.photos/400/240?random=4"
            }
        ]
        
        now = datetime.now()
        success_count = 0
        for i, moment_data in enumerate(moments_data):
            try:
                # 根据索引设置不同的创建时间（越靠前越新）
                create_time = now - timedelta(minutes=i * 30)
                
                # 使用ORM模型插入
                moment = Moment(
                    user_id=moment_data["user_id"],
                    type=moment_data["type"],
                    title=moment_data.get("title"),
                    content=moment_data["content"],
                    tags=moment_data["tags"],  # SQLAlchemy会自动处理JSON
                    is_top=moment_data.get("is_top", 0),
                    ad_info=moment_data.get("ad_info"),
                    like_count=moment_data.get("like_count", 0),
                    comment_count=moment_data.get("comment_count", 0),
                    share_count=moment_data.get("share_count", 0),
                    image_url=moment_data.get("image_url"),
                    status=1,  # 1表示已发布
                    create_time=create_time,
                    update_time=create_time
                )
                db.add(moment)
                db.commit()  # 逐个commit避免批量trigger问题
                
                success_count += 1
                type_name = "广告" if moment_data["type"] == 2 else ("干货" if moment_data["type"] == 1 else "动态")
                user_name = next(u["username"] for u in users_data if u["id"] == moment_data["user_id"])
                print(f"   ✓ 创建{type_name}: {user_name} - {moment_data.get('title') or moment_data['content'][:30]}...")
            except Exception as e:
                # 如果个别插入失败（比如badge trigger问题），回滚并继续
                db.rollback()
                type_name = "广告" if moment_data["type"] == 2 else ("干货" if moment_data["type"] == 1 else "动态")
                user_name = next(u["username"] for u in users_data if u["id"] == moment_data["user_id"])
                print(f"   ✗ 跳过{type_name}: {user_name} (触发器错误)")
        
        print(f"✅ 共创建 {success_count}/{len(moments_data)} 条动态\n")
        
        # 3. 统计信息
        print("📊 数据统计:")
        count_query = text("SELECT COUNT(*) FROM \"user\" WHERE id >= 101 AND id <= 108")
        user_count = db.execute(count_query).scalar()
        
        moment_count_query = text("SELECT COUNT(*) FROM moment WHERE user_id >= 101 AND user_id <= 108")
        moment_count = db.execute(moment_count_query).scalar()
        
        dynamic_count_query = text("SELECT COUNT(*) FROM moment WHERE user_id >= 101 AND user_id <= 108 AND type = 0")
        dynamic_count = db.execute(dynamic_count_query).scalar()
        
        drygoods_count_query = text("SELECT COUNT(*) FROM moment WHERE user_id >= 101 AND user_id <= 108 AND type = 1")
        drygoods_count = db.execute(drygoods_count_query).scalar()
        
        ad_count_query = text("SELECT COUNT(*) FROM moment WHERE user_id >= 101 AND user_id <= 108 AND type = 2")
        ad_count = db.execute(ad_count_query).scalar()
        
        print(f"   • 用户数: {user_count}")
        print(f"   • 总动态数: {moment_count}")
        print(f"   • 动态: {dynamic_count}")
        print(f"   • 干货: {drygoods_count}")
        print(f"   • 广告: {ad_count}")
        
        print("\n✅ 动态页面测试数据添加成功！")
        print("\n🌐 现在可以在前端查看:")
        print("   • 打开 http://localhost:3000/moments")
        print("   • 查看带头像的用户动态")
        print("   • 切换动态/干货模式\n")
        
        print("📋 用户列表:")
        for user in users_data:
            print(f"   • ID {user['id']}: {user['username']} - {user['avatar']}")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    add_moment_users_and_posts() 