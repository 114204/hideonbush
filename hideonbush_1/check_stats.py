#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='eva100422',
        database='eco_db'
    )
    
    if conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        
        # 检查 orders 表的列
        print("=== Orders 表结构 ===")
        cursor.execute("DESCRIBE orders")
        for col in cursor.fetchall():
            print(f"- {col['Field']}: {col['Type']}")
        
        # 检查用户 ID 1 的订单
        print("\n=== 用户 1 的订单 ===")
        cursor.execute("SELECT COUNT(*) as count FROM orders WHERE member_id = 1 AND status != 'cancelled'")
        result = cursor.fetchone()
        print(f"记录数: {result['count']}")
        
        # 检查用户 1 的回收记录
        print("\n=== 用户 1 的回收记录 ===")
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM recycle_reviews WHERE member_id = 1 AND status = 'approved'")
        result = cursor.fetchone()
        print(f"总数量: {result['total']}")
        
        cursor.close()
        conn.close()
        
except Error as e:
    print(f"错误: {e}")
