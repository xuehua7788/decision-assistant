# 📋 数据库查询指南

## 问题
- bbb 用户在哪里？
- 如何查看数据库中的用户？

## 解决方案（3种方法）

---

## 方法1：告诉我 DATABASE_URL（最快）

### 步骤：
1. 登录 https://dashboard.render.com
2. 找到 PostgreSQL 数据库
3. 复制 "External Database URL"
4. **发给我**，格式类似：
   ```
   postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname
   ```

### 我会帮你：
- ✅ 查询所有用户
- ✅ 查看 bbb 是否存在
- ✅ 查看 bbb 的策略
- ✅ 运行数据库迁移

---

## 方法2：在 Render Shell 运行（推荐）

### 步骤：
1. 登录 https://dashboard.render.com
2. 进入你的 **backend 服务**（不是数据库）
3. 点击右上角 **"Shell"** 按钮
4. 在 Shell 中运行：

```bash
# 查看所有用户
python list_registered_users.py

# 或者查看策略
python query_strategies_simple.py
```

### 优点：
- ✅ 不需要手动输入 DATABASE_URL
- ✅ Render 会自动提供环境变量
- ✅ 安全（不会泄露密码）

---

## 方法3：本地查询（需要手动输入）

### 步骤：
1. 获取 DATABASE_URL（见方法1）
2. 在命令行设置环境变量：

**Windows PowerShell:**
```powershell
$env:DATABASE_URL="postgresql://user:pass@host/db"
python query_users_db.py
```

**Windows CMD:**
```cmd
set DATABASE_URL=postgresql://user:pass@host/db
python query_users_db.py
```

**Linux/Mac:**
```bash
export DATABASE_URL="postgresql://user:pass@host/db"
python query_users_db.py
```

---

## 💡 我的建议

**最简单的方式：**

**直接告诉我你的 DATABASE_URL**，我会：
1. 立即查询 bbb 用户
2. 显示所有用户列表
3. 检查策略关联情况
4. 运行数据库迁移（如果需要）

**或者**，你可以：
- 在 Render Shell 里自己运行
- 在 Render Dashboard 直接查看数据库

---

## 🔐 安全提示

如果不想分享 DATABASE_URL，可以：
1. 使用 Render Shell（推荐）
2. 查询后只告诉我结果
3. 等我提供其他方案

---

**你想用哪种方法？** 🤔


