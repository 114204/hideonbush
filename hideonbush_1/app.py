from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql
import os

app = Flask(__name__, static_folder='static', static_url_path='/')
CORS(app)
app.config['JWT_SECRET_KEY'] = 'supersecret'
jwt = JWTManager(app)

# 建立資料庫連線的函數
def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='eva100422',
        database='eco_db',
        cursorclass=pymysql.cursors.DictCursor
    )

# 首頁
@app.route('/')
def serve_index():
    return send_from_directory('static', 'index.html')

# 註冊
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'message': '請提供完整資料'}), 400

    hashed_password = generate_password_hash(password)
    conn = None  # 先定義 conn

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO users (username, password, points) VALUES (%s, %s, %s)",
                (username, hashed_password, 100)
            )
        conn.commit()
        return jsonify({'message': '註冊成功！'})
    except pymysql.err.IntegrityError:
        return jsonify({'message': '使用者名稱已存在'}), 400
    except Exception as e:
        return jsonify({'message': '資料庫錯誤', 'error': str(e)}), 500
    finally:
        if conn:
            conn.close()

# 登入
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                token = create_access_token(identity=username)
                return jsonify({'token': token})
            else:
                return jsonify({'message': '登入失敗，帳號或密碼錯誤'}), 401
    finally:
        conn.close()

# 查詢點數
@app.route('/points', methods=['GET'])
@jwt_required()
def get_points():
    current_user = get_jwt_identity()
    username = request.args.get('username')

    if username != current_user:
        return jsonify({'message': '無權限'}), 403

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT points FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                return jsonify({'points': result['points']})
            else:
                return jsonify({'message': '使用者不存在'}), 404
    finally:
        conn.close()

# 商品列表
@app.route('/products', methods=['GET'])
@jwt_required()
def get_products():
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, name, points_required FROM products")
            products = cursor.fetchall()
            return jsonify(products)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
