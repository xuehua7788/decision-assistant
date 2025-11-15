# CORS 配置修复指南

## 🔍 问题诊断

### 原始错误
```
Access to fetch at 'https://decision-assistant-backend.onrender.com/api/ml/decision-tree/train'
from origin 'https://decision-assistant-frontend-prod.vercel.app' has been blocked by CORS policy:
Response to preflight request doesn't pass access control check:
The 'Access-Control-Allow-Origin' header contains multiple values, but only one is allowed.
```

### 根本原因
**CORS headers 被设置了两次**：
1. `CORS(app, ...)` - Flask-CORS 扩展自动添加
2. `@app.after_request` - 手动添加 headers

这导致响应中包含重复的 `Access-Control-Allow-Origin` header。

---

## ✅ 修复方案

### 1. 删除重复的 CORS 配置

**修改前** (`app.py`):
```python
CORS(app, 
     resources={r"/*": {"origins": "*"}},
     allow_headers=["Content-Type", "Authorization"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=False)

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')  # ❌ 重复！
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,PUT,DELETE,OPTIONS')
    return response
```

**修改后** (`app.py`):
```python
# 使用环境变量配置允许的源
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*')
if ALLOWED_ORIGINS == '*':
    origins = '*'
else:
    origins = [origin.strip() for origin in ALLOWED_ORIGINS.split(',')]

CORS(app, 
     resources={r"/*": {"origins": origins}},
     allow_headers=["Content-Type", "Authorization", "Access-Control-Allow-Origin"],
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
     supports_credentials=False,
     expose_headers=["Content-Type", "Authorization"])

# ✅ 删除了 @app.after_request 装饰器
```

---

## 🔧 环境变量配置

### 开发环境 (本地)
```bash
# .env
ALLOWED_ORIGINS=*
```

### 生产环境 (Render)
在 Render Dashboard 中设置环境变量：
```
ALLOWED_ORIGINS=https://decision-assistant-frontend-prod.vercel.app
```

或允许多个域名：
```
ALLOWED_ORIGINS=https://decision-assistant-frontend-prod.vercel.app,https://your-other-domain.com
```

---

## 🧪 测试 CORS 配置

### 1. 测试 OPTIONS 预检请求
```bash
curl -X OPTIONS https://decision-assistant-backend.onrender.com/api/ml/decision-tree/train \
  -H "Origin: https://decision-assistant-frontend-prod.vercel.app" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v 2>&1 | grep -i "access-control"
```

**预期输出**（只有一个 Access-Control-Allow-Origin）：
```
< Access-Control-Allow-Origin: *
< Access-Control-Allow-Methods: GET,POST,PUT,DELETE,OPTIONS
< Access-Control-Allow-Headers: Content-Type,Authorization,Access-Control-Allow-Origin
```

### 2. 测试实际 POST 请求
```bash
curl -X POST https://decision-assistant-backend.onrender.com/api/ml/decision-tree/train \
  -H "Origin: https://decision-assistant-frontend-prod.vercel.app" \
  -H "Content-Type: application/json" \
  -d '{}' \
  -v 2>&1 | grep -i "access-control"
```

### 3. PowerShell 测试（Windows）
```powershell
# 测试 OPTIONS
$response = Invoke-WebRequest -Uri "https://decision-assistant-backend.onrender.com/api/ml/decision-tree/train" `
  -Method OPTIONS `
  -Headers @{
    "Origin" = "https://decision-assistant-frontend-prod.vercel.app"
    "Access-Control-Request-Method" = "POST"
    "Access-Control-Request-Headers" = "Content-Type"
  } `
  -UseBasicParsing

$response.Headers["Access-Control-Allow-Origin"]
# 应该只输出一个值
```

---

## 📋 部署检查清单

- [x] 删除 `@app.after_request` 中的 CORS headers
- [x] 只保留 `CORS(app, ...)` 配置
- [x] 添加环境变量 `ALLOWED_ORIGINS` 支持
- [x] 创建 `env.example` 文件
- [ ] 在 Render 中设置 `ALLOWED_ORIGINS` 环境变量
- [ ] 重新部署后端
- [ ] 测试前端请求是否成功
- [ ] 验证 CORS headers 只出现一次

---

## 🚨 常见问题

### Q1: 为什么不能同时使用 CORS() 和 @app.after_request？
**A**: Flask-CORS 扩展已经自动处理了 CORS headers。手动添加会导致重复，浏览器会拒绝包含重复 headers 的响应。

### Q2: 生产环境应该用 `*` 还是指定域名？
**A**: 
- **开发环境**: 可以用 `*` 方便测试
- **生产环境**: **强烈建议**指定具体域名，提高安全性

### Q3: 如何验证 CORS 是否正确配置？
**A**: 
1. 打开浏览器开发者工具 → Network 标签
2. 触发前端请求
3. 查看 Response Headers
4. 确认 `Access-Control-Allow-Origin` **只出现一次**

---

## 📚 相关资源

- [Flask-CORS 文档](https://flask-cors.readthedocs.io/)
- [MDN CORS 指南](https://developer.mozilla.org/en-US/docs/Web/HTTP/CORS)
- [Render 环境变量配置](https://render.com/docs/environment-variables)

