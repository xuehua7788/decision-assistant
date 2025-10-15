# 🤖 决策助手

一个基于 React + Flask 的 AI 决策辅助系统，集成 OpenAI API。

## ✨ 功能特性

- 📊 **决策分析** - AI 智能分析决策问题
- 💬 **聊天咨询** - 与 AI 助手对话
- 🔐 **用户认证** - 安全的用户注册和登录
- 📝 **聊天记录** - 保存和管理对话历史
- 🌐 **响应式设计** - 支持各种设备

## 🏗️ 技术栈

### 前端
- React 17
- Create React App
- 现代 CSS

### 后端
- Flask 2.3.3
- OpenAI API
- JWT 认证
- CORS 支持

## 🚀 快速开始

### 本地开发

1. **克隆项目**
   ```bash
   git clone https://github.com/xuehua7788/decision-assistant.git
   cd decision-assistant
   ```

2. **启动后端**
   ```bash
   cd backend
   pip install -r requirements.txt
   export OPENAI_API_KEY=your-api-key
   python app.py
   ```

3. **启动前端**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **访问应用**
   - 前端: http://localhost:3000
   - 后端: http://localhost:8000

## 🌐 部署

### 前端部署到 Vercel

1. 访问 [Vercel](https://vercel.com)
2. 导入 GitHub 仓库
3. 配置：
   - Framework: Create React App
   - Root Directory: frontend
4. 添加环境变量：
   ```
   REACT_APP_API_URL=https://your-backend-url.onrender.com
   ```

### 后端部署到 Render

1. 访问 [Render](https://render.com)
2. 创建 Web Service
3. 连接 GitHub 仓库
4. 配置：
   ```
   Root Directory: backend
   Build Command: pip install -r requirements.txt
   Start Command: python app.py
   ```
5. 添加环境变量：
   ```
   OPENAI_API_KEY=your-openai-api-key
   ```

## 📚 API 文档

### 基础端点
- `GET /` - API 状态
- `GET /health` - 健康检查
- `GET /api/test` - 测试端点

### 认证端点
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `POST /api/auth/logout` - 用户退出
- `GET /api/auth/me` - 获取用户信息

### 功能端点
- `POST /api/decision` - 决策分析
- `POST /api/chat` - 聊天对话

## 🔧 环境变量

### 后端 (.env)
```bash
OPENAI_API_KEY=sk-your-openai-api-key
PORT=8000
FLASK_ENV=production
```

### 前端 (.env)
```bash
REACT_APP_API_URL=http://localhost:8000
```

## 🧪 测试

### 后端测试
```bash
cd backend
python test_local.py
```

### 健康检查
```bash
curl http://localhost:8000/health
```

## 📁 项目结构

```
decision-assistant/
├── frontend/              # React 前端
│   ├── src/
│   │   ├── config/       # API 配置
│   │   └── services/     # API 服务
│   ├── package.json
│   └── vite.config.js
├── backend/               # Flask 后端
│   ├── app.py            # 主应用
│   ├── config.py         # 配置管理
│   ├── requirements.txt  # Python 依赖
│   └── test_local.py     # 本地测试
├── .github/workflows/     # GitHub Actions
├── vercel.json           # Vercel 配置
└── README.md
```

## 🤝 贡献

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题，请：

1. 查看 [Issues](https://github.com/xuehua7788/decision-assistant/issues)
2. 创建新的 Issue
3. 联系维护者

## 🎯 路线图

- [ ] 添加更多 AI 模型支持
- [ ] 实现实时聊天
- [ ] 添加数据可视化
- [ ] 支持多语言
- [ ] 移动端应用

---

**版本**: 1.0.0  
**维护者**: Decision Assistant Team  
**最后更新**: 2025-10-15