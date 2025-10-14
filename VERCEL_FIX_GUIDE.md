# 🔧 Vercel 部署修复指南

## ⚠️ 当前问题

你的 Vercel 当前部署的是**错误的文件**：

```
❌ 当前部署：
decision-assistant/
└── index.html          ← 根目录的纯 HTML 版本
```

**问题：**
1. API Key 暴露在前端代码中（第 235 行）
2. 没有后端，直接调用 DeepSeek API
3. 缺少完整功能（Chat Viewer）
4. 数据只保存在浏览器 localStorage

---

## ✅ 正确的部署

应该部署的是 `frontend/` 目录下的 React 应用：

```
✅ 正确部署：
decision-assistant/
└── frontend/           ← 部署这个目录
    ├── src/
    │   ├── App.js
    │   ├── ChatViewer.js
    │   └── ...
    ├── package.json
    └── vercel.json
```

---

## 🚀 快速修复步骤

### 方法 1：在 Vercel 网站修改（推荐）

#### 第一步：修改 Root Directory

1. 登录 https://vercel.com
2. 找到你的项目 (decision-assistant)
3. 点击 "Settings"
4. 左侧选择 "General"
5. 找到 "Root Directory" 设置
6. 点击 "Edit"
7. 输入：`frontend`
8. 点击 "Save"

#### 第二步：确认其他配置

在同一页面确认：

```
Framework Preset: Create React App  (或 Other)
Build Command: npm run build
Output Directory: build
Install Command: npm install
```

#### 第三步：重新部署

1. 点击顶部 "Deployments" 标签
2. 点击最新部署右侧的 "..." 菜单
3. 选择 "Redeploy"
4. 等待 2-3 分钟

---

### 方法 2：使用 Vercel CLI 重新部署

```bash
# 1. 删除 .vercel 配置（如果存在）
rm -rf .vercel

# 2. 进入 frontend 目录
cd frontend

# 3. 登录 Vercel
vercel login

# 4. 重新部署
vercel --prod
```

执行时的配置选项：
```
? Set up and deploy "~/decision-assistant/frontend"? Y
? Which scope? (选择你的账号)
? Link to existing project? N
? What's your project's name? decision-assistant
? In which directory is your code located? ./
? Auto-detected Project Settings (Create React App):
  - Build Command: npm run build
  - Output Directory: build
  - Development Command: npm start
? Want to override the settings? N
```

---

### 方法 3：删除项目重新创建

如果上述方法不行：

1. **删除 Vercel 项目**
   - 进入 Vercel 项目页面
   - Settings → General → 滚动到底部
   - 点击 "Delete Project"

2. **重新部署**
   ```bash
   cd frontend
   vercel --prod
   ```

---

## 🔍 验证部署成功

### 1. 检查部署的文件

部署成功后，在 Vercel 项目页面：
- 点击 "Deployments" → 最新部署
- 点击 "Source" 标签
- 应该看到：
  ```
  ✅ frontend/
      ├── src/
      ├── public/
      ├── package.json
      └── build/
  ```

### 2. 检查构建日志

在 "Deployments" 页面查看构建日志，应该看到：

```
✅ Running "npm run build"
✅ Creating an optimized production build...
✅ Compiled successfully.
✅ Build Completed
```

### 3. 访问网站

访问 Vercel URL，应该看到：
- React 应用界面
- 三个模式按钮：Decision Analysis、Chat Mode、Chat Viewer
- 打开 F12 控制台，应该有 React 相关的消息

### 4. 检查 API 调用

打开 F12 → Network 标签：
- 发送一条消息
- 应该看到请求发送到 `http://localhost:8000` 或你配置的后端 URL
- **不是**直接发送到 `api.deepseek.com`

---

## 📋 修复检查清单

完成修复后，确认：

- [ ] Vercel Root Directory 设置为 `frontend`
- [ ] 部署日志显示 React 构建成功
- [ ] 访问网站看到 React 应用（不是纯 HTML）
- [ ] 页面有 "Chat Viewer" 按钮
- [ ] F12 控制台没有构建错误
- [ ] Network 标签显示 API 请求发送到后端（不是 DeepSeek API）

---

## ❓ 常见问题

### Q1: 为什么会部署错误的文件？

**原因：** Vercel 默认部署根目录。如果根目录有 `index.html`，它会当作静态网站部署。

**解决：** 设置 Root Directory 为 `frontend`

---

### Q2: 修改 Root Directory 后还是部署根目录

**原因：** 缓存或配置未生效

**解决：**
1. 清除浏览器缓存
2. 强制重新部署（Redeploy）
3. 或删除项目重新创建

---

### Q3: 部署后显示 404

**原因：** 构建失败或输出目录错误

**解决：**
1. 检查构建日志
2. 确认 Output Directory 设置为 `build`
3. 确认 `frontend/package.json` 中有正确的 build 脚本

---

### Q4: API 请求失败

**原因：** 还没部署后端或环境变量未设置

**解决：**
1. 先部署后端到 Render/Railway
2. 在 Vercel 设置环境变量 `REACT_APP_API_URL`
3. 参考 `TECHNICAL_SUMMARY.md` 完整部署指南

---

## 🎯 下一步

修复 Vercel 部署后：

1. ✅ **部署后端**
   - 参考 `TECHNICAL_SUMMARY.md` 第一步
   - 部署到 Render.com 或 Railway

2. ✅ **配置环境变量**
   - 在 Vercel 设置 `REACT_APP_API_URL`
   - 在 Render 设置 `DEEPSEEK_API_KEY`

3. ✅ **修改代码**
   - `frontend/src/App.js` - 使用环境变量
   - `backend/app/main.py` - 添加 CORS 域名
   - `backend/app/services/ai_service.py` - 移除硬编码 API Key

4. ✅ **测试**
   - 前端可以访问
   - 后端 API 正常
   - 无 CORS 错误

---

## 📚 相关文档

- `TECHNICAL_SUMMARY.md` - 完整部署修改清单
- `VERCEL_DEPLOYMENT_GUIDE.md` - 详细部署指南
- `部署到生产环境.md` - 生产环境配置

---

**文档版本：** 1.0  
**创建日期：** 2025-10-13

---

**🚀 修复完成后，继续参考 `TECHNICAL_SUMMARY.md` 完成完整部署！**




