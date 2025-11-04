# 更新 Alpha Vantage API 密钥

## 新的API密钥
```
OIYWUJEPSR9RQAGU
```

## 更新步骤

### 1️⃣ 在 Render Dashboard 更新环境变量

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 找到后端服务：`decision-assistant-backend`
3. 点击左侧菜单 **Environment**
4. 找到环境变量 `ALPHA_VANTAGE_KEY`
5. 点击编辑，更新为新值：`OIYWUJEPSR9RQAGU`
6. 点击 **Save Changes**
7. Render会自动重启服务（约30秒）

### 2️⃣ 验证更新

等待服务重启后，运行测试：

```bash
python test_alpha_vantage_key.py
```

或者访问健康检查：
```
https://decision-assistant-backend.onrender.com/api/stock/health
```

响应中会显示：
```json
{
  "alpha_vantage_key_prefix": "OIYWUJE",
  "alpha_vantage_key_set": true,
  "status": "healthy"
}
```

### 3️⃣ 测试股票数据获取

```bash
curl https://decision-assistant-backend.onrender.com/api/stock/AAPL
```

应该能成功返回股票数据。

## 注意事项

⚠️ **Alpha Vantage免费版限制：**
- 每分钟最多5次请求
- 每天最多500次请求

如果超出限制，会返回空数据或错误。

## 本地开发环境（可选）

如果需要在本地测试，创建 `backend/.env` 文件：

```env
ALPHA_VANTAGE_KEY=OIYWUJEPSR9RQAGU
DEEPSEEK_API_KEY=your-deepseek-key
DATABASE_URL=your-database-url
```

**注意：不要提交 `.env` 文件到 Git！**

