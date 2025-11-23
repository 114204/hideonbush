#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
管理員帳號創建腳本 - 自動適配表結構
用於在 MySQL 資料庫中創建管理員帳號
"""

import mysql.connector
from werkzeug.security import generate_password_hash
from datetime import datetime
import getpass

def create_admin_account():
    """創建管理員帳號"""
    
    print("=" * 50)
    print("管理員帳號創建工具")
    print("=" * 50)
    
    # 資料庫連接設定
    print("\n請輸入資料庫連接資訊:")
    db_config = {
        'host': input("資料庫主機 (預設 localhost): ").strip() or 'localhost',
        'user': input("資料庫用戶名: ").strip(),
        'password': getpass.getpass("資料庫密碼: "),
        'database': input("資料庫名稱: ").strip()
    }
    
    try:
        # 連接資料庫
        print("\n正在連接資料庫...")
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        print("✅ 資料庫連接成功!")
        
        # 檢查 admins 表是否存在
        cursor.execute("SHOW TABLES LIKE 'admins'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("\n⚠️  admins 表不存在")
            create_new = input("是否創建新的 admins 表? (y/n): ").strip().lower()
            
            if create_new == 'y':
                create_table_sql = """
                CREATE TABLE admins (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP NULL,
                    is_active BOOLEAN DEFAULT TRUE
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """
                cursor.execute(create_table_sql)
                conn.commit()
                print("✅ admins 表創建成功!")
            else:
                print("操作已取消")
                return
        
        # 查看表結構
        print("\n正在檢查 admins 表結構...")
        cursor.execute("DESCRIBE admins")
        columns = cursor.fetchall()
        
        print("\n📋 現有欄位:")
        column_names = []
        for col in columns:
            print(f"  - {col[0]} ({col[1]})")
            column_names.append(col[0])
        
        # 檢查必要欄位 (password 或 password_hash)
        has_username = 'username' in column_names
        has_password = 'password' in column_names or 'password_hash' in column_names
        password_field = 'password_hash' if 'password_hash' in column_names else 'password'
        
        if not has_username or not has_password:
            print("\n❌ 錯誤: 表結構缺少必要欄位!")
            print(f"需要欄位: username, {password_field}")
            print(f"現有欄位: {', '.join(column_names)}")
            
            add_columns = input("\n是否自動添加缺少的欄位? (y/n): ").strip().lower()
            if add_columns == 'y':
                if not has_username:
                    cursor.execute("ALTER TABLE admins ADD COLUMN username VARCHAR(50) UNIQUE NOT NULL")
                    print("✅ 已添加 username 欄位")
                if not has_password:
                    cursor.execute(f"ALTER TABLE admins ADD COLUMN {password_field} VARCHAR(255) NOT NULL")
                    print(f"✅ 已添加 {password_field} 欄位")
                conn.commit()
            else:
                print("操作已取消")
                return
        
        # 管理員帳號資訊
        print("\n" + "=" * 50)
        print("請輸入管理員帳號資訊:")
        print("=" * 50)
        admin_username = input("管理員用戶名: ").strip()
        
        # 檢查是否需要 email
        admin_email = None
        if 'email' in column_names:
            admin_email = input("管理員 Email: ").strip()
            while not admin_email or '@' not in admin_email:
                print("❌ 請輸入有效的 Email 地址")
                admin_email = input("管理員 Email: ").strip()
        
        admin_password = getpass.getpass("管理員密碼: ")
        admin_password_confirm = getpass.getpass("確認密碼: ")
        
        # 驗證密碼
        if admin_password != admin_password_confirm:
            print("\n❌ 錯誤: 兩次輸入的密碼不一致!")
            return
        
        if len(admin_password) < 6:
            print("\n❌ 錯誤: 密碼長度至少需要 6 個字符!")
            return
        
        # 檢查用戶名是否已存在
        cursor.execute("SELECT * FROM admins WHERE username = %s", (admin_username,))
        if cursor.fetchone():
            print(f"\n❌ 錯誤: 用戶名 '{admin_username}' 已存在!")
            return
        
        # 加密密碼
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        
        # 動態構建 INSERT 語句
        insert_columns = ['username']
        insert_values = [admin_username]
        
        # 添加密碼欄位 (同時支援 password 和 password_hash)
        if 'password_hash' in column_names:
            insert_columns.append('password_hash')
            insert_values.append(hashed_password)
        
        if 'password' in column_names:
            insert_columns.append('password')
            insert_values.append(hashed_password)
        
        # 如果有 email 欄位，添加它
        if 'email' in column_names and admin_email:
            insert_columns.append('email')
            insert_values.append(admin_email)
        
        # 如果有 created_at 欄位，添加它
        if 'created_at' in column_names:
            insert_columns.append('created_at')
            insert_values.append(datetime.now())
        
        # 如果有 is_active 欄位，添加它
        if 'is_active' in column_names:
            insert_columns.append('is_active')
            insert_values.append(True)
        
        # 構建 SQL
        placeholders = ', '.join(['%s'] * len(insert_values))
        columns_str = ', '.join(insert_columns)
        insert_sql = f"INSERT INTO admins ({columns_str}) VALUES ({placeholders})"
        
        # 插入管理員帳號
        cursor.execute(insert_sql, tuple(insert_values))
        conn.commit()
        
        print("\n" + "=" * 50)
        print("✅ 管理員帳號創建成功!")
        print("=" * 50)
        print(f"用戶名: {admin_username}")
        if admin_email:
            print(f"Email: {admin_email}")
        print(f"創建時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\n請妥善保管您的密碼!")
        print("\n您現在可以使用此帳號登入後台管理系統。")
        
    except mysql.connector.Error as err:
        print(f"\n❌ 資料庫錯誤: {err}")
        print("\n請檢查:")
        print("1. 資料庫連接資訊是否正確")
        print("2. 資料庫用戶是否有足夠的權限")
        print("3. 資料庫是否正在運行")
        
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
            print("\n資料庫連接已關閉")

if __name__ == "__main__":
    try:
        create_admin_account()
    except KeyboardInterrupt:
        print("\n\n程序已取消")
    except Exception as e:
        print(f"\n程序執行失敗: {e}")