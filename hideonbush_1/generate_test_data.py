#!/usr/bin/env python3
import mysql.connector
from mysql.connector import Error
from datetime import datetime

try:
    conn = mysql.connector.connect(
        host='localhost',
        user='root',
        password='eva100422',
        database='eco_db'
    )
    
    if conn.is_connected():
        cursor = conn.cursor(dictionary=True)
        
        # 检查用户 ID 1 (testuser)
        cursor.execute("SELECT id, username FROM users WHERE id = 1")
        user = cursor.fetchone()
        print(f"目标用户: {user['username']} (ID: {user['id']})")
        
        # 删除现有的测试数据
        cursor.execute("DELETE FROM recycle_reviews WHERE member_id = 1 AND review_id LIKE 'REC_TEST_%'")
        deleted = cursor.rowcount
        print(f"删除了 {deleted} 条现有测试数据")
        
        # 添加测试数据
        test_data = [
            ('REC_TEST_001', 1, '寶特瓶', 15, 150),
            ('REC_TEST_002', 1, '鋁罐', 8, 80),
            ('REC_TEST_003', 1, '紙類', 12, 120),
            ('REC_TEST_004', 1, '玻璃瓶', 5, 100),
        ]
        
        for review_id, member_id, item_type, quantity, points in test_data:
            cursor.execute("""
                INSERT INTO recycle_reviews 
                (review_id, member_id, member_name, item_type, quantity, estimated_points, status, submit_time)
                VALUES (%s, %s, %s, %s, %s, %s, 'approved', NOW())
            """, (review_id, member_id, user['username'], item_type, quantity, points))
        
        conn.commit()
        print(f"添加了 {len(test_data)} 条测试数据")
        
        # 验证数据
        cursor.execute("""
            SELECT 
                item_type as type,
                COUNT(*) as count,
                SUM(estimated_points) as points
            FROM recycle_reviews
            WHERE member_id = 1 AND status = 'approved'
            GROUP BY item_type
        """)
        
        results = cursor.fetchall()
        print("\n用户 1 的统计数据:")
        for row in results:
            print(f"  {row['type']}: {row['count']} 个, {row['points']} 点")
        
        cursor.close()
        conn.close()
        print("\n✓ 数据生成完成!")
        
except Error as e:
    print(f"❌ 错误: {e}")
