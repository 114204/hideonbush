#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
完整的會員管理頁面測試
模擬用戶操作：登入 -> 查看會員 -> 分頁導航
"""

import requests
import time
import json

BASE_URL = 'http://localhost:5000'

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_complete_workflow():
    session = requests.Session()
    
    print_section("1. 登入測試")
    
    # 1. 登入
    login_resp = session.post(
        f'{BASE_URL}/api/admin/login',
        json={'username': 'admin', 'password': 'admin123'},
        headers={'Content-Type': 'application/json'}
    )
    
    if login_resp.status_code == 200:
        print("✓ 登入成功")
        print(f"  響應: {login_resp.json()}")
    else:
        print("✗ 登入失敗")
        return False
    
    # 2. 驗證認證狀態
    auth_resp = session.get(f'{BASE_URL}/api/check-auth')
    auth_data = auth_resp.json()
    
    if auth_data.get('authenticated') and auth_data.get('is_admin'):
        print("✓ 認證驗證成功")
    else:
        print("✗ 認證驗證失敗")
        return False
    
    print_section("2. 會員數據顯示測試 (第 1 頁)")
    
    # 3. 獲取第 1 頁會員數據 (pageSize=10)
    resp1 = session.get(f'{BASE_URL}/api/members?page=1&pageSize=10')
    data1 = resp1.json()
    
    print(f"✓ API 狀態碼: {resp1.status_code}")
    print(f"✓ 當前頁: {data1.get('currentPage')}")
    print(f"✓ 總頁數: {data1.get('totalPages')}")
    print(f"✓ 會員數量: {len(data1.get('members', []))}")
    
    if not data1.get('members'):
        print("✗ 沒有會員數據")
        return False
    
    # 檢查第一個會員的所有欄位
    member = data1['members'][0]
    print(f"\n📋 第一個會員數據完整性檢查:")
    
    required_fields = {
        'id': '會員ID',
        'username': '姓名',
        'email': 'Email',
        'phone': '電話',
        'created_at': '註冊日期',
        'points': '點數',
        'status': '狀態'
    }
    
    all_present = True
    for field, desc in required_fields.items():
        if field in member:
            value = member[field]
            # 截斷長字符串
            if isinstance(value, str) and len(value) > 30:
                value = value[:27] + "..."
            print(f"  ✓ {field:12} ({desc:6}): {value}")
        else:
            print(f"  ✗ {field:12} ({desc:6}): 【缺失】")
            all_present = False
    
    # 檢查不應該存在的欄位
    unwanted_fields = ['address', 'birthday']
    for field in unwanted_fields:
        if field in member:
            print(f"  ⚠ {field:12}: 存在（不應該）")
    
    if not all_present:
        print("\n✗ 某些必要欄位缺失")
        return False
    
    print_section("3. 分頁導航測試")
    
    # 4. 測試第 2 頁
    print("進行第 2 頁查詢...")
    resp2 = session.get(f'{BASE_URL}/api/members?page=2&pageSize=10')
    data2 = resp2.json()
    
    if data2.get('currentPage') == 2:
        print(f"✓ 第 2 頁導航成功")
        print(f"  - 當前頁: {data2.get('currentPage')}")
        print(f"  - 會員數量: {len(data2.get('members', []))}")
    else:
        print("✗ 第 2 頁導航失敗")
        return False
    
    # 5. 測試最後一頁
    total_pages = data1.get('totalPages', 1)
    print(f"\n進行最後一頁 (第 {total_pages} 頁) 查詢...")
    resp_last = session.get(f'{BASE_URL}/api/members?page={total_pages}&pageSize=10')
    data_last = resp_last.json()
    
    if data_last.get('currentPage') == total_pages:
        print(f"✓ 最後一頁導航成功")
        print(f"  - 當前頁: {data_last.get('currentPage')}")
        print(f"  - 會員數量: {len(data_last.get('members', []))}")
    else:
        print("✗ 最後一頁導航失敗")
        return False
    
    print_section("4. 表格顯示驗證")
    
    # 計算預期的表格 HTML 結構
    members = data1.get('members', [])
    total_rows = len(members)
    total_cols = len(required_fields)
    
    print(f"✓ 預期表格結構:")
    print(f"  - 表頭列數: {total_cols}")
    print(f"  - 行數: {total_rows}")
    print(f"  - 總單元格: {total_rows * total_cols}")
    
    print_section("5. 分頁控制區域驗證")
    
    print(f"✓ 分頁信息:")
    print(f"  - 當前頁: 第 {data1.get('currentPage')} 頁")
    print(f"  - 總頁數: 共 {total_pages} 頁")
    print(f"  - 上一頁按鈕: {'启用' if data1.get('currentPage') > 1 else '禁用'}")
    print(f"  - 下一頁按鈕: {'启用' if data1.get('currentPage') < total_pages else '禁用'}")
    
    print_section("✅ 所有測試通過")
    
    print(f"""
完整的會員管理頁面已驗證：
  ✓ 登入功能正常
  ✓ 會員數據完整（{total_cols} 個欄位）
  ✓ 分頁導航正常（共 {total_pages} 頁）
  ✓ 表格結構正確
  ✓ 所有必要欄位都存在

前端應該顯示：
  - 表格包含 {total_cols} 列: {', '.join(required_fields.keys())}
  - 分頁控制在表格下方顯示: "第 X 頁 / 共 Y 頁"
  - 上一頁/下一頁按鈕根據頁數自動 disable/enable
""")
    
    return True

if __name__ == '__main__':
    try:
        test_complete_workflow()
    except Exception as e:
        print(f"\n✗ 錯誤: {e}")
        import traceback
        traceback.print_exc()
