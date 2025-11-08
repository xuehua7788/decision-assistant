# 如何获取 DATABASE_URL

## 步骤1：登录 Render Dashboard

访问：https://dashboard.render.com

## 步骤2：找到数据库

1. 在左侧菜单找到 "PostgreSQL" 或 "Databases"
2. 点击你的数据库（通常名字包含 decision-assistant）

## 步骤3：复制连接URL

在数据库详情页面：

### 找到 "Connections" 部分

你会看到两个URL：

#### Internal Database URL（内部URL）
```
postgresql://user:pass@dpg-xxx-a/dbname
```
**用途**：Render服务之间通信（免费，更快）

#### External Database URL（外部URL）
```
postgresql://user:pass@dpg-xxx-a.oregon-postgres.render.com/dbname
```
**用途**：从本地电脑连接（推荐用这个）

### 复制 External Database URL

点击 External URL 旁边的 📋 复制按钮

## 步骤4：使用URL

复制后的URL格式类似：
```
postgresql://decision_assistant_db_user:xxxxxxxxxxx@dpg-xxxxxxxxxxxx.oregon-postgres.render.com/decision_assistant_db
```

**不要分享这个URL！** 它包含数据库密码。


