# Vercel 部署指南 - 正确方法

## 问题根源
Vercel 一直在检测到项目根目录的 Python 文件，误认为这是一个 FastAPI 项目。

## 解决方案：在 Vercel Dashboard 中重新配置项目

### 方法 1：修改现有项目设置（推荐）

1. **访问项目设置**：
   - https://vercel.com/bruces-projects-409b2d51/decision-assistant-bx/settings

2. **在 "Build & Development Settings" 中设置**：
   - **Framework Preset**: 选择 `Create React App`
   - **Root Directory**: `frontend` （如果这个选项存在）
   - **Build Command**: 留空（让 Vercel 自动检测）
   - **Output Directory**: `build`
   - **Install Command**: 留空（让 Vercel 自动检测）

3. **保存设置**

4. **重新部署**

### 方法 2：创建新项目（如果方法 1 不行）

1. **访问 Vercel Dashboard**：
   - https://vercel.com/new

2. **导入 GitHub 仓库**：
   - 选择 `xuehua7788/decision-assistant`
   - 点击 "Import"

3. **配置项目**：
   - **Framework Preset**: `Create React App`
   - **Root Directory**: `frontend`
   - **Build Command**: 留空
   - **Output Directory**: `build`
   - **Install Command**: 留空

4. **部署**

### 方法 3：使用 Vercel CLI（最可靠）

在 PowerShell 中运行：

```powershell
# 安装 Vercel CLI
npm install -g vercel

# 登录
vercel login

# 进入 frontend 目录
cd frontend

# 部署
vercel --prod
```

## 验证部署

部署成功后，访问你的 Vercel 域名，应该能看到登录页面，并且 Console 中不再有 `127.0.0.1:8000` 的错误。


