import pymysql
import json

def get_db_connection():
    conn = pymysql.connect(
        host='localhost',
        user='root',
        password='eva100422',
        db='eco_db',
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

def inspect():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            print("--- Table: admins ---")
            cursor.execute("DESCRIBE admins")
            columns = cursor.fetchall()
            for col in columns:
                print(col)
            
            print("\n--- Data: admins (first 1) ---")
            cursor.execute("SELECT * FROM admins LIMIT 1")
            row = cursor.fetchone()
            print(row)

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    inspect()
