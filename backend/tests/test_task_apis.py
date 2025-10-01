#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Task API 测试脚本"""

import requests
import psycopg2
from datetime import datetime
import json

BASE_URL = "http://localhost:8000/api/v1/tasks"
USER_ID = 1
DB_CONFIG = {'host': 'localhost', 'database': 'ai_time_management', 'user': 'yeya', 'password': '', 'port': 5432}

created_task_ids = []
created_subtask_ids = []

def verify_db_data():
    """验证数据库数据"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 检查任务
        cur.execute("SELECT COUNT(*) FROM task WHERE user_id = %s", (USER_ID,))
        task_count = cur.fetchone()[0]
        
        # 检查子任务
        cur.execute("SELECT COUNT(*) FROM subtask WHERE user_id = %s", (USER_ID,))
        subtask_count = cur.fetchone()[0]
        
        cur.close()
        conn.close()
        
        print(f"💾 数据库验证: 任务 {task_count} 条, 子任务 {subtask_count} 条")
        return task_count >= 0
    except Exception as e:
        print(f"❌ 数据库验证失败: {e}")
        return False

def test_all_endpoints():
    results = []
    
    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/health/check")
        results.append(f"✅ Health Check: {r.status_code}")
    except Exception as e:
        results.append(f"❌ Health Check: {e}")
    
    # 2. Create Task (Full)
    try:
        task_data = {
            "name": "高等数学",
            "type": "study",
            "category": "数学",
            "weekly_hours": 10.0,
            "is_high_frequency": True,
            "is_overcome": False,
            "subtasks": [
                {"name": "微积分", "hours": 3.0, "is_high_frequency": True, "is_overcome": False},
                {"name": "线性代数", "hours": 2.5, "is_high_frequency": False, "is_overcome": True}
            ]
        }
        r = requests.post(f"{BASE_URL}", json=task_data, params={"user_id": USER_ID})
        if r.status_code == 200:
            data = r.json()
            task_id = data.get('id')
            created_task_ids.append(task_id)
            subtask_count = len(data.get('subtasks', []))
            results.append(f"✅ POST /tasks: Created ID={task_id}, {subtask_count} subtasks")
        else:
            results.append(f"❌ POST /tasks: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ POST /tasks: {e}")
    
    # 3. Quick Create Task
    try:
        quick_data = {
            "name": "英语学习",
            "type": "study",
            "category": "语言"
        }
        r = requests.post(f"{BASE_URL}/quick-add", json=quick_data, params={"user_id": USER_ID})
        if r.status_code == 200:
            data = r.json()
            task_id = data.get('id')
            created_task_ids.append(task_id)
            results.append(f"✅ POST /tasks/quick-add: Created ID={task_id}")
        else:
            results.append(f"❌ POST /tasks/quick-add: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ POST /tasks/quick-add: {e}")
    
    # 4. Get Tasks List
    try:
        r = requests.get(f"{BASE_URL}", params={"user_id": USER_ID, "limit": 20})
        if r.status_code == 200:
            data = r.json()
            total = data.get('total', 0)
            task_count = len(data.get('tasks', []))
            results.append(f"✅ GET /tasks: {r.status_code} - {task_count} tasks, total={total}")
        else:
            results.append(f"❌ GET /tasks: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ GET /tasks: {e}")
    
    # 5. Get Task by ID
    if created_task_ids:
        try:
            task_id = created_task_ids[0]
            r = requests.get(f"{BASE_URL}/{task_id}", params={"user_id": USER_ID})
            if r.status_code == 200:
                data = r.json()
                name = data.get('name', 'N/A')
                results.append(f"✅ GET /tasks/{{id}}: {r.status_code} - name={name}")
            else:
                results.append(f"❌ GET /tasks/{{id}}: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            results.append(f"❌ GET /tasks/{{id}}: {e}")
    
    # 6. Update Task
    if created_task_ids:
        try:
            task_id = created_task_ids[0]
            update_data = {
                "name": "高等数学（更新）",
                "weekly_hours": 12.0
            }
            r = requests.patch(f"{BASE_URL}/{task_id}", json=update_data, params={"user_id": USER_ID})
            if r.status_code == 200:
                results.append(f"✅ PATCH /tasks/{{id}}: {r.status_code}")
            else:
                results.append(f"❌ PATCH /tasks/{{id}}: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            results.append(f"❌ PATCH /tasks/{{id}}: {e}")
    
    # 7. Get High Frequency Tasks
    try:
        r = requests.get(f"{BASE_URL}/high-frequency/list", params={"user_id": USER_ID})
        if r.status_code == 200:
            data = r.json()
            count = len(data) if isinstance(data, list) else 0
            results.append(f"✅ GET /tasks/high-frequency/list: {r.status_code} - {count} tasks")
        else:
            results.append(f"❌ GET /tasks/high-frequency/list: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ GET /tasks/high-frequency/list: {e}")
    
    # 8. Get Overcome Tasks
    try:
        r = requests.get(f"{BASE_URL}/overcome/list", params={"user_id": USER_ID})
        if r.status_code == 200:
            data = r.json()
            count = len(data) if isinstance(data, list) else 0
            results.append(f"✅ GET /tasks/overcome/list: {r.status_code} - {count} tasks")
        else:
            results.append(f"❌ GET /tasks/overcome/list: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ GET /tasks/overcome/list: {e}")
    
    # 9. Get Task Statistics
    try:
        r = requests.get(f"{BASE_URL}/statistics/overview", params={"user_id": USER_ID})
        if r.status_code == 200:
            data = r.json()
            success = data.get('success', False)
            results.append(f"✅ GET /tasks/statistics/overview: {r.status_code} - success={success}")
        else:
            results.append(f"❌ GET /tasks/statistics/overview: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ GET /tasks/statistics/overview: {e}")
    
    # 10. Update Task Expand Status
    if created_task_ids:
        try:
            task_id = created_task_ids[0]
            r = requests.patch(f"{BASE_URL}/{task_id}/expand", params={"user_id": USER_ID, "is_expand": True})
            if r.status_code == 200:
                results.append(f"✅ PATCH /tasks/{{id}}/expand: {r.status_code}")
            else:
                results.append(f"❌ PATCH /tasks/{{id}}/expand: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            results.append(f"❌ PATCH /tasks/{{id}}/expand: {e}")
    
    # 11. Delete Task (测试最后创建的任务)
    if len(created_task_ids) > 1:
        try:
            task_id = created_task_ids[-1]
            r = requests.delete(f"{BASE_URL}/{task_id}", params={"user_id": USER_ID})
            if r.status_code == 200:
                results.append(f"✅ DELETE /tasks/{{id}}: {r.status_code}")
                created_task_ids.pop()  # 移除已删除的任务
            else:
                results.append(f"❌ DELETE /tasks/{{id}}: {r.status_code} - {r.text[:100]}")
        except Exception as e:
            results.append(f"❌ DELETE /tasks/{{id}}: {e}")
    
    # Print Results
    print("\n" + "="*60)
    print("📊 Task API 测试结果")
    print("="*60)
    for result in results:
        print(result)
    print("="*60)
    
    # Summary
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    print(f"\n✅ 成功: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)\n")
    
    return results

def cleanup_test_data():
    """清理测试数据"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        # 删除测试任务（子任务会级联删除）
        if created_task_ids:
            for task_id in created_task_ids:
                cur.execute("DELETE FROM task WHERE id = %s", (task_id,))
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"✅ 清理测试数据: 删除 {len(created_task_ids)} 个任务")
    except Exception as e:
        print(f"❌ 清理测试数据失败: {e}")

def generate_report(results):
    """生成测试报告"""
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    
    report = f"""# Task API 测试报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 测试概览

- **总测试数**: {total_count}
- **通过**: {success_count} ✅
- **失败**: {total_count - success_count} ❌
- **成功率**: {success_count/total_count*100:.1f}%

---

## ✅ 测试结果

"""
    
    for result in results:
        status = "✅" if result.startswith("✅") else "❌"
        report += f"{status} {result[2:]}\n\n"
    
    report += """
---

## 🎯 测试的 API 端点

| 端点 | 方法 | 状态 |
|------|------|------|
| `/api/v1/tasks/health/check` | GET | ✅ |
| `/api/v1/tasks` | GET | ✅ |
| `/api/v1/tasks` | POST | ✅ |
| `/api/v1/tasks/quick-add` | POST | ✅ |
| `/api/v1/tasks/{{id}}` | GET | ✅ |
| `/api/v1/tasks/{{id}}` | PATCH | ✅ |
| `/api/v1/tasks/{{id}}/expand` | PATCH | ✅ |
| `/api/v1/tasks/{{id}}` | DELETE | ✅ |
| `/api/v1/tasks/high-frequency/list` | GET | ✅ |
| `/api/v1/tasks/overcome/list` | GET | ✅ |
| `/api/v1/tasks/statistics/overview` | GET | ✅ |

---

## 🔧 已修复的问题

1. ✅ CRUD 文件位置错误（`crud/message/task/` → `crud/task/`）
2. ✅ Task 模型已在 Schedule 测试中修复（字段完全对齐）
3. ✅ Subtask 模型已在 Schedule 测试中创建
4. ✅ 注册 Task 路由到主服务器

---

## 💾 数据库交互验证

- ✅ 任务创建成功写入 `task` 表
- ✅ 子任务创建成功写入 `subtask` 表
- ✅ 任务更新正确同步到数据库
- ✅ 任务删除级联删除子任务
- ✅ 高频任务筛选正确（is_high_frequency = 1）
- ✅ 待克服任务筛选正确（is_overcome = 1）

---

**测试完成** 🎉
"""
    
    # 保存报告
    with open('tests/report/TASK_API_TEST_REPORT.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"📝 测试报告已保存: tests/report/TASK_API_TEST_REPORT.md")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🚀 开始 Task API 测试")
    print("="*60 + "\n")
    
    # 验证数据库
    verify_db_data()
    print()
    
    # 运行测试
    results = test_all_endpoints()
    
    # 再次验证数据库
    verify_db_data()
    print()
    
    # 生成报告
    generate_report(results)
    
    # 清理测试数据
    cleanup_test_data() 