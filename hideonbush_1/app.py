from flask import Flask, request, jsonify, session, redirect, render_template, url_for
from flask_cors import CORS
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from functools import wraps
from flask_jwt_extended import get_jwt_header
from flask_jwt_extended import get_jwt
from flask_jwt_extended import verify_jwt_in_request
from flask_jwt_extended import decode_token
import pymysql
import bcrypt
import logging
import json  # 新增 json 模組用於正確序列化 JSON
from datetime import datetime

# 設置日誌
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

app = Flask(__name__)
CORS(app, supports_credentials=True, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

app.config['JWT_SECRET_KEY'] = 'supersecret'
app.secret_key = 'another_secret'
# 配置 session - 確保 cookie 可以在不同域名之間傳遞
app.config['SESSION_COOKIE_SECURE'] = False  # 開發環境不使用 HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止 JS 訪問
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # 允許跨站請求時傳遞 cookie
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7  # 7 天
jwt = JWTManager(app)
app.logger = logging.getLogger(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'eva100422',
    'database': 'eco_db',
    'cursorclass': pymysql.cursors.DictCursor
}

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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'status': 'fail', 'message': '請先登錄'}), 401
        return f(*args, **kwargs)
    return decorated_function

# ========= HTML 頁面路由 =========
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ai3_0-page')
def ai3_0_page():
    return render_template('ai3_0.html')

@app.route('/admin_login-page')
def admin_login_page():
    return render_template('admin_login.html')

@app.route('/backmanament-page')
def backmanament_page():
    return render_template('backmanament.html')

@app.route('/login-page')
def login_page():
    return render_template('login.html')

@app.route('/register-page')
def register_page():
    return render_template('register.html')

@app.route('/shop-page')
def shop_page():
    return render_template('shop.html')

@app.route('/goals-page')
def goals_page():
    return render_template('goals.html')

@app.route('/howto-page')
def howto_page():
    return render_template('howto.html')

@app.route('/about-page')
def about_page():
    return render_template('about.html')

@app.route('/contact-page')
def contact_page():
    return render_template('contact.html')

@app.route('/faq-page')
def faq_page():
    return render_template('faq.html')

@app.route('/profile-page')
def profile_page():
    return render_template('profile_1.html')

@app.route('/center-page')
def center_page():
    return render_template('center.html')

@app.route('/point-page')
def point_page():
    return render_template('point.html')

@app.route('/member_order-page')
def member_order_page():
    return render_template('member_order.html')

@app.route('/control-page')
def control_page():
    return render_template('control.html')

@app.route('/db_management-page')
def db_management_page():
    return render_template('db_management.html')

@app.route('/create-account-page')
def create_account_page():
    return render_template('create_account.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login-page')
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/', code=302)

@app.route('/api/logout', methods=['POST'])
def api_logout():
    """JSON API 登出端點"""
    try:
        session.clear()
        return jsonify({
            'status': 'success',
            'message': '登出成功'
        }), 200
    except Exception as e:
        app.logger.error(f"登出失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '登出失敗'
        }), 500

@app.route('/api/user/current', methods=['GET'])
def get_current_user():
    """獲取當前登入用戶的完整資料"""
    if 'user_id' not in session:
        return jsonify({
            'status': 'fail',
            'message': '未登入'
        }), 401

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, username, email, phone, points, address, birthday, status, created_at
                FROM users WHERE id = %s
            """, (session['user_id'],))
            user = cursor.fetchone()

            if user:
                return jsonify({
                    'status': 'success',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'phone': user['phone'],
                        'points': user['points'],
                        'address': user['address'],
                        'birthday': str(user['birthday']) if user['birthday'] else None,
                        'status': user['status'],
                        'created_at': str(user['created_at']) if user['created_at'] else None
                    }
                }), 200
            else:
                session.clear()
                return jsonify({
                    'status': 'fail',
                    'message': '用戶不存在'
                }), 404
    except Exception as e:
        app.logger.error(f"獲取用戶資料失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '獲取用戶資料失敗'
        }), 500
    finally:
        conn.close()

# ========= 註冊 API =========
@app.route('/register', methods=['POST'])
def register():
    try:
        # 檢查請求內容類型和數據
        if not request.is_json:
            app.logger.warning("註冊請求未使用JSON格式")
            return jsonify({'status': 'fail', 'message': '請使用JSON格式提交數據'}), 400
            
        data = request.get_json()
        if data is None:
            app.logger.warning("無法解析JSON數據")
            return jsonify({'status': 'fail', 'message': '無法解析請求數據'}), 400
            
        app.logger.info(f"收到註冊數據: {data}")  # 記錄收到的數據（開發環境使用）

        # 檢查所有必要欄位
        required_fields = ['username', 'email', 'phone', 'password', 'address', 'birthday']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            app.logger.warning(f"缺少必要欄位: {missing_fields}")
            return jsonify({
                'status': 'fail', 
                'message': f'請提供必要欄位: {", ".join(missing_fields)}'
            }), 400

        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        address = data.get('address')
        birthday = data.get('birthday')

        # 確保密碼不為空
        if not password:
            return jsonify({'status': 'fail', 'message': '密碼不能為空'}), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM users WHERE username=%s OR email=%s", (username, email))
                if cursor.fetchone():
                    return jsonify({'status': 'fail', 'message': '使用者名稱或Email已存在'}), 409

                # 生成密碼雜湊
                try:
                    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    app.logger.debug(f"生成的密碼雜湊: {hashed_pw[:10]}... (長度: {len(hashed_pw)})")
                except Exception as hash_error:
                    app.logger.error(f"生成密碼雜湊錯誤: {str(hash_error)}")
                    return jsonify({'status': 'error', 'message': '密碼處理錯誤'}), 500
                
                # 執行插入
                try:
                    cursor.execute("""
                        INSERT INTO users (username, email, phone, password, address, birthday)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (username, email, phone, hashed_pw, address, birthday))
                    conn.commit()
                except Exception as db_error:
                    app.logger.error(f"資料庫插入錯誤: {str(db_error)}")
                    return jsonify({'status': 'fail', 'message': '資料庫錯誤，註冊失敗'}), 500
                
                # 取得新註冊用戶的ID
                cursor.execute("SELECT id FROM users WHERE username=%s", (username,))
                user = cursor.fetchone()
                
                if not user:
                    app.logger.error("註冊後無法找到用戶記錄")
                    return jsonify({'status': 'error', 'message': '註冊處理錯誤'}), 500
                
                # 登入用戶 (設置session)
                session['user_id'] = user['id']
                session['username'] = username
                
                # 產生JWT token
                token = create_access_token(identity=username)
                
                app.logger.info(f"用戶 {username} 註冊成功")
                return jsonify({
                    'status': 'success', 
                    'message': '註冊成功',
                    'token': token,
                    'redirect': '/dashboard'
                }), 200
        finally:
            conn.close()
    except Exception as e:
        app.logger.error(f"註冊處理異常: {str(e)}")
        return jsonify({'status': 'error', 'message': '伺服器錯誤，請稍後再試'}), 500

# ========= 用戶相關 API =========
@app.route('/api/users', methods=['GET'])
def get_user():
    username = request.args.get('username')
    if not username:
        return jsonify({'message': 'Username parameter is missing'}), 400

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        query = "SELECT id, username, points, address, birthday, email, phone FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        user = cursor.fetchone()

        cursor.close()
        connection.close()

        if user:
            return jsonify(user), 200
        else:
            return jsonify({'message': 'User not found'}), 404
    except Exception as e:
        app.logger.error(f"獲取用戶失敗: {str(e)}")
        return jsonify({'message': 'Error fetching user data', 'error': str(e)}), 500

@app.route('/api/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        try:
            # 檢查是否為管理員
            is_admin = session.get('is_admin', False)
            
            if is_admin:
                # 查詢 admins 表
                conn = get_db_connection()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT admin_id as id, username, email
                            FROM admins WHERE admin_id = %s
                        """, (session['user_id'],))
                        user = cursor.fetchone()

                        if user:
                            return jsonify({
                                'authenticated': True,
                                'is_admin': True,
                                'user': {
                                    'id': user['id'],
                                    'username': user['username'],
                                    'email': user['email']
                                }
                            })
                        else:
                            session.clear()
                            return jsonify({'authenticated': False})
                finally:
                    conn.close()
            else:
                # 查詢 users 表（普通用戶）
                conn = get_db_connection()
                try:
                    with conn.cursor() as cursor:
                        cursor.execute("""
                            SELECT id, username, email, phone, points, address, birthday, status
                            FROM users WHERE id = %s
                        """, (session['user_id'],))
                        user = cursor.fetchone()

                        if user:
                            return jsonify({
                                'authenticated': True,
                                'is_admin': False,
                                'user': {
                                    'id': user['id'],
                                    'username': user['username'],
                                    'email': user['email'],
                                    'phone': user['phone'],
                                    'points': user['points'],
                                    'address': user['address'],
                                    'birthday': str(user['birthday']) if user['birthday'] else None,
                                    'status': user['status']
                                }
                            })
                        else:
                            session.clear()
                            return jsonify({'authenticated': False})
                finally:
                    conn.close()
        except Exception as e:
            app.logger.error(f"檢查認證失敗: {str(e)}", exc_info=True)
            return jsonify({'authenticated': False}), 500
    else:
        return jsonify({'authenticated': False})
    


# ========= 登入 API =========
@app.route('/login', methods=['POST'])
def login():
    try:
        app.logger.info("開始處理登入請求")

        if request.is_json:
            app.logger.info("處理JSON格式登入請求")
            data = request.get_json()
        elif request.form:
            app.logger.info("處理表單格式登入請求")
            data = request.form
        else:
            app.logger.warning("未檢測到有效的請求數據")
            return jsonify({'status': 'fail', 'message': '無法解析請求數據'}), 400

        username = data.get('username')
        password = data.get('password')

        app.logger.info(f"用戶 {username} 嘗試登入")

        if not username or not password:
            app.logger.warning("缺少用戶名或密碼")
            return jsonify({'status': 'fail', 'message': '請輸入使用者名稱和密碼'}), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id, password FROM users WHERE username = %s", (username,))
                user = cursor.fetchone()

                app.logger.debug(f"用戶查詢結果: {user}")

                if not user:
                    app.logger.warning(f"使用者不存在: {username}")
                    return jsonify({'status': 'fail', 'message': '帳號或密碼錯誤'}), 401

                stored_pw = user['password']
                is_valid = False

                app.logger.debug(f"存儲的密碼雜湊 (前10位): {stored_pw[:10] if len(stored_pw) > 10 else stored_pw}")

                try:
                    pw_bytes = password.encode('utf-8')
                    stored_pw_bytes = stored_pw.encode('utf-8')
                    is_valid = bcrypt.checkpw(pw_bytes, stored_pw_bytes)
                    app.logger.debug(f"Bcrypt驗證結果: {is_valid}")
                except Exception as e:
                    app.logger.error(f"Bcrypt驗證失敗: {str(e)}, 將嘗試純文本比較")
                    is_valid = (stored_pw == password)
                    app.logger.debug(f"純文本比較結果: {is_valid}")

                if is_valid:
                    app.logger.info(f"用戶 {username} 登入成功")

                    session['user_id'] = user['id']
                    session['username'] = username

                    token = create_access_token(identity=username)

                    if request.is_json:
                        app.logger.debug("返回JSON登入成功響應")
                        return jsonify({
                            'status': 'success',
                            'message': '登入成功',
                            'token': token,
                            'redirect': '/dashboard'
                        })
                    else:
                        app.logger.debug("重定向到儀表板")
                        return redirect(url_for('dashboard') + f'?token={token}')
                else:
                    app.logger.warning(f"密碼不正確: {username}")
                    return jsonify({'status': 'fail', 'message': '帳號或密碼錯誤'}), 401
        finally:
            conn.close()
    except Exception as e:
        app.logger.error(f"登入處理異常: {str(e)}")
        return jsonify({'status': 'error', 'message': '伺服器錯誤，請稍後再試'}), 500

# ========= 管理員功能 =========
def user_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 會員必須有 user_id，且不是管理員
        if 'user_id' not in session or session.get('is_admin'):
            return jsonify({'status': 'fail', 'message': '請用會員帳號登入'}), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 管理員必須有 user_id 且 is_admin
        if 'user_id' not in session or not session.get('is_admin'):
            return jsonify({'status': 'fail', 'message': '請用管理員帳號登入'}), 401
        return f(*args, **kwargs)
    return decorated_function
@app.route('/api/admin/login', methods=['POST', 'OPTIONS'])
def admin_login():
    """管理員登入 API - 自動適配表結構"""
    # 處理 OPTIONS 請求
    if request.method == 'OPTIONS':
        return '', 204
        
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        app.logger.info(f"[v0] 管理員登入嘗試: username={username}")

        if not username or not password:
            app.logger.warning(f"[v0] 登入失敗: 缺少用戶名或密碼")
            return jsonify({
                'status': 'fail',
                'message': '請輸入用戶名和密碼'
            }), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 使用 SELECT * 來自動適配表結構
                cursor.execute("SELECT * FROM admins WHERE username = %s", (username,))
                admin = cursor.fetchone()

                if not admin:
                    app.logger.warning(f"[v0] 登入失敗: 管理員不存在 username={username}")
                    return jsonify({
                        'status': 'fail',
                        'message': '用戶名或密碼錯誤'
                    }), 401

                # 記錄實際的表結構
                app.logger.info(f"[v0] admins 表欄位: {list(admin.keys())}")
                
                # 動態尋找密碼欄位
                pwd_field = None
                if 'password_hash' in admin:
                    pwd_field = admin['password_hash']
                    app.logger.info("[v0] 使用 password_hash 欄位")
                elif 'password' in admin:
                    pwd_field = admin['password']
                    app.logger.info("[v0] 使用 password 欄位")
                else:
                    app.logger.error(f"[v0] 找不到密碼欄位! 可用欄位: {list(admin.keys())}")
                    return jsonify({
                        'status': 'error',
                        'message': '資料庫結構錯誤'
                    }), 500

                # 驗證密碼
                is_valid = False
                
                # 1. 嘗試 bcrypt
                try:
                    is_valid = bcrypt.checkpw(password.encode('utf-8'), pwd_field.encode('utf-8'))
                    app.logger.info(f"[v0] Bcrypt 密碼驗證結果: {is_valid}")
                except Exception as bcrypt_error:
                    app.logger.warning(f"[v0] Bcrypt 驗證失敗: {str(bcrypt_error)}")
                    
                    # 2. 嘗試 Werkzeug
                    try:
                        from werkzeug.security import check_password_hash
                        is_valid = check_password_hash(pwd_field, password)
                        app.logger.info(f"[v0] Werkzeug 密碼驗證結果: {is_valid}")
                    except Exception as werkzeug_error:
                        app.logger.warning(f"[v0] Werkzeug 驗證失敗: {str(werkzeug_error)}")
                        
                        # 3. 純文本比較 (僅用於測試)
                        is_valid = (pwd_field == password)
                        app.logger.info(f"[v0] 純文本密碼驗證結果: {is_valid}")

                if is_valid:
                    # 動態獲取 ID 欄位
                    admin_id = None
                    for id_field in ['id', 'admin_id', 'user_id']:
                        if id_field in admin:
                            admin_id = admin[id_field]
                            break
                    
                    if not admin_id:
                        # 如果找不到標準 ID 欄位，使用第一個欄位
                        admin_id = list(admin.values())[0]
                        app.logger.warning(f"[v0] 使用第一個欄位作為 ID: {admin_id}")
                    
                    # 設置 session
                    session.permanent = True  # 使 session 永久性
                    session['user_id'] = admin_id
                    session['username'] = username
                    session['is_admin'] = True

                    app.logger.info(f"[v0] 管理員 {username} 登入成功, ID={admin_id}")

                    return jsonify({
                        'status': 'success',
                        'message': '登入成功'
                    }), 200
                else:
                    app.logger.warning(f"[v0] 登入失敗: 密碼錯誤 username={username}")
                    return jsonify({
                        'status': 'fail',
                        'message': '用戶名或密碼錯誤'
                    }), 401

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"[v0] 管理員登入異常: {str(e)}")
        app.logger.error(f"[v0] 錯誤堆疊: ", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'登入失敗: {str(e)}'
        }), 500

@app.route('/admin/reset-password', methods=['POST'])
def reset_password():
    if not app.debug:
        return jsonify({'status': 'error', 'message': '此功能僅在開發模式可用'}), 403

    data = request.get_json()
    username = data.get('username')
    new_password = data.get('password', 'temp123')

    if not username:
        return jsonify({'status': 'fail', 'message': '請提供用戶名'}), 400

    try:
        hashed_pw = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("UPDATE users SET password = %s WHERE username = %s",
                              (hashed_pw, username))
                conn.commit()
                if cursor.rowcount > 0:
                    return jsonify({
                        'status': 'success',
                        'message': f'用戶 {username} 密碼已重置',
                        'password': new_password
                    })
                else:
                    return jsonify({'status': 'fail', 'message': '找不到指定用戶'}), 404
        finally:
            conn.close()
    except Exception as e:
        app.logger.error(f"重置密碼錯誤: {str(e)}")
        return jsonify({'status': 'error', 'message': '密碼重置失敗'}), 500

@app.route('/admin/create-account', methods=['POST'])
def admin_create_account():
    try:
        if not request.is_json:
            return jsonify({'status': 'fail', 'message': '請使用JSON格式提交數據'}), 400

        data = request.get_json()
        if data is None:
            return jsonify({'status': 'fail', 'message': '無法解析請求數據'}), 400

        app.logger.info(f"管理員建立帳號數據: {data}")

        required_fields = ['username', 'email', 'phone', 'password', 'address', 'birthday']
        missing_fields = [field for field in required_fields if not data.get(field)]

        if missing_fields:
            return jsonify({
                'status': 'fail',
                'message': f'請提供必要欄位: {", ".join(missing_fields)}'
            }), 400

        username = data.get('username')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        address = data.get('address')
        birthday = data.get('birthday')
        points = int(data.get('points', 0))

        if not password:
            return jsonify({'status': 'fail', 'message': '密碼不能為空'}), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
                if cursor.fetchone():
                    return jsonify({'status': 'fail', 'message': '該Email已被註冊'}), 409

                hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

                cursor.execute("""
                    INSERT INTO users (username, email, phone, password, address, birthday, points, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 1)
                """, (username, email, phone, hashed_pw, address, birthday, points))
                conn.commit()

                app.logger.info(f"管理員成功建立帳號: {username}")
                return jsonify({
                    'status': 'success',
                    'message': '帳號建立成功',
                    'account_info': {
                        'username': username,
                        'email': email,
                        'points': points
                    }
                }), 200
        finally:
            conn.close()
    except Exception as e:
        app.logger.error(f"管理員建立帳號異常: {str(e)}")
        return jsonify({'status': 'fail', 'message': '伺服器錯誤，請稍後再試'}), 500

@app.route('/admin/init-db', methods=['GET'])
def init_db():
    if not app.debug:
        return jsonify({'status': 'error', 'message': '此功能僅在開發模式可用'}), 403

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            # 創建 users 表
            cursor.execute("SHOW TABLES LIKE 'users'")
            if not cursor.fetchone():
                cursor.execute("""
                CREATE TABLE users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    phone VARCHAR(20) NOT NULL,
                    password VARCHAR(100) NOT NULL,
                    address TEXT NOT NULL,
                    birthday DATE NOT NULL,
                    points INT DEFAULT 0,
                    status TINYINT DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                app.logger.info("創建users表成功")

            # 創建 products 表
            cursor.execute("SHOW TABLES LIKE 'products'")
            if not cursor.fetchone():
                cursor.execute("""
                CREATE TABLE products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    points_required INT NOT NULL,
                    description TEXT,
                    image_url VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                app.logger.info("創建products表成功")

                cursor.execute("""
                INSERT INTO products (name, points_required, description) VALUES
                ('環保袋', 50, '可重複使用的環保購物袋'),
                ('不鏽鋼吸管', 100, '可重複使用的不鏽鋼吸管套裝'),
                ('有機肥料', 200, '由回收有機垃圾製成的優質肥料')
                """)
                app.logger.info("添加示例產品成功")

            # 創建 recycle_reviews 表
            cursor.execute("SHOW TABLES LIKE 'recycle_reviews'")
            if not cursor.fetchone():
                cursor.execute("""
                CREATE TABLE recycle_reviews (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    review_id VARCHAR(50) UNIQUE NOT NULL,
                    member_id INT NOT NULL,
                    member_name VARCHAR(50) NOT NULL,
                    item_type VARCHAR(50) NOT NULL,
                    item_id VARCHAR(50),
                    quantity INT NOT NULL,
                    estimated_points INT NOT NULL,
                    confidence DECIMAL(5,2),
                    image_data TEXT,
                    ai_details TEXT,
                    submit_time DATETIME NOT NULL,
                    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
                    review_time DATETIME,
                    reviewer VARCHAR(50),
                    reject_reason TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                app.logger.info("創建recycle_reviews表成功")

            # 創建 point_history 表
            cursor.execute("SHOW TABLES LIKE 'point_history'")
            if not cursor.fetchone():
                cursor.execute("""
                CREATE TABLE point_history (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    points_change INT NOT NULL,
                    reason VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                """)
                app.logger.info("創建point_history表成功")

            conn.commit()
            return jsonify({'status': 'success', 'message': '資料庫初始化成功'})
    except Exception as e:
        app.logger.error(f"資料庫初始化錯誤: {str(e)}")
        return jsonify({'status': 'error', 'message': f'資料庫初始化失敗: {str(e)}'}), 500
    finally:
        conn.close()

# ========= 積分相關 API =========
@app.route('/api/points', methods=['GET'])
@jwt_required()
def get_points():
    current_user = get_jwt_identity()

    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT points FROM users WHERE username = %s", (current_user,))
            result = cursor.fetchone()
            if result:
                return jsonify({'points': result['points']})
            else:
                return jsonify({'message': '使用者不存在'}), 404
    finally:
        conn.close()

@app.route('/api/products', methods=['GET'])
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

# ========= 回收審核 API =========
@app.route('/api/recycle/submit', methods=['POST'])
def submit_recycle():
    try:
        data = request.get_json()
        app.logger.info(f"收到回收提交請求: {data}")

        required_fields = ['memberId', 'memberName', 'itemType', 'quantity', 'estimatedPoints']
        missing_fields = [field for field in required_fields if field not in data]

        if missing_fields:
            return jsonify({
                'success': False,
                'message': f'缺少必填欄位: {", ".join(missing_fields)}'
            }), 400

        now = datetime.now()
        recycle_id = f"REC{now.strftime('%Y%m%d%H%M%S%f')[:-3]}"

        ai_details = data.get('aiDetails')
        if ai_details is None or ai_details == 'null':
            ai_details_json = None
        else:
            ai_details_json = json.dumps(ai_details, ensure_ascii=False)

        submit_time_str = data.get('submitTime')
        if submit_time_str:
            try:
                # 移除 'Z' 並解析 ISO 8601 格式
                if submit_time_str.endswith('Z'):
                    submit_time_str = submit_time_str[:-1]
                submit_time = datetime.fromisoformat(submit_time_str)
            except ValueError:
                # 如果解析失敗，使用當前時間
                submit_time = now
        else:
            submit_time = now

        # 格式化為 MySQL DATETIME 格式: 'YYYY-MM-DD HH:MM:SS'
        submit_time_mysql = submit_time.strftime('%Y-%m-%d %H:%M:%S')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                insert_query = """
                    INSERT INTO recycle_reviews
                    (review_id, member_id, member_name, item_type, item_id, quantity,
                     estimated_points, confidence, image_data, ai_details,
                     submit_time, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(insert_query, (
                    recycle_id,
                    data['memberId'],
                    data['memberName'],
                    data['itemType'],
                    data.get('itemId', ''),
                    data['quantity'],
                    data['estimatedPoints'],
                    data.get('confidence', 0),
                    data.get('imageData', ''),
                    ai_details_json,
                    submit_time_mysql,  # 使用正確格式化的 MySQL datetime
                    'pending'
                ))
                conn.commit()

                app.logger.info(f"回收記錄創建成功: {recycle_id}")

                return jsonify({
                    'success': True,
                    'reviewId': recycle_id,
                    'message': '提交成功,等待審核'
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"提交回收審核失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'提交失敗: {str(e)}'
        }), 500

@app.route('/api/recycle/user/<int:user_id>', methods=['GET'])
def get_user_reviews(user_id):
    """獲取指定用戶的回收審核記錄"""
    try:
        status = request.args.get('status', 'all')  # all, pending, approved, rejected

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                if status == 'all':
                    cursor.execute("""
                        SELECT * FROM recycle_reviews
                        WHERE member_id = %s
                        ORDER BY submit_time DESC
                    """, (user_id,))
                else:
                    cursor.execute("""
                        SELECT * FROM recycle_reviews
                        WHERE member_id = %s AND status = %s
                        ORDER BY submit_time DESC
                    """, (user_id, status))

                reviews = cursor.fetchall()

                # 格式化日期時間
                for review in reviews:
                    if review.get('submit_time'):
                        review['submit_time'] = review['submit_time'].strftime('%Y-%m-%d %H:%M:%S')
                    if review.get('review_time'):
                        review['review_time'] = review['review_time'].strftime('%Y-%m-%d %H:%M:%S')

                return jsonify({
                    'success': True,
                    'data': reviews
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取用戶回收記錄失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取記錄失敗: {str(e)}'
        }), 500

@app.route('/api/recycle/pending', methods=['GET'])
def get_pending_reviews():
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM recycle_reviews
                    WHERE status = 'pending'
                    ORDER BY submit_time DESC
                """)
                reviews = cursor.fetchall()

                return jsonify({
                    'success': True,
                    'data': reviews
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取待審核列表失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'獲取列表失敗: {str(e)}'
        }), 500

@app.route('/api/recycle/approve/<review_id>', methods=['POST'])
def approve_review(review_id):
    conn = get_db_connection()

    try:
        conn.begin()

        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM recycle_reviews WHERE review_id = %s",
                (review_id,)
            )
            review = cursor.fetchone()

            if not review:
                return jsonify({
                    'success': False,
                    'message': '找不到記錄'
                }), 404

            cursor.execute("""
                UPDATE recycle_reviews
                SET status = 'approved',
                    review_time = NOW(),
                    reviewer = %s
                WHERE review_id = %s
            """, (request.json.get('reviewer', '管理員'), review_id))

            cursor.execute("""
                UPDATE users
                SET points = points + %s
                WHERE id = %s
            """, (review['estimated_points'], review['member_id']))

            try:
                cursor.execute("""
                    INSERT INTO point_history
                    (user_id, points_change, reason, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (
                    review['member_id'],
                    review['estimated_points'],
                    f"回收{review['item_type']} x{review['quantity']}"
                ))
            except:
                pass

            conn.commit()

            app.logger.info(f"審核通過: {review_id}, 積分已發放: {review['estimated_points']}")

            return jsonify({
                'success': True,
                'message': '審核通過,積分已發放'
            }), 200

    except Exception as e:
        conn.rollback()
        app.logger.error(f"核准審核失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'核准失敗: {str(e)}'
        }), 500
    finally:
        conn.close()

@app.route('/api/recycle/reject/<review_id>', methods=['POST'])
def reject_review(review_id):
    try:
        data = request.get_json()
        reviewer = data.get('reviewer', '管理員')
        reason = data.get('reason', '不符合回收標準')

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    UPDATE recycle_reviews
                    SET status = 'rejected',
                        review_time = NOW(),
                        reviewer = %s,
                        reject_reason = %s
                    WHERE review_id = %s
                """, (reviewer, reason, review_id))

                conn.commit()

                if cursor.rowcount == 0:
                    return jsonify({
                        'success': False,
                        'message': '找不到記錄'
                    }), 404

                app.logger.info(f"審核拒絕: {review_id}, 原因: {reason}")

                return jsonify({
                    'success': True,
                    'message': '已拒絕審核'
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"拒絕審核失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'拒絕失敗: {str(e)}'
        }), 500

# ========= 用戶相關 API =========
@app.route('/api/user/update', methods=['PUT'])
def update_user_profile():
    """更新用戶個人資料"""
    if 'user_id' not in session:
        return jsonify({
            'status': 'fail',
            'message': '未登入'
        }), 401

    try:
        data = request.get_json()
        user_id = session['user_id']

        # 驗證必填欄位
        if not data.get('username') or not data.get('email'):
            return jsonify({
                'status': 'fail',
                'message': '用戶名和Email為必填項'
            }), 400

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 檢查 email 作詞是否被其他用戶使用
                cursor.execute("""
                    SELECT id FROM users
                    WHERE email = %s AND id != %s
                """, (data['email'], user_id))

                if cursor.fetchone():
                    return jsonify({
                        'status': 'fail',
                        'message': '該Email已被其他用戶使用'
                    }), 409

                # 更新用戶資料
                cursor.execute("""
                    UPDATE users
                    SET username = %s,
                        email = %s,
                        phone = %s,
                        address = %s,
                        birthday = %s
                    WHERE id = %s
                """, (
                    data['username'],
                    data['email'],
                    data.get('phone', ''),
                    data.get('address', ''),
                    data.get('birthday', None),
                    user_id
                ))

                conn.commit()

                # 更新 session 中的 username
                session['username'] = data['username']

                app.logger.info(f"用戶 {user_id} 更新資料成功")

                return jsonify({
                    'status': 'success',
                    'message': '資料更新成功'
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"更新用戶資料失敗: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': '更新失敗,請稍後再試'
        }), 500

# ========= 會員管理 API =========
@app.route('/api/members', methods=['GET'])
@admin_login_required
def get_members_paginated():
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        search = request.args.get('search', '')  # 新增搜尋參數處理
        offset = (page - 1) * page_size

        conn = get_db_connection()
        with conn.cursor() as cursor:
            where_clause = ""
            params = []
            
            if search:
                where_clause = "WHERE username LIKE %s OR email LIKE %s OR phone LIKE %s"
                search_param = f"%{search}%"
                params = [search_param, search_param, search_param]
            
            count_query = f"SELECT COUNT(*) AS total FROM users {where_clause}"
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']
            total_pages = (total + page_size - 1) // page_size

            query = f"""
                SELECT
                    id AS member_id,
                    username,
                    email,
                    phone,
                    address,
                    points,
                    DATE_FORMAT(created_at, '%%Y-%%m-%%d') AS created_at,
                    DATE_FORMAT(birthday, '%%Y-%%m-%%d') AS birthday,
                    CASE WHEN status = 1 THEN 'active' ELSE 'inactive' END AS status
                FROM users
                {where_clause}
                ORDER BY id DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, params + [page_size, offset])
            members = cursor.fetchall()

            formatted_members = [
                {
                    'id': f"MEM{str(member['member_id']).zfill(3)}",
                    'username': member['username'],
                    'email': member['email'],
                    'phone': member['phone'],
                    'points': member['points'] or 0,
                    'created_at': member['created_at'],
                    'status': member['status']
                }
                for member in members
            ]

        app.logger.info(f"查詢會員: 頁面={page}, 搜尋='{search}', 結果數={len(formatted_members)}")  # 新增日誌
        
        return jsonify({
            'members': formatted_members,
            'total_pages': total_pages,
            'current_page': page
        }), 200

    except Exception as e:
        app.logger.error(f"分頁查詢會員錯誤: {str(e)}")
        return jsonify({'status': 'fail', 'message': '加載會員失敗'}), 500
    finally:
        conn.close()

@app.route('/api/members', methods=['POST'])
@admin_login_required
def add_member():
    try:
        data = request.get_json()
        if not all(k in data for k in ['username', 'email']):
            return jsonify({'status': 'fail', 'message': '姓名和Email為必填項'}), 400

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE email = %s", (data['email'],))
            if cursor.fetchone():
                return jsonify({'status': 'fail', 'message': '該Email已被註冊'}), 409

            status = 1 if data.get('status') == 'active' else 0
            cursor.execute("""
                INSERT INTO users (username, email, phone, status, created_at)
                VALUES (%s, %s, %s, %s, NOW())
            """, (data['username'], data['email'], data.get('phone', ''), status))
            conn.commit()

        return jsonify({'status': 'success', 'message': '會員新增成功'}), 201

    except Exception as e:
        app.logger.error(f"新增會員錯誤: {str(e)}")
        return jsonify({'status': 'fail', 'message': '新增會員失敗'}), 500
    finally:
        conn.close()

@app.route('/api/members/<string:member_id>', methods=['PUT'])
@admin_login_required
def update_member(member_id):
    try:
        numeric_id = int(member_id.replace('MEM', ''))
        data = request.get_json()

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE id = %s", (numeric_id,))
            if not cursor.fetchone():
                return jsonify({'status': 'fail', 'message': '會員不存在'}), 404

            cursor.execute("""
                SELECT id FROM users WHERE email = %s AND id != %s
            """, (data['email'], numeric_id))
            if cursor.fetchone():
                return jsonify({'status': 'fail', 'message': '該Email已被使用'}), 409

            status = 1 if data.get('status') == 'active' else 0
            cursor.execute("""
                UPDATE users
                SET username = %s, email = %s, phone = %s, status = %s
                WHERE id = %s
            """, (data['username'], data['email'], data.get('phone', ''), status, numeric_id))
            conn.commit()

        return jsonify({'status': 'success', 'message': '會員更新成功'}), 200

    except Exception as e:
        app.logger.error(f"編輯會員錯誤: {str(e)}")
        return jsonify({'status': 'fail', 'message': '更新會員失敗'}), 500
    finally:
        conn.close()

@app.route('/api/members/<string:member_id>', methods=['DELETE'])
@admin_login_required
def delete_member(member_id):
    try:
        numeric_id = int(member_id.replace('MEM', ''))

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE id = %s", (numeric_id,))
            conn.commit()
            if cursor.rowcount == 0:
                return jsonify({'status': 'fail', 'message': '會員不存在'}), 404
        return jsonify({'status': 'success', 'message': '會員已刪除'}), 200
    except Exception as e:
        app.logger.error(f"刪除會員錯誤: {str(e)}")
        return jsonify({'status': 'fail', 'message': '刪除會員失敗'}), 500
    finally:
        conn.close()

# ========= 儀表板統計 API =========
@app.route('/api/dashboard/stats', methods=['GET'])
@admin_login_required
def get_dashboard_stats():
    """獲取儀表板統計數據"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) as total FROM users WHERE status = 1")
                total_members = cursor.fetchone()['total']

                cursor.execute("SELECT COUNT(*) as total FROM recycle_reviews WHERE status = 'approved'")
                total_orders = cursor.fetchone()['total']

                cursor.execute("SELECT COALESCE(SUM(points_change), 0) as total FROM point_history WHERE points_change > 0")
                total_points = cursor.fetchone()['total']

                cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM recycle_reviews WHERE status = 'approved'")
                total_recycled = cursor.fetchone()['total']

                cursor.execute("SELECT COUNT(*) as total FROM recycle_reviews WHERE status = 'pending'")
                pending_reviews = cursor.fetchone()['total']

                return jsonify({
                    'success': True,
                    'data': {
                        'totalMembers': total_members,
                        'totalOrders': total_orders,
                        'totalPoints': total_points,
                        'totalRecycled': total_recycled,
                        'pendingReviews': pending_reviews
                    }
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取儀表板統計失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取統計數據失敗'
        }), 500

@app.route('/api/dashboard/activities', methods=['GET'])
@admin_login_required
def get_dashboard_activities():
    """獲取最近活動記錄"""
    try:
        limit = int(request.args.get('limit', 10))

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                activities = []

                # 最近註冊的會員
                cursor.execute("""
                    SELECT username, created_at, 'user_register' as type
                    FROM users
                    ORDER BY created_at DESC
                    LIMIT 3
                """)
                for row in cursor.fetchall():
                    activities.append({
                        'type': 'user',
                        'icon': 'user-plus',
                        'title': f'新會員註冊：{row["username"]}',
                        'time': row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    })

                # 最近審核通過的回收
                cursor.execute("""
                    SELECT member_name, item_type, quantity, review_time
                    FROM recycle_reviews
                    WHERE status = 'approved'
                    ORDER BY review_time DESC
                    LIMIT 3
                """)
                for row in cursor.fetchall():
                    activities.append({
                        'type': 'recycle',
                        'icon': 'recycle',
                        'title': f'回收審核：{row["item_type"]} x {row["quantity"]} 已核准',
                        'time': row['review_time'].strftime('%Y-%m-%d %H:%M:%S') if row['review_time'] else ''
                    })

                # 最近的點數變動
                cursor.execute("""
                    SELECT u.username, ph.points_change, ph.reason, ph.created_at
                    FROM point_history ph
                    JOIN users u ON ph.user_id = u.id
                    ORDER BY ph.created_at DESC
                    LIMIT 4
                """)
                for row in cursor.fetchall():
                    activities.append({
                        'type': 'points',
                        'icon': 'coins',
                        'title': f'{row["username"]}：{row["reason"]}',
                        'time': row['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    })

                # 按時間排序並限制數量
                activities.sort(key=lambda x: x['time'], reverse=True)
                activities = activities[:limit]

                return jsonify({
                    'success': True,
                    'data': activities
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取活動記錄失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取活動記錄失敗'
        }), 500

# ========= 點數管理 API =========
@app.route('/api/points/history', methods=['GET'])
@login_required
def get_points_history():
    """獲取點數交易記錄"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        search = request.args.get('search', '')
        offset = (page - 1) * page_size

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                where_clause = ""
                params = []

                if search:
                    where_clause = "WHERE u.username LIKE %s OR u.email LIKE %s"
                    search_param = f"%{search}%"
                    params = [search_param, search_param]

                # 獲取總數
                count_query = f"""
                    SELECT COUNT(*) as total
                    FROM point_history ph
                    JOIN users u ON ph.user_id = u.id
                    {where_clause}
                """
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                total_pages = (total + page_size - 1) // page_size

                # 獲取分頁數據
                query = f"""
                    SELECT
                        ph.id,
                        u.username,
                        ph.points_change,
                        ph.reason,
                        ph.created_at,
                        u.points as current_balance
                    FROM point_history ph
                    JOIN users u ON ph.user_id = u.id
                    {where_clause}
                    ORDER BY ph.created_at DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, params + [page_size, offset])
                records = cursor.fetchall()

                formatted_records = []
                for record in records:
                    formatted_records.append({
                        'id': f'PT{str(record["id"]).zfill(3)}',
                        'member': record['username'],
                        'type': 'earn' if record['points_change'] > 0 else 'spend' if record['points_change'] < 0 else 'adjust',
                        'change': f'+{record["points_change"]}' if record['points_change'] > 0 else str(record['points_change']),
                        'balance': record['current_balance'],
                        'description': record['reason'],
                        'date': record['created_at'].strftime('%Y-%m-%d %H:%M')
                    })

                return jsonify({
                    'success': True,
                    'data': formatted_records,
                    'totalPages': total_pages,
                    'currentPage': page
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取點數記錄失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取點數記錄失敗'
        }), 500

@app.route('/api/points/adjust', methods=['POST'])
@login_required
def adjust_points():
    """手動調整會員點數"""
    try:
        data = request.get_json()
        member_id = data.get('memberId')
        points_change = int(data.get('pointsChange', 0))
        reason = data.get('reason', '管理員調整')

        if not member_id or points_change == 0:
            return jsonify({
                'success': False,
                'message': '請提供會員ID和點數變動'
            }), 400

        conn = get_db_connection()
        try:
            conn.begin()

            with conn.cursor() as cursor:
                # 檢查會員是否存在
                cursor.execute("SELECT id, username, points FROM users WHERE id = %s", (member_id,))
                user = cursor.fetchone()

                if not user:
                    return jsonify({
                        'success': False,
                        'message': '會員不存在'
                    }), 404

                # 檢查點數是否足夠(如果是扣除)
                if points_change < 0 and user['points'] + points_change < 0:
                    return jsonify({
                        'success': False,
                        'message': '點數不足'
                    }), 400

                # 更新用戶點數
                cursor.execute("""
                    UPDATE users
                    SET points = points + %s
                    WHERE id = %s
                """, (points_change, member_id))

                # 記錄點數變動
                cursor.execute("""
                    INSERT INTO point_history
                    (user_id, points_change, reason, created_at)
                    VALUES (%s, %s, %s, NOW())
                """, (member_id, points_change, reason))

                conn.commit()

                app.logger.info(f"管理員調整會員 {member_id} 點數: {points_change}")

                return jsonify({
                    'success': True,
                    'message': '點數調整成功'
                }), 200

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"調整點數失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '調整點數失敗'
        }), 500

# ========= 訂單管理 API =========
@app.route('/api/orders', methods=['GET'])
@login_required
def get_orders():
    """獲取訂單列表"""
    try:
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 10))
        search = request.args.get('search', '')
        status_filter = request.args.get('status', '')
        offset = (page - 1) * page_size

        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                where_clauses = []
                params = []

                if search:
                    where_clauses.append("(rr.review_id LIKE %s OR rr.member_name LIKE %s OR rr.item_type LIKE %s)")
                    search_param = f"%{search}%"
                    params.extend([search_param, search_param, search_param])

                if status_filter:
                    where_clauses.append("rr.status = %s")
                    params.append(status_filter)

                where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"

                # 獲取總數
                count_query = f"""
                    SELECT COUNT(*) as total
                    FROM recycle_reviews rr
                    WHERE {where_clause}
                """
                cursor.execute(count_query, params)
                total = cursor.fetchone()['total']
                total_pages = (total + page_size - 1) // page_size

                # 獲取分頁數據
                query = f"""
                    SELECT
                        rr.review_id,
                        rr.member_name,
                        rr.item_type,
                        rr.quantity,
                        rr.estimated_points,
                        rr.submit_time,
                        rr.status
                    FROM recycle_reviews rr
                    WHERE {where_clause}
                    ORDER BY rr.submit_time DESC
                    LIMIT %s OFFSET %s
                """
                cursor.execute(query, params + [page_size, offset])
                orders = cursor.fetchall()

                formatted_orders = []
                for order in orders:
                    formatted_orders.append({
                        'id': order['review_id'],
                        'member': order['member_name'],
                        'product': order['item_type'],
                        'quantity': order['quantity'],
                        'total': order['estimated_points'],
                        'date': order['submit_time'].strftime('%Y-%m-%d'),
                        'status': order['status']
                    })

                return jsonify({
                    'success': True,
                    'data': formatted_orders,
                    'totalPages': total_pages,
                    'currentPage': page
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取訂單列表失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取訂單列表失敗'
        }), 500

@app.route('/api/orders/<order_id>', methods=['GET'])
@login_required
def get_order_detail(order_id):
    """獲取訂單詳情"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT * FROM recycle_reviews
                    WHERE review_id = %s
                """, (order_id,))
                order = cursor.fetchone()

                if not order:
                    return jsonify({
                        'success': False,
                        'message': '訂單不存在'
                    }), 404

                return jsonify({
                    'success': True,
                    'data': {
                        'id': order['review_id'],
                        'member': order['member_name'],
                        'product': order['item_type'],
                        'quantity': order['quantity'],
                        'total': order['estimated_points'],
                        'date': order['submit_time'].strftime('%Y-%m-%d %H:%M:%S'),
                        'status': order['status'],
                        'confidence': float(order['confidence']) if order['confidence'] else 0,
                        'reviewer': order['reviewer'] if order['reviewer'] else '',
                        'review_time': order['review_time'].strftime('%Y-%m-%d %H:%M:%S') if order['review_time'] else '',
                        'reject_reason': order['reject_reason'] if order['reject_reason'] else ''
                    }
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取訂單詳情失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取訂單詳情失敗'
        }), 500

# ========= 商城相關 API =========
@app.route('/api/shop/products', methods=['GET'])
def get_shop_products():
    """獲取商城商品列表"""
    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        id,
                        name,
                        points_required,
                        original_price,
                        category,
                        description,
                        image_emoji,
                        in_stock,
                        rating
                    FROM shop_products
                    WHERE in_stock = 1
                    ORDER BY category, points_required
                """)
                products = cursor.fetchall()

                return jsonify({
                    'success': True,
                    'data': products
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取商品列表失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取商品列表失敗'
        }), 500

@app.route('/api/shop/user-points', methods=['GET'])
def get_user_points():
    """獲取當前用戶點數"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': '未登入'
        }), 401

    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT id, username, points
                    FROM users
                    WHERE id = %s
                """, (session['user_id'],))
                user = cursor.fetchone()

                if user:
                    return jsonify({
                        'success': True,
                        'data': {
                            'userId': user['id'],
                            'username': user['username'],
                            'points': user['points']
                        }
                    }), 200
                else:
                    return jsonify({
                        'success': False,
                        'message': '用戶不存在'
                    }), 404

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取用戶點數失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取用戶點數失敗'
        }), 500

@app.route('/api/shop/order', methods=['POST'])
def create_shop_order():
    """創建商城訂單"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': '請先登入'
        }), 401

    try:
        data = request.get_json()
        product_id = data.get('productId')
        quantity = int(data.get('quantity', 1))

        if not product_id or quantity <= 0:
            return jsonify({
                'success': False,
                'message': '無效的商品或數量'
            }), 400

        conn = get_db_connection()
        try:
            conn.begin()

            with conn.cursor() as cursor:
                # 1. 檢查商品是否存在且有庫存
                cursor.execute("""
                    SELECT id, name, points_required, in_stock
                    FROM shop_products
                    WHERE id = %s
                """, (product_id,))
                product = cursor.fetchone()

                if not product:
                    return jsonify({
                        'success': False,
                        'message': '商品不存在'
                    }), 404

                if not product['in_stock']:
                    return jsonify({
                        'success': False,
                        'message': '商品已售罄'
                    }), 400

                # 2. 檢查用戶點數是否足夠
                cursor.execute("""
                    SELECT id, username, points
                    FROM users
                    WHERE id = %s
                """, (session['user_id'],))
                user = cursor.fetchone()

                total_points = product['points_required'] * quantity

                if user['points'] < total_points:
                    return jsonify({
                        'success': False,
                        'message': '點數不足'
                    }), 400

                # 3. 創建訂單
                now = datetime.now()
                order_id = f"ORD{now.strftime('%Y%m%d%H%M%S%f')[:-3]}"

                cursor.execute("""
                    INSERT INTO shop_orders
                    (order_id, user_id, username, product_id, product_name, 
                     quantity, points_used, status, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    order_id,
                    user['id'],
                    user['username'],
                    product['id'],
                    product['name'],
                    quantity,
                    total_points,
                    'completed',
                    now
                ))

                # 4. 扣除用戶點數
                cursor.execute("""
                    UPDATE users
                    SET points = points - %s
                    WHERE id = %s
                """, (total_points, user['id']))

                # 5. 記錄點數變動
                cursor.execute("""
                    INSERT INTO point_history
                    (user_id, points_change, reason, created_at)
                    VALUES (%s, %s, %s, %s)
                """, (
                    user['id'],
                    -total_points,
                    f"兌換商品：{product['name']} x{quantity}",
                    now
                ))

                conn.commit()

                app.logger.info(f"訂單創建成功: {order_id}, 用戶: {user['username']}, 商品: {product['name']}, 點數: {total_points}")

                return jsonify({
                    'success': True,
                    'message': '兌換成功！',
                    'data': {
                        'orderId': order_id,
                        'pointsUsed': total_points,
                        'remainingPoints': user['points'] - total_points
                    }
                }), 200

        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"創建訂單失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'兌換失敗: {str(e)}'
        }), 500

@app.route('/api/shop/orders', methods=['GET'])
def get_user_shop_orders():
    """獲取用戶的商城訂單歷史"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': '未登入'
        }), 401

    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        order_id,
                        product_name,
                        quantity,
                        points_used,
                        status,
                        created_at
                    FROM shop_orders
                    WHERE user_id = %s
                    ORDER BY created_at DESC
                """, (session['user_id'],))
                orders = cursor.fetchall()

                formatted_orders = []
                for order in orders:
                    formatted_orders.append({
                        'orderId': order['order_id'],
                        'productName': order['product_name'],
                        'quantity': order['quantity'],
                        'pointsUsed': order['points_used'],
                        'status': order['status'],
                        'createdAt': order['created_at'].strftime('%Y-%m-%d %H:%M:%S')
                    })

                return jsonify({
                    'success': True,
                    'data': formatted_orders
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"獲取訂單歷史失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': '獲取訂單歷史失敗'
        }), 500

@app.route('/api/shop/init-products', methods=['GET'])
def init_shop_products():
    """初始化商城商品數據（僅開發模式）"""
    if not app.debug:
        return jsonify({'status': 'error', 'message': '此功能僅在開發模式可用'}), 403

    try:
        conn = get_db_connection()
        try:
            with conn.cursor() as cursor:
                # 創建商品表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shop_products (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        points_required INT NOT NULL,
                        original_price INT NOT NULL,
                        category VARCHAR(50) NOT NULL,
                        description TEXT,
                        image_emoji VARCHAR(10),
                        in_stock BOOLEAN DEFAULT TRUE,
                        rating DECIMAL(2,1) DEFAULT 5.0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # 創建訂單表
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS shop_orders (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        order_id VARCHAR(50) UNIQUE NOT NULL,
                        user_id INT NOT NULL,
                        username VARCHAR(50) NOT NULL,
                        product_id INT NOT NULL,
                        product_name VARCHAR(100) NOT NULL,
                        quantity INT NOT NULL,
                        points_used INT NOT NULL,
                        status ENUM('pending', 'completed', 'cancelled') DEFAULT 'completed',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id)
                    )
                """)

                # 檢查是否已有商品數據
                cursor.execute("SELECT COUNT(*) as count FROM shop_products")
                count = cursor.fetchone()['count']

                if count == 0:
                    # 插入示例商品
                    products = [
                        ('環保購物袋', 150, 299, '生活用品', '100%有機棉製作，可重複使用', '🛍️', True, 4.8),
                        ('竹製餐具組', 280, 560, '餐具', '天然竹子製成，環保無毒', '🥢', True, 4.9),
                        ('太陽能行動電源', 850, 1699, '電子產品', '綠能充電，戶外必備', '🔋', True, 4.7),
                        ('有機蔬菜種子包', 120, 240, '園藝', '在家種植新鮮蔬菜', '🌱', True, 4.6),
                        ('節水蓮蓬頭', 450, 899, '家用', '節水50%，環保省錢', '🚿', False, 4.8),
                        ('環保清潔劑套組', 320, 640, '清潔用品', '天然成分，無化學添加', '🧽', True, 4.5)
                    ]

                    cursor.executemany("""
                        INSERT INTO shop_products 
                        (name, points_required, original_price, category, description, image_emoji, in_stock, rating)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, products)

                conn.commit()

                return jsonify({
                    'success': True,
                    'message': '商城數據初始化成功'
                }), 200

        finally:
            conn.close()

    except Exception as e:
        app.logger.error(f"初始化商城數據失敗: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'初始化失敗: {str(e)}'
        }), 500


if __name__ == '__main__':
    print("\n可用路由：")
    for rule in app.url_map.iter_rules():
        print(f"  {rule}")
    print()

    app.run(debug=True, host='0.0.0.0', port=5000)
