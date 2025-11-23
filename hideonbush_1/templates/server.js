const express = require('express');
const mysql = require('mysql2/promise');
const cors = require('cors');
const bodyParser = require('body-parser');

const app = express();

// 中間件
app.use(cors());
app.use(bodyParser.json({ limit: '50mb' }));
app.use(bodyParser.urlencoded({ limit: '50mb', extended: true }));

// 資料庫配置
const dbConfig = {
    host: 'localhost',
    port: 3306,
    user: 'root',
    password: 'eva100422',
    database: 'eco_db',
    waitForConnections: true,
    connectionLimit: 10,
    queueLimit: 0
};

// 創建連接池
const pool = mysql.createPool(dbConfig);

// 測試資料庫連接
pool.getConnection()
    .then(connection => {
        console.log('✅ 資料庫連接成功');
        connection.release();
    })
    .catch(err => {
        console.error('❌ 資料庫連接失敗:', err);
    });

// ============= API 端點 =============

// 1. 提交回收審核
app.post('/api/recycle/submit', async (req, res) => {
    const connection = await pool.getConnection();
    
    try {
        const {
            memberId,
            memberName,
            itemType,
            itemId,
            quantity,
            estimatedPoints,
            confidence,
            imageData,
            aiDetails,
            submitTime
        } = req.body;

        // 驗證必填欄位
        if (!memberId || !memberName || !itemType || !quantity) {
            return res.status(400).json({
                success: false,
                message: '缺少必填欄位'
            });
        }

        // 生成唯一 ID
        const now = new Date();
        const recycleId = `REC${now.getFullYear()}${String(now.getMonth() + 1).padStart(2, '0')}${String(now.getDate()).padStart(2, '0')}${String(now.getHours()).padStart(2, '0')}${String(now.getMinutes()).padStart(2, '0')}${String(now.getSeconds()).padStart(2, '0')}${String(now.getMilliseconds()).padStart(3, '0')}`;

        // 插入審核記錄
        const insertQuery = `
            INSERT INTO recycle_reviews 
            (review_id, member_id, member_name, item_type, item_id, quantity, 
             estimated_points, confidence, image_data, ai_details, 
             submit_time, status, review_time, reviewer, reject_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', NULL, NULL, NULL)
        `;

        await connection.execute(insertQuery, [
            recycleId,
            memberId,
            memberName,
            itemType,
            itemId,
            quantity,
            estimatedPoints,
            confidence,
            imageData,
            aiDetails ? JSON.stringify(aiDetails) : null,
            submitTime
        ]);

        await connection.commit();

        res.json({
            success: true,
            reviewId: recycleId,
            message: '提交成功,等待審核'
        });

    } catch (error) {
        await connection.rollback();
        console.error('提交失敗:', error);
        res.status(500).json({
            success: false,
            message: '提交失敗: ' + error.message
        });
    } finally {
        connection.release();
    }
});

// 2. 獲取待審核列表
app.get('/api/recycle/pending', async (req, res) => {
    try {
        const [rows] = await pool.execute(
            'SELECT * FROM recycle_reviews WHERE status = ? ORDER BY submit_time DESC',
            ['pending']
        );

        res.json({
            success: true,
            data: rows
        });

    } catch (error) {
        console.error('獲取列表失敗:', error);
        res.status(500).json({
            success: false,
            message: '獲取列表失敗: ' + error.message
        });
    }
});

// 3. 核准審核
app.post('/api/recycle/approve/:reviewId', async (req, res) => {
    const connection = await pool.getConnection();
    
    try {
        await connection.beginTransaction();
        
        const { reviewId } = req.params;
        const { reviewer } = req.body;

        // 獲取審核記錄
        const [reviews] = await connection.execute(
            'SELECT * FROM recycle_reviews WHERE review_id = ?',
            [reviewId]
        );

        if (reviews.length === 0) {
            await connection.rollback();
            return res.status(404).json({
                success: false,
                message: '找不到記錄'
            });
        }

        const review = reviews[0];

        // 更新審核狀態
        await connection.execute(
            `UPDATE recycle_reviews 
             SET status = 'approved', 
                 review_time = NOW(), 
                 reviewer = ? 
             WHERE review_id = ?`,
            [reviewer || '管理員', reviewId]
        );

        // 增加會員積分
        await connection.execute(
            'UPDATE users SET points = points + ? WHERE id = ?',
            [review.estimated_points, review.member_id]
        );

        // 記錄積分變動
        await connection.execute(
            `INSERT INTO point_history 
             (user_id, points_change, reason, created_at) 
             VALUES (?, ?, ?, NOW())`,
            [review.member_id, review.estimated_points, `回收${review.item_type} x${review.quantity}`]
        );

        await connection.commit();

        res.json({
            success: true,
            message: '審核通過,積分已發放'
        });

    } catch (error) {
        await connection.rollback();
        console.error('核准失敗:', error);
        res.status(500).json({
            success: false,
            message: '核准失敗: ' + error.message
        });
    } finally {
        connection.release();
    }
});

// 4. 拒絕審核
app.post('/api/recycle/reject/:reviewId', async (req, res) => {
    try {
        const { reviewId } = req.params;
        const { reviewer, reason } = req.body;

        const [result] = await pool.execute(
            `UPDATE recycle_reviews 
             SET status = 'rejected', 
                 review_time = NOW(), 
                 reviewer = ?,
                 reject_reason = ?
             WHERE review_id = ?`,
            [reviewer || '管理員', reason || '不符合回收標準', reviewId]
        );

        if (result.affectedRows === 0) {
            return res.status(404).json({
                success: false,
                message: '找不到記錄'
            });
        }

        res.json({
            success: true,
            message: '已拒絕審核'
        });

    } catch (error) {
        console.error('拒絕失敗:', error);
        res.status(500).json({
            success: false,
            message: '拒絕失敗: ' + error.message
        });
    }
});

// 5. 獲取用戶資訊
app.get('/api/users', async (req, res) => {
    try {
        const { username } = req.query;

        if (!username) {
            return res.status(400).json({
                success: false,
                message: '請提供用戶名'
            });
        }

        const [users] = await pool.execute(
            'SELECT id, username, email, phone, address, birthday, points FROM users WHERE username = ?',
            [username]
        );

        if (users.length === 0) {
            return res.status(404).json({
                success: false,
                message: '找不到用戶'
            });
        }

        res.json(users[0]);

    } catch (error) {
        console.error('獲取用戶失敗:', error);
        res.status(500).json({
            success: false,
            message: '獲取用戶失敗: ' + error.message
        });
    }
});

// 啟動伺服器
const PORT = 3000;
app.listen(PORT, () => {
    console.log(`🚀 伺服器運行在 http://localhost:${PORT}`);
});