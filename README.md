# 🤖 Decision Assistant

一个基于 React + FastAPI 的 AI 决策辅助系统，集成 DeepSeek AI。

---

## ⚠️ 重要：部署前必读

### 项目结构

```
decision-assistant/
├── frontend/              ← React 应用（部署到 Vercel）
│   ├── src/
│   ├── package.json
│   └── vercel.json
├── backend/               ← FastAPI 后端（部署到 Render/Railway）
│   ├── app/
│   └── requirements.txt
├── index.html            ← ⚠️ 旧版纯 HTML（请勿部署此文件）
└── README.md             ← 本文件
```

### 当前 Vercel 部署问题

❌ **错误：** Vercel 当前部署的是根目录的 `index.html`（纯 HTML 版本）

✅ **正确：** 应该部署 `frontend/` 目录（React 应用）

---

## 🚀 快速修复

### 第一步：修复 Vercel 部署

详细步骤请查看：**[VERCEL_FIX_GUIDE.md](VERCEL_FIX_GUIDE.md)**

**快速操作：**

1. 登录 Vercel 控制台
2. Settings → General → Root Directory
3. 修改为：`frontend`
4. 保存并重新部署

### 第二步：完整部署

详细步骤请查看：**[TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)**

**需要修改的文件（仅 3 个）：**

1. `frontend/src/App.js` - API 地址
2. `backend/app/main.py` - CORS 配置
3. `backend/app/services/ai_service.py` - API Key

---

## 📚 文档指南

| 文档 | 用途 | 适合人群 |
|------|------|----------|
| **[重新部署指南.md](重新部署指南.md)** | 🔥 完整部署教程（前端+后端） | 所有人（推荐！） |
| **[TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)** | 部署修改清单（哪个文件改什么） | 第三方开发者 |
| **[VERCEL_FIX_GUIDE.md](VERCEL_FIX_GUIDE.md)** | 修复 Vercel 部署问题 | 遇到问题时看 |
| **[VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)** | 详细部署步骤指南 | 初学者 |
| **[快速启动指南.md](快速启动指南.md)** | 本地开发环境搭建 | 开发者 |

---

## 🏃 本地开发

```bash
# 终端 1：启动后端
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 终端 2：启动前端
cd frontend
npm install
npm start
```

访问：http://localhost:3000

---

## 🌐 生产部署

### 前端（Vercel）

```bash
cd frontend
vercel --prod
```

### 后端（Render.com）

1. 访问 https://render.com
2. 连接 GitHub 仓库
3. 配置：
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

---

## 🔑 环境变量

### Vercel（前端）
```bash
REACT_APP_API_URL=https://your-backend.onrender.com
```

### Render（后端）
```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxx
PORT=8000
```

---

## ✅ 功能特性

- 📊 **Decision Analysis** - AI 决策分析
- 💬 **Chat Mode** - 对话咨询
- 📝 **Chat Viewer** - 聊天记录查看
- 🤖 **DeepSeek AI** - 智能 AI 支持
- 💾 **数据持久化** - 聊天记录保存

---

## 🛠️ 技术栈

**前端：**
- React 17
- Create React App
- Vercel 部署

**后端：**
- FastAPI
- Python 3.10+
- DeepSeek API
- Render/Railway 部署

---

## 📞 获取帮助

1. **部署问题：** 查看 [VERCEL_FIX_GUIDE.md](VERCEL_FIX_GUIDE.md)
2. **修改代码：** 查看 [TECHNICAL_SUMMARY.md](TECHNICAL_SUMMARY.md)
3. **详细步骤：** 查看 [VERCEL_DEPLOYMENT_GUIDE.md](VERCEL_DEPLOYMENT_GUIDE.md)

---

## ⚡ 部署检查清单

- [ ] ✅ Vercel Root Directory 设置为 `frontend`
- [ ] ✅ 后端部署到 Render/Railway
- [ ] ✅ Vercel 环境变量 `REACT_APP_API_URL` 已设置
- [ ] ✅ Render 环境变量 `DEEPSEEK_API_KEY` 已设置
- [ ] ✅ `backend/app/main.py` CORS 包含 Vercel 域名
- [ ] ✅ `frontend/src/App.js` 使用环境变量
- [ ] ✅ 测试通过：前端可访问，API 调用正常

---

**版本：** 2.0  
**更新：** 2025-10-13

**🚀 祝部署顺利！**

