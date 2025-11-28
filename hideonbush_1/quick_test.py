#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import json

BASE_URL = 'http://localhost:5000'
session = requests.Session()

# 登入
login_resp = session.post(
    f'{BASE_URL}/api/admin/login',
    json={'username': 'admin', 'password': 'admin123'}
)

if login_resp.status_code != 200:
    print("❌ 登入失敗")
    exit(1)

# 測試第 1 頁
print("測試第 1 頁:")
resp1 = session.get(f'{BASE_URL}/api/members?page=1&pageSize=5')
data1 = resp1.json()
print(f"✓ 當前頁: {data1.get('currentPage')}")
print(f"✓ 總頁數: {data1.get('totalPages')}")
print(f"✓ 會員數: {len(data1.get('members', []))}")

# 檢查第一個會員的欄位
if data1.get('members'):
    member = data1['members'][0]
    print(f"\n第一個會員欄位:")
    for key in ['id', 'username', 'email', 'phone', 'created_at', 'points', 'status']:
        value = member.get(key, '❌ 不存在')
        print(f"  - {key}: {value}")
    
    # 檢查不應該存在的欄位
    if 'address' in member:
        print(f"  ⚠ address: {member.get('address')} (不應該存在)")
    if 'birthday' in member:
        print(f"  ⚠ birthday: {member.get('birthday')} (不應該存在)")

# 測試第 2 頁
print(f"\n測試第 2 頁:")
resp2 = session.get(f'{BASE_URL}/api/members?page=2&pageSize=5')
data2 = resp2.json()
print(f"✓ 當前頁: {data2.get('currentPage')}")
print(f"✓ 會員數: {len(data2.get('members', []))}")

print("\n✅ 所有測試完成")
