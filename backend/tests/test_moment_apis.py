#!/usr/bin/env python3
"""
Moment API 完整测试脚本
测试所有动态相关的API端点
"""

import httpx
import asyncio
import json
from datetime import datetime
from typing import Dict, Any

# 测试配置
BASE_URL = "http://localhost:8000"
API_PREFIX = "/api/v1"
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
    "moment_id": None,
    "comment_id": None
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

async def run_moment_tests():
    """
    执行所有Moment API测试
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        
        print("\n" + "="*60)
        print("🚀 开始测试 Moment API")
        print("="*60)
        
        # ============= 动态管理相关测试 =============
        print("\n\n📋 第一部分：动态管理 API")
        
        # 1. 创建动态（Dynamic）
        result = await test_api(
            client,
            "创建动态",
            "POST",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID},
            json={
                "moment_type": "dynamic",
                "content": "这是一条测试动态，分享我的学习心得！#学习 #效率",
                "tags": ["学习", "效率", "测试"]
            }
        )
        
        if result.get("success") and result.get("data"):
            test_data_ids["moment_id"] = result["data"].get("id")
            print(f"✅ 已保存动态ID: {test_data_ids['moment_id']}")
        
        # 2. 创建干货（Dry Goods）
        result = await test_api(
            client,
            "创建干货",
            "POST",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID},
            json={
                "moment_type": "dryGoods",
                "title": "高效学习方法分享",
                "content": "这是一篇关于如何高效学习的干货文章...",
                "tags": ["学习方法", "干货", "分享"],
                "attachments": [
                    {
                        "type": "file",
                        "url": "https://example.com/study-guide.pdf",
                        "name": "学习指南.pdf",
                        "size": 1024000
                    }
                ]
            }
        )
        
        # 3. 获取动态列表（默认）
        await test_api(
            client,
            "获取动态列表（默认）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
        )
        
        # 4. 获取动态列表（仅dynamic）
        await test_api(
            client,
            "获取动态列表（仅dynamic）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID, "moment_type": "dynamic", "page": 1, "page_size": 10}
        )
        
        # 5. 获取动态列表（仅dryGoods）
        await test_api(
            client,
            "获取动态列表（仅dryGoods）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID, "moment_type": "dryGoods", "page": 1, "page_size": 10}
        )
        
        # 6. 获取动态列表（按标签筛选）
        await test_api(
            client,
            "获取动态列表（按标签筛选）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID, "tags": ["学习"], "page": 1, "page_size": 10}
        )
        
        # 7. 获取动态列表（按时间范围筛选）
        await test_api(
            client,
            "获取动态列表（今日）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID, "time_range": "today", "page": 1, "page_size": 10}
        )
        
        # 8. 获取动态列表（按热度排序）
        await test_api(
            client,
            "获取动态列表（按热度排序）",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments",
            params={"user_id": TEST_USER_ID, "hot_type": "hot", "page": 1, "page_size": 10}
        )
        
        # 9. 搜索动态
        await test_api(
            client,
            "搜索动态",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/search",
            params={"user_id": TEST_USER_ID, "keyword": "学习", "page": 1, "page_size": 10}
        )
        
        # 10. 获取热门标签
        await test_api(
            client,
            "获取热门标签",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/tags/popular",
            params={"limit": 20}
        )
        
        # 11. 获取我发布的动态
        await test_api(
            client,
            "获取我发布的动态",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/me/published",
            params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
        )
        
        # 测试单个动态相关操作（如果成功创建了动态）
        if test_data_ids["moment_id"]:
            moment_id = test_data_ids["moment_id"]
            
            # 12. 获取动态详情
            await test_api(
                client,
                "获取动态详情",
                "GET",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}",
                params={"user_id": TEST_USER_ID}
            )
            
            # 13. 更新动态
            await test_api(
                client,
                "更新动态",
                "PUT",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}",
                params={"user_id": TEST_USER_ID},
                json={
                    "content": "这是更新后的动态内容！",
                    "tags": ["学习", "效率", "更新"]
                }
            )
            
            # 14. 获取用户动态
            await test_api(
                client,
                "获取指定用户的动态",
                "GET",
                f"{BASE_URL}{API_PREFIX}/moments/user/{TEST_USER_ID}",
                params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
            )
        
        # ============= 动态互动相关测试 =============
        print("\n\n💬 第二部分：动态互动 API")
        
        if test_data_ids["moment_id"]:
            moment_id = test_data_ids["moment_id"]
            
            # 15. 点赞动态
            await test_api(
                client,
                "点赞动态",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/like",
                params={"user_id": TEST_USER_ID}
            )
            
            # 16. 再次点赞（取消点赞）
            await test_api(
                client,
                "取消点赞",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/like",
                params={"user_id": TEST_USER_ID}
            )
            
            # 17. 收藏动态
            await test_api(
                client,
                "收藏动态",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/bookmark",
                params={"user_id": TEST_USER_ID}
            )
            
            # 18. 取消收藏
            await test_api(
                client,
                "取消收藏",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/bookmark",
                params={"user_id": TEST_USER_ID}
            )
            
            # 19. 记录浏览
            await test_api(
                client,
                "记录浏览",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/view",
                params={"user_id": TEST_USER_ID, "view_duration": 30}
            )
            
            # 20. 分享动态
            await test_api(
                client,
                "分享动态",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/share",
                params={"user_id": TEST_USER_ID},
                json={"share_type": "general"}
            )
            
            # 21. 提交评论
            result = await test_api(
                client,
                "提交评论",
                "POST",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/comments",
                params={"user_id": TEST_USER_ID},
                json={"content": "这是一条测试评论！"}
            )
            
            if result.get("success") and result.get("data"):
                test_data_ids["comment_id"] = result["data"].get("id")
                print(f"✅ 已保存评论ID: {test_data_ids['comment_id']}")
            
            # 22. 获取评论列表
            await test_api(
                client,
                "获取评论列表",
                "GET",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/comments",
                params={"page": 1, "page_size": 10}
            )
            
            # 23. 提交回复评论
            if test_data_ids["comment_id"]:
                await test_api(
                    client,
                    "回复评论",
                    "POST",
                    f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/comments",
                    params={"user_id": TEST_USER_ID},
                    json={
                        "content": "这是对评论的回复！",
                        "parent_comment_id": test_data_ids["comment_id"]
                    }
                )
            
            # 24. 获取互动状态
            await test_api(
                client,
                "获取互动状态",
                "GET",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/interaction-status",
                params={"user_id": TEST_USER_ID}
            )
            
            # 25. 获取互动统计
            await test_api(
                client,
                "获取互动统计",
                "GET",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/stats"
            )
            
            # 26. 获取互动摘要
            await test_api(
                client,
                "获取互动摘要",
                "GET",
                f"{BASE_URL}{API_PREFIX}/moments/{moment_id}/summary",
                params={"user_id": TEST_USER_ID}
            )
        
        # 27. 获取我的收藏
        await test_api(
            client,
            "获取我的收藏",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/me/bookmarks",
            params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
        )
        
        # 28. 获取我点赞的动态
        await test_api(
            client,
            "获取我点赞的动态",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/me/likes",
            params={"user_id": TEST_USER_ID, "page": 1, "page_size": 10}
        )
        
        # 29. 获取我的互动统计
        await test_api(
            client,
            "获取我的互动统计",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/me/stats",
            params={"user_id": TEST_USER_ID}
        )
        
        # 清理测试数据：删除评论和动态
        if test_data_ids["comment_id"]:
            # 30. 删除评论
            await test_api(
                client,
                "删除评论",
                "DELETE",
                f"{BASE_URL}{API_PREFIX}/moments/comments/{test_data_ids['comment_id']}",
                params={"user_id": TEST_USER_ID}
            )
        
        if test_data_ids["moment_id"]:
            # 31. 删除动态
            await test_api(
                client,
                "删除动态",
                "DELETE",
                f"{BASE_URL}{API_PREFIX}/moments/{test_data_ids['moment_id']}",
                params={"user_id": TEST_USER_ID}
            )
        
        # 健康检查
        await test_api(
            client,
            "动态服务健康检查",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/health"
        )
        
        await test_api(
            client,
            "动态互动服务健康检查",
            "GET",
            f"{BASE_URL}{API_PREFIX}/moments/health"
        )

async def main():
    """
    主函数
    """
    print("\n" + "="*60)
    print("🧪 Moment API 完整测试")
    print("="*60)
    print(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试服务: {BASE_URL}")
    print(f"测试用户: {TEST_USER_ID}")
    
    await run_moment_tests()
    
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
    report_file = "tests/report/MOMENT_API_TEST_RESULT.json"
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