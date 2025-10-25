# Render后台测试指南

## 🎯 在Render Shell中测试

### 方法1: 使用自动化脚本

1. 进入Render Dashboard
2. 选择你的Web Service
3. 点击 **Shell** 标签
4. 运行以下命令：

```bash
cd backend
bash test_in_render_shell.sh
```

---

### 方法2: 手动逐步测试

#### 步骤1: 检查环境变量

```bash
echo $DATABASE_URL
echo $DEEPSEEK_API_KEY
echo $USE_DATABASE
```

**预期输出**: 应该显示完整的连接字符串和API密钥

---

#### 步骤2: 创建数据库表

```bash
cd backend
python create_user_profile_tables.py
```

**预期输出**:
```
=== 创建用户画像数据库表 ===

1. 创建用户画像表 (user_profiles)...
   ✅ 用户画像表创建成功

2. 创建策略推荐历史表 (strategy_recommendations)...
   ✅ 策略推荐历史表创建成功

...

🎉 所有表创建/更新成功！
```

---

#### 步骤3: 运行系统测试

```bash
python test_profile_system.py
```

**预期输出**:
```
测试总结
======================================================================
   ✅ 通过: environment
   ✅ 通过: database_connection
   ✅ 通过: database_tables
   ✅ 通过: integration_helpers
   ✅ 通过: strategy_optimizer
   ⏭️ 跳过: ai_analyzer (需要API调用)

🎉 所有测试通过！系统已准备就绪。
```

---

#### 步骤4: 查看现有用户

```bash
python -c "
import os, json
chat_dir = 'chat_data'
if os.path.exists(chat_dir):
    files = [f for f in os.listdir(chat_dir) if f.endswith('.json')]
    print(f'找到 {len(files)} 个用户')
    for f in files[:10]:
        print(f'  - {f.replace(\".json\", \"\")}')
"
```

---

#### 步骤5: 分析第一个用户（如果有）

```bash
# 替换 alice 为实际用户名
python scheduled_profile_analysis.py --user alice
```

**预期输出**:
```
======================================================================
单用户画像分析 - alice
======================================================================

🔍 开始分析用户 alice 的画像...
   时间范围: 最近 30 天
   消息总数: 25 条
   ✅ 筛选出 25 条有效消息
   🤖 调用DeepSeek API进行分析...
   ✅ AI分析完成
   ✅ 用户画像生成成功
   📝 更新用户 alice 的画像...
   ✅ 用户画像已保存到数据库

✅ 分析完成

画像摘要:
  - 风险偏好: conservative
  - 期权经验: basic
  - 投资风格: value
  - 分析消息数: 25
```

---

## 🔍 验证API接口

在Render Shell中测试API：

```bash
# 测试健康检查
curl http://localhost:$PORT/health

# 测试用户画像统计
curl http://localhost:$PORT/api/profile/stats

# 测试获取用户画像
curl http://localhost:$PORT/api/profile/alice
```

---

## ⚠️ 常见问题

### 问题1: 数据库连接失败

**症状**: `❌ DATABASE_URL 环境变量未设置`

**解决**:
1. 在Render Dashboard → Environment 中检查变量
2. 确保变量名完全匹配（区分大小写）
3. 重新部署服务

---

### 问题2: 表已存在错误

**症状**: `relation "user_profiles" already exists`

**解决**: 这是正常的！表已经创建过了，可以继续。

---

### 问题3: AI分析失败

**症状**: `DEEPSEEK_API_KEY not configured`

**解决**:
1. 检查API密钥是否设置
2. 检查API密钥格式（应以`sk-`开头）
3. 确认API密钥有余额

---

### 问题4: 没有用户数据

**症状**: `找到 0 个用户`

**解决**: 
- 这是正常的，用户需要先使用聊天功能
- 用户聊天后会自动保存到 `chat_data/` 目录
- 至少需要5条消息才能进行画像分析

---

## 📊 成功标志

如果看到以下输出，说明系统正常：

✅ 环境变量已设置  
✅ 数据库连接成功  
✅ 数据库表已创建  
✅ API接口正常响应  
✅ 可以分析用户画像  

---

## 🚀 下一步

1. ✅ 确认所有测试通过
2. 📝 用户开始使用聊天功能
3. 🔄 定期运行画像分析
4. 📊 查看用户画像统计

---

## 💡 提示

- Render Shell会话有时间限制，长时间操作可能断开
- 可以使用 `screen` 或 `tmux` 保持会话
- 建议设置Cron Job自动运行定时分析
- 查看日志: `tail -f /var/log/*.log`

---

**需要帮助？** 查看完整文档: `USER_PROFILE_SYSTEM_GUIDE.md`

