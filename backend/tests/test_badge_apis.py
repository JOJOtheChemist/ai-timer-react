#!/usr/bin/env python3
"""
Badge API 综合测试
测试所有徽章相关的API端点及数据库交互
"""

import asyncio
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, Any, List
import json


class BadgeAPITester:
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
        self.test_badge_id = None
        
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
    
    async def test_get_user_badges(self) -> bool:
        """测试获取用户徽章列表"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/badges/my",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_badges = self.check_database_record(
                        "SELECT COUNT(*) as count FROM badge WHERE is_active = 1"
                    )
                    
                    db_user_badges = self.check_database_record(
                        "SELECT COUNT(*) as count FROM user_badge WHERE user_id = %s",
                        (self.test_user_id,)
                    )
                    
                    total_badges = db_badges[0]['count'] if db_badges else 0
                    user_badges = db_user_badges[0]['count'] if db_user_badges else 0
                    
                    self.log_test_result(
                        "获取用户徽章列表",
                        True,
                        f"总徽章数:{total_badges}, 用户已获得:{user_badges}"
                    )
                    return True
                else:
                    self.log_test_result("获取用户徽章列表", False, f"HTTP {response.status_code}: {response.text[:200]}")
                    return False
        except Exception as e:
            self.log_test_result("获取用户徽章列表", False, str(e))
            return False
    
    async def test_get_all_badges(self) -> bool:
        """测试获取所有徽章"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/badges",
                    params={"user_id": self.test_user_id, "limit": 20},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    badges = data if isinstance(data, list) else []
                    
                    # 验证数据库
                    db_badges = self.check_database_record(
                        "SELECT * FROM badge WHERE is_active = 1 ORDER BY sort_order LIMIT 20"
                    )
                    
                    # 保存第一个徽章ID用于后续测试
                    if len(badges) > 0:
                        self.test_badge_id = badges[0].get('id') or badges[0].get('badge_id')
                    
                    self.log_test_result(
                        "获取所有徽章",
                        True,
                        f"返回{len(badges)}个徽章，数据库有{len(db_badges)}个"
                    )
                    return True
                else:
                    self.log_test_result("获取所有徽章", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取所有徽章", False, str(e))
            return False
    
    async def test_get_badges_by_category(self) -> bool:
        """测试按分类获取徽章"""
        try:
            categories = ['general', 'study', 'social']
            success_count = 0
            
            for category in categories:
                async with httpx.AsyncClient() as client:
                    response = await client.get(
                        f"{self.base_url}/api/v1/badges",
                        params={"user_id": self.test_user_id, "category": category},
                        timeout=10.0
                    )
                    
                    if response.status_code == 200:
                        # 验证数据库
                        db_count = self.check_database_record(
                            "SELECT COUNT(*) as count FROM badge WHERE category = %s AND is_active = 1",
                            (category,)
                        )
                        success_count += 1
            
            self.log_test_result(
                "按分类获取徽章",
                success_count == len(categories),
                f"测试了{len(categories)}个分类，成功{success_count}个"
            )
            return success_count == len(categories)
        except Exception as e:
            self.log_test_result("按分类获取徽章", False, str(e))
            return False
    
    async def test_get_badge_detail(self) -> bool:
        """测试获取徽章详情"""
        if not self.test_badge_id:
            # 从数据库获取一个徽章ID
            badges = self.check_database_record(
                "SELECT id FROM badge WHERE is_active = 1 LIMIT 1"
            )
            if badges:
                self.test_badge_id = badges[0]['id']
            else:
                self.log_test_result("获取徽章详情", False, "没有可用的测试徽章ID")
                return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/badges/{self.test_badge_id}",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_badge = self.check_database_record(
                        "SELECT * FROM badge WHERE id = %s",
                        (self.test_badge_id,)
                    )
                    
                    badge_name = db_badge[0]['name'] if db_badge else 'N/A'
                    self.log_test_result(
                        "获取徽章详情",
                        True,
                        f"徽章ID {self.test_badge_id}，名称: {badge_name}"
                    )
                    return True
                else:
                    self.log_test_result("获取徽章详情", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取徽章详情", False, str(e))
            return False
    
    async def test_update_badge_display(self) -> bool:
        """测试更新徽章展示设置"""
        # 先获取用户拥有的徽章
        user_badges = self.check_database_record(
            "SELECT badge_id FROM user_badge WHERE user_id = %s LIMIT 1",
            (self.test_user_id,)
        )
        
        if not user_badges:
            self.log_test_result("更新徽章展示", False, "用户没有徽章可以设置展示")
            return False
        
        badge_id = user_badges[0]['badge_id']
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/api/v1/badges/display",
                    json=[
                        {"badge_id": badge_id, "is_displayed": 1}
                    ],
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    await asyncio.sleep(0.3)
                    
                    # 验证数据库
                    db_check = self.check_database_record(
                        "SELECT is_displayed FROM user_badge WHERE user_id = %s AND badge_id = %s",
                        (self.test_user_id, badge_id)
                    )
                    
                    is_displayed = db_check[0]['is_displayed'] if db_check else 0
                    self.log_test_result(
                        "更新徽章展示",
                        is_displayed == 1,
                        f"徽章展示状态: {is_displayed}"
                    )
                    return is_displayed == 1
                else:
                    self.log_test_result("更新徽章展示", False, f"HTTP {response.status_code}: {response.text[:200]}")
                    return False
        except Exception as e:
            self.log_test_result("更新徽章展示", False, str(e))
            return False
    
    async def test_get_displayed_badges(self) -> bool:
        """测试获取展示的徽章"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/badges/display/current",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_displayed = self.check_database_record(
                        """
                        SELECT COUNT(*) as count 
                        FROM user_badge 
                        WHERE user_id = %s AND is_displayed = 1
                        """,
                        (self.test_user_id,)
                    )
                    
                    displayed_count = db_displayed[0]['count'] if db_displayed else 0
                    self.log_test_result(
                        "获取展示的徽章",
                        True,
                        f"展示徽章数: {displayed_count}"
                    )
                    return True
                else:
                    self.log_test_result("获取展示的徽章", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取展示的徽章", False, str(e))
            return False
    
    async def test_badge_rarity_system(self) -> bool:
        """测试徽章稀有度系统"""
        try:
            # 验证数据库中的稀有度分布
            rarity_stats = self.check_database_record(
                """
                SELECT 
                    rarity,
                    COUNT(*) as count
                FROM badge
                WHERE is_active = 1
                GROUP BY rarity
                ORDER BY rarity
                """
            )
            
            rarity_distribution = {r['rarity']: r['count'] for r in rarity_stats}
            
            self.log_test_result(
                "徽章稀有度系统",
                len(rarity_stats) > 0,
                f"稀有度分布: {rarity_distribution}"
            )
            return len(rarity_stats) > 0
        except Exception as e:
            self.log_test_result("徽章稀有度系统", False, str(e))
            return False
    
    async def test_badge_categories(self) -> bool:
        """测试徽章分类系统"""
        try:
            # 验证数据库中的分类分布
            category_stats = self.check_database_record(
                """
                SELECT 
                    category,
                    COUNT(*) as count
                FROM badge
                WHERE is_active = 1
                GROUP BY category
                ORDER BY category
                """
            )
            
            category_distribution = {c['category']: c['count'] for c in category_stats}
            
            self.log_test_result(
                "徽章分类系统",
                len(category_stats) > 0,
                f"分类分布: {category_distribution}"
            )
            return len(category_stats) > 0
        except Exception as e:
            self.log_test_result("徽章分类系统", False, str(e))
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("🧪 Badge API 综合测试")
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
            ("获取用户徽章列表", self.test_get_user_badges),
            ("获取所有徽章", self.test_get_all_badges),
            ("按分类获取徽章", self.test_get_badges_by_category),
            ("获取徽章详情", self.test_get_badge_detail),
            ("更新徽章展示", self.test_update_badge_display),
            ("获取展示的徽章", self.test_get_displayed_badges),
            ("徽章稀有度系统", self.test_badge_rarity_system),
            ("徽章分类系统", self.test_badge_categories),
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
        report_file = f"tests/report/badge_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    tester = BadgeAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 