from flask import Flask, request, jsonify, session, redirect, render_template, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
import pymysql

app = Flask(__name__, static_folder='static')
CORS(app)

app.config['JWT_SECRET_KEY'] = 'supersecret'
app.secret_key = 'another_secret'
jwt = JWTManager(app)

def get_db_connection():
    return pymysql.connect(
        host='localhost',
        user='root',
        password='eva100422',
        database='eco_db',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/dashboard')
@jwt_required()
def dashboard():
    return render_template('dashboard.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

@app.route('/register', methods=['POST'])
def register():
    data = request.form
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    phone = data.get('phone')
    address = data.get('address')
    birthday = data.get('birthday')

    if not username or not password or not email:
        return jsonify({'message': '請提供必要欄位'}), 400

    hashed_password = generate_password_hash(password)
    conn = None

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, phone, password, address, birthday, points)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (username, email, phone, hashed_password, address, birthday, 100)
            )
        conn.commit()
        return redirect(url_for('login_page'))
    except pymysql.err.IntegrityError:
        return '使用者名稱或 Email 已存在', 400
    except Exception as e:
        return '資料庫錯誤: ' + str(e), 500
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.form
    username = data.get('username')
    password = data.get('password')

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and check_password_hash(user['password'], password):
                token = create_access_token(identity=username)
                return redirect(url_for('dashboard') + f'?token={token}')
            else:
                return '登入失敗，帳號或密碼錯誤', 401
    finally:
        conn.close()

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
