#!/usr/bin/env python3
"""
Tutor API 完整测试脚本
测试所有导师相关的API端点
"""

import httpx
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1/tutors"
TEST_USER_ID = 1  # 测试用户ID

# 测试结果统计
test_results = {
    "total": 0,
    "passed": 0,
    "failed": 0,
    "errors": []
}

# 存储创建的测试数据ID
test_data_ids = {
    "tutor_id": None
}

async def test_api(client: httpx.AsyncClient, name: str, method: str, url: str, **kwargs) -> Dict[str, Any]:
    """
    测试单个API端点
    """
    test_results["total"] += 1
    
    try:
        print(f"\n{'='*60}")
        print(f"测试: {name}")
        print(f"方法: {method} {url}")
        
        if "params" in kwargs:
            print(f"参数: {json.dumps(kwargs['params'], ensure_ascii=False)}")
        if "json" in kwargs:
            print(f"数据: {json.dumps(kwargs['json'], ensure_ascii=False, indent=2)}")
        
        response = await client.request(method, url, **kwargs)
        
        print(f"状态码: {response.status_code}")
        
        try:
            response_data = response.json()
            print(f"响应: {json.dumps(response_data, ensure_ascii=False, indent=2)[:500]}")
        except:
            print(f"响应: {response.text[:500]}")
            response_data = None
        
        if response.status_code in [200, 201]:
            test_results["passed"] += 1
            print(f"✅ 测试通过")
            return {"success": True, "data": response_data, "status_code": response.status_code}
        else:
            test_results["failed"] += 1
            error_msg = f"{name}: HTTP {response.status_code}"
            test_results["errors"].append(error_msg)
            print(f"❌ 测试失败: {error_msg}")
            return {"success": False, "data": response_data, "status_code": response.status_code}
            
    except Exception as e:
        test_results["failed"] += 1
        error_msg = f"{name}: {str(e)}"
        test_results["errors"].append(error_msg)
        print(f"❌ 测试异常: {error_msg}")
        return {"success": False, "error": str(e)}

async def run_tutor_tests():
    """
    执行所有Tutor API测试
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("\n" + "="*60)
        print("🚀 开始测试 Tutor API")
        print("="*60)
        
        # ============= 导师列表相关测试 =============
        print("\n\n📋 第一部分：导师列表 API")
        
        # 1. 获取导师列表（默认）
        await test_api(
            client,
            "获取导师列表（默认）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/",
            params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
        )
        
        # 2. 获取导师列表（按类型筛选）
        await test_api(
            client,
            "获取导师列表（按类型筛选）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/",
            params={"user_id": TEST_USER_ID, "tutor_type": "0", "page": 1, "page_size": 10}
        )
        
        # 3. 获取导师列表（按领域筛选）
        await test_api(
            client,
            "获取导师列表（按领域筛选）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/",
            params={"user_id": TEST_USER_ID, "domain": "考研", "page": 1, "page_size": 10}
        )
        
        # 4. 获取导师列表（按评分排序）
        await test_api(
            client,
            "获取导师列表（按评分排序）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/",
            params={"user_id": TEST_USER_ID, "sort_by": "rating", "page": 1, "page_size": 10}
        )
        
        # 5. 获取导师列表（按价格排序）
        await test_api(
            client,
            "获取导师列表（按价格排序）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/",
            params={"user_id": TEST_USER_ID, "sort_by": "price", "page": 1, "page_size": 10}
        )
        
        # 6. 搜索导师
        await test_api(
            client,
            "搜索导师",
            "GET",
            f"{BASE_URL}{API_PREFIX}/search",
            params={"user_id": TEST_USER_ID, "keyword": "考研", "page": 1, "page_size": 10}
        )
        
        # 7. 获取导师领域列表
        await test_api(
            client,
            "获取导师领域列表",
            "GET",
            f"{BASE_URL}{API_PREFIX}/domains",
            params={"user_id": TEST_USER_ID}
        )
        
        # 8. 获取导师类型列表
        await test_api(
            client,
            "获取导师类型列表",
            "GET",
            f"{BASE_URL}{API_PREFIX}/types",
            params={"user_id": TEST_USER_ID}
        )
        
        # 9. 获取导师统计摘要
        await test_api(
            client,
            "获取导师统计摘要",
            "GET",
            f"{BASE_URL}{API_PREFIX}/stats/summary",
            params={"user_id": TEST_USER_ID}
        )
        
        # 10. 获取热门推荐导师
        await test_api(
            client,
            "获取热门推荐导师",
            "GET",
            f"{BASE_URL}{API_PREFIX}/popular",
            params={"user_id": TEST_USER_ID, "limit": 5}
        )
        
        # ============= 导师详情相关测试 =============
        print("\n\n📖 第二部分：导师详情 API")
        
        # 测试用导师ID（如果数据库为空，使用一个不存在的ID测试404）
        test_tutor_id = 1
        
        # 11. 获取导师详情
        result = await test_api(
            client,
            "获取导师详情",
            "GET",
            f"{BASE_URL}{API_PREFIX}/{test_tutor_id}",
            params={"user_id": TEST_USER_ID}
        )
        
        # 12. 获取导师服务列表
        await test_api(
            client,
            "获取导师服务列表",
            "GET",
            f"{BASE_URL}{API_PREFIX}/{test_tutor_id}/services",
            params={"user_id": TEST_USER_ID}
        )
        
        # 13. 获取导师评价列表
        await test_api(
            client,
            "获取导师评价列表",
            "GET",
            f"{BASE_URL}{API_PREFIX}/{test_tutor_id}/reviews",
            params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
        )
        
        # 14. 获取导师指导数据
        await test_api(
            client,
            "获取导师指导数据",
            "GET",
            f"{BASE_URL}{API_PREFIX}/{test_tutor_id}/metrics",
            params={"user_id": TEST_USER_ID}
        )
        
        # 15. 记录导师页面浏览
        await test_api(
            client,
            "记录导师页面浏览",
            "POST",
            f"{BASE_URL}{API_PREFIX}/{test_tutor_id}/view",
            params={"user_id": TEST_USER_ID}
        )
        
        # 16. 获取相似推荐导师
        await test_api(
            client,
            "获取相似推荐导师",
            "GET",
            f"{BASE_URL}{API_PREFIX}/{test_tutor_id}/similar",
            params={"user_id": TEST_USER_ID, "limit": 5}
        )

async def main():
    """
    主函数
    """
    print("\n" + "="*60)
    print("🧪 Tutor API 完整测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务: {BASE_URL}")
    print(f"测试用户: {TEST_USER_ID}")
    
    await run_tutor_tests()
    
    # 输出测试结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    print(f"总测试数: {test_results['total']}")
    print(f"✅ 通过: {test_results['passed']}")
    print(f"❌ 失败: {test_results['failed']}")
    print(f"通过率: {(test_results['passed']/test_results['total']*100) if test_results['total'] > 0 else 0:.1f}%")
    
    if test_results['errors']:
        print("\n❌ 失败的测试:")
        for i, error in enumerate(test_results['errors'], 1):
            print(f"  {i}. {error}")
    
    print("\n" + "="*60)
    print("✅ 测试完成")
    print("="*60)
    
    # 保存测试结果到文件
    report_file = "tests/report/TUTOR_API_TEST_RESULT.json"
    try:
        import os
        os.makedirs("tests/report", exist_ok=True)
        
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "base_url": BASE_URL,
                "test_user_id": TEST_USER_ID,
                "results": test_results,
                "test_data_ids": test_data_ids
            }, f, ensure_ascii=False, indent=2)
        
        print(f"\n📄 测试结果已保存到: {report_file}")
    except Exception as e:
        print(f"\n⚠️  保存测试结果失败: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 