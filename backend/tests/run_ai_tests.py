#!/usr/bin/env python3
"""
AI API 测试运行器
执行AI API测试并生成详细的测试报告
"""

import asyncio
import sys
import os
from pathlib import Path
import time
import json
from datetime import datetime

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 导入测试类
from tests.test_ai_apis import AIAPITester

class AITestRunner:
    def __init__(self):
        self.test_results = {}
        self.start_time = None
        self.end_time = None
        
    def check_server_running(self) -> bool:
        """检查服务器是否运行"""
        try:
            import httpx
            response = httpx.get("http://localhost:8000/health", timeout=5.0)
            return response.status_code == 200
        except:
            return False
    
    async def run_tests(self):
        """运行所有测试"""
        print("🧪 开始执行AI API测试")
        print("=" * 60)
        
        # 检查服务器是否运行
        if not self.check_server_running():
            print("❌ 服务器未运行！")
            print("\n请在另一个终端窗口中启动服务器：")
            print("  cd /Users/yeya/FlutterProjects/ai-time/backend")
            print("  source venv/bin/activate")
            print("  python main.py")
            print("\n或者运行：")
            print("  uvicorn main:app --reload")
            print("\n等待服务器启动后，再次运行此测试脚本。")
            return False
        
        print("✅ 服务器正在运行\n")
        
        self.start_time = datetime.now()
        
        async with AIAPITester() as tester:
            await tester.check_database_tables()
            
            # 定义测试用例
            test_cases = [
                ("健康检查", tester.test_health_check),
                ("发送聊天消息", tester.test_chat_message),
                ("获取聊天历史", tester.test_chat_history),
                ("获取最近聊天历史", tester.test_recent_chat_history),
                ("获取聊天会话列表", tester.test_chat_sessions),
                ("学习方法推荐", tester.test_study_method_recommendations),
                ("个性化推荐", tester.test_personalized_recommendations),
                ("推荐反馈", tester.test_recommendation_feedback),
                ("用户行为分析", tester.test_user_behavior_analysis),
            ]
            
            # 执行测试
            for test_name, test_func in test_cases:
                print(f"\n🔍 执行测试: {test_name}")
                start_time = time.time()
                
                try:
                    result = await test_func()
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    self.test_results[test_name] = {
                        "status": "PASS" if result else "FAIL",
                        "duration": duration,
                        "error": None
                    }
                    
                    status_icon = "✅" if result else "❌"
                    print(f"{status_icon} {test_name}: {'通过' if result else '失败'} ({duration:.2f}s)")
                    
                except Exception as e:
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    self.test_results[test_name] = {
                        "status": "ERROR",
                        "duration": duration,
                        "error": str(e)
                    }
                    
                    print(f"💥 {test_name}: 异常 - {e} ({duration:.2f}s)")
        
        self.end_time = datetime.now()
        return True
    
    def generate_report(self) -> str:
        """生成测试报告"""
        if not self.test_results:
            return "❌ 没有测试结果可生成报告"
        
        # 统计结果
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r["status"] == "PASS")
        failed_tests = sum(1 for r in self.test_results.values() if r["status"] == "FAIL")
        error_tests = sum(1 for r in self.test_results.values() if r["status"] == "ERROR")
        
        total_duration = sum(r["duration"] for r in self.test_results.values())
        test_duration = (self.end_time - self.start_time).total_seconds()
        
        # 生成报告
        report = f"""
# AI API 测试报告

## 📊 测试概览

- **测试时间**: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} - {self.end_time.strftime('%H:%M:%S')}
- **总耗时**: {test_duration:.2f} 秒
- **测试用例总数**: {total_tests}
- **通过**: {passed_tests} ✅
- **失败**: {failed_tests} ❌
- **异常**: {error_tests} 💥
- **成功率**: {(passed_tests/total_tests*100):.1f}%

## 📋 详细测试结果

"""
        
        # 添加每个测试的详细结果
        for test_name, result in self.test_results.items():
            status_icon = {
                "PASS": "✅",
                "FAIL": "❌", 
                "ERROR": "💥"
            }.get(result["status"], "❓")
            
            report += f"### {status_icon} {test_name}\n"
            report += f"- **状态**: {result['status']}\n"
            report += f"- **耗时**: {result['duration']:.2f}s\n"
            
            if result["error"]:
                report += f"- **错误**: {result['error']}\n"
            
            report += "\n"
        
        # 添加数据库检查结果
        report += self.check_database_status()
        
        # 添加建议
        if failed_tests > 0 or error_tests > 0:
            report += """
## 🛠️ 问题排查建议

1. **检查服务器状态**: 确保FastAPI服务器正在运行
2. **验证数据库连接**: 检查PostgreSQL连接配置
3. **确认表结构**: 运行数据库初始化脚本
4. **查看服务器日志**: 检查详细错误信息
5. **验证依赖**: 确保所有Python包已正确安装

"""
        else:
            report += """
## 🎉 测试总结

所有AI API测试均通过！系统功能正常，数据库交互正确。

### ✅ 验证的功能
- AI聊天对话功能
- 聊天历史记录管理
- 学习方法推荐系统
- 用户行为分析
- 数据库记录持久化

"""
        
        return report
    
    def check_database_status(self) -> str:
        """检查数据库状态"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            conn = psycopg2.connect(
                host="localhost",
                port=5432,
                database="ai_time_management",
                user="yeya",
                password=""
            )
            
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # 检查AI相关表
            tables_info = []
            ai_tables = [
                "ai_chat_record",
                "ai_analysis_record", 
                "ai_recommendation",
                "ai_recommendation_feedback",
                "study_methods",
                "method_checkins"
            ]
            
            for table in ai_tables:
                try:
                    # 检查表是否存在
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
                        
                        # 获取最新记录
                        cursor.execute(f"""
                            SELECT * FROM {table} 
                            ORDER BY created_at DESC 
                            LIMIT 1
                        """)
                        latest = cursor.fetchone()
                        
                        tables_info.append({
                            "table": table,
                            "exists": True,
                            "count": count,
                            "latest": dict(latest) if latest else None
                        })
                    else:
                        tables_info.append({
                            "table": table,
                            "exists": False,
                            "count": 0,
                            "latest": None
                        })
                        
                except Exception as e:
                    tables_info.append({
                        "table": table,
                        "exists": False,
                        "count": 0,
                        "error": str(e)
                    })
            
            cursor.close()
            conn.close()
            
            # 生成数据库状态报告
            db_report = "\n## 🗄️ 数据库状态检查\n\n"
            
            for info in tables_info:
                table_name = info["table"]
                if info["exists"]:
                    db_report += f"### ✅ {table_name}\n"
                    db_report += f"- **记录数**: {info['count']}\n"
                    
                    if info["latest"] and info["count"] > 0:
                        latest = info["latest"]
                        # 显示最新记录的关键信息
                        if "content" in latest:
                            content = str(latest["content"])[:100] + "..." if len(str(latest["content"])) > 100 else str(latest["content"])
                            db_report += f"- **最新记录**: {content}\n"
                        elif "name" in latest:
                            db_report += f"- **最新记录**: {latest['name']}\n"
                        
                        if "created_at" in latest:
                            db_report += f"- **最新时间**: {latest['created_at']}\n"
                    
                    db_report += "\n"
                else:
                    db_report += f"### ❌ {table_name}\n"
                    db_report += "- **状态**: 表不存在\n"
                    if "error" in info:
                        db_report += f"- **错误**: {info['error']}\n"
                    db_report += "\n"
            
            return db_report
            
        except Exception as e:
            return f"\n## ❌ 数据库状态检查失败\n\n错误: {e}\n"
    
    def save_report(self, report: str):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ai_api_test_report_{timestamp}.md"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report)
        
        print(f"📄 测试报告已保存到: {filename}")
        return filename

async def main():
    """主函数"""
    print("🚀 AI API 测试运行器")
    print("=" * 60)
    
    runner = AITestRunner()
    
    try:
        # 运行测试
        success = await runner.run_tests()
        
        if not success:
            return
        
        # 生成报告
        report = runner.generate_report()
        print("\n" + "=" * 60)
        print(report)
        
        # 保存报告
        filename = runner.save_report(report)
        
        # 显示总结
        total_tests = len(runner.test_results)
        passed_tests = sum(1 for r in runner.test_results.values() if r["status"] == "PASS")
        
        print(f"\n🎯 测试完成: {passed_tests}/{total_tests} 通过")
        
        if passed_tests == total_tests:
            print("🎉 所有测试通过！AI API功能正常")
        else:
            print("⚠️  部分测试失败，请查看详细报告")
        
    except KeyboardInterrupt:
        print("\n⏹️  测试被用户中断")
    except Exception as e:
        print(f"\n💥 测试运行异常: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 