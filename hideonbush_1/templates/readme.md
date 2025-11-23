# 绿色点数商城系统

完整的会员点数购物流程系统，包含前端 HTML 页面和 Flask 后端 API。

## 系统架构

### 前端页面
1. **dashboard.html** - 会员仪表板
   - 显示用户点数余额
   - 查看回收记录和统计
   - 编辑个人资料

2. **shop.html** - 商城购物页面
   - 浏览商品并按分类筛选
   - 使用点数兑换商品
   - 查看订单历史
   - 回收统计和排行榜

3. **member_order.html** - 订单管理后台
   - 查看所有用户订单
   - 搜索和筛选订单
   - 查看订单详情

### 后端 API (app.py)
- Flask 应用，提供完整的 RESTful API
- Session 认证管理
- MySQL 数据库连接

## 完整流程

### 1. 用户登录
- 用户在登录页面输入账号密码
- 后端验证并创建 session
- 重定向到 dashboard.html

### 2. 查看点数 (dashboard.html)
- 页面加载时调用 `/api/check-auth` 获取用户信息
- 显示用户当前点数余额
- 每 30 秒自动刷新点数

### 3. 商城购物 (shop.html)
- 调用 `/api/shop/products` 获取商品列表
- 用户选择商品，点击"立即兑换"
- 弹出确认对话框，显示所需点数和剩余点数
- 确认后调用 `/api/shop/order` 创建订单
- 后端扣除点数并创建订单记录
- 前端更新显示的点数余额

### 4. 查看订单 (shop.html)
- 切换到"我的订单"标签
- 调用 `/api/shop/orders` 获取订单历史
- 显示订单编号、商品名称、数量、点数等信息

### 5. 管理后台 (member_order.html)
- 管理员登录后访问
- 查看所有用户的订单记录
- 支持搜索和状态筛选

## 数据库表结构

### users (用户表)
- id, username, email, phone, password
- points (点数余额)
- address, birthday, status

### shop_products (商品表)
- id, name, points_required, original_price
- category, description, image_emoji
- in_stock, rating

### shop_orders (订单表)
- id, order_id, user_id, username
- product_id, product_name, quantity
- points_used, status, created_at

### point_history (点数历史)
- id, user_id, points_change
- reason, created_at

## API 端点

### 认证相关
- `GET /api/check-auth` - 检查登录状态并返回用户信息
- `POST /login` - 用户登录
- `POST /register` - 用户注册
- `POST /api/logout` - 用户登出

### 商城相关
- `GET /api/shop/products` - 获取商品列表
- `GET /api/shop/user-points` - 获取用户点数
- `POST /api/shop/order` - 创建订单（兑换商品）
- `GET /api/shop/orders` - 获取用户订单历史

### 管理后台
- `GET /api/orders` - 获取所有订单（分页、搜索、筛选）
- `GET /api/orders/<order_id>` - 获取订单详情

## 运行说明

### 1. 安装依赖
\`\`\`bash
pip install flask flask-cors pymysql bcrypt flask-jwt-extended python-dotenv
\`\`\`

### 2. 配置数据库
在 app.py 中配置 MySQL 连接信息：
\`\`\`python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'your_user',
    'password': 'your_password',
    'database': 'your_database'
}
\`\`\`

### 3. 启动后端
\`\`\`bash
python app.py
\`\`\`
后端将运行在 http://localhost:5000

### 4. 访问前端
直接在浏览器中打开 HTML 文件：
- dashboard.html - 会员仪表板
- shop.html - 商城页面
- member_order.html - 订单管理

## 技术栈

- **前端**: HTML5, CSS3, JavaScript (原生)
- **后端**: Flask (Python)
- **数据库**: MySQL
- **认证**: Session + JWT
- **样式**: Font Awesome 图标

## 特色功能

✅ 完整的用户认证流程
✅ 实时点数余额显示
✅ 商品分类筛选
✅ 订单确认对话框
✅ 订单历史记录
✅ 管理后台订单管理
✅ 响应式设计
✅ 自动刷新点数
✅ 点数变动历史记录

## 注意事项

1. 所有 HTML 文件需要通过 HTTP 服务器访问（不能直接用 file:// 协议）
2. 确保后端 API 运行在 http://localhost:5000
3. 前端使用 `credentials: 'include'` 发送 session cookies
4. 点数扣除和订单创建使用数据库事务确保一致性
