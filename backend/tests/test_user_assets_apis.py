#!/usr/bin/env python3
"""
User Assets API 测试脚本
测试用户资产管理、充值、购买导师服务等API

⚠️  注意: 此测试需要以下数据库表：
- user_asset_record (资产变动记录)
- recharge_order (充值订单)

当前数据库缺少这些表，因此部分测试将被跳过。

测试内容:
1. 获取用户资产信息 ✓
2. 创建充值订单 (需要 recharge_order 表)
3. 获取资产变动记录 (需要 user_asset_record 表)
4. 购买导师服务（扣减钻石） ✓
5. 查询导师服务订单历史 ✓
"""

import requests
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal
from datetime import datetime
import time

# API和数据库配置
API_BASE_URL = "http://localhost:8000"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ai_time_management",
    "user": "yeya",
    "password": ""
}

# 测试用户ID
TEST_USER_ID = 1001
TEST_TUTOR_ID = 1
TEST_SERVICE_ID = 1

def get_db_connection():
    """获取数据库连接"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def check_table_exists(table_name):
    """检查表是否存在"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = %s
            )
        """, (table_name,))
        result = cursor.fetchone()
        return result['exists']
    finally:
        cursor.close()
        conn.close()

def setup_test_data():
    """准备测试数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("🔧 准备测试数据...")
        
        # 1. 确保测试用户存在
        cursor.execute("""
            INSERT INTO "user" (id, username, phone, password_hash, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET username = EXCLUDED.username
        """, (TEST_USER_ID, f"test_user_{TEST_USER_ID}", f"+8613800{TEST_USER_ID}", "hashed_pwd", 0, datetime.now(), datetime.now()))
        
        # 2. 创建用户资产记录（初始500钻石）
        cursor.execute("DELETE FROM user_asset WHERE user_id = %s", (TEST_USER_ID,))
        cursor.execute("""
            INSERT INTO user_asset (user_id, diamond_count, created_at, updated_at)
            VALUES (%s, %s, %s, %s)
        """, (TEST_USER_ID, 500, datetime.now(), datetime.now()))
        
        # 3. 删除旧导师数据
        cursor.execute("DELETE FROM tutor WHERE id = %s", (TEST_TUTOR_ID,))
        
        # 4. 创建测试导师
        cursor.execute("""
            INSERT INTO tutor (id, username, type, domain, education, experience, rating, student_count, success_rate, monthly_guide_count, status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (TEST_TUTOR_ID, "测试导师", 0, "数学", "清华大学", "5年教学经验", 48, 100, 95, 10, 1))
        
        # 5. 创建导师服务（价格100钻石）
        cursor.execute("""
            INSERT INTO tutor_service (id, tutor_id, name, price, description, service_type, is_active, create_time, update_time)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO UPDATE SET price = EXCLUDED.price
        """, (TEST_SERVICE_ID, TEST_TUTOR_ID, "一对一咨询", 100, "1小时一对一辅导", "consultation", 1, datetime.now(), datetime.now()))
        
        conn.commit()
        print("✅ 测试数据准备完成")
        print(f"   - 测试用户ID: {TEST_USER_ID}, 初始钻石: 500")
        print(f"   - 测试导师ID: {TEST_TUTOR_ID}")
        print(f"   - 测试服务ID: {TEST_SERVICE_ID}, 价格: 100钻石")
        
        # 检查缺失的表
        missing_tables = []
        for table in ['user_asset_record', 'recharge_order']:
            if not check_table_exists(table):
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️  警告: 以下表不存在，相关测试将被跳过: {', '.join(missing_tables)}")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 准备测试数据失败: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def cleanup_test_data():
    """清理测试数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        print("\n🧹 清理测试数据...")
        
        # 按外键依赖顺序删除
        cursor.execute("DELETE FROM tutor_service_order WHERE user_id = %s", (TEST_USER_ID,))
        cursor.execute("DELETE FROM user_asset WHERE user_id = %s", (TEST_USER_ID,))
        cursor.execute("DELETE FROM tutor_service WHERE tutor_id = %s", (TEST_TUTOR_ID,))
        cursor.execute("DELETE FROM tutor WHERE id = %s", (TEST_TUTOR_ID,))
        cursor.execute('DELETE FROM "user" WHERE id IN (%s, %s)', (TEST_USER_ID, TEST_USER_ID + 1000))
        
        conn.commit()
        print("✅ 测试数据清理完成")
        
    except Exception as e:
        conn.rollback()
        print(f"❌ 清理测试数据失败: {e}")
    finally:
        cursor.close()
        conn.close()

def verify_in_database(query, params=None):
    """在数据库中验证数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchone()
        return result
    finally:
        cursor.close()
        conn.close()

# ============================================================================
# 测试用例
# ============================================================================

def test_get_user_assets():
    """测试1: 获取用户资产信息"""
    print("\n" + "="*80)
    print("测试1: GET /api/v1/users/me/assets - 获取用户资产信息")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/users/me/assets"
    params = {"user_id": TEST_USER_ID}
    
    response = requests.get(url, params=params)
    
    print(f"请求: GET {url}")
    print(f"参数: {params}")
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 验证数据库
    db_result = verify_in_database(
        "SELECT user_id, diamond_count FROM user_asset WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    if response.status_code == 200:
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert data["diamond_count"] == 500
        
        if db_result:
            print(f"✅ 数据库验证: diamond_count = {db_result['diamond_count']}")
        
        print("✅ 测试通过")
        return True
    else:
        print(f"❌ 测试失败: {response.text}")
        return False

def test_create_recharge_order():
    """测试2: 创建充值订单"""
    print("\n" + "="*80)
    print("测试2: POST /api/v1/users/me/assets/recharge - 创建充值订单")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/users/me/assets/recharge"
    params = {"user_id": TEST_USER_ID}
    payload = {
        "amount": 50.0,
        "payment_method": "alipay"
    }
    
    response = requests.post(url, json=payload, params=params)
    
    print(f"请求: POST {url}")
    print(f"参数: {params}")
    print(f"请求体: {payload}")
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        assert "order_id" in data
        assert data["amount"] == 50.0
        assert data["diamond_count"] == 500  # 50元 * 10 = 500钻石
        assert "payment_url" in data
        
        # 验证数据库中订单已创建
        db_result = verify_in_database(
            "SELECT order_id, amount, diamond_count, status FROM recharge_order WHERE order_id = %s",
            (data["order_id"],)
        )
        
        if db_result:
            print(f"✅ 数据库验证: 订单 {db_result['order_id']}, 状态: {db_result['status']}")
        
        print("✅ 测试通过")
        return True
    else:
        print(f"❌ 测试失败: {response.text}")
        return False

def test_get_asset_records():
    """测试3: 获取资产变动记录"""
    print("\n" + "="*80)
    print("测试3: GET /api/v1/users/me/assets/records - 获取资产变动记录")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/users/me/assets/records"
    params = {"user_id": TEST_USER_ID, "limit": 10, "offset": 0}
    
    response = requests.get(url, params=params)
    
    print(f"请求: GET {url}")
    print(f"参数: {params}")
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 验证数据库
    db_count = verify_in_database(
        "SELECT COUNT(*) as count FROM user_asset_record WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least the initial reward record
        
        if db_count:
            print(f"✅ 数据库验证: 共 {db_count['count']} 条记录")
        
        print("✅ 测试通过")
        return True
    else:
        print(f"❌ 测试失败: {response.text}")
        return False

def test_purchase_tutor_service():
    """测试4: 购买导师服务"""
    print("\n" + "="*80)
    print("测试4: POST /api/v1/users/me/assets/purchase - 购买导师服务")
    print("="*80)
    
    # 先查询初始余额
    initial_balance = verify_in_database(
        "SELECT diamond_count FROM user_asset WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    print(f"购买前余额: {initial_balance['diamond_count'] if initial_balance else 0} 钻石")
    
    url = f"{API_BASE_URL}/api/v1/users/me/assets/purchase"
    params = {"user_id": TEST_USER_ID}
    payload = {
        "tutor_id": TEST_TUTOR_ID,
        "service_id": TEST_SERVICE_ID
    }
    
    response = requests.post(url, json=payload, params=params)
    
    print(f"请求: POST {url}")
    print(f"参数: {params}")
    print(f"请求体: {payload}")
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        assert data["user_id"] == TEST_USER_ID
        assert data["tutor_id"] == TEST_TUTOR_ID
        assert data["service_id"] == TEST_SERVICE_ID
        assert data["amount"] == 100  # Service price
        assert "order_id" in data
        
        # 验证数据库中钻石已扣减
        final_balance = verify_in_database(
            "SELECT diamond_count FROM user_asset WHERE user_id = %s",
            (TEST_USER_ID,)
        )
        
        if initial_balance and final_balance:
            expected_balance = initial_balance['diamond_count'] - 100
            actual_balance = final_balance['diamond_count']
            print(f"购买后余额: {actual_balance} 钻石")
            print(f"预期余额: {expected_balance} 钻石")
            assert actual_balance == expected_balance, f"余额不匹配: 预期 {expected_balance}, 实际 {actual_balance}"
            print(f"✅ 数据库验证: 钻石已扣减 100, 剩余 {actual_balance}")
        
        # 验证订单已创建
        order_result = verify_in_database(
            "SELECT order_no, amount, status FROM tutor_service_order WHERE order_no = %s",
            (data["order_id"],)
        )
        
        if order_result:
            print(f"✅ 订单验证: {order_result['order_no']}, 金额: {order_result['amount']}, 状态: {order_result['status']}")
        
        # 验证消费记录已创建
        record_result = verify_in_database(
            "SELECT record_type, amount, description FROM user_asset_record WHERE user_id = %s AND record_type = 'consume' ORDER BY create_time DESC LIMIT 1",
            (TEST_USER_ID,)
        )
        
        if record_result:
            print(f"✅ 记录验证: {record_result['description']}, 金额: {record_result['amount']}")
        
        print("✅ 测试通过")
        return True
    else:
        print(f"❌ 测试失败: {response.text}")
        return False

def test_get_tutor_service_orders():
    """测试5: 查询导师服务订单历史"""
    print("\n" + "="*80)
    print("测试5: GET /api/v1/users/me/orders/tutor - 查询导师服务订单历史")
    print("="*80)
    
    url = f"{API_BASE_URL}/api/v1/users/me/orders/tutor"
    params = {"user_id": TEST_USER_ID, "page": 1, "page_size": 20}
    
    response = requests.get(url, params=params)
    
    print(f"请求: GET {url}")
    print(f"参数: {params}")
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    # 验证数据库
    db_count = verify_in_database(
        "SELECT COUNT(*) as count FROM tutor_service_order WHERE user_id = %s",
        (TEST_USER_ID,)
    )
    
    if response.status_code == 200:
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # At least one order from previous test
        
        # 验证订单信息
        first_order = data[0]
        assert first_order["user_id"] == TEST_USER_ID
        assert first_order["tutor_id"] == TEST_TUTOR_ID
        assert first_order["service_id"] == TEST_SERVICE_ID
        
        if db_count:
            print(f"✅ 数据库验证: 共 {db_count['count']} 个订单")
        
        print("✅ 测试通过")
        return True
    else:
        print(f"❌ 测试失败: {response.text}")
        return False

def test_insufficient_balance():
    """测试6: 余额不足时购买服务"""
    print("\n" + "="*80)
    print("测试6: POST /api/v1/users/me/assets/purchase - 余额不足测试")
    print("="*80)
    
    # 先将用户余额设置为50（不足以购买100钻石的服务）
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_asset SET diamond_count = 50 WHERE user_id = %s", (TEST_USER_ID,))
    conn.commit()
    cursor.close()
    conn.close()
    
    url = f"{API_BASE_URL}/api/v1/users/me/assets/purchase"
    params = {"user_id": TEST_USER_ID}
    payload = {
        "tutor_id": TEST_TUTOR_ID,
        "service_id": TEST_SERVICE_ID
    }
    
    response = requests.post(url, json=payload, params=params)
    
    print(f"请求: POST {url}")
    print(f"当前余额: 50 钻石, 服务价格: 100 钻石")
    print(f"响应状态: {response.status_code}")
    print(f"响应内容: {response.json()}")
    
    if response.status_code == 500:  # Should fail with insufficient balance
        error_data = response.json()
        assert "钻石余额不足" in error_data.get("detail", "")
        print("✅ 测试通过: 正确拒绝余额不足的购买")
        return True
    else:
        print(f"❌ 测试失败: 应该返回余额不足错误")
        return False

# ============================================================================
# 主测试流程
# ============================================================================

def main():
    print("\n" + "🚀 " + "="*76)
    print("   User Assets API 测试开始")
    print("="*80)
    
    # 准备测试数据
    setup_test_data()
    
    # 等待服务器启动
    time.sleep(2)
    
    # 执行测试
    results = []
    tests = [
        ("获取用户资产信息", test_get_user_assets),
        ("创建充值订单", test_create_recharge_order),
        ("获取资产变动记录", test_get_asset_records),
        ("购买导师服务", test_purchase_tutor_service),
        ("查询导师服务订单历史", test_get_tutor_service_orders),
        ("余额不足测试", test_insufficient_balance)
    ]
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            results.append((test_name, False))
    
    # 清理测试数据
    cleanup_test_data()
    
    # 输出测试总结
    print("\n" + "="*80)
    print("📊 测试总结")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {test_name}")
    
    print("="*80)
    print(f"总计: {passed}/{total} 测试通过 ({passed/total*100:.1f}%)")
    print("="*80)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 