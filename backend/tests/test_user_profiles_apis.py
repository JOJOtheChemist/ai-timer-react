#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Profiles API 测试脚本
测试所有用户个人信息相关的API端点
"""

import requests
import psycopg2
from datetime import datetime
import json

# ===== 配置 =====
API_BASE_URL = "http://localhost:8000/api/v1/users"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ai_time_management",
    "user": "yeya",
    "password": ""
}

# 测试用户ID
TEST_USER_ID = 2001

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG)

def setup_test_data():
    """准备测试数据"""
    print("🔧 准备测试数据...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 1. 清理旧数据
        cur.execute("DELETE FROM user_profile WHERE user_id = %s", (TEST_USER_ID,))
        cur.execute("DELETE FROM \"user\" WHERE id = %s", (TEST_USER_ID,))
        
        # 2. 创建测试用户（user表）
        cur.execute("""
            INSERT INTO "user" (id, username, password_hash, phone, avatar, goal, major)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (TEST_USER_ID, f"testuser{TEST_USER_ID}", "hashed_password", "13900000001", 
              "https://example.com/avatar.jpg", "考研上岸", "计算机科学"))
        
        # 3. 创建用户资料（user_profile表）
        cur.execute("""
            INSERT INTO user_profile (user_id, real_name, bio, total_study_hours)
            VALUES (%s, %s, %s, %s)
        """, (TEST_USER_ID, "测试用户", "这是一个测试用户的简介", 100.5))
        
        conn.commit()
        print("✅ 测试数据准备完成")
        print(f"   - 测试用户ID: {TEST_USER_ID}")
        print(f"   - 用户名: testuser{TEST_USER_ID}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 准备测试数据失败: {e}")
        raise
    finally:
        cur.close()
        conn.close()

def cleanup_test_data():
    """清理测试数据"""
    print("\n🧹 清理测试数据...")
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM user_profile WHERE user_id = %s", (TEST_USER_ID,))
        cur.execute("DELETE FROM \"user\" WHERE id = %s", (TEST_USER_ID,))
        conn.commit()
        print("✅ 测试数据清理完成")
    except Exception as e:
        conn.rollback()
        print(f"❌ 清理测试数据失败: {e}")
    finally:
        cur.close()
        conn.close()

def test_get_current_user_profile():
    """测试1: 获取当前用户完整个人信息"""
    print("\n" + "=" * 80)
    print("测试1: GET /api/v1/users/me/profile - 获取用户完整个人信息")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/profile"
    params = {"user_id": TEST_USER_ID}
    
    try:
        print(f"请求: GET {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 验证数据
            assert data["user_id"] == TEST_USER_ID
            assert data["username"] == f"testuser{TEST_USER_ID}"
            assert data["goal"] == "考研上岸"
            assert data["major"] == "计算机科学"
            assert data["real_name"] == "测试用户"
            assert data["bio"] == "这是一个测试用户的简介"
            
            print("✅ 测试通过")
            return True
        else:
            print(f"响应内容: {response.json()}")
            print(f"❌ 测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_update_current_user_profile():
    """测试2: 更新当前用户个人信息"""
    print("\n" + "=" * 80)
    print("测试2: PUT /api/v1/users/me/profile - 更新用户个人信息")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/profile"
    params = {"user_id": TEST_USER_ID}
    data = {
        "goal": "更新后的目标-考博",
        "bio": "更新后的简介"
    }
    
    try:
        print(f"请求: PUT {url}")
        print(f"参数: {params}")
        print(f"请求体: {data}")
        
        response = requests.put(url, params=params, json=data)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            assert result.get("success") == True
            
            # 验证数据库
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT u.goal, up.bio 
                FROM "user" u
                LEFT JOIN user_profile up ON u.id = up.user_id
                WHERE u.id = %s
            """, (TEST_USER_ID,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                print(f"✅ 数据库验证: goal={row[0]}, bio={row[1]}")
                assert row[0] == "更新后的目标-考博"
                assert row[1] == "更新后的简介"
            
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_get_user_simple_info():
    """测试3: 获取用户简易信息"""
    print("\n" + "=" * 80)
    print("测试3: GET /api/v1/users/{user_id}/simple-info - 获取用户简易信息")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/{TEST_USER_ID}/simple-info"
    
    try:
        print(f"请求: GET {url}")
        
        response = requests.get(url)
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 验证数据
            assert data["id"] == TEST_USER_ID
            assert data["username"] == f"testuser{TEST_USER_ID}"
            
            print("✅ 测试通过")
            return True
        else:
            print(f"响应内容: {response.json()}")
            print(f"❌ 测试失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_database_direct_queries():
    """测试4: 直接数据库查询验证"""
    print("\n" + "=" * 80)
    print("测试4: 数据库直接查询 - 验证数据完整性")
    print("=" * 80)
    
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # 查询user表
        cur.execute("""
            SELECT id, username, avatar, phone, goal, major 
            FROM "user" 
            WHERE id = %s
        """, (TEST_USER_ID,))
        user_row = cur.fetchone()
        
        # 查询user_profile表
        cur.execute("""
            SELECT user_id, real_name, bio, total_study_hours
            FROM user_profile 
            WHERE user_id = %s
        """, (TEST_USER_ID,))
        profile_row = cur.fetchone()
        
        if user_row and profile_row:
            print(f"✅ User表数据:")
            print(f"   ID: {user_row[0]}, 用户名: {user_row[1]}")
            print(f"   目标: {user_row[4]}, 专业: {user_row[5]}")
            print(f"\n✅ UserProfile表数据:")
            print(f"   真实姓名: {profile_row[1]}")
            print(f"   简介: {profile_row[2]}")
            print(f"   总学习时长: {profile_row[3]}小时")
            print("\n✅ 测试通过 - 数据库数据完整")
            return True
        else:
            print("❌ 测试失败 - 数据不完整")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False
    finally:
        cur.close()
        conn.close()

def main():
    """主测试流程"""
    print("\n🚀 " + "=" * 76)
    print("   User Profiles API 测试开始")
    print("=" * 80)
    
    # 准备测试数据
    setup_test_data()
    
    # 运行所有测试
    test_results = {
        "获取用户完整个人信息": test_get_current_user_profile(),
        "更新用户个人信息": test_update_current_user_profile(),
        "获取用户简易信息": test_get_user_simple_info(),
        "数据库直接查询验证": test_database_direct_queries()
    }
    
    # 清理测试数据
    cleanup_test_data()
    
    # 输出测试总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    passed = sum(1 for result in test_results.values() if result == True)
    failed = sum(1 for result in test_results.values() if result == False)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("=" * 80)
    print(f"总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main() 