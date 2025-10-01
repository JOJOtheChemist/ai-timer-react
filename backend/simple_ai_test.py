#!/usr/bin/env python3
"""
简化的AI API测试脚本
直接测试API功能
"""

import asyncio
import httpx
from datetime import datetime
import json

BASE_URL = "http://localhost:8000"

class SimpleAITester:
    def __init__(self):
        self.results = []
        
    async def test_health(self):
        """测试健康检查"""
        print("\n1️⃣  测试健康检查...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{BASE_URL}/health", timeout=10.0)
                success = response.status_code == 200
                self.results.append(("健康检查", success, response.json() if success else str(response.status_code)))
                print(f"   {'✅' if success else '❌'} {response.status_code}")
                return success
        except Exception as e:
            self.results.append(("健康检查", False, str(e)))
            print(f"   ❌ {e}")
            return False
    
    async def test_chat(self):
        """测试AI聊天"""
        print("\n2️⃣  测试AI聊天...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{BASE_URL}/api/v1/ai/chat",
                    params={"user_id": 1, "stream": False},
                    json={"content": "你好，请帮我规划一下学习时间"},
                    timeout=30.0
                )
                success = response.status_code == 200
                self.results.append(("AI聊天", success, response.text[:100] if success else str(response.status_code)))
                print(f"   {'✅' if success else '❌'} {response.status_code}")
                if success:
                    data = response.json()
                    print(f"   回复: {data.get('content', '')[:50]}...")
                return success
        except Exception as e:
            self.results.append(("AI聊天", False, str(e)))
            print(f"   ❌ {e}")
            return False
    
    async def test_chat_history(self):
        """测试聊天历史"""
        print("\n3️⃣  测试聊天历史...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/api/v1/ai/chat/history",
                    params={"user_id": 1, "page": 1, "page_size": 10},
                    timeout=10.0
                )
                success = response.status_code == 200
                self.results.append(("聊天历史", success, response.text[:100] if success else str(response.status_code)))
                print(f"   {'✅' if success else '❌'} {response.status_code}")
                if success:
                    data = response.json()
                    print(f"   历史记录数: {data.get('total', 0)}")
                return success
        except Exception as e:
            self.results.append(("聊天历史", False, str(e)))
            print(f"   ❌ {e}")
            return False
    
    async def test_recommendations(self):
        """测试学习方法推荐"""
        print("\n4️⃣  测试学习方法推荐...")
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{BASE_URL}/api/v1/ai/recommendations/method",
                    params={"user_id": 1, "limit": 5},
                    timeout=30.0
                )
                success = response.status_code == 200
                self.results.append(("学习方法推荐", success, response.text[:100] if success else str(response.status_code)))
                print(f"   {'✅' if success else '❌'} {response.status_code}")
                if success:
                    data = response.json()
                    print(f"   推荐数量: {len(data) if isinstance(data, list) else 0}")
                return success
        except Exception as e:
            self.results.append(("学习方法推荐", False, str(e)))
            print(f"   ❌ {e}")
            return False
    
    async def run_all_tests(self):
        """运行所有测试"""
        print("=" * 60)
        print("🧪 AI API 简化测试")
        print("=" * 60)
        
        # 测试健康检查
        if not await self.test_health():
            print("\n❌ 服务器未响应，请确保服务器正在运行！")
            print("\n启动服务器命令:")
            print("  cd /Users/yeya/FlutterProjects/ai-time/backend")
            print("  source venv/bin/activate")
            print("  python test_server.py")
            return
        
        # 运行其他测试
        await self.test_chat()
        await self.test_chat_history()
        await self.test_recommendations()
        
        # 生成报告
        print("\n" + "=" * 60)
        print("📊 测试结果总结")
        print("=" * 60)
        
        total = len(self.results)
        passed = sum(1 for _, success, _ in self.results if success)
        
        print(f"总测试数: {total}")
        print(f"通过: {passed} ✅")
        print(f"失败: {total - passed} ❌")
        print(f"成功率: {(passed/total*100):.1f}%")
        
        print("\n详细结果:")
        for name, success, detail in self.results:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"  {status} - {name}")
            if not success and detail:
                print(f"      错误: {detail}")

async def main():
    tester = SimpleAITester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main()) 