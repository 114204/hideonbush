#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test fixed stats endpoints with corrected SQL column names
"""
import requests
import json
import bcrypt
import mysql.connector
from mysql.connector import Error

# Database configuration
config = {
    'user': 'root',
    'password': 'eva100422',
    'host': 'localhost',
    'database': 'eco_db'
}

# API base URL
API_URL = "http://localhost:5000"

print("=" * 60)
print("Testing Stats Endpoints with Fixed SQL (member_id)")
print("=" * 60)

# Step 1: Set user password for testing
print("\n[Step 1] Setting test user password...")
try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    # Create bcrypt hash
    test_password = "testpass123"
    hashed = bcrypt.hashpw(test_password.encode('utf-8'), bcrypt.gensalt())
    
    # Update password for testuser
    cursor.execute(
        "UPDATE users SET password = %s WHERE username = %s",
        (hashed.decode('utf-8'), 'testuser')
    )
    conn.commit()
    print("[OK] Password updated for testuser")
    
    cursor.close()
    conn.close()
except Error as e:
    print(f"[ERROR] Database error: {e}")
    exit(1)

# Step 2: Login
print("\n[Step 2] Logging in...")
login_response = requests.post(
    f"{API_URL}/login",
    json={"username": "testuser", "password": "testpass123"}
)

if login_response.status_code != 200:
    print(f"[ERROR] Login failed: {login_response.status_code}")
    print(f"Response: {login_response.text}")
    exit(1)

login_data = login_response.json()
print(f"[OK] Login successful")
print(f"  Token: {login_data.get('token')[:20]}...")

# Extract session cookie
session_cookie = login_response.cookies

# Step 3: Check auth with stats
print("\n[Step 3] Testing /api/check-auth with stats...")
check_auth_response = requests.get(
    f"{API_URL}/api/check-auth",
    cookies=session_cookie
)

if check_auth_response.status_code != 200:
    print(f"[ERROR] Check auth failed: {check_auth_response.status_code}")
    print(f"Response: {check_auth_response.text}")
else:
    auth_data = check_auth_response.json()
    print(f"[OK] Check auth successful")
    print(f"  Status: {auth_data.get('authenticated')}")
    
    stats = auth_data.get('stats')
    if stats:
        print(f"  [OK] Stats found:")
        print(f"    - totalRecycled: {stats.get('totalRecycled')}")
        print(f"    - itemsExchanged: {stats.get('itemsExchanged')}")
        print(f"    - totalPoints: {stats.get('totalPoints')}")
        print(f"    - rankLevel: {stats.get('rankLevel')}")
    else:
        print(f"  [ERROR] Stats is null")
        print(f"    Full response: {json.dumps(auth_data, indent=2)}")

# Step 4: Test direct /api/user/stats endpoint
print("\n[Step 4] Testing /api/user/stats endpoint...")
stats_response = requests.get(
    f"{API_URL}/api/user/stats",
    cookies=session_cookie
)

if stats_response.status_code != 200:
    print(f"[ERROR] Stats endpoint failed: {stats_response.status_code}")
    print(f"Response: {stats_response.text}")
else:
    stats_data = stats_response.json()
    print(f"[OK] Stats endpoint successful")
    if stats_data.get('success'):
        data = stats_data.get('data', {})
        print(f"  [OK] Stats retrieved:")
        print(f"    - totalRecycled: {data.get('totalRecycled')}")
        print(f"    - itemsExchanged: {data.get('itemsExchanged')}")
        print(f"    - totalPoints: {data.get('totalPoints')}")
        print(f"    - rankLevel: {data.get('rankLevel')}")
    else:
        print(f"  [ERROR] Error: {stats_data.get('message')}")
        print(f"    Full response: {json.dumps(stats_data, indent=2)}")

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
