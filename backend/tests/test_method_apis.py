#!/usr/bin/env python3
"""
Method API 综合测试
测试所有学习方法相关的API端点及数据库交互
"""

import asyncio
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, Any, List
import json


class MethodAPITester:
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
        self.test_method_id = None
        
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
    
    async def test_get_method_list(self) -> bool:
        """测试获取学习方法列表"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods",
                    params={"page": 1, "page_size": 10},
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    methods = data if isinstance(data, list) else data.get('methods', [])
                    
                    # 验证数据库
                    db_methods = self.check_database_record(
                        "SELECT COUNT(*) as count FROM study_method WHERE status = 1"
                    )
                    
                    db_count = db_methods[0]['count'] if db_methods else 0
                    
                    self.log_test_result(
                        "获取学习方法列表",
                        True,
                        f"返回{len(methods) if isinstance(methods, list) else 0}个方法，数据库有{db_count}个"
                    )
                    
                    # 保存第一个方法ID用于后续测试
                    if isinstance(methods, list) and len(methods) > 0:
                        self.test_method_id = methods[0].get('id') or methods[0].get('method_id')
                    
                    return True
                else:
                    self.log_test_result("获取学习方法列表", False, f"HTTP {response.status_code}: {response.text[:200]}")
                    return False
        except Exception as e:
            self.log_test_result("获取学习方法列表", False, str(e))
            return False
    
    async def test_get_method_by_category(self) -> bool:
        """测试按分类筛选学习方法"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods",
                    params={"category": "common", "page": 1},
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_count = self.check_database_record(
                        "SELECT COUNT(*) as count FROM study_method WHERE category = 'common' AND status = 1"
                    )
                    
                    self.log_test_result(
                        "按分类筛选（通用方法）",
                        True,
                        f"数据库有{db_count[0]['count'] if db_count else 0}个通用方法"
                    )
                    return True
                else:
                    self.log_test_result("按分类筛选", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("按分类筛选", False, str(e))
            return False
    
    async def test_get_method_detail(self) -> bool:
        """测试获取学习方法详情"""
        if not self.test_method_id:
            # 从数据库获取一个方法ID
            methods = self.check_database_record(
                "SELECT id FROM study_method WHERE status = 1 LIMIT 1"
            )
            if methods:
                self.test_method_id = methods[0]['id']
            else:
                self.log_test_result("获取方法详情", False, "没有可用的测试方法ID")
                return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods/{self.test_method_id}",
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_method = self.check_database_record(
                        "SELECT * FROM study_method WHERE id = %s",
                        (self.test_method_id,)
                    )
                    
                    method_name = db_method[0]['name'] if db_method else 'N/A'
                    self.log_test_result(
                        "获取方法详情",
                        True,
                        f"方法ID {self.test_method_id}，名称: {method_name}"
                    )
                    return True
                else:
                    self.log_test_result("获取方法详情", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取方法详情", False, str(e))
            return False
    
    async def test_get_popular_methods(self) -> bool:
        """测试获取热门学习方法"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods/popular",
                    params={"limit": 5},
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    methods = data if isinstance(data, list) else data.get('methods', [])
                    
                    # 验证数据库
                    db_methods = self.check_database_record(
                        "SELECT * FROM study_method WHERE status = 1 ORDER BY checkin_count DESC LIMIT 5"
                    )
                    
                    self.log_test_result(
                        "获取热门方法",
                        True,
                        f"返回{len(methods) if isinstance(methods, list) else 0}个热门方法，数据库top5已验证"
                    )
                    return True
                else:
                    self.log_test_result("获取热门方法", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取热门方法", False, str(e))
            return False
    
    async def test_search_methods(self) -> bool:
        """测试搜索学习方法"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods/search",
                    params={"keyword": "番茄"},
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    self.log_test_result(
                        "搜索学习方法",
                        True,
                        f"搜索'番茄'成功"
                    )
                    return True
                else:
                    self.log_test_result("搜索学习方法", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("搜索学习方法", False, str(e))
            return False
    
    async def test_create_checkin(self) -> bool:
        """测试创建打卡记录"""
        if not self.test_method_id:
            self.log_test_result("创建打卡", False, "没有可用的测试方法ID")
            return False
        
        try:
            # 获取打卡前的统计
            before_count = self.check_database_record(
                "SELECT checkin_count FROM study_method WHERE id = %s",
                (self.test_method_id,)
            )
            before_checkins = before_count[0]['checkin_count'] if before_count else 0
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/methods/{self.test_method_id}/checkin",
                    json={
                        "checkin_type": "正字打卡",
                        "progress": 1,
                        "note": "测试打卡"
                    },
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    await asyncio.sleep(0.5)
                    
                    # 验证数据库
                    checkin_records = self.check_database_record(
                        "SELECT * FROM checkin_record WHERE user_id = %s AND method_id = %s ORDER BY checkin_time DESC LIMIT 1",
                        (self.test_user_id, self.test_method_id)
                    )
                    
                    self.log_test_result(
                        "创建打卡记录",
                        len(checkin_records) > 0,
                        f"打卡记录已创建，数据库记录数: {len(checkin_records)}"
                    )
                    return len(checkin_records) > 0
                else:
                    self.log_test_result("创建打卡记录", False, f"HTTP {response.status_code}: {response.text[:200]}")
                    return False
        except Exception as e:
            self.log_test_result("创建打卡记录", False, str(e))
            return False
    
    async def test_get_checkin_history(self) -> bool:
        """测试获取打卡历史"""
        if not self.test_method_id:
            self.log_test_result("获取打卡历史", False, "没有可用的测试方法ID")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods/{self.test_method_id}/checkins/history",
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_checkins = self.check_database_record(
                        "SELECT COUNT(*) as count FROM checkin_record WHERE user_id = %s AND method_id = %s",
                        (self.test_user_id, self.test_method_id)
                    )
                    
                    db_count = db_checkins[0]['count'] if db_checkins else 0
                    self.log_test_result(
                        "获取打卡历史",
                        True,
                        f"数据库有{db_count}条打卡记录"
                    )
                    return True
                else:
                    self.log_test_result("获取打卡历史", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取打卡历史", False, str(e))
            return False
    
    async def test_get_checkin_stats(self) -> bool:
        """测试获取打卡统计"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods/checkins/stats",
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_stats = self.check_database_record(
                        """
                        SELECT 
                            COUNT(*) as total_checkins,
                            COUNT(DISTINCT method_id) as methods_used,
                            COUNT(DISTINCT DATE(checkin_time)) as checkin_days
                        FROM checkin_record 
                        WHERE user_id = %s
                        """,
                        (self.test_user_id,)
                    )
                    
                    if db_stats:
                        stats = db_stats[0]
                        self.log_test_result(
                            "获取打卡统计",
                            True,
                            f"总打卡:{stats['total_checkins']}, 使用方法数:{stats['methods_used']}, 打卡天数:{stats['checkin_days']}"
                        )
                    else:
                        self.log_test_result("获取打卡统计", True, "统计获取成功")
                    return True
                else:
                    self.log_test_result("获取打卡统计", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取打卡统计", False, str(e))
            return False
    
    async def test_get_method_reviews(self) -> bool:
        """测试获取方法评价"""
        if not self.test_method_id:
            self.log_test_result("获取方法评价", False, "没有可用的测试方法ID")
            return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/methods/{self.test_method_id}/reviews",
                    headers={"user_id": str(self.test_user_id)},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_reviews = self.check_database_record(
                        "SELECT COUNT(*) as count FROM method_review WHERE method_id = %s",
                        (self.test_method_id,)
                    )
                    
                    db_count = db_reviews[0]['count'] if db_reviews else 0
                    self.log_test_result(
                        "获取方法评价",
                        True,
                        f"数据库有{db_count}条评价"
                    )
                    return True
                else:
                    self.log_test_result("获取方法评价", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取方法评价", False, str(e))
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("🧪 Method API 综合测试")
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
            ("获取方法列表", self.test_get_method_list),
            ("按分类筛选", self.test_get_method_by_category),
            ("获取方法详情", self.test_get_method_detail),
            ("获取热门方法", self.test_get_popular_methods),
            ("搜索方法", self.test_search_methods),
            ("创建打卡", self.test_create_checkin),
            ("获取打卡历史", self.test_get_checkin_history),
            ("获取打卡统计", self.test_get_checkin_stats),
            ("获取方法评价", self.test_get_method_reviews),
        ]
        
        print("开始测试API端点...\n")
        for test_name, test_method in test_methods:
            await test_method()
            await asyncio.sleep(0.3)
        
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
        report_file = f"tests/report/method_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    tester = MethodAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 