# Render 后端部署指南

## ✅ 前端已部署成功
- **Vercel URL**: https://decision-assistant-kxqqlg6uc-bruces-projects-409b2d51.vercel.app
- **状态**: ✅ 部署成功

---

## 🔧 后端部署步骤（Render）

### 1. 登录 Render
访问: https://dashboard.render.com

### 2. 创建新的 Web Service（如果还没有）
- 点击 "New +" → "Web Service"
- 连接 GitHub 仓库: `xuehua7788/decision-assistant`
- 选择仓库后点击 "Connect"

### 3. 配置 Web Service

#### 基本设置
- **Name**: `decision-assistant-api`
- **Region**: 选择离您最近的区域（如 Singapore）
- **Branch**: `main`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`

#### 构建和部署设置
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python app.py`

#### 环境变量（Environment Variables）
点击 "Advanced" → "Add Environment Variable"，添加以下变量：

```
OPENAI_API_KEY=your-openai-api-key-here
PORT=8000
FLASK_ENV=production
```

⚠️ **重要**: 将 `your-openai-api-key-here` 替换为您的实际 OpenAI API 密钥

#### 实例类型
- **Instance Type**: `Free` （免费套餐）

### 4. 部署
1. 点击 "Create Web Service"
2. 等待部署完成（通常需要 3-5 分钟）
3. 部署成功后，您会看到类似这样的 URL:
   ```
   https://decision-assistant-api.onrender.com
   ```

### 5. 验证部署
部署完成后，访问以下 URL 测试：

- **健康检查**: https://decision-assistant-api.onrender.com/health
  - 预期响应: `{"status": "healthy"}`

- **API 状态**: https://decision-assistant-api.onrender.com/
  - 预期响应: `{"status": "API is running", "version": "1.0"}`

---

## 🔄 重新部署（如果已存在服务）

如果您已经创建了 Render Web Service：

1. 登录 Render Dashboard
2. 找到 `decision-assistant-api` 服务
3. 点击 "Manual Deploy" → "Deploy latest commit"
4. 等待部署完成

---

## 📝 文件清单

确保以下文件在 `backend/` 目录中：

✅ `requirements.txt` - Python 依赖
```
Flask==2.3.3
Flask-CORS==4.0.0
python-dotenv==1.0.0
openai==1.3.0
gunicorn==21.2.0
Werkzeug==2.3.7
```

✅ `app.py` - Flask 应用主文件
- 包含 CORS 配置
- 健康检查端点 `/health`
- API 端点 `/api/decision`

---

## 🎯 完成后测试

### 测试后端
```bash
# 健康检查
curl https://decision-assistant-api.onrender.com/health

# API 状态
curl https://decision-assistant-api.onrender.com/
```

### 测试前端
1. 访问: https://decision-assistant-kxqqlg6uc-bruces-projects-409b2d51.vercel.app
2. 确认前端能够成功调用后端 API

---

## ⚠️ 常见问题

### 问题1: 部署失败 "Exited with status 128"
**解决**: 检查 `requirements.txt` 是否存在且格式正确

### 问题2: API 返回 500 错误
**解决**: 检查 Render 日志，确认 `OPENAI_API_KEY` 环境变量已设置

### 问题3: CORS 错误
**解决**: 确认 `backend/app.py` 中的 CORS 配置包含您的 Vercel 域名

---

## 📞 支持

如果遇到问题：
1. 查看 Render Logs: Dashboard → Service → Logs
2. 检查环境变量是否正确设置
3. 确认 GitHub 仓库代码已更新

---

**最后更新**: 2025-10-15

