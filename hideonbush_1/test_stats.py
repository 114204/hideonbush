#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql
import requests
import json

# 1. 查詢資料庫中的測試用戶
print("=== 查詢資料庫用戶 ===")
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='eva100422',
    database='eco_db',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        cursor.execute('SELECT id, username, email FROM users LIMIT 5')
        users = cursor.fetchall()
        print(f'找到 {len(users)} 個用戶：')
        for user in users:
            print(f"  - id={user['id']}, username={user['username']}, email={user['email']}")
        
        if users:
            first_user = users[0]
            print(f"\n使用第一個用戶登入：{first_user['username']}")
finally:
    conn.close()

# 2. 嘗試登入第一個用戶（假設密碼是 password123）
print("\n=== 嘗試登入 ===")
session = requests.Session()

# 先嘗試用常見密碼登入
passwords_to_try = ['password123', '123456', 'admin', 'test']

login_success = False
for pwd in passwords_to_try:
    try:
        login_resp = session.post(
            'http://localhost:5000/login',
            json={'username': first_user['username'], 'password': pwd},
            timeout=5
        )
        print(f"嘗試密碼 '{pwd}'：{login_resp.status_code}")
        if login_resp.status_code == 200:
            data = login_resp.json()
            if data.get('status') == 'success':
                print(f"✓ 登入成功！")
                login_success = True
                break
    except Exception as e:
        print(f"登入例外：{e}")
        break

# 3. 檢查認證狀態並查看 stats
print("\n=== 檢查 /api/check-auth ===")
try:
    auth_resp = session.get('http://localhost:5000/api/check-auth', timeout=5)
    print(f"狀態碼：{auth_resp.status_code}")
    data = auth_resp.json()
    print(f"回應 JSON：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    if data.get('authenticated'):
        print(f"\n✓ 認證成功")
        if 'stats' in data:
            print(f"✓ 包含 stats 欄位：{data['stats']}")
        else:
            print(f"✗ 缺少 stats 欄位")
    else:
        print(f"✗ 未認證")
except Exception as e:
    print(f"檢查認證例外：{e}")

# 4. 也測試 /api/user/stats
print("\n=== 檢查 /api/user/stats ===")
try:
    stats_resp = session.get('http://localhost:5000/api/user/stats', timeout=5)
    print(f"狀態碼：{stats_resp.status_code}")
    data = stats_resp.json()
    print(f"回應 JSON：")
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"檢查 stats 例外：{e}")
