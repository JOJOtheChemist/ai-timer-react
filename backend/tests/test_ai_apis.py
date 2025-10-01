#!/usr/bin/env python3
"""
AI API 测试脚本
测试所有AI相关的API端点，验证数据库交互功能
"""

import asyncio
import httpx
import json
import time
from datetime import datetime
from typing import Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor

# 配置
BASE_URL = "http://localhost:8000/api/v1"
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "ai_time_management",
    "user": "yeya",
    "password": ""  # 如果有密码请填写
}

class AIAPITester:
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)
        self.test_user_id = 1  # 测试用户ID
        self.session_id = None
        self.db_conn = None
        
    async def __aenter__(self):
        # 连接数据库
        try:
            self.db_conn = psycopg2.connect(**DB_CONFIG)
            print("✅ 数据库连接成功")
        except Exception as e:
            print(f"❌ 数据库连接失败: {e}")
            
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
        if self.db_conn:
            self.db_conn.close()
            
    def check_database_record(self, table_name: str, conditions: Dict[str, Any]) -> Dict:
        """检查数据库中的记录"""
        if not self.db_conn:
            return {"error": "数据库未连接"}
            
        try:
            cursor = self.db_conn.cursor(cursor_factory=RealDictCursor)
            
            # 构建WHERE条件
            where_conditions = []
            params = []
            for key, value in conditions.items():
                where_conditions.append(f"{key} = %s")
                params.append(value)
                
            query = f"SELECT * FROM {table_name}"
            if where_conditions:
                query += f" WHERE {' AND '.join(where_conditions)}"
            query += " ORDER BY created_at DESC LIMIT 5"
            
            cursor.execute(query, params)
            records = cursor.fetchall()
            
            cursor.close()
            return {"records": [dict(record) for record in records]}
            
        except Exception as e:
            return {"error": str(e)}
    
    def count_database_records(self, table_name: str, conditions: Dict[str, Any] = None) -> int:
        """统计数据库记录数量"""
        if not self.db_conn:
            return 0
            
        try:
            cursor = self.db_conn.cursor()
            
            query = f"SELECT COUNT(*) FROM {table_name}"
            params = []
            
            if conditions:
                where_conditions = []
                for key, value in conditions.items():
                    where_conditions.append(f"{key} = %s")
                    params.append(value)
                query += f" WHERE {' AND '.join(where_conditions)}"
            
            cursor.execute(query, params)
            count = cursor.fetchone()[0]
            cursor.close()
            
            return count
            
        except Exception as e:
            print(f"❌ 统计记录失败: {e}")
            return 0

    async def test_health_check(self):
        """测试健康检查端点"""
        print("\n🔍 测试 AI 聊天健康检查...")
        
        try:
            response = await self.client.get(f"{BASE_URL}/ai/chat/health")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 健康检查成功: {data['message']}")
                return True
            else:
                print(f"❌ 健康检查失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 健康检查异常: {e}")
            return False

    async def test_chat_message(self):
        """测试发送聊天消息"""
        print("\n🔍 测试发送聊天消息...")
        
        # 记录发送前的记录数
        before_count = self.count_database_records("ai_chat_records", {"user_id": self.test_user_id})
        
        try:
            # 测试数据
            message_data = {
                "content": "你好，我想了解一些学习方法",
                "message_type": "text",
                "context": {"page": "study_method"}
            }
            
            response = await self.client.post(
                f"{BASE_URL}/ai/chat",
                json=message_data,
                params={"user_id": self.test_user_id}
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 聊天消息发送成功")
                print(f"   AI回复: {data.get('content', '')[:100]}...")
                
                # 保存session_id用于后续测试
                if 'session_id' in data:
                    self.session_id = data['session_id']
                    print(f"   会话ID: {self.session_id}")
                
                # 检查数据库记录
                time.sleep(1)  # 等待数据库写入
                after_count = self.count_database_records("ai_chat_records", {"user_id": self.test_user_id})
                
                if after_count > before_count:
                    print(f"✅ 数据库记录已更新: {before_count} -> {after_count}")
                    
                    # 查看最新记录
                    records = self.check_database_record("ai_chat_records", {"user_id": self.test_user_id})
                    if records.get("records"):
                        latest = records["records"][0]
                        print(f"   最新记录: {latest.get('message_type')} - {latest.get('content', '')[:50]}...")
                else:
                    print(f"⚠️  数据库记录未增加: {before_count} -> {after_count}")
                
                return True
            else:
                print(f"❌ 聊天消息发送失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 聊天消息测试异常: {e}")
            return False

    async def test_chat_history(self):
        """测试获取聊天历史"""
        print("\n🔍 测试获取聊天历史...")
        
        try:
            params = {
                "user_id": self.test_user_id,
                "page": 1,
                "page_size": 10
            }
            
            if self.session_id:
                params["session_id"] = self.session_id
            
            response = await self.client.get(
                f"{BASE_URL}/ai/chat/history",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取聊天历史成功")
                print(f"   总记录数: {data.get('total', 0)}")
                print(f"   当前页记录数: {len(data.get('messages', []))}")
                
                # 显示最近的几条消息
                messages = data.get('messages', [])
                for i, msg in enumerate(messages[:3]):
                    print(f"   消息{i+1}: {msg.get('message_type')} - {msg.get('content', '')[:50]}...")
                
                return True
            else:
                print(f"❌ 获取聊天历史失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 聊天历史测试异常: {e}")
            return False

    async def test_recent_chat_history(self):
        """测试获取最近聊天历史"""
        print("\n🔍 测试获取最近聊天历史...")
        
        try:
            params = {
                "user_id": self.test_user_id,
                "days": 7
            }
            
            response = await self.client.get(
                f"{BASE_URL}/ai/chat/history/recent",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取最近聊天历史成功")
                print(f"   最近7天记录数: {data.get('total', 0)}")
                return True
            else:
                print(f"❌ 获取最近聊天历史失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 最近聊天历史测试异常: {e}")
            return False

    async def test_chat_sessions(self):
        """测试获取聊天会话列表"""
        print("\n🔍 测试获取聊天会话列表...")
        
        try:
            params = {
                "user_id": self.test_user_id,
                "days": 7
            }
            
            response = await self.client.get(
                f"{BASE_URL}/ai/chat/sessions",
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取聊天会话列表成功")
                print(f"   会话数量: {len(data.get('data', []))}")
                
                # 显示会话信息
                sessions = data.get('data', [])
                for i, session in enumerate(sessions[:3]):
                    print(f"   会话{i+1}: {session.get('session_id', 'N/A')} - {session.get('message_count', 0)}条消息")
                
                return True
            else:
                print(f"❌ 获取聊天会话列表失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 聊天会话列表测试异常: {e}")
            return False

    async def test_study_method_recommendations(self):
        """测试学习方法推荐"""
        print("\n🔍 测试学习方法推荐...")
        
        try:
            # 模拟用户认证（实际项目中应该使用JWT token）
            headers = {"Authorization": "Bearer fake-token"}
            params = {
                "limit": 5,
                "category": "记忆法"
            }
            
            response = await self.client.get(
                f"{BASE_URL}/ai/recommendations/method",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取学习方法推荐成功")
                print(f"   推荐方法数量: {len(data)}")
                
                # 显示推荐方法
                for i, method in enumerate(data[:3]):
                    print(f"   方法{i+1}: {method.get('name', 'N/A')} - 相关性: {method.get('relevance_score', 0)}")
                
                return True
            else:
                print(f"❌ 获取学习方法推荐失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 学习方法推荐测试异常: {e}")
            return False

    async def test_personalized_recommendations(self):
        """测试个性化推荐"""
        print("\n🔍 测试个性化推荐...")
        
        try:
            headers = {"Authorization": "Bearer fake-token"}
            
            response = await self.client.get(
                f"{BASE_URL}/ai/recommendations/personalized",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取个性化推荐成功")
                print(f"   推荐内容: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                return True
            else:
                print(f"❌ 获取个性化推荐失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 个性化推荐测试异常: {e}")
            return False

    async def test_recommendation_feedback(self):
        """测试推荐反馈"""
        print("\n🔍 测试推荐反馈...")
        
        # 记录反馈前的记录数
        before_count = self.count_database_records("ai_recommendation_feedback")
        
        try:
            headers = {"Authorization": "Bearer fake-token"}
            params = {
                "method_id": 1,
                "feedback_type": "helpful",
                "rating": 5,
                "comment": "这个方法很有用"
            }
            
            response = await self.client.post(
                f"{BASE_URL}/ai/recommendations/feedback",
                params=params,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 提交推荐反馈成功: {data.get('message', '')}")
                
                # 检查数据库记录
                time.sleep(1)
                after_count = self.count_database_records("ai_recommendation_feedback")
                
                if after_count > before_count:
                    print(f"✅ 反馈记录已保存到数据库: {before_count} -> {after_count}")
                else:
                    print(f"⚠️  反馈记录未增加: {before_count} -> {after_count}")
                
                return True
            else:
                print(f"❌ 提交推荐反馈失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 推荐反馈测试异常: {e}")
            return False

    async def test_user_behavior_analysis(self):
        """测试用户行为分析"""
        print("\n🔍 测试用户行为分析...")
        
        try:
            headers = {"Authorization": "Bearer fake-token"}
            
            response = await self.client.get(
                f"{BASE_URL}/ai/analysis/user-behavior",
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ 获取用户行为分析成功")
                print(f"   分析结果: {json.dumps(data, ensure_ascii=False, indent=2)[:200]}...")
                return True
            else:
                print(f"❌ 获取用户行为分析失败: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ 用户行为分析测试异常: {e}")
            return False

    async def check_database_tables(self):
        """检查数据库表结构"""
        print("\n🔍 检查数据库表结构...")
        
        if not self.db_conn:
            print("❌ 数据库未连接")
            return False
            
        try:
            cursor = self.db_conn.cursor()
            
            # 检查AI相关表是否存在
            tables_to_check = [
                "ai_chat_records",
                "ai_analysis_records", 
                "ai_recommendation_feedback",
                "study_methods",
                "method_checkins"
            ]
            
            for table in tables_to_check:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                """, (table,))
                
                exists = cursor.fetchone()[0]
                if exists:
                    # 获取记录数
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    print(f"✅ 表 {table} 存在，记录数: {count}")
                else:
                    print(f"❌ 表 {table} 不存在")
            
            cursor.close()
            return True
            
        except Exception as e:
            print(f"❌ 检查数据库表失败: {e}")
            return False

    async def run_all_tests(self):
        """运行所有测试"""
        print("🚀 开始 AI API 综合测试")
        print("=" * 50)
        
        # 检查数据库表
        await self.check_database_tables()
        
        # 测试结果统计
        results = []
        
        # 运行各项测试
        test_functions = [
            ("健康检查", self.test_health_check),
            ("发送聊天消息", self.test_chat_message),
            ("获取聊天历史", self.test_chat_history),
            ("获取最近聊天历史", self.test_recent_chat_history),
            ("获取聊天会话列表", self.test_chat_sessions),
            ("学习方法推荐", self.test_study_method_recommendations),
            ("个性化推荐", self.test_personalized_recommendations),
            ("推荐反馈", self.test_recommendation_feedback),
            ("用户行为分析", self.test_user_behavior_analysis),
        ]
        
        for test_name, test_func in test_functions:
            try:
                result = await test_func()
                results.append((test_name, result))
            except Exception as e:
                print(f"❌ {test_name} 测试异常: {e}")
                results.append((test_name, False))
        
        # 输出测试总结
        print("\n" + "=" * 50)
        print("📊 测试结果总结")
        print("=" * 50)
        
        passed = sum(1 for _, result in results if result)
        total = len(results)
        
        for test_name, result in results:
            status = "✅ 通过" if result else "❌ 失败"
            print(f"{status} {test_name}")
        
        print(f"\n总计: {passed}/{total} 项测试通过")
        
        if passed == total:
            print("🎉 所有测试通过！AI API 功能正常")
        else:
            print("⚠️  部分测试失败，请检查相关服务和配置")

async def main():
    """主函数"""
    print("AI API 测试工具")
    print("确保以下服务正在运行:")
    print("1. FastAPI 服务器 (http://localhost:8000)")
    print("2. PostgreSQL 数据库")
    print("3. 相关数据表已创建")
    print()
    
    async with AIAPITester() as tester:
        await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 