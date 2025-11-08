# 如何获取Render数据库URL

## 方法1：从Render Dashboard获取

1. 登录 https://dashboard.render.com
2. 找到你的 PostgreSQL 数据库服务
3. 点击进入数据库详情页
4. 找到 "Connections" 部分
5. 复制 "External Database URL" 或 "Internal Database URL"

格式类似：
```
postgresql://user:password@dpg-xxxxx.oregon-postgres.render.com/dbname
```

## 方法2：从环境变量获取

如果你的backend已部署在Render，可以在backend服务的环境变量中找到 `DATABASE_URL`

## 方法3：使用本地环境变量（如果你之前设置过）

```bash
# Windows
echo %DATABASE_URL%

# Linux/Mac
echo $DATABASE_URL
```


