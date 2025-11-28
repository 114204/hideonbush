#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import json

# 創建 session
session = requests.Session()

# 1. 測試管理員登入
print("=" * 50)
print("1. 測試管理員登入")
print("=" * 50)

login_data = {
    "username": "admin",
    "password": "admin123"
}

response = session.post(
    'http://127.0.0.1:5000/api/admin/login',
    json=login_data
)

print(f"Status: {response.status_code}")
print(f"Response: {response.json()}")

if response.status_code != 200:
    print("❌ 登入失敗")
    exit(1)

print("✅ 登入成功")

# 2. 測試獲取會員列表
print("\n" + "=" * 50)
print("2. 測試獲取會員列表")
print("=" * 50)

response = session.get(
    'http://127.0.0.1:5000/api/members?page=1&pageSize=5'
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"會員數量: {len(data.get('members', []))}")
    print(f"總頁數: {data.get('totalPages')}")
    print(f"當前頁: {data.get('currentPage')}")
    
    if data.get('members'):
        print("\n會員列表:")
        for member in data['members'][:3]:
            print(f"  - ID: {member['id']}, 姓名: {member['username']}, 郵件: {member['email']}")
        print("✅ 會員列表獲取成功")
    else:
        print("❌ 沒有會員數據")
else:
    print(f"❌ 請求失敗: {response.text}")

# 3. 測試搜尋會員
print("\n" + "=" * 50)
print("3. 測試搜尋會員")
print("=" * 50)

response = session.get(
    'http://127.0.0.1:5000/api/members?page=1&pageSize=10&search=eva'
)

print(f"Status: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    members = data.get('members', [])
    print(f"搜尋結果: {len(members)} 個會員")
    if members:
        print(f"✅ 搜尋功能正常")
        for member in members[:2]:
            print(f"  - {member['username']} ({member['email']})")
    else:
        print("⚠️  搜尋沒有找到匹配的會員")
else:
    print(f"❌ 搜尋失敗: {response.text}")

print("\n" + "=" * 50)
print("所有測試完成!")
print("=" * 50)
