#!/usr/bin/env python3
"""
添加用户101的关系数据（关注导师、粉丝）
"""
import psycopg2
from datetime import datetime
import json

def main():
    # 数据库连接
    conn = psycopg2.connect(
        host="localhost",
        database="ai_time_management",
        user="yeya"
    )
    
    cursor = conn.cursor()
    
    try:
        print("=" * 60)
        print("开始添加用户101的关系数据...")
        print("=" * 60)
        
        # 1. 获取现有导师数据
        cursor.execute("SELECT id, username FROM tutor LIMIT 5")
        tutors = cursor.fetchall()
        print(f"找到 {len(tutors)} 个导师")
        
        # 2. 添加用户101关注的导师（前3个导师）
        # relation_type: 0 = tutor (关注导师)
        print("\n添加用户101关注的导师...")
        for tutor_id, tutor_name in tutors[:3]:
            try:
                cursor.execute("""
                    INSERT INTO user_relation (user_id, target_user_id, relation_type, create_time)
                    VALUES (101, %s, 0, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, target_user_id, relation_type) DO NOTHING
                """, (tutor_id,))
                if cursor.rowcount > 0:
                    print(f"✅ 用户101关注导师: {tutor_name} (ID: {tutor_id})")
                else:
                    print(f"⚠️  用户101已经关注了导师: {tutor_name}")
            except Exception as e:
                print(f"⚠️  关注导师失败: {e}")
        
        conn.commit()
        
        # 3. 创建一些其他用户作为粉丝
        print("\n创建一些用户作为粉丝...")
        fans_data = [
            ("fan_user1", "粉丝用户1", "13800000001", "https://example.com/fan1.jpg"),
            ("fan_user2", "粉丝用户2", "13800000002", "https://example.com/fan2.jpg"),
            ("fan_user3", "粉丝用户3", "13800000003", "https://example.com/fan3.jpg"),
            ("fan_user4", "粉丝用户4", "13800000004", "https://example.com/fan4.jpg"),
        ]
        
        fan_ids = []
        for username, nickname, phone, avatar in fans_data:
            try:
                # 首先检查用户是否已存在
                cursor.execute("SELECT id FROM \"user\" WHERE phone = %s", (phone,))
                result = cursor.fetchone()
                if result:
                    fan_ids.append((result[0], username))
                    print(f"ℹ️  粉丝用户已存在: {username} (ID: {result[0]})")
                else:
                    cursor.execute("""
                        INSERT INTO "user" (username, phone, password_hash, avatar, created_at, updated_at)
                        VALUES (%s, %s, 'hashed_password_placeholder', %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        RETURNING id
                    """, (username, phone, avatar))
                    fan_id = cursor.fetchone()[0]
                    fan_ids.append((fan_id, username))
                    print(f"✅ 创建粉丝用户: {username} (ID: {fan_id})")
                    conn.commit()
            except Exception as e:
                print(f"⚠️  创建粉丝用户失败: {e}")
                conn.rollback()
                # 再次尝试获取已存在的用户
                try:
                    cursor.execute("SELECT id FROM \"user\" WHERE phone = %s", (phone,))
                    result = cursor.fetchone()
                    if result:
                        fan_ids.append((result[0], username))
                        print(f"ℹ️  已找到用户: {username} (ID: {result[0]})")
                except:
                    pass
        
        # 4. 让这些粉丝关注用户101
        # relation_type: 1 = following (关注普通用户，用户101的粉丝)
        print("\n添加粉丝关注用户101...")
        for fan_id, fan_name in fan_ids:
            try:
                cursor.execute("""
                    INSERT INTO user_relation (user_id, target_user_id, relation_type, create_time)
                    VALUES (%s, 101, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT (user_id, target_user_id, relation_type) DO NOTHING
                """, (fan_id,))
                if cursor.rowcount > 0:
                    print(f"✅ {fan_name} (ID: {fan_id}) 关注了用户101")
                else:
                    print(f"⚠️  {fan_name} 已经关注了用户101")
            except Exception as e:
                print(f"⚠️  添加粉丝关系失败: {e}")
        
        conn.commit()
        
        # 5. 验证数据
        print("\n" + "=" * 60)
        print("验证关系数据...")
        print("=" * 60)
        
        # 统计用户101关注的导师数（relation_type = 0）
        cursor.execute("""
            SELECT COUNT(*) FROM user_relation 
            WHERE user_id = 101 AND relation_type = 0
        """)
        tutor_count = cursor.fetchone()[0]
        print(f"✅ 用户101关注的导师数: {tutor_count}")
        
        # 统计用户101的粉丝数（relation_type = 1）
        cursor.execute("""
            SELECT COUNT(*) FROM user_relation 
            WHERE target_user_id = 101 AND relation_type = 1
        """)
        fan_count = cursor.fetchone()[0]
        print(f"✅ 用户101的粉丝数: {fan_count}")
        
        print("\n" + "=" * 60)
        print("✅ 用户关系数据添加完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main() 