# 🔄 数据库迁移指南

## 问题
本地网络连接到 Render 新加坡数据库太慢，Python脚本一直卡住。

## 解决方案
直接在 Render Dashboard 中执行SQL命令

---

## 📝 操作步骤

### 1️⃣ 打开 Render Dashboard
1. 访问：https://dashboard.render.com
2. 登录你的账号
3. 找到数据库：`decision_assistant_098l`
4. 点击进入数据库详情页

### 2️⃣ 打开 SQL Shell
1. 在数据库页面，找到 **"Shell"** 或 **"Connect"** 按钮
2. 选择 **"Connect Externally"** 下的 **"PSQL Command"**
3. 或者点击 **"Shell"** 标签页，会打开一个在线终端

### 3️⃣ 执行迁移SQL

**方法A：逐条执行（推荐）**

```sql
-- 1. 添加字段
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS accepted_strategies JSONB DEFAULT '[]'::jsonb;

-- 2. 迁移 bbb 的策略
UPDATE users 
SET accepted_strategies = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'strategy_id', strategy_id,
            'symbol', symbol,
            'company_name', company_name,
            'investment_style', investment_style,
            'recommendation', recommendation,
            'target_price', target_price,
            'stop_loss', stop_loss,
            'position_size', position_size,
            'score', score,
            'strategy_text', strategy_text,
            'analysis_summary', analysis_summary,
            'current_price', current_price,
            'option_strategy', option_strategy,
            'created_at', created_at,
            'status', status
        )
    )
    FROM accepted_strategies
    WHERE accepted_strategies.username = users.username
)
WHERE username = 'bbb';

-- 3. 验证结果
SELECT 
    username,
    jsonb_array_length(accepted_strategies) as strategy_count
FROM users
WHERE username = 'bbb';
```

**应该看到：`bbb | 9`**

```sql
-- 4. 确认无误后，删除旧表
DROP TABLE accepted_strategies CASCADE;
```

---

## ✅ 验证迁移成功

执行以下SQL确认：

```sql
-- 查看 bbb 的策略数量
SELECT 
    username, 
    jsonb_array_length(accepted_strategies) as count,
    accepted_strategies->0->>'symbol' as first_symbol
FROM users 
WHERE username = 'bbb';
```

**期望结果：**
- `count`: 9
- `first_symbol`: AAPL 或 NVDA 等

---

## 🔧 后续步骤

迁移完成后，需要修改后端API：

### 修改文件列表
1. ✅ `backend/app.py` - 修改保存策略的逻辑
2. ✅ `backend/strategy_storage_api.py` - 删除或重写
3. ✅ `frontend/src/StockAnalysis.js` - 修改保存API地址
4. ✅ `frontend/src/StrategyEvaluation.js` - 修改读取API地址

---

## 📌 新的API设计

### 保存策略
```
POST /api/user/save-strategy
Body: {
    "username": "bbb",
    "strategy": { ... }
}
```

### 获取用户策略
```
GET /api/user/bbb/strategies
Response: {
    "username": "bbb",
    "strategies": [ ... ]
}
```

---

## ⚠️ 注意事项

1. **先验证，后删除** - 确认数据迁移成功后再执行 DROP TABLE
2. **备份** - Render数据库会自动备份，但建议手动导出一次
3. **测试** - 删除表后，立即测试前端是否还能正常工作

---

**你现在需要做的：**
1. 打开 Render Dashboard
2. 进入数据库 Shell
3. 复制粘贴上面的SQL命令
4. 执行并验证结果
5. 告诉我结果，我会继续修改后端和前端代码


