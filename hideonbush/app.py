from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import pymysql
from werkzeug.security import generate_password_hash, check_password_hash

# 初始化 Flask 應用程式
app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)
app.config['JWT_SECRET_KEY'] = 'supersecret'
jwt = JWTManager(app)

# 連接資料庫
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='100422',
        database='eco_db',
        cursorclass=pymysql.cursors.DictCursor
    )

# 提供前端首頁
@app.route('/')
def serve_frontend():
    return send_from_directory('static', 'index.html')

# 提供後台管理頁面
@app.route('/admin')
def serve_admin():
    return send_from_directory('static', 'admin.html')

# 註冊使用者
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"message": "請提供完整的使用者名稱與密碼"}), 400

    hashed_password = generate_password_hash(password)
    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("INSERT INTO users (username, password, points) VALUES (%s, %s, %s)", 
                       (username, hashed_password, 100))
        conn.commit()
        return jsonify({"message": "註冊成功！"})
    except pymysql.MySQLError as e:
        conn.rollback()
        return jsonify({"message": "使用者已存在或資料庫錯誤", "error": str(e)}), 400
    finally:
        cursor.close()
        conn.close()

# 使用者登入
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()

    if user and check_password_hash(user['password'], password):
        token = create_access_token(identity=username)
        return jsonify({"token": token})
    else:
        return jsonify({"message": "登入失敗，帳號或密碼錯誤"}), 401

# 查詢使用者點數
@app.route('/points', methods=['GET'])
@jwt_required()
def get_points():
    current_user = get_jwt_identity()
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT points FROM users WHERE username = %s", (current_user,))
    user = cursor.fetchone()
    
    if user:
        return jsonify({"points": user['points']})
    else:
        return jsonify({"message": "找不到使用者"}), 404

# 管理者登入
@app.route('/admin/login', methods=['POST'])
def admin_login():
    data = request.json
    admin_username = data.get('username')
    admin_password = data.get('password')

    if admin_username == "admin" and admin_password == "admin123":
        token = create_access_token(identity="admin")
        return jsonify({"token": token})
    else:
        return jsonify({"message": "管理者登入失敗"}), 401

# 查詢所有使用者（限管理者）
@app.route('/admin/users', methods=['GET'])
@jwt_required()
def get_all_users():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"message": "無權限訪問"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, points FROM users")
    users = cursor.fetchall()

    return jsonify(users)

# 查詢所有商品（限管理者）
@app.route('/admin/products', methods=['GET'])
@jwt_required()
def get_all_products():
    current_user = get_jwt_identity()
    if current_user != "admin":
        return jsonify({"message": "無權限訪問"}), 403

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()

    return jsonify(products)

# 啟動 Flask 伺服器
if __name__ == '__main__':
    app.run(debug=True)
