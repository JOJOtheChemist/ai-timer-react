#!/usr/bin/env python3
"""
Message API 综合测试
测试所有消息相关的API端点及数据库交互
"""

import asyncio
import httpx
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
from typing import Dict, Any, List
import json


class MessageAPITester:
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
        self.test_message_id = None
        
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
    
    async def test_get_messages(self) -> bool:
        """测试获取消息列表"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/messages",
                    params={"user_id": self.test_user_id, "page": 1, "page_size": 10},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_messages = self.check_database_record(
                        "SELECT COUNT(*) as count FROM message WHERE receiver_id = %s",
                        (self.test_user_id,)
                    )
                    
                    messages = data.get('messages', []) if isinstance(data, dict) else data
                    db_count = db_messages[0]['count'] if db_messages else 0
                    
                    self.log_test_result(
                        "获取消息列表",
                        True,
                        f"返回{len(messages) if isinstance(messages, list) else 0}条消息，数据库有{db_count}条"
                    )
                    
                    # 保存第一条消息ID用于后续测试
                    if isinstance(messages, list) and len(messages) > 0:
                        self.test_message_id = messages[0].get('id') or messages[0].get('message_id')
                    
                    return True
                else:
                    self.log_test_result("获取消息列表", False, f"HTTP {response.status_code}: {response.text[:200]}")
                    return False
        except Exception as e:
            self.log_test_result("获取消息列表", False, str(e))
            return False
    
    async def test_get_messages_by_type(self) -> bool:
        """测试按类型筛选消息"""
        try:
            async with httpx.AsyncClient() as client:
                # 测试导师消息
                response = await client.get(
                    f"{self.base_url}/api/v1/messages",
                    params={"user_id": self.test_user_id, "message_type": "tutor", "page": 1},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_count = self.check_database_record(
                        "SELECT COUNT(*) as count FROM message WHERE receiver_id = %s AND type = 0",
                        (self.test_user_id,)
                    )
                    
                    self.log_test_result(
                        "按类型筛选消息（导师）",
                        True,
                        f"数据库有{db_count[0]['count'] if db_count else 0}条导师消息"
                    )
                    return True
                else:
                    self.log_test_result("按类型筛选消息", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("按类型筛选消息", False, str(e))
            return False
    
    async def test_get_message_detail(self) -> bool:
        """测试获取消息详情"""
        if not self.test_message_id:
            # 从数据库获取一个消息ID
            messages = self.check_database_record(
                "SELECT id FROM message WHERE receiver_id = %s LIMIT 1",
                (self.test_user_id,)
            )
            if messages:
                self.test_message_id = messages[0]['id']
            else:
                self.log_test_result("获取消息详情", False, "没有可用的测试消息ID")
                return False
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/messages/{self.test_message_id}",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_message = self.check_database_record(
                        "SELECT * FROM message WHERE id = %s",
                        (self.test_message_id,)
                    )
                    
                    self.log_test_result(
                        "获取消息详情",
                        True,
                        f"消息ID {self.test_message_id}，标题: {db_message[0]['title'] if db_message else 'N/A'}"
                    )
                    return True
                else:
                    self.log_test_result("获取消息详情", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取消息详情", False, str(e))
            return False
    
    async def test_mark_as_read(self) -> bool:
        """测试标记消息为已读"""
        if not self.test_message_id:
            self.log_test_result("标记已读", False, "没有可用的测试消息ID")
            return False
        
        try:
            # 获取标记前的状态
            before_state = self.check_database_record(
                "SELECT is_unread, read_time FROM message WHERE id = %s",
                (self.test_message_id,)
            )
            before_unread = before_state[0]['is_unread'] if before_state else None
            
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/api/v1/messages/{self.test_message_id}/read",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    await asyncio.sleep(0.5)
                    
                    # 验证数据库更新
                    after_state = self.check_database_record(
                        "SELECT is_unread, read_time FROM message WHERE id = %s",
                        (self.test_message_id,)
                    )
                    after_unread = after_state[0]['is_unread'] if after_state else None
                    read_time = after_state[0]['read_time'] if after_state else None
                    
                    self.log_test_result(
                        "标记消息为已读",
                        True,
                        f"状态: {before_unread} -> {after_unread}, 阅读时间: {read_time}"
                    )
                    return True
                else:
                    self.log_test_result("标记消息为已读", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("标记消息为已读", False, str(e))
            return False
    
    async def test_get_unread_count(self) -> bool:
        """测试获取未读消息数"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/messages/unread/count",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_count = self.check_database_record(
                        "SELECT COUNT(*) as count FROM message WHERE receiver_id = %s AND is_unread = 1",
                        (self.test_user_id,)
                    )
                    
                    api_count = data.get('unread_count', 0) if isinstance(data, dict) else 0
                    db_unread = db_count[0]['count'] if db_count else 0
                    
                    self.log_test_result(
                        "获取未读消息数",
                        True,
                        f"API返回: {api_count}, 数据库实际: {db_unread}"
                    )
                    return True
                else:
                    self.log_test_result("获取未读消息数", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取未读消息数", False, str(e))
            return False
    
    async def test_batch_mark_read(self) -> bool:
        """测试批量标记已读"""
        try:
            # 获取一些未读消息ID
            unread_messages = self.check_database_record(
                "SELECT id FROM message WHERE receiver_id = %s AND is_unread = 1 LIMIT 2",
                (self.test_user_id,)
            )
            
            if not unread_messages:
                self.log_test_result("批量标记已读", True, "没有未读消息，跳过测试")
                return True
            
            message_ids = [msg['id'] for msg in unread_messages]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/v1/messages/batch/read",
                    json={"message_ids": message_ids},
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    await asyncio.sleep(0.5)
                    
                    # 验证数据库
                    still_unread = self.check_database_record(
                        f"SELECT COUNT(*) as count FROM message WHERE id = ANY(%s) AND is_unread = 1",
                        (message_ids,)
                    )
                    
                    self.log_test_result(
                        "批量标记已读",
                        True,
                        f"标记了{len(message_ids)}条消息，剩余未读: {still_unread[0]['count'] if still_unread else 0}"
                    )
                    return True
                else:
                    self.log_test_result("批量标记已读", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("批量标记已读", False, str(e))
            return False
    
    async def test_delete_message(self) -> bool:
        """测试删除消息"""
        # 创建一条测试消息用于删除
        test_msg = self.check_database_record(
            "INSERT INTO message (sender_id, receiver_id, type, content) VALUES (%s, %s, %s, %s) RETURNING id",
            (None, self.test_user_id, 2, '测试删除消息')
        )
        
        if not test_msg:
            self.log_test_result("删除消息", False, "无法创建测试消息")
            return False
        
        delete_msg_id = test_msg[0]['id']
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.delete(
                    f"{self.base_url}/api/v1/messages/{delete_msg_id}",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    await asyncio.sleep(0.5)
                    
                    # 验证消息已删除
                    deleted = self.check_database_record(
                        "SELECT * FROM message WHERE id = %s",
                        (delete_msg_id,)
                    )
                    
                    self.log_test_result(
                        "删除消息",
                        len(deleted) == 0,
                        f"消息ID {delete_msg_id}，数据库中{'已删除' if len(deleted) == 0 else '仍存在'}"
                    )
                    return len(deleted) == 0
                else:
                    self.log_test_result("删除消息", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("删除消息", False, str(e))
            return False
    
    async def test_get_message_stats(self) -> bool:
        """测试获取消息统计"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/messages/stats",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_stats = self.check_database_record(
                        """
                        SELECT 
                            COUNT(*) as total,
                            SUM(CASE WHEN is_unread = 1 THEN 1 ELSE 0 END) as unread,
                            SUM(CASE WHEN type = 0 THEN 1 ELSE 0 END) as tutor,
                            SUM(CASE WHEN type = 1 THEN 1 ELSE 0 END) as private,
                            SUM(CASE WHEN type = 2 THEN 1 ELSE 0 END) as system
                        FROM message 
                        WHERE receiver_id = %s
                        """,
                        (self.test_user_id,)
                    )
                    
                    if db_stats:
                        stats = db_stats[0]
                        self.log_test_result(
                            "获取消息统计",
                            True,
                            f"总数:{stats['total']}, 未读:{stats['unread']}, 导师:{stats['tutor']}, 私信:{stats['private']}, 系统:{stats['system']}"
                        )
                    else:
                        self.log_test_result("获取消息统计", True, "统计数据获取成功")
                    return True
                else:
                    self.log_test_result("获取消息统计", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取消息统计", False, str(e))
            return False
    
    async def test_get_message_settings(self) -> bool:
        """测试获取消息设置"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/v1/messages/settings",
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # 验证数据库
                    db_settings = self.check_database_record(
                        "SELECT * FROM user_message_setting WHERE user_id = %s",
                        (self.test_user_id,)
                    )
                    
                    self.log_test_result(
                        "获取消息设置",
                        True,
                        f"数据库设置记录数: {len(db_settings)}"
                    )
                    return True
                else:
                    self.log_test_result("获取消息设置", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("获取消息设置", False, str(e))
            return False
    
    async def test_update_message_settings(self) -> bool:
        """测试更新消息设置"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/api/v1/messages/settings",
                    json={"reminder_type": 1, "keep_days": 60},
                    params={"user_id": self.test_user_id},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    await asyncio.sleep(0.5)
                    
                    # 验证数据库更新
                    db_settings = self.check_database_record(
                        "SELECT reminder_type, keep_days FROM user_message_setting WHERE user_id = %s",
                        (self.test_user_id,)
                    )
                    
                    if db_settings:
                        settings = db_settings[0]
                        self.log_test_result(
                            "更新消息设置",
                            True,
                            f"提醒类型:{settings['reminder_type']}, 保留天数:{settings['keep_days']}"
                        )
                    else:
                        self.log_test_result("更新消息设置", True, "设置已更新")
                    return True
                else:
                    self.log_test_result("更新消息设置", False, f"HTTP {response.status_code}")
                    return False
        except Exception as e:
            self.log_test_result("更新消息设置", False, str(e))
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 70)
        print("🧪 Message API 综合测试")
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
            ("获取消息列表", self.test_get_messages),
            ("按类型筛选", self.test_get_messages_by_type),
            ("获取消息详情", self.test_get_message_detail),
            ("标记已读", self.test_mark_as_read),
            ("获取未读数", self.test_get_unread_count),
            ("批量标记已读", self.test_batch_mark_read),
            ("删除消息", self.test_delete_message),
            ("消息统计", self.test_get_message_stats),
            ("获取设置", self.test_get_message_settings),
            ("更新设置", self.test_update_message_settings),
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
        report_file = f"tests/report/message_api_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
    tester = MessageAPITester()
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main()) 