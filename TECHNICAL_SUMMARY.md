# 🔧 Decision Assistant - 部署修改清单（第三方开发者必读）

> **目标：** 将项目部署到 Vercel (前端) + Render/Railway (后端)

---

## ⚠️ 重要提示：当前部署状态

### 当前 Vercel 部署的文件

```
❌ 当前部署（错误）：
decision-assistant/
└── index.html          ← 根目录的纯 HTML 版本（15KB）
```

**问题：**
- Vercel 当前部署的是根目录的 `index.html`（纯 HTML + JS，直接调用 DeepSeek API）
- **没有**部署 `frontend/` 目录下的 React 应用
- API Key 暴露在前端代码中（不安全）

### 正确的部署方式

```
✅ 正确部署（本文档指导）：
decision-assistant/
├── frontend/           ← 应该部署这个目录的 React 应用
│   ├── src/
│   ├── package.json
│   └── vercel.json
└── backend/            ← 部署到 Render/Railway
    ├── app/
    └── requirements.txt
```

**两个版本的对比：**

| 项目 | 根目录 `index.html` (当前) | `frontend/` React 应用 (推荐) |
|------|---------------------------|------------------------------|
| 技术栈 | 纯 HTML + JS | React + FastAPI |
| 安全性 | ❌ API Key 暴露在前端 | ✅ API Key 在后端 |
| 功能 | 基础聊天和分析 | 完整功能 + Chat Viewer |
| 架构 | 前端直接调用 DeepSeek | 前端 → 后端 → DeepSeek |
| 数据存储 | ❌ 仅 localStorage | ✅ 后端文件/数据库 |

**建议：** 重新配置 Vercel 部署 `frontend/` 目录

---

## ⚡ 快速索引

- [当前部署状态](#当前部署状态)
- [必须修改的文件](#必须修改的文件-3个)
- [重新配置 Vercel](#重新配置-vercel-部署)
- [部署步骤](#部署步骤)
- [环境变量配置](#环境变量配置)
- [测试验证](#测试验证)

---

## 🔄 重新配置 Vercel 部署

### 选项 1：在 Vercel 网站修改配置

1. 登录 Vercel 控制台
2. 选择你的项目
3. 进入 "Settings" → "General"
4. 修改：
   ```
   Root Directory: frontend         👈 关键：指向 frontend 目录
   Framework Preset: Create React App
   Build Command: npm run build
   Output Directory: build
   ```
5. 保存后重新部署

### 选项 2：删除当前部署，重新部署

```bash
# 1. 进入 frontend 目录
cd frontend

# 2. 使用 Vercel CLI 部署
vercel --prod
```

---

## 📋 必须修改的文件 (3个)

### ✏️ 1. `frontend/src/App.js` - 修改 API 地址

#### 📍 位置：第 49 行和第 78 行

#### ❌ 当前代码（需要修改）：
```javascript
// 第 49 行
const response = await fetch('http://localhost:8000/api/decisions/analyze', {

// 第 78 行
const response = await fetch('http://localhost:8000/api/decisions/chat', {
```

#### ✅ 修改为（两种方案任选一种）：

**方案 A：使用环境变量（推荐）**
```javascript
// 在文件顶部（第 5 行后）添加：
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 第 49 行修改为：
const response = await fetch(`${API_URL}/api/decisions/analyze`, {

// 第 78 行修改为：
const response = await fetch(`${API_URL}/api/decisions/chat`, {
```

**方案 B：直接硬编码（不推荐，但更简单）**
```javascript
// 第 49 行修改为：
const response = await fetch('https://your-backend.onrender.com/api/decisions/analyze', {

// 第 78 行修改为：
const response = await fetch('https://your-backend.onrender.com/api/decisions/chat', {
```

⚠️ **注意：** 将 `your-backend.onrender.com` 替换为实际的后端 URL

---

### ✏️ 2. `backend/app/main.py` - 添加 Vercel 域名到 CORS

#### 📍 位置：第 9-17 行

#### ❌ 当前代码：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 本地开发
        "https://decision-assistant-6a9f3h29e-bruces-projects-409b2d51.vercel.app",  # Vercel 生产环境
        "https://*.vercel.app",  # 其他 Vercel 预览部署
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

#### ✅ 修改为（添加你的 Vercel 域名）：
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 本地开发
        "https://your-app.vercel.app",  # 👈 替换为你的 Vercel 域名
        "https://*.vercel.app",  # 允许所有 Vercel 预览部署
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

⚠️ **注意：** 部署前端到 Vercel 后，将 `your-app.vercel.app` 替换为实际域名

---

### ✏️ 3. `backend/app/services/ai_service.py` - 配置 DeepSeek API Key

#### 📍 位置：第 12 行

#### ❌ 当前代码（硬编码的 API Key）：
```python
self.api_key = os.getenv("DEEPSEEK_API_KEY", "sk-d3196d8e68c44690998d79c715ce715d")
```

#### ✅ 修改为（使用环境变量）：
```python
self.api_key = os.getenv("DEEPSEEK_API_KEY")  # 👈 移除默认值
```

⚠️ **重要：** 必须在部署平台（Render/Railway）设置环境变量 `DEEPSEEK_API_KEY`

---

## 🚀 部署步骤

### 第一步：部署后端到 Render.com

1. **注册 Render：** https://render.com
2. **创建 Web Service：** 
   - 连接 GitHub 仓库
   - 选择 `decision-assistant` 项目
3. **配置参数：**
   ```
   Name: decision-assistant-backend
   Region: Oregon (或离你最近的)
   Branch: main
   
   Root Directory: backend          👈 重要！
   Runtime: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   
   Instance Type: Free
   ```

4. **设置环境变量：**
   ```
   DEEPSEEK_API_KEY=你的DeepSeek密钥
   PORT=8000
   ```

5. **等待部署完成（3-5分钟）**
6. **复制后端 URL：** 例如 `https://decision-assistant-backend.onrender.com`

---

### 第二步：部署前端到 Vercel

#### 方法 A：使用 Vercel CLI（推荐）

```bash
# 1. 安装 Vercel CLI
npm install -g vercel

# 2. 进入前端目录
cd frontend

# 3. 登录 Vercel
vercel login

# 4. 部署（会自动检测 React 项目）
vercel --prod
```

#### 方法 B：使用 Vercel 网站

1. 访问 https://vercel.com
2. 点击 "Import Project"
3. 选择 GitHub 仓库
4. 配置：
   ```
   Framework Preset: Create React App
   Root Directory: frontend         👈 重要！
   Build Command: npm run build
   Output Directory: build
```

---

### 第三步：配置环境变量连接前后端

#### 在 Vercel 添加环境变量

1. 进入 Vercel 项目控制台
2. 点击 "Settings" → "Environment Variables"
3. 添加：
   ```
   Name: REACT_APP_API_URL
   Value: https://decision-assistant-backend.onrender.com  👈 替换为你的后端 URL
   Environments: Production, Preview, Development (全选)
   ```
4. 保存后点击 "Redeploy" 重新部署

---

### 第四步：更新 CORS 配置

1. 复制 Vercel 前端 URL（例如：`https://your-app.vercel.app`）
2. 修改 `backend/app/main.py` 第 12 行，添加这个域名
3. 推送代码到 GitHub
4. Render 会自动重新部署后端

---

## 🔑 环境变量配置清单

### 后端 (Render.com)
```bash
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx  # 必须设置
PORT=8000                                   # 自动设置（可选）
```

### 前端 (Vercel)
```bash
REACT_APP_API_URL=https://your-backend.onrender.com  # 必须设置
```

---

## ✅ 测试验证

### 1. 测试后端

```bash
# 健康检查
curl https://your-backend.onrender.com/health

# 预期返回：
{"status":"healthy","service":"backend","ai":"DeepSeek"}
```

### 2. 测试前端

1. 访问 Vercel URL：`https://your-app.vercel.app`
2. 打开浏览器开发者工具（F12）
3. 检查：
   - ✅ Console 无 CORS 错误
   - ✅ Network 标签显示 API 请求成功（200）
   - ✅ 可以正常发送消息和查看分析

### 3. 测试完整功能

- [ ] Decision Analysis 可以分析决策
- [ ] Chat Mode 可以对话
- [ ] Chat Viewer 可以查看聊天记录

---

## 🐛 常见问题

### Q1: 前端显示 "CORS 错误"

**原因：** 后端 CORS 未允许前端域名

**解决：**
1. 检查 `backend/app/main.py` 的 `allow_origins` 列表
2. 确保包含你的 Vercel 域名
3. 推送代码，等待 Render 重新部署

---

### Q2: API 请求失败 "Could not connect to server"

**原因：** 环境变量未设置或后端未启动

**解决：**
1. 检查 Vercel 环境变量 `REACT_APP_API_URL` 是否正确
2. 访问后端 URL `/health` 确认后端运行正常
3. 如果 Render 休眠，等待 30-60 秒唤醒

---

### Q3: 后端部署失败

**原因：** 配置错误

**解决：**
1. 确认 Root Directory 设置为 `backend`
2. 确认 `backend/requirements.txt` 存在
3. 查看 Render 日志找到具体错误

---

### Q4: DeepSeek API 不工作

**原因：** API Key 未设置或无效

**解决：**
1. 检查 Render 环境变量 `DEEPSEEK_API_KEY`
2. 确认 API Key 有效且有余额
3. 查看后端日志确认 API 调用情况

---

## 📁 文件修改总结

| 文件 | 位置 | 修改内容 | 是否必须 |
|------|------|----------|----------|
| `frontend/src/App.js` | 第 5 行（新增）<br>第 49 行<br>第 78 行 | 添加 API_URL 变量<br>使用环境变量 | ✅ 必须 |
| `backend/app/main.py` | 第 12 行 | 添加 Vercel 域名到 CORS | ✅ 必须 |
| `backend/app/services/ai_service.py` | 第 12 行 | 移除硬编码 API Key | ✅ 必须 |

---

## 🎯 部署检查清单

完成后，确认以下事项：

- [ ] 后端已部署到 Render，URL 可访问
- [ ] 前端已部署到 Vercel，页面可打开
- [ ] Render 环境变量 `DEEPSEEK_API_KEY` 已设置
- [ ] Vercel 环境变量 `REACT_APP_API_URL` 已设置
- [ ] `backend/app/main.py` CORS 包含 Vercel 域名
- [ ] `frontend/src/App.js` 使用环境变量获取 API URL
- [ ] 健康检查 API 返回正常
- [ ] 前端可以正常调用后端 API
- [ ] 无 CORS 错误

---

## 📚 相关文档

- `VERCEL_DEPLOYMENT_GUIDE.md` - 详细部署指南
- `部署到生产环境.md` - 生产环境配置
- `快速启动指南.md` - 本地开发指南

---

## 💡 提示

### 本地开发（无需修改）
```bash
# 终端 1：启动后端
cd backend
uvicorn app.main:app --reload

# 终端 2：启动前端
cd frontend
npm start
```

### 生产部署（需要修改上述 3 个文件）
- 前端：Vercel
- 后端：Render/Railway

---

**文档版本：** 2.0  
**更新日期：** 2025-10-13  
**适用人员：** 第三方开发者

---

**🚀 祝部署顺利！有问题请参考 `VERCEL_DEPLOYMENT_GUIDE.md` 或在 Issues 提问。**

