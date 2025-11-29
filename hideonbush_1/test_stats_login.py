#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import bcrypt
import requests
import json

# 1. 創建或更新測試用戶密碼
print("=== 設置測試用戶 ===")
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='eva100422',
    database='eco_db',
    cursorclass=pymysql.cursors.DictCursor
)

test_password = 'testpass123'
hashed_pw = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

try:
    with conn.cursor() as cursor:
        # 使用第一個用戶 (testuser)
        cursor.execute(
            "UPDATE users SET password = %s WHERE username = %s",
            (hashed_pw, 'testuser')
        )
        conn.commit()
        print(f"✓ 用戶 'testuser' 密碼已更新為：{test_password}")
finally:
    conn.close()

# 2. 登入測試
print("\n=== 登入測試 ===")
session = requests.Session()
login_resp = session.post(
    'http://localhost:5000/login',
    json={'username': 'testuser', 'password': test_password},
    timeout=5
)
print(f"登入狀態碼：{login_resp.status_code}")
print(f"登入回應：{login_resp.json()}")

# 3. 檢查認證狀態（應包含 stats）
print("\n=== 檢查 /api/check-auth（應包含 stats）===")
auth_resp = session.get('http://localhost:5000/api/check-auth', timeout=5)
print(f"狀態碼：{auth_resp.status_code}")
data = auth_resp.json()
print(json.dumps(data, ensure_ascii=False, indent=2))

# 驗證結果
if data.get('authenticated'):
    print("\n✓ 認證成功")
    if 'stats' in data and data['stats'] is not None:
        print("✓ 包含 stats 欄位")
        print(f"  - totalRecycled: {data['stats'].get('totalRecycled')}")
        print(f"  - itemsExchanged: {data['stats'].get('itemsExchanged')}")
        print(f"  - totalPoints: {data['stats'].get('totalPoints')}")
        print(f"  - rankLevel: {data['stats'].get('rankLevel')}")
    else:
        print("✗ 缺少 stats 欄位（前端會 fallback 至 /api/user/stats）")
else:
    print("✗ 認證失敗")

# 4. 如果沒有 stats，測試 /api/user/stats
if not data.get('stats'):
    print("\n=== 檢查 /api/user/stats（fallback）===")
    stats_resp = session.get('http://localhost:5000/api/user/stats', timeout=5)
    print(f"狀態碼：{stats_resp.status_code}")
    stats_data = stats_resp.json()
    print(json.dumps(stats_data, ensure_ascii=False, indent=2))
