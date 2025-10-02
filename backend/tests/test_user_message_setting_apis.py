#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
User Message Setting API 测试脚本
测试所有用户消息设置相关的API端点
"""

import requests
import psycopg2
from datetime import datetime, timedelta
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
TEST_USER_ID = 1001

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
        cur.execute("DELETE FROM user_message_setting WHERE user_id = %s", (TEST_USER_ID,))
        cur.execute("DELETE FROM \"user\" WHERE id = %s", (TEST_USER_ID,))
        
        # 2. 创建测试用户
        cur.execute("""
            INSERT INTO "user" (id, username, password_hash, phone)
            VALUES (%s, %s, %s, %s)
        """, (TEST_USER_ID, f"test_user_{TEST_USER_ID}", "hashed_password", "13800000000"))
        
        conn.commit()
        print("✅ 测试数据准备完成")
        print(f"   - 测试用户ID: {TEST_USER_ID}")
        
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
        cur.execute("DELETE FROM user_message_setting WHERE user_id = %s", (TEST_USER_ID,))
        cur.execute("DELETE FROM \"user\" WHERE id = %s", (TEST_USER_ID,))
        conn.commit()
        print("✅ 测试数据清理完成")
    except Exception as e:
        conn.rollback()
        print(f"❌ 清理测试数据失败: {e}")
    finally:
        cur.close()
        conn.close()

def test_get_message_settings():
    """测试1: 获取用户消息设置"""
    print("\n" + "=" * 80)
    print("测试1: GET /api/v1/users/me/message-settings - 获取用户消息设置")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/message-settings"
    params = {"user_id": TEST_USER_ID}
    
    try:
        print(f"请求: GET {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            # 验证返回数据结构
            assert "user_id" in data, "响应缺少user_id字段"
            assert data["user_id"] == TEST_USER_ID, "user_id不匹配"
            assert "reminder_type" in data, "响应缺少reminder_type字段"
            assert "keep_days" in data, "响应缺少keep_days字段"
            
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_update_message_settings():
    """测试2: 更新用户消息设置"""
    print("\n" + "=" * 80)
    print("测试2: PUT /api/v1/users/me/message-settings - 更新用户消息设置")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/message-settings"
    params = {"user_id": TEST_USER_ID}
    data = {
        "reminder_type": "email",
        "keep_days": 60
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
            assert result.get("success") == True, "更新操作失败"
            
            # 验证数据库中的更新
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT keep_days FROM user_message_setting 
                WHERE user_id = %s
            """, (TEST_USER_ID,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                print(f"✅ 数据库验证: keep_days = {row[0]}")
                assert row[0] == 60, f"keep_days更新失败，期望60，实际{row[0]}"
            
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_reset_message_settings():
    """测试3: 重置消息设置为默认值"""
    print("\n" + "=" * 80)
    print("测试3: POST /api/v1/users/me/message-settings/reset - 重置消息设置")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/message-settings/reset"
    params = {"user_id": TEST_USER_ID}
    
    try:
        print(f"请求: POST {url}")
        print(f"参数: {params}")
        
        response = requests.post(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            result = response.json()
            assert result.get("success") == True, "重置操作失败"
            
            # 验证是否重置为默认值
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("""
                SELECT reminder_type, keep_days FROM user_message_setting 
                WHERE user_id = %s
            """, (TEST_USER_ID,))
            row = cur.fetchone()
            cur.close()
            conn.close()
            
            if row:
                print(f"✅ 数据库验证: reminder_type={row[0]}, keep_days={row[1]}")
            
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_get_setting_summary():
    """测试4: 获取消息设置摘要"""
    print("\n" + "=" * 80)
    print("测试4: GET /api/v1/users/me/message-settings/summary - 获取设置摘要")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/message-settings/summary"
    params = {"user_id": TEST_USER_ID}
    
    try:
        print(f"请求: GET {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data, "响应缺少user_id字段"
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_get_reminder_preferences():
    """测试5: 获取提醒偏好"""
    print("\n" + "=" * 80)
    print("测试5: GET /api/v1/users/me/reminder-preferences - 获取提醒偏好")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/reminder-preferences"
    params = {"user_id": TEST_USER_ID}
    
    try:
        print(f"请求: GET {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data, "响应缺少user_id字段"
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_get_cleanup_settings():
    """测试6: 获取消息清理设置"""
    print("\n" + "=" * 80)
    print("测试6: GET /api/v1/users/me/cleanup-settings - 获取清理设置")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/cleanup-settings"
    params = {"user_id": TEST_USER_ID}
    
    try:
        print(f"请求: GET {url}")
        print(f"参数: {params}")
        
        response = requests.get(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert "user_id" in data, "响应缺少user_id字段"
            assert "keep_days" in data, "响应缺少keep_days字段"
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_check_reminder():
    """测试7: 检查是否应该发送提醒"""
    print("\n" + "=" * 80)
    print("测试7: POST /api/v1/users/me/check-reminder - 检查提醒设置")
    print("=" * 80)
    
    url = f"{API_BASE_URL}/me/check-reminder"
    params = {"user_id": TEST_USER_ID, "message_type": "tutor"}
    
    try:
        print(f"请求: POST {url}")
        print(f"参数: {params}")
        
        response = requests.post(url, params=params)
        print(f"响应状态: {response.status_code}")
        print(f"响应内容: {response.json()}")
        
        if response.status_code == 200:
            data = response.json()
            assert "should_send_reminder" in data, "响应缺少should_send_reminder字段"
            print("✅ 测试通过")
            return True
        else:
            print(f"❌ 测试失败: {response.json()}")
            return False
            
    except Exception as e:
        print(f"❌ 测试异常: {e}")
        return False

def test_admin_endpoints():
    """测试8: 管理员接口"""
    print("\n" + "=" * 80)
    print("测试8: 管理员接口测试")
    print("=" * 80)
    
    tests = [
        ("GET", f"{API_BASE_URL}/admin/reminder-users/tutor", {}, "获取提醒用户列表"),
        ("GET", f"{API_BASE_URL}/admin/auto-read-users", {}, "获取自动已读用户列表"),
        ("GET", f"{API_BASE_URL}/admin/cleanup-candidates", {}, "获取清理候选用户")
    ]
    
    all_passed = True
    for method, url, params, desc in tests:
        try:
            print(f"\n  {desc}:")
            print(f"  请求: {method} {url}")
            
            if method == "GET":
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, params=params)
                
            print(f"  响应状态: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ {desc} - 通过")
            else:
                print(f"  ❌ {desc} - 失败: {response.json()}")
                all_passed = False
                
        except Exception as e:
            print(f"  ❌ {desc} - 异常: {e}")
            all_passed = False
    
    return all_passed

def main():
    """主测试流程"""
    print("\n🚀 " + "=" * 76)
    print("   User Message Setting API 测试开始")
    print("=" * 80)
    
    # 准备测试数据
    setup_test_data()
    
    # 运行所有测试
    test_results = {
        "获取用户消息设置": test_get_message_settings(),
        "更新用户消息设置": test_update_message_settings(),
        "重置消息设置": test_reset_message_settings(),
        "获取设置摘要": test_get_setting_summary(),
        "获取提醒偏好": test_get_reminder_preferences(),
        "获取清理设置": test_get_cleanup_settings(),
        "检查提醒设置": test_check_reminder(),
        "管理员接口": test_admin_endpoints()
    }
    
    # 清理测试数据
    cleanup_test_data()
    
    # 输出测试总结
    print("\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)
    
    passed = sum(1 for result in test_results.values() if result)
    total = len(test_results)
    
    for test_name, result in test_results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("=" * 80)
    print(f"总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
    print("=" * 80)

if __name__ == "__main__":
    main() 