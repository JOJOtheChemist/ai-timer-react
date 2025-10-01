#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schedule API 简化测试脚本"""

import requests
import psycopg2
from datetime import date, datetime

BASE_URL = "http://localhost:8000/api/v1/schedule"
USER_ID = 1
DB_CONFIG = {'host': 'localhost', 'database': 'ai_time_management', 'user': 'yeya', 'password': '', 'port': 5432}

def test_all_endpoints():
    results = []
    
    # 1. Health Check
    try:
        r = requests.get(f"{BASE_URL}/health/check")
        results.append(f"✅ Health Check: {r.status_code}")
    except Exception as e:
        results.append(f"❌ Health Check: {e}")
    
    # 2. Get Time Slots
    try:
        r = requests.get(f"{BASE_URL}/time-slots", params={"user_id": USER_ID, "target_date": str(date.today())})
        results.append(f"✅ GET /time-slots: {r.status_code} - {len(r.json().get('time_slots', []))} slots")
    except Exception as e:
        results.append(f"❌ GET /time-slots: {e}")
    
    # 3. Create Time Slot
    try:
        slot_data = {
            "date": f"{date.today()}T00:00:00",
            "time_range": "18:00-19:00",
            "status": "pending",
            "note": "测试创建"
        }
        r = requests.post(f"{BASE_URL}/time-slots", json=slot_data, params={"user_id": USER_ID})
        if r.status_code == 200:
            slot_id = r.json()['id']
            results.append(f"✅ POST /time-slots: Created ID={slot_id}")
            
            # 4. Update Time Slot
            r2 = requests.patch(f"{BASE_URL}/time-slots/{slot_id}", json={"status": "completed"}, params={"user_id": USER_ID})
            results.append(f"✅ PATCH /time-slots/{{id}}: {r2.status_code}")
            
            # 5. Complete Time Slot (shortcut)
            r3 = requests.patch(f"{BASE_URL}/time-slots/{slot_id}/complete", params={"user_id": USER_ID})
            results.append(f"✅ PATCH /time-slots/{{id}}/complete: {r3.status_code}")
        else:
            results.append(f"❌ POST /time-slots: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        results.append(f"❌ POST /time-slots: {e}")
    
    # 6. Get Completion Stats
    try:
        r = requests.get(f"{BASE_URL}/time-slots/completion-stats", params={"user_id": USER_ID})
        results.append(f"✅ GET /time-slots/completion-stats: {r.status_code}")
    except Exception as e:
        results.append(f"❌ GET /time-slots/completion-stats: {e}")
    
    # 7. Get AI Recommended Slots
    try:
        r = requests.get(f"{BASE_URL}/time-slots/ai-recommended", params={"user_id": USER_ID})
        results.append(f"✅ GET /time-slots/ai-recommended: {r.status_code}")
    except Exception as e:
        results.append(f"❌ GET /time-slots/ai-recommended: {e}")
    
    # Print Results
    print("\n" + "="*60)
    print("📊 Schedule API 测试结果")
    print("="*60)
    for result in results:
        print(result)
    print("="*60)
    
    # Database Verification
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM time_slot WHERE user_id = %s AND date = %s", (USER_ID, date.today()))
        count = cur.fetchone()[0]
        print(f"\n💾 数据库验证: 今日共有 {count} 个时间段")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"\n❌ 数据库验证失败: {e}")
    
    # Summary
    success_count = sum(1 for r in results if r.startswith("✅"))
    total_count = len(results)
    print(f"\n✅ 成功: {success_count}/{total_count} ({success_count/total_count*100:.1f}%)\n")

if __name__ == "__main__":
    test_all_endpoints() 