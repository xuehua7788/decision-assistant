# Vercel 部署指南 - 给第三方开发者

## 📌 重要说明

本项目是一个 **前后端分离** 的应用，由于架构限制，**无法完全部署到 Vercel**。

### 架构组成
- **前端**: React 应用（可部署到 Vercel ✅）
- **后端**: FastAPI Python 服务（需部署到其他平台 ⚠️）

---

## 🚀 推荐部署方案

### 方案 A：Vercel (前端) + Render (后端) - 全免费 ⭐ 推荐

| 组件 | 平台 | 成本 | 部署难度 |
|------|------|------|----------|
| 前端 | Vercel | 免费 | ⭐ 简单 |
| 后端 | Render.com | 免费 | ⭐⭐ 中等 |

**优点:**
- 完全免费
- 自动 HTTPS
- 支持文件持久化
- 全球 CDN

**缺点:**
- Render 免费版 15 分钟无活动会休眠
- 首次访问需要 30-60 秒唤醒

---

## 📝 部署步骤

### 第一步：部署前端到 Vercel

#### 1.1 准备工作

确保你的项目中有以下文件：

```bash
frontend/
├── package.json          # ✅ 已存在
├── vercel.json          # ✅ 已配置
└── src/
    └── App.js           # ✅ 已存在
```

#### 1.2 使用 Vercel CLI 部署

```bash
# 安装 Vercel CLI
npm install -g vercel

# 进入前端目录
cd frontend

# 登录 Vercel
vercel login

# 部署到生产环境
vercel --prod
```

#### 1.3 或者使用 GitHub 集成（推荐）

1. 将代码推送到 GitHub
2. 访问 [vercel.com](https://vercel.com)
3. 点击 "Import Project"
4. 选择你的 GitHub 仓库
5. 配置项目：
   - **Framework Preset**: Create React App
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `build`

#### 1.4 配置环境变量（稍后设置）

等后端部署完成后，需要在 Vercel 添加：

```
REACT_APP_API_URL=https://your-backend-url.onrender.com
```

---

### 第二步：部署后端到 Render.com

#### 2.1 注册 Render

1. 访问 [render.com](https://render.com)
2. 使用 GitHub 账号注册
3. 授权访问你的仓库

#### 2.2 创建 Web Service

1. 点击 "New +" → "Web Service"
2. 连接你的 GitHub 仓库
3. 配置如下：

```
Name: decision-assistant-backend
Region: Oregon (或选择离用户最近的)
Branch: main

Root Directory: backend
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT

Instance Type: Free
```

4. 点击 "Create Web Service"

#### 2.3 环境变量配置

在 Render 的 Environment 设置中添加：

```
DEEPSEEK_API_KEY=你的DeepSeek API密钥
PORT=8000
```

#### 2.4 等待部署

- 部署时间约 3-5 分钟
- 部署成功后会显示 URL，例如：
  ```
  https://decision-assistant-backend.onrender.com
  ```

**📋 复制这个 URL，下一步要用！**

---

### 第三步：连接前端和后端

#### 3.1 在 Vercel 添加环境变量

1. 登录 Vercel 控制台
2. 选择你的项目
3. 进入 "Settings" → "Environment Variables"
4. 添加：

```
Name: REACT_APP_API_URL
Value: https://decision-assistant-backend.onrender.com  (替换为你的实际 URL)
Environments: Production, Preview, Development (全选)
```

5. 保存后重新部署前端

#### 3.2 更新后端 CORS 配置

确保 `backend/app/main.py` 中的 CORS 包含你的 Vercel 域名：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # 替换为你的 Vercel 域名
        "https://*.vercel.app",  # 允许所有 Vercel 预览部署
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

修改后推送代码，Render 会自动重新部署。

---

## ✅ 测试部署

### 测试后端

```bash
# 健康检查
curl https://your-backend-url.onrender.com/health

# 预期返回:
{"status":"healthy","service":"backend","ai":"DeepSeek"}
```

### 测试前端

1. 访问你的 Vercel URL
2. 打开浏览器开发者工具 (F12)
3. 检查 Console 标签：不应该有 CORS 错误
4. 检查 Network 标签：API 请求应该返回 200

### 测试完整功能

1. **Decision Analysis**: 输入决策问题，测试 AI 分析
2. **Chat Mode**: 发送消息，测试对话功能
3. **Chat Viewer**: 查看聊天记录（需先创建一些对话）

---

## 🔧 替代方案

### 方案 B：Vercel + Railway

如果 Render 不适合，可以使用 Railway：

1. 访问 [railway.app](https://railway.app)
2. 创建新项目，选择从 GitHub 部署
3. 配置：
   ```
   Root Directory: backend
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
4. 费用：约 $5/月，但性能更稳定

### 方案 C：Vercel + Fly.io

```bash
# 安装 Fly CLI
curl -L https://fly.io/install.sh | sh

# 进入后端目录
cd backend

# 初始化并部署
fly launch
fly deploy
```

---

## ⚠️ 重要限制和注意事项

### Vercel Serverless Functions 的限制

有些开发者可能会尝试将 FastAPI 作为 Vercel Function 部署，但存在以下限制：

❌ **不推荐的原因：**
1. Vercel Functions 主要为 Node.js 优化
2. Python runtime 有严格的时间限制（10-60 秒）
3. **无法持久化文件存储**（chat_data 会丢失）
4. 冷启动时间长

### Render 免费版限制

⚠️ **需要注意：**
- 15 分钟无活动会自动休眠
- 首次访问需要 30-60 秒唤醒
- 数据可能在重启时丢失（需配置持久化存储）

### 推荐的生产环境配置

对于正式生产环境，建议：

1. **后端**: 升级到 Render 付费版 ($7/月) 或使用 Railway
2. **数据存储**: 使用 PostgreSQL 数据库存储聊天记录
3. **文件存储**: 使用 AWS S3 或阿里云 OSS
4. **监控**: 配置 Sentry 或其他错误追踪服务

---

## 📊 成本对比

| 方案 | 月成本 | 性能 | 稳定性 | 适用场景 |
|------|--------|------|--------|----------|
| Vercel + Render 免费版 | $0 | ⭐⭐⭐ | ⭐⭐⭐ | 个人项目、测试 |
| Vercel + Render 付费版 | $7 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 小型生产环境 |
| Vercel + Railway | $5-10 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 中小型生产环境 |
| Vercel + AWS/云服务器 | $20+ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 企业级应用 |

---

## 🐛 常见问题

### Q1: 前端显示"网络错误"

**原因**: 
- 后端未部署或已休眠
- CORS 配置错误
- 环境变量未设置

**解决**:
1. 检查后端 URL 是否可访问
2. 确认 Vercel 环境变量正确
3. 检查浏览器 Console 的具体错误信息

### Q2: Render 部署失败

**常见原因**:
- `requirements.txt` 路径错误
- Root Directory 设置错误
- Python 版本不兼容

**解决**:
1. 确认 Root Directory 设置为 `backend`
2. 检查 `backend/requirements.txt` 是否存在
3. 查看 Render 部署日志的具体错误

### Q3: 聊天记录无法保存

**原因**: Render 免费版重启会丢失文件

**解决方案**:
1. 使用 Render Disks（付费功能）
2. 改用数据库存储（PostgreSQL）
3. 使用外部对象存储（S3）

### Q4: API 响应很慢

**原因**: Render 免费版从休眠状态唤醒

**解决**:
- 等待 30-60 秒（首次访问）
- 使用定时 ping 保持活跃
- 升级到付费版

---

## 📋 部署检查清单

完成部署后，检查以下项目：

- [ ] 前端成功部署到 Vercel
  - [ ] 可以访问 Vercel URL
  - [ ] 页面正常显示
  
- [ ] 后端成功部署到 Render/Railway
  - [ ] 健康检查 API 返回正常
  - [ ] 日志无错误
  
- [ ] 环境变量配置完成
  - [ ] Vercel: `REACT_APP_API_URL` 已设置
  - [ ] Render: `DEEPSEEK_API_KEY` 已设置
  
- [ ] CORS 配置正确
  - [ ] 后端允许前端域名
  - [ ] 浏览器 Console 无 CORS 错误
  
- [ ] 功能测试通过
  - [ ] Decision Analysis 可用
  - [ ] Chat Mode 可以对话
  - [ ] Chat Viewer 可以查看记录

---

## 🔗 有用的资源

### 官方文档
- [Vercel 部署文档](https://vercel.com/docs)
- [Render 部署指南](https://render.com/docs)
- [FastAPI 部署](https://fastapi.tiangolo.com/deployment/)
- [Railway 文档](https://docs.railway.app)

### 项目文档
- `TECHNICAL_SUMMARY.md` - 完整技术总结
- `部署到生产环境.md` - 详细部署步骤
- `快速启动指南.md` - 本地开发指南

### 社区支持
- [Vercel 社区](https://github.com/vercel/vercel/discussions)
- [Render 社区](https://community.render.com)

---

## 💡 给第三方开发者的建议

### 1. 理解架构限制
- **Vercel 不是万能的**：它主要为前端和 Serverless 优化
- 本项目的后端需要独立部署

### 2. 选择合适的方案
- **测试/演示**: 使用免费方案（Vercel + Render 免费版）
- **小型生产**: 使用付费方案，确保稳定性
- **企业级**: 考虑云服务器或容器化部署

### 3. 数据持久化
- 免费方案无法保证数据持久化
- 重要数据必须使用数据库或对象存储

### 4. 性能优化
- 使用 CDN 加速静态资源
- 配置合理的缓存策略
- 监控和优化 API 响应时间

### 5. 安全考虑
- 不要在前端暴露 API 密钥
- 使用环境变量管理敏感信息
- 配置合理的 CORS 策略

---

## 🎯 总结

**部署到 Vercel 的正确理解：**

✅ **可以做的：**
- 将前端 React 应用部署到 Vercel
- 享受免费的 CDN、HTTPS、自动部署

❌ **不能做的：**
- 将完整的 FastAPI 后端部署到 Vercel
- 依赖文件系统进行数据持久化

✨ **推荐做法：**
- 前端 → Vercel（免费）
- 后端 → Render/Railway（免费或低成本）
- 数据 → 数据库或对象存储

**这是现代 Web 应用的标准部署模式！**

---

**文档版本**: 1.0  
**更新日期**: 2025-10-13  
**适用对象**: 第三方开发者、DevOps 工程师

---

**祝部署顺利！** 🚀

如有问题，请参考项目其他文档或在 GitHub Issues 中提问。




