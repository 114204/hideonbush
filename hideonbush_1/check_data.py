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
        
        # 检查 recycle_reviews 表中的数据
        cursor.execute("SELECT * FROM recycle_reviews WHERE member_id IN (1, 2) LIMIT 10")
        reviews = cursor.fetchall()
        print("=== Recycle Reviews (用户1或2) ===")
        
        for review in reviews:
            print(f"- ID: {review.get('review_id')}, Member: {review.get('member_id')}, Status: {review.get('status')}, Type: {review.get('item_type')}")
        
        # 检查每个用户的统计
        for user_id in [1, 2]:
            print(f"\n=== 用户 ID={user_id} 的回收数据 ===")
            cursor.execute(f"""
                SELECT 
                    item_type as type,
                    COUNT(*) as count,
                    SUM(estimated_points) as points
                FROM recycle_reviews
                WHERE member_id = {user_id} AND status IN ('approved', 'completed', 'verified')
                GROUP BY item_type
                ORDER BY count DESC
            """)
            
            result = cursor.fetchall()
            if result:
                for row in result:
                    print(f"  {row['type']}: {row['count']} 个, {row['points']} 点")
            else:
                print("  无数据")
        
        cursor.close()
        conn.close()
        
except Error as e:
    print(f"错误: {e}")

