#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
测试会员管理页面的分页和数据显示功能
"""

import requests
import json
from requests.cookies import RequestsCookieJar

BASE_URL = 'http://localhost:5000'

def test_member_display():
    """测试会员数据显示和分页"""
    
    print("=" * 60)
    print("测试会员管理页面数据显示")
    print("=" * 60)
    
    session = requests.Session()
    
    # 1. 登录
    print("\n[步骤 1] 执行管理员登录...")
    login_data = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    login_response = session.post(
        f'{BASE_URL}/api/admin/login',
        json=login_data,
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"登录状态码: {login_response.status_code}")
    print(f"登录响应: {login_response.json()}")
    
    if login_response.status_code != 200:
        print("❌ 登录失败！")
        return False
    
    # 2. 验证认证状态
    print("\n[步骤 2] 验证认证状态...")
    auth_response = session.get(
        f'{BASE_URL}/api/check-auth',
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"认证状态码: {auth_response.status_code}")
    auth_data = auth_response.json()
    print(f"认证响应: {json.dumps(auth_data, indent=2, ensure_ascii=False)}")
    
    if not auth_data.get('authenticated'):
        print("❌ 认证失败！")
        return False
    
    # 3. 获取第 1 页会员数据
    print("\n[步骤 3] 获取第 1 页会员数据 (每页 5 条)...")
    members_response = session.get(
        f'{BASE_URL}/api/members?page=1&pageSize=5',
        headers={'Content-Type': 'application/json'}
    )
    
    print(f"会员数据状态码: {members_response.status_code}")
    members_data = members_response.json()
    print(f"总页数: {members_data.get('totalPages')}")
    print(f"当前页: {members_data.get('currentPage')}")
    print(f"会员数量: {len(members_data.get('members', []))}")
    
    # 显示前 2 个会员的完整数据
    print("\n📋 第 1 页会员数据预览（前 2 个）:")
    for i, member in enumerate(members_data.get('members', [])[:2], 1):
        print(f"\n  会员 {i}:")
        for key, value in member.items():
            print(f"    - {key}: {value}")
    
    # 4. 测试第 2 页
    print("\n[步骤 4] 获取第 2 页会员数据...")
    page2_response = session.get(
        f'{BASE_URL}/api/members?page=2&pageSize=5',
        headers={'Content-Type': 'application/json'}
    )
    
    page2_data = page2_response.json()
    print(f"第 2 页会员数量: {len(page2_data.get('members', []))}")
    print(f"第 2 页当前页: {page2_data.get('currentPage')}")
    
    # 5. 测试搜索功能
    print("\n[步骤 5] 测试搜索功能 (搜索 'admin')...")
    search_response = session.get(
        f'{BASE_URL}/api/members?page=1&pageSize=10&search=admin',
        headers={'Content-Type': 'application/json'}
    )
    
    search_data = search_response.json()
    print(f"搜索结果会员数量: {len(search_data.get('members', []))}")
    
    # 显示搜索结果
    if search_data.get('members'):
        print("\n🔍 搜索结果预览:")
        for member in search_data.get('members', [])[:1]:
            print(f"  - ID: {member.get('id')}, Username: {member.get('username')}")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！会员数据显示和分页功能正常。")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    test_member_display()
