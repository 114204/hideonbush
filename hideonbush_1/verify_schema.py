#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify database schema for orders table column names"""

import mysql.connector
from mysql.connector import Error

config = {
    'user': 'root',
    'password': 'eva100422',
    'host': 'localhost',
    'database': 'eco_db'
}

try:
    conn = mysql.connector.connect(**config)
    cursor = conn.cursor(dictionary=True)
    
    print("=" * 60)
    print("Database Schema Verification")
    print("=" * 60)
    
    # Check orders table columns
    print("\n[orders table columns]")
    cursor.execute("DESCRIBE orders")
    for col in cursor.fetchall():
        print(f"  {col['Field']}: {col['Type']}")
    
    # Check if member_id or user_id exists
    print("\n[Column search]")
    cursor.execute("DESCRIBE orders")
    cols = [c['Field'] for c in cursor.fetchall()]
    
    if 'member_id' in cols:
        print("  [OK] 'member_id' column found in orders")
    elif 'user_id' in cols:
        print("  [ERROR] 'user_id' column found (should be member_id)")
    else:
        print("  [ERROR] Neither member_id nor user_id found")
    
    # Show sample data
    print("\n[Sample orders records]")
    cursor.execute("SELECT * FROM orders LIMIT 1")
    sample = cursor.fetchone()
    if sample:
        print(f"  Sample record keys: {list(sample.keys())}")
    else:
        print("  No records in orders table")
    
    # Count orders
    cursor.execute("SELECT COUNT(*) as cnt FROM orders")
    count = cursor.fetchone()
    print(f"  Total orders: {count['cnt']}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("Schema verification complete")
    print("=" * 60)
    
except Error as e:
    print(f"[ERROR] {e}")
