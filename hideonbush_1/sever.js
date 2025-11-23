// server.js — eco_db.users 欄位：id, username, password, points, address, birthday, email, phone, status
const express = require('express');
const mysql = require('mysql2/promise');
const dotenv = require('dotenv');
const cors = require('cors');
const bcrypt = require('bcryptjs');
const path = require('path');

dotenv.config();
const app = express();

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

const pool = mysql.createPool({
  host: process.env.DB_HOST, port: Number(process.env.DB_PORT || 3306),
  user: process.env.DB_USER, password: process.env.DB_PASS, database: process.env.DB_NAME,
  connectionLimit: 10, dateStrings: true
});

const pickPublic = (r) => ({
  id: r.id, username: r.username, points: r.points, address: r.address,
  birthday: r.birthday, email: r.email, phone: r.phone, status: r.status
});

// 分頁查詢
app.get('/api/members', async (req, res, next) => {
  try {
    const page = Math.max(1, parseInt(req.query.page || '1', 10));
    const pageSize = Math.max(1, Math.min(100, parseInt(req.query.pageSize || '10', 10)));
    const offset = (page - 1) * pageSize;

    const [[{ total }]] = await pool.query('SELECT COUNT(*) AS total FROM users');
    const [rows] = await pool.query(
      `SELECT id, username, points, address, birthday, email, phone, status
       FROM users
       ORDER BY birthday IS NULL, birthday DESC, id
       LIMIT ? OFFSET ?`, [pageSize, offset]
    );
    res.json({ status: 'success', members: rows.map(pickPublic), totalPages: Math.ceil(total / pageSize) });
  } catch (e) { next(e); }
});

// 新增
app.post('/api/members', async (req, res, next) => {
  try {
    let { id, username, password, points, address, birthday, email, phone, status } = req.body || {};
    if (!username || !email) return res.status(400).json({ status: 'fail', message: 'username / email 為必填' });
    if (!password) return res.status(400).json({ status: 'fail', message: 'password 為必填（新增時）' });

    id = id || `MEM${Date.now().toString().slice(-6)}`;
    status = status || 'active';
    points = points ?? 0;
    const hash = await bcrypt.hash(password, 10);

    await pool.query(
      `INSERT INTO users (id, username, password, points, address, birthday, email, phone, status)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [id, username, hash, points, address ?? null, birthday ?? null, email, phone ?? null, status]
    );

    const [rows] = await pool.query(`SELECT id, username, points, address, birthday, email, phone, status FROM users WHERE id=?`, [id]);
    res.status(201).json({ status: 'success', member: pickPublic(rows[0]) });
  } catch (e) {
    if (String(e.code) === 'ER_DUP_ENTRY') return res.status(409).json({ status: 'fail', message: 'ID 或 Email 已存在' });
    next(e);
  }
});

// 更新（password 選填）
app.put('/api/members/:id', async (req, res, next) => {
  try {
    const id = req.params.id;
    const { username, password, points, address, birthday, email, phone, status } = req.body || {};

    const [exists] = await pool.query(`SELECT 1 FROM users WHERE id=?`, [id]);
    if (!exists.length) return res.status(404).json({ status: 'fail', message: 'Not found' });

    const fields = ['username=?','points=?','address=?','birthday=?','email=?','phone=?','status=?'];
    const params = [username, points ?? null, address ?? null, birthday ?? null, email, phone ?? null, status, id];

    if (password && password.trim() !== '') {
      const hash = await bcrypt.hash(password, 10);
      fields.splice(1, 0, 'password=?');
      params.splice(1, 0, hash);
    }

    await pool.query(`UPDATE users SET ${fields.join(', ')} WHERE id=?`, params);
    const [rows] = await pool.query(`SELECT id, username, points, address, birthday, email, phone, status FROM users WHERE id=?`, [id]);
    res.json({ status: 'success', member: pickPublic(rows[0]) });
  } catch (e) {
    if (String(e.code) === 'ER_DUP_ENTRY') return res.status(409).json({ status: 'fail', message: 'Email 已存在' });
    next(e);
  }
});

// 刪除
app.delete('/api/members/:id', async (req, res, next) => {
  try {
    await pool.query(`DELETE FROM users WHERE id=?`, [req.params.id]);
    res.json({ status: 'success' });
  } catch (e) { next(e); }
});

// 錯誤處理
app.use((err, req, res, next) => {
  console.error('[Server Error]', err);
  res.status(500).json({ status: 'fail', message: 'Server error' });
});

const PORT = Number(process.env.PORT || 3000);
app.listen(PORT, () => console.log(`Server running → http://localhost:${PORT}`));
