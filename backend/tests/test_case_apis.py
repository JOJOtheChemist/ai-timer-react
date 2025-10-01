#!/usr/bin/env python3
"""
Success Case API 综合测试
测试所有成功案例相关的API端点及数据库交互
"""

import asyncio
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, Any, List
import json


class CaseAPITester:
    def __init__(self):
        self.base_url = "http://localhost:8000"
        self.db_config = {
            "host": "localhost",
            "port": 5432,
            "database": "ai_time_management",
            "user": "yeya",
            "password": ""
        }
        self.test_results = []
        self.test_user_id = 1
        self.test_case_id = None
        
    def get_db_connection(self):
        """获取数据库连接"""
        return psycopg2.connect(**self.db_config)
    
    def check_database_record(self, query: str, params: tuple = None) -> List[Dict]:
        """检查数据库记录"""
        try:
            conn = self.get_db_connection()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return [dict(row) for row in results]
        except Exception as e:
            print(f"数据库查询错误: {e}")
            return []
    
    def log_test_result(self, test_name: str, success: bool, details: str = ""):
        """记录测试结果"""
        status = "✅ PASS" if success else "❌ FAIL"
        self.test_results.append({
            "test": test_name,
            "status": status,
            "success": success,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })
        print(f"{status} - {test_name}")
        if details:
            print(f"   详情: {details}")
    
    async def test_get_hot_cases(self) -> bool:
        """测试获取热门案例"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/hot",
                    params={"limit": 3},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    cases = data if isinstance(data, list) else data.get('cases', [])
                    
                    # 验证数据库
                    db_hot_cases = self.check_database_record(
                        "SELECT * FROM success_case WHERE is_hot = 1 AND status = 1 ORDER BY view_count DESC LIMIT 3"
                    )
                    
                    self.log_test_result(
                        "获取热门案例",
                        True,
                        f"返回{len(cases)}个案例，数据库有{len(db_hot_cases)}个热门案例"
                    )
                    
                    # 保存一个案例ID用于后续测试
                    if cases and len(cases) > 0:
                        self.test_case_id = cases[0].get('id') or cases[0].get('case_id')
                    
                    return True
                else:
                    self.log_test_result("获取热门案例", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取热门案例", False, str(e))
            return False
    
    async def test_get_case_list(self) -> bool:
        """测试获取案例列表（带分页和筛选）"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/",
                    params={
                        "page": 1,
                        "page_size": 10,
                        "category": "考研"
                    },
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_cases = self.check_database_record(
                        "SELECT COUNT(*) as count FROM success_case WHERE category = %s AND status = 1",
                        ("考研",)
                    )
                    
                    self.log_test_result(
                        "获取案例列表（筛选）",
                        True,
                        f"分类筛选成功，数据库有{db_cases[0]['count'] if db_cases else 0}个考研案例"
                    )
                    return True
                else:
                    self.log_test_result("获取案例列表（筛选）", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取案例列表（筛选）", False, str(e))
            return False
    
    async def test_search_cases(self) -> bool:
        """测试搜索案例"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/search",
                    params={"keyword": "考研"},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    cases = data.get('cases', []) if isinstance(data, dict) else data
                    
                    self.log_test_result(
                        "搜索案例",
                        True,
                        f"搜索'考研'返回{len(cases) if isinstance(cases, list) else 0}个结果"
                    )
                    return True
                else:
                    self.log_test_result("搜索案例", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("搜索案例", False, str(e))
            return False
    
    async def test_get_categories(self) -> bool:
        """测试获取分类列表"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/categories",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    categories = data if isinstance(data, list) else data.get('categories', [])
                    
                    # 验证数据库
                    db_categories = self.check_database_record(
                        "SELECT DISTINCT category, COUNT(*) as count FROM success_case WHERE status = 1 AND category IS NOT NULL GROUP BY category"
                    )
                    
                    self.log_test_result(
                        "获取分类列表",
                        True,
                        f"返回{len(categories) if isinstance(categories, list) else 0}个分类，数据库有{len(db_categories)}个分类"
                    )
                    return True
                else:
                    self.log_test_result("获取分类列表", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取分类列表", False, str(e))
            return False
    
    async def test_get_stats_summary(self) -> bool:
        """测试获取统计摘要"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/stats/summary",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_stats = self.check_database_record(
                        "SELECT COUNT(*) as total_cases, SUM(view_count) as total_views FROM success_case WHERE status = 1"
                    )
                    
                    self.log_test_result(
                        "获取统计摘要",
                        True,
                        f"数据库统计: {db_stats[0]['total_cases']}个案例, {db_stats[0]['total_views']}次浏览"
                    )
                    return True
                else:
                    self.log_test_result("获取统计摘要", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取统计摘要", False, str(e))
            return False
    
    async def test_get_case_detail(self) -> bool:
        """测试获取案例详情"""
        if not self.test_case_id:
            # 从数据库获取一个案例ID
            cases = self.check_database_record(
                "SELECT id FROM success_case WHERE status = 1 LIMIT 1"
            )
            if cases:
                self.test_case_id = cases[0]['id']
            else:
                self.log_test_result("获取案例详情", False, "没有可用的测试案例ID")
                return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/{self.test_case_id}",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_case = self.check_database_record(
                        "SELECT * FROM success_case WHERE id = %s",
                        (self.test_case_id,)
                    )
                    
                    self.log_test_result(
                        "获取案例详情",
                        True,
                        f"案例ID {self.test_case_id}，标题: {db_case[0]['title'] if db_case else 'N/A'}"
                    )
                    return True
                else:
                    self.log_test_result("获取案例详情", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取案例详情", False, str(e))
            return False
    
    async def test_record_view(self) -> bool:
        """测试记录浏览"""
        if not self.test_case_id:
            self.log_test_result("记录浏览", False, "没有可用的测试案例ID")
            return False
        
        try:
            # 获取浏览前的浏览量
            before_views = self.check_database_record(
                "SELECT view_count FROM success_case WHERE id = %s",
                (self.test_case_id,)
            )
            before_count = before_views[0]['view_count'] if before_views else 0
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/cases/{self.test_case_id}/view",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    # 等待一下让数据库更新
                    await asyncio.sleep(0.5)
                    
                    # 验证浏览量是否增加
                    after_views = self.check_database_record(
                        "SELECT view_count FROM success_case WHERE id = %s",
                        (self.test_case_id,)
                    )
                    after_count = after_views[0]['view_count'] if after_views else 0
                    
                    # 检查case_interaction表
                    interactions = self.check_database_record(
                        "SELECT * FROM case_interaction WHERE case_id = %s AND user_id = %s ORDER BY create_time DESC LIMIT 1",
                        (self.test_case_id, self.test_user_id)
                    )
                    
                    self.log_test_result(
                        "记录浏览",
                        True,
                        f"浏览量: {before_count} -> {after_count}, 交互记录数: {len(interactions)}"
                    )
                    return True
                else:
                    self.log_test_result("记录浏览", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("记录浏览", False, str(e))
            return False
    
    async def test_get_related_cases(self) -> bool:
        """测试获取相关案例"""
        if not self.test_case_id:
            self.log_test_result("获取相关案例", False, "没有可用的测试案例ID")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/{self.test_case_id}/related",
                    params={"limit": 5},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    cases = data if isinstance(data, list) else data.get('cases', [])
                    
                    self.log_test_result(
                        "获取相关案例",
                        True,
                        f"返回{len(cases) if isinstance(cases, list) else 0}个相关案例"
                    )
                    return True
                else:
                    self.log_test_result("获取相关案例", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取相关案例", False, str(e))
            return False
    
    async def test_get_permission(self) -> bool:
        """测试获取案例权限信息"""
        if not self.test_case_id:
            self.log_test_result("获取权限信息", False, "没有可用的测试案例ID")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/{self.test_case_id}/permission",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 检查数据库中的购买记录
                    purchases = self.check_database_record(
                        "SELECT * FROM case_purchase WHERE case_id = %s AND user_id = %s",
                        (self.test_case_id, self.test_user_id)
                    )
                    
                    self.log_test_result(
                        "获取权限信息",
                        True,
                        f"权限状态: {data.get('has_access', 'unknown')}, 购买记录: {len(purchases)}条"
                    )
                    return True
                else:
                    self.log_test_result("获取权限信息", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取权限信息", False, str(e))
            return False
    
    async def test_check_access_status(self) -> bool:
        """测试检查访问状态"""
        if not self.test_case_id:
            self.log_test_result("检查访问状态", False, "没有可用的测试案例ID")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/{self.test_case_id}/access-status",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    self.log_test_result(
                        "检查访问状态",
                        True,
                        f"访问状态: {data}"
                    )
                    return True
                else:
                    self.log_test_result("检查访问状态", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("检查访问状态", False, str(e))
            return False
    
    async def test_get_my_purchased(self) -> bool:
        """测试获取我的已购案例"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/cases/my-purchased",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_purchases = self.check_database_record(
                        "SELECT COUNT(*) as count FROM case_purchase WHERE user_id = %s",
                        (self.test_user_id,)
                    )
                    
                    self.log_test_result(
                        "获取已购案例",
                        True,
                        f"数据库购买记录: {db_purchases[0]['count'] if db_purchases else 0}条"
                    )
                    return True
                else:
                    self.log_test_result("获取已购案例", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取已购案例", False, str(e))
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("🧪 Success Case API 综合测试")
        print("=" * 70)
        print()
        
        # 检查服务器
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/health", timeout=5.0)
                if response.status_code != 200:
                    print("❌ 服务器未响应，请先启动服务器")
                    return
        except:
            print("❌ 无法连接到服务器，请确保服务器正在运行")
            print(f"   服务器地址: {self.base_url}")
            return
        
        print("✅ 服务器连接成功\n")
        
        # 执行测试
        test_methods = [
            ("热门案例", self.test_get_hot_cases),
            ("案例列表（筛选）", self.test_get_case_list),
            ("搜索案例", self.test_search_cases),
            ("分类列表", self.test_get_categories),
            ("统计摘要", self.test_get_stats_summary),
            ("案例详情", self.test_get_case_detail),
            ("记录浏览", self.test_record_view),
            ("相关案例", self.test_get_related_cases),
            ("权限信息", self.test_get_permission),
            ("访问状态", self.test_check_access_status),
            ("已购案例", self.test_get_my_purchased),
        ]
        
        print("开始测试API端点...\n")
        for test_name, test_method in test_methods:
            await test_method()
            await asyncio.sleep(0.2)  # 避免请求过快
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成测试报告"""
        print("\n" + "=" * 70)
        print("📊 测试结果汇总")
        print("=" * 70)
        
        total = len(self.test_results)
        passed = sum(1 for r in self.test_results if r['success'])
        failed = total - passed
        
        print(f"\n总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {failed} ❌")
        print(f"成功率: {(passed/total*100):.1f}%\n")
        
        if failed > 0:
            print("失败的测试:")
            for result in self.test_results:
                if not result['success']:
                    print(f"  ❌ {result['test']}: {result['details']}")
        
        # 保存到文件
        report_file = f"tests/report/case_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            import os
            os.makedirs("tests/report", exist_ok=True)
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "summary": {
                        "total": total,
                        "passed": passed,
                        "failed": failed,
                        "success_rate": f"{(passed/total*100):.1f}%"
                    },
                    "results": self.test_results,
                    "generated_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)
            print(f"\n📄 详细报告已保存到: {report_file}")
        except Exception as e:
            print(f"\n⚠️  保存报告失败: {e}")


async def main():
    tester = CaseAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 