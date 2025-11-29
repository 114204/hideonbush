#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='eva100422',
    database='eco_db',
    cursorclass=pymysql.cursors.DictCursor
)

try:
    with conn.cursor() as cursor:
        # 查詢 orders 表的欄位
        print("=== orders 表結構 ===")
        cursor.execute("DESC orders")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col['Field']}: {col['Type']} ({col['Null']})")
        
        # 查詢 recycle_reviews 表的欄位
        print("\n=== recycle_reviews 表結構 ===")
        cursor.execute("DESC recycle_reviews")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col['Field']}: {col['Type']} ({col['Null']})")
        
        # 查詢 orders 資料筆數
        print("\n=== orders 資料 ===")
        cursor.execute("SELECT COUNT(*) as count FROM orders")
        count = cursor.fetchone()
        print(f"  筆數：{count['count']}")
        if count['count'] > 0:
            cursor.execute("SELECT * FROM orders LIMIT 1")
            sample = cursor.fetchone()
            print(f"  樣本：{sample}")
        
        # 查詢 recycle_reviews 資料筆數
        print("\n=== recycle_reviews 資料 ===")
        cursor.execute("SELECT COUNT(*) as count FROM recycle_reviews")
        count = cursor.fetchone()
        print(f"  筆數：{count['count']}")
        if count['count'] > 0:
            cursor.execute("SELECT * FROM recycle_reviews LIMIT 1")
            sample = cursor.fetchone()
            print(f"  樣本：{sample}")

finally:
    conn.close()
