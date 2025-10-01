#!/usr/bin/env python3
"""手动测试Badge API"""

import requests
import json

base_url = "http://localhost:8000"
user_id = 1

def test_api(name, url, method="GET", data=None):
    """测试API端点"""
    print(f"\n{'='*60}")
    print(f"测试: {name}")
    print(f"URL: {url}")
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 成功")
            print(f"响应: {json.dumps(result, ensure_ascii=False, indent=2)[:500]}")
        else:
            print(f"❌ 失败")
            print(f"响应: {response.text[:300]}")
            
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False

# 测试列表
tests = [
    ("获取所有徽章", f"{base_url}/api/v1/badges/?user_id={user_id}&limit=5", "GET"),
    ("获取用户徽章", f"{base_url}/api/v1/badges/my?user_id={user_id}", "GET"),
    ("获取徽章详情", f"{base_url}/api/v1/badges/1?user_id={user_id}", "GET"),
    ("获取展示的徽章", f"{base_url}/api/v1/badges/display/current?user_id={user_id}", "GET"),
]

print("="*60)
print("🧪 Badge API 手动测试")
print("="*60)

passed = 0
total = len(tests)

for name, url, method in tests:
    if test_api(name, url, method):
        passed += 1

print(f"\n{'='*60}")
print(f"📊 测试结果: {passed}/{total} 通过")
print(f"成功率: {(passed/total*100):.1f}%")
print("="*60)
