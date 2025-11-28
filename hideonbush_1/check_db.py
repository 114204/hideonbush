import pymysql

conn = pymysql.connect(
    host='localhost',
    user='root',
    password='eva100422',
    database='eco_db',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

cursor = conn.cursor()

# Check if admins table exists
cursor.execute("SHOW TABLES LIKE 'admins'")
result = cursor.fetchone()
print('Admins table exists:', bool(result))

if result:
    # Get admin count
    cursor.execute('SELECT COUNT(*) as count FROM admins')
    count = cursor.fetchone()
    print('Admin count:', count['count'])
    
    # Get first admin
    cursor.execute('SELECT * FROM admins LIMIT 1')
    admin = cursor.fetchone()
    if admin:
        print('First admin:', {k: ('***' if k in ['password', 'password_hash'] else v) for k, v in admin.items()})

# Check users table
cursor.execute('SELECT COUNT(*) as count FROM users')
count = cursor.fetchone()
print('Users count:', count['count'])

cursor.close()
conn.close()
