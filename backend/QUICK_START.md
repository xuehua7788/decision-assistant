# 用户画像系统 - 快速开始

## 🚀 5分钟快速部署

### 步骤1: 获取数据库密码

从你的Render PostgreSQL Dashboard获取密码（已显示在截图中）

### 步骤2: 编辑测试脚本

编辑 `test_with_env.ps1`，填入：

```powershell
$env:DATABASE_URL = "postgresql://decision_user:你的密码@dpg-d3otin3ipnbc739gk7g-a.singapore-postgres.render.com:5432/decision_assistant_0981"
$env:DEEPSEEK_API_KEY = "你的DeepSeek API密钥"
```

### 步骤3: 运行测试

```powershell
cd backend
.\test_with_env.ps1
```

### 步骤4: 在Render设置环境变量

1. 进入Render Dashboard → 你的Web Service
2. 点击 "Environment" 标签
3. 添加环境变量：
   - `DATABASE_URL`: `postgresql://decision_user:密码@dpg-d3otin3ipnbc739gk7g-a.singapore-postgres.render.com:5432/decision_assistant_0981`
   - `DEEPSEEK_API_KEY`: `sk-your-key`
   - `USE_DATABASE`: `true`
   - `ENABLE_USER_PROFILING`: `true`

4. 点击 "Save Changes" 并重新部署

---

## 📁 已创建的文件

### 核心功能
- ✅ `create_user_profile_tables.py` - 创建数据库表
- ✅ `ai_profile_analyzer.py` - AI #3用户画像分析器
- ✅ `profile_based_strategy_optimizer.py` - 策略优化器
- ✅ `profile_integration_helpers.py` - 集成辅助函数
- ✅ `profile_api_routes.py` - API路由

### 工具脚本
- ✅ `scheduled_profile_analysis.py` - 定时分析任务
- ✅ `test_profile_system.py` - 系统测试脚本
- ✅ `test_with_env.ps1` - Windows测试脚本
- ✅ `setup_profile_system.sh` - Linux部署脚本

### 文档
- ✅ `USER_PROFILE_SYSTEM_GUIDE.md` - 完整使用指南
- ✅ `QUICK_START.md` - 本文档

---

## 🎯 核心功能

### 1. 用户画像分析（AI #3）

```bash
python scheduled_profile_analysis.py --user alice
```

**输出示例**:
```
✅ 分析完成
画像摘要:
  - 风险偏好: conservative
  - 期权经验: basic
  - 投资风格: value
  - 分析消息数: 25
```

### 2. API接口

```bash
# 获取用户画像
GET /api/profile/alice

# 触发画像分析
POST /api/profile/alice/analyze

# 获取推荐历史
GET /api/profile/alice/recommendations

# 统计信息
GET /api/profile/stats
```

### 3. 策略优化

在聊天API中自动集成：
- 用户表达投资意图 → AI #1识别
- 加载用户画像 → AI #3分析
- 优化策略参数 → 个性化推荐

---

## 🔧 故障排查

### 问题1: 数据库连接失败

```bash
# 测试连接
python -c "from profile_integration_helpers import get_db_connection; print('✅ 成功' if get_db_connection() else '❌ 失败')"
```

### 问题2: 表不存在

```bash
python create_user_profile_tables.py
```

### 问题3: AI分析失败

检查DEEPSEEK_API_KEY是否设置

---

## 📊 数据流程

```
用户聊天
   ↓
保存到数据库（chat_messages）
   ↓
定期分析（AI #3）
   ↓
生成用户画像（user_profiles）
   ↓
实时意图识别（AI #1）
   ↓
策略优化（基于画像）
   ↓
个性化推荐
```

---

## 下一步

1. ✅ 运行测试确保系统正常
2. 📝 在Render设置环境变量
3. 🔄 重新部署后端
4. 🧪 测试API接口
5. ⏰ 设置定时任务（可选）

---

**需要帮助？** 查看 `USER_PROFILE_SYSTEM_GUIDE.md` 获取详细文档

