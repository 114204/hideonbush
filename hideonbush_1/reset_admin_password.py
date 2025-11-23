import pymysql
from werkzeug.security import generate_password_hash

# 資料庫連線設定
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'eva100422',  # 請填入你的 MySQL 密碼
    'database': 'eco_db',
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor
}

def reset_admin_password():
    """重置管理員密碼"""
    
    # 新密碼設定
    new_password = 'admin123'  # 你可以修改這個密碼
    
    # 生成密碼雜湊
    password_hash = generate_password_hash(new_password, method='pbkdf2:sha256')
    
    print(f"[v0] 新密碼: {new_password}")
    print(f"[v0] 密碼雜湊: {password_hash}")
    
    try:
        # 連接資料庫
        connection = pymysql.connect(**db_config)
        print("[v0] 資料庫連接成功")
        
        with connection.cursor() as cursor:
            # 更新管理員密碼
            sql = """
                UPDATE admins 
                SET password_hash = %s, password = %s 
                WHERE username = 'admin'
            """
            cursor.execute(sql, (password_hash, password_hash))
            connection.commit()
            
            if cursor.rowcount > 0:
                print(f"[v0] ✓ 管理員密碼已重置")
                print(f"[v0] 帳號: admin")
                print(f"[v0] 新密碼: {new_password}")
            else:
                print("[v0] ✗ 找不到管理員帳號")
        
        connection.close()
        print("[v0] 資料庫連接已關閉")
        
    except Exception as e:
        print(f"[v0] ✗ 錯誤: {str(e)}")

if __name__ == '__main__':
    print("=" * 50)
    print("管理員密碼重置工具")
    print("=" * 50)
    reset_admin_password()
    print("=" * 50)
