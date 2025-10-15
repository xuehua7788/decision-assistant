# Render 快速设置指南

## 🚀 后端已准备好部署！

**GitHub 仓库**: https://github.com/xuehua7788/decision-assistant  
**最新提交**: aa53427 - Configure backend for Render deployment

---

## 📋 快速设置步骤（5分钟）

### 1️⃣ 打开 Render Dashboard
访问: https://dashboard.render.com/new/web

### 2️⃣ 连接 GitHub
- 点击 "Connect GitHub account"（如果还没连接）
- 授权 Render 访问你的仓库

### 3️⃣ 选择仓库
- 搜索: `decision-assistant`
- 选择: `xuehua7788/decision-assistant`
- 点击 "Connect"

### 4️⃣ 配置服务

#### 基本设置
```
Name: decision-assistant-api
Region: Oregon (US West)
Branch: main
Root Directory: backend
```

#### 运行环境
```
Environment: Python 3
```

#### 构建设置
```
Build Command: pip install -r requirements.txt
Start Command: gunicorn app:app
```

### 5️⃣ 环境变量
点击 **"Advanced"** 展开，添加以下环境变量：

| Key | Value |
|-----|-------|
| `OPENAI_API_KEY` | `sk-your-actual-openai-key` ⚠️ 必填 |
| `PORT` | `8000` |
| `FLASK_ENV` | `production` |
| `PYTHON_VERSION` | `3.9.0` |

⚠️ **重要**: 将 `sk-your-actual-openai-key` 替换为你的实际 OpenAI API 密钥

### 6️⃣ 选择计划
- 选择 **Free** 计划
- 点击 **"Create Web Service"**

### 7️⃣ 等待部署
- 部署通常需要 **3-5 分钟**
- 观察日志确保没有错误
- 等待状态变为 **"Live"** 🟢

---

## ✅ 验证部署

部署完成后，运行测试脚本：

```powershell
powershell -ExecutionPolicy Bypass -File test-render-api.ps1
```

或者手动访问：
- **健康检查**: https://decision-assistant-api.onrender.com/health
- **API 状态**: https://decision-assistant-api.onrender.com/

预期响应：
```json
{
  "status": "healthy"
}
```

---

## 🔗 完整 URL 列表

| 服务 | URL |
|------|-----|
| **前端** | https://decision-assistant-kxqqlg6uc-bruces-projects-409b2d51.vercel.app |
| **后端** | https://decision-assistant-api.onrender.com |
| **Render Dashboard** | https://dashboard.render.com |
| **Vercel Dashboard** | https://vercel.com/dashboard |

---

## 📁 已准备的文件

✅ `backend/app.py` - Flask 应用  
✅ `backend/requirements.txt` - Python 依赖  
✅ `backend/render.yaml` - Render 配置  
✅ `backend/build.sh` - 构建脚本  
✅ `backend/.env.example` - 环境变量示例  

---

## ⚠️ 常见问题

### 问题1: 部署失败 "Build failed"
**解决**: 检查 `requirements.txt` 是否正确

### 问题2: "Exited with status 3"
**解决**: 确认 `Start Command` 为 `gunicorn app:app`

### 问题3: API 返回 500 错误
**解决**: 检查 `OPENAI_API_KEY` 环境变量是否设置

### 问题4: CORS 错误
**解决**: 已配置允许所有来源，应该不会有问题

---

## 📞 需要帮助？

1. 查看 Render 日志: Dashboard → Service → Logs
2. 检查环境变量是否正确设置
3. 确认 GitHub 代码已更新（commit: aa53427）

---

**准备就绪！现在去 Render 创建服务吧！** 🚀

