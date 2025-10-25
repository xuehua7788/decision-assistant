# 用户画像系统完整指南

## 📋 目录

1. [系统概述](#系统概述)
2. [快速开始](#快速开始)
3. [环境配置](#环境配置)
4. [数据库设置](#数据库设置)
5. [API使用](#api使用)
6. [定时任务](#定时任务)
7. [集成到现有系统](#集成到现有系统)
8. [故障排查](#故障排查)

---

## 系统概述

### 架构图

```
用户聊天 → 数据库存储 → AI #3分析 → 用户画像 → 策略优化 → 个性化推荐
```

### 核心组件

| 组件 | 文件 | 功能 |
|------|------|------|
| **数据库表** | `create_user_profile_tables.py` | 创建user_profiles等表 |
| **AI #3分析器** | `ai_profile_analyzer.py` | 分析聊天记录生成画像 |
| **策略优化器** | `profile_based_strategy_optimizer.py` | 基于画像优化策略 |
| **辅助函数** | `profile_integration_helpers.py` | 数据库操作辅助 |
| **API路由** | `profile_api_routes.py` | 画像管理API |
| **定时任务** | `scheduled_profile_analysis.py` | 自动分析脚本 |

---

## 快速开始

### 1. 环境配置

在Render Dashboard或本地`.env`文件中设置：

```bash
# 数据库配置
DATABASE_URL=postgresql://decision_user:PASSWORD@dpg-d3otin3ipnbc739gk7g-a:5432/decision_assistant_0981
USE_DATABASE=true

# AI配置
DEEPSEEK_API_KEY=sk-your-deepseek-api-key

# 功能开关
ENABLE_USER_PROFILING=true
```

### 2. 创建数据库表

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

### 3. 测试AI #3

```bash
python ai_profile_analyzer.py
```

### 4. 分析第一个用户

```bash
python scheduled_profile_analysis.py --user alice
```

---

## 环境配置

### Render环境变量设置

1. 登录Render Dashboard
2. 进入你的Web Service
3. 点击"Environment"标签
4. 添加以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `DATABASE_URL` | `postgresql://...` | 从Render PostgreSQL复制 |
| `DEEPSEEK_API_KEY` | `sk-...` | DeepSeek API密钥 |
| `USE_DATABASE` | `true` | 启用数据库 |
| `ENABLE_USER_PROFILING` | `true` | 启用用户画像 |

5. 点击"Save Changes"并重新部署

### 本地开发配置

创建`backend/.env`文件：

```bash
DATABASE_URL=postgresql://decision_user:PASSWORD@dpg-d3otin3ipnbc739gk7g-a:5432/decision_assistant_0981
DEEPSEEK_API_KEY=sk-your-key-here
USE_DATABASE=true
ENABLE_USER_PROFILING=true
```

---

## 数据库设置

### 表结构

#### 1. user_profiles（用户画像表）

```sql
CREATE TABLE user_profiles (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    
    -- 投资偏好
    risk_tolerance VARCHAR(20),        -- conservative/moderate/aggressive
    investment_style VARCHAR(20),      -- value/growth/momentum
    time_horizon VARCHAR(20),          -- short/medium/long
    
    -- 知识水平
    financial_knowledge VARCHAR(20),   -- beginner/intermediate/advanced
    option_experience VARCHAR(20),     -- none/basic/experienced
    
    -- AI分析结果
    ai_analysis JSONB,
    analysis_summary TEXT,
    
    -- 元数据
    last_analyzed_at TIMESTAMP,
    total_messages_analyzed INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 2. strategy_recommendations（策略推荐历史）

```sql
CREATE TABLE strategy_recommendations (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL,
    user_intent JSONB,
    user_profile_snapshot JSONB,
    strategy_type VARCHAR(50),
    strategy_parameters JSONB,
    adjustment_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 数据库连接测试

```bash
python -c "from profile_integration_helpers import get_db_connection; print('✅ 连接成功' if get_db_connection() else '❌ 连接失败')"
```

---

## API使用

### 1. 获取用户画像

```bash
GET /api/profile/<username>
```

**示例**:
```bash
curl http://localhost:8000/api/profile/alice
```

**响应**:
```json
{
  "status": "success",
  "profile": {
    "investment_preferences": {
      "risk_tolerance": "conservative",
      "investment_style": "value",
      "time_horizon": "medium"
    },
    "knowledge_level": {
      "financial_knowledge": "intermediate",
      "option_experience": "basic"
    },
    "analysis_summary": "该用户是保守型投资者...",
    "last_analyzed_at": "2024-10-23T10:00:00",
    "total_messages_analyzed": 25
  }
}
```

### 2. 触发画像分析

```bash
POST /api/profile/<username>/analyze
Content-Type: application/json

{
  "days": 30,
  "force": false
}
```

**示例**:
```bash
curl -X POST http://localhost:8000/api/profile/alice/analyze \
  -H "Content-Type: application/json" \
  -d '{"days": 30, "force": false}'
```

### 3. 获取画像摘要

```bash
GET /api/profile/<username>/summary
```

### 4. 获取推荐历史

```bash
GET /api/profile/<username>/recommendations?limit=10
```

### 5. 获取统计信息（管理员）

```bash
GET /api/profile/stats
```

**响应**:
```json
{
  "status": "success",
  "stats": {
    "total_profiles": 15,
    "recently_analyzed": 8,
    "risk_distribution": {
      "conservative": 5,
      "moderate": 8,
      "aggressive": 2
    },
    "experience_distribution": {
      "none": 3,
      "basic": 9,
      "experienced": 3
    }
  }
}
```

---

## 定时任务

### 方式1: 手动运行

```bash
# 分析所有活跃用户
python scheduled_profile_analysis.py --all

# 分析单个用户
python scheduled_profile_analysis.py --user alice

# 强制重新分析
python scheduled_profile_analysis.py --user alice --force

# 自定义参数
python scheduled_profile_analysis.py --all --days 14 --min-messages 10
```

### 方式2: Cron定时任务

编辑crontab:
```bash
crontab -e
```

添加任务（每周日凌晨2点运行）:
```bash
0 2 * * 0 cd /path/to/backend && python scheduled_profile_analysis.py --all >> /var/log/profile_analysis.log 2>&1
```

### 方式3: Render Cron Jobs

在`render.yaml`中添加:
```yaml
services:
  - type: cron
    name: profile-analysis
    env: python
    schedule: "0 2 * * 0"  # 每周日凌晨2点
    buildCommand: "pip install -r requirements.txt"
    startCommand: "python scheduled_profile_analysis.py --all"
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: decision-assistant-db
          property: connectionString
      - key: DEEPSEEK_API_KEY
        sync: false
```

---

## 集成到现有系统

### 在app.py中集成

```python
# 1. 导入模块
from profile_integration_helpers import (
    load_user_profile_from_db,
    check_profile_freshness,
    trigger_profile_analysis_async
)
from profile_based_strategy_optimizer import ProfileBasedStrategyOptimizer
from profile_api_routes import profile_bp

# 2. 注册蓝图
app.register_blueprint(profile_bp)

# 3. 初始化优化器
strategy_optimizer = ProfileBasedStrategyOptimizer()

# 4. 在聊天API中使用
@app.route('/api/decisions/chat', methods=['POST'])
def chat():
    # ... 现有代码 ...
    
    if intent_analysis.get('need_option_strategy'):
        # 加载用户画像
        user_profile = load_user_profile_from_db(session_id)
        
        # 生成基础策略
        base_strategy = mapper.map_strategy(parsed_intent, current_price)
        
        # 基于画像优化策略
        if user_profile:
            optimized_strategy = strategy_optimizer.optimize_strategy(
                base_strategy=base_strategy,
                user_profile=user_profile,
                parsed_intent=parsed_intent
            )
        else:
            optimized_strategy = base_strategy
            
            # 异步触发画像分析
            if not check_profile_freshness(session_id):
                trigger_profile_analysis_async(session_id)
        
        # 返回优化后的策略
        # ...
```

---

## 故障排查

### 问题1: 数据库连接失败

**症状**: `❌ DATABASE_URL 环境变量未设置`

**解决**:
1. 检查环境变量是否设置
2. 检查DATABASE_URL格式是否正确
3. 测试连接: `python -c "from profile_integration_helpers import get_db_connection; print(get_db_connection())"`

### 问题2: 表不存在

**症状**: `relation "user_profiles" does not exist`

**解决**:
```bash
python create_user_profile_tables.py
```

### 问题3: AI分析失败

**症状**: `❌ AI #3 分析失败: DEEPSEEK_API_KEY not configured`

**解决**:
1. 检查DEEPSEEK_API_KEY是否设置
2. 检查API密钥是否有效
3. 检查网络连接

### 问题4: 聊天记录不足

**症状**: `用户的聊天记录不足（少于5条）`

**解决**:
- 用户需要先进行至少5轮对话
- 或降低`min_messages`参数

### 问题5: JSON解析失败

**症状**: `JSON解析失败`

**解决**:
- AI #3的输出格式可能不正确
- 检查DeepSeek API响应
- 调整temperature参数（降低到0.1-0.3）

---

## 性能优化

### 1. 数据库索引

已创建的索引:
- `idx_user_profiles_username`
- `idx_user_profiles_risk_tolerance`
- `idx_strategy_recommendations_username`
- `idx_chat_messages_created_at`

### 2. 缓存策略

```python
# 在内存中缓存用户画像（可选）
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_profile(username):
    return load_user_profile_from_db(username)
```

### 3. 异步处理

使用后台线程进行画像分析，避免阻塞主请求。

---

## 成本估算

| 项目 | 成本 |
|------|------|
| PostgreSQL (Render Free) | $0/月 |
| DeepSeek API (每用户/月) | $0.50-1.00 |
| **总计（100用户）** | **$50-100/月** |

---

## 下一步

1. ✅ 配置环境变量
2. ✅ 创建数据库表
3. ✅ 测试AI #3分析
4. ✅ 集成到app.py
5. ✅ 设置定时任务
6. 📊 监控和优化

---

## 技术支持

如有问题，请查看:
- 日志文件: `/var/log/profile_analysis.log`
- 数据库日志: Render Dashboard → PostgreSQL → Logs
- API日志: Render Dashboard → Web Service → Logs

---

**🎉 恭喜！用户画像系统已准备就绪！**

