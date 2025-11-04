# Alpha Vantage API 历史数据限制

## 当前使用情况

### 代码配置
```python
# backend/stock_analysis/alpha_vantage_client.py
params = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': symbol,
    'apikey': self.api_key,
    'outputsize': 'compact'  # ← 最近100天
}
```

---

## Alpha Vantage 历史数据限制

### TIME_SERIES_DAILY

| 参数 | 说明 | 数据量 |
|------|------|--------|
| `outputsize=compact` | 紧凑输出（默认） | **最近100个交易日** |
| `outputsize=full` | 完整输出 | **20+年完整历史** |

### 其他时间序列

| API | 最大历史 |
|-----|----------|
| `TIME_SERIES_INTRADAY` | 最近1-2个月（取决于间隔） |
| `TIME_SERIES_WEEKLY` | 20+年 |
| `TIME_SERIES_MONTHLY` | 20+年 |

---

## 免费版限制

| 限制类型 | 限制值 |
|----------|--------|
| **每分钟请求数** | 5次 |
| **每天请求数** | 25次 ⚠️ |

**新API密钥:** `OIYWUJEPSR9RQAGU`
- 类型：免费版
- 限制：25次/天

---

## 当前使用

### 每次股票分析需要的API调用

1. `GLOBAL_QUOTE` - 获取实时报价（1次）
2. `TIME_SERIES_DAILY` - 获取历史数据（1次）
3. `NEWS_SENTIMENT` - 获取新闻（1次，如果启用）

**总计：2-3次API调用/股票**

### 每日可分析股票数

```
25次/天 ÷ 2次/股票 = 约12只股票/天
```

---

## 建议改进

### 1️⃣ 增加历史数据量（Strategy Evaluation需要）

修改 `alpha_vantage_client.py`:

```python
# 当前
'outputsize': 'compact'  # 100天

# 改为
'outputsize': 'full'  # 20+年数据
```

**优点：** 
- ✅ 可以回测更长时间
- ✅ Strategy Evaluation更准确

**缺点：**
- ⚠️ 响应速度稍慢（数据量大）
- ⚠️ 仍然占用1次API调用

### 2️⃣ 添加缓存策略

当前代码已有15分钟缓存：
```python
self.cache_ttl = 900  # 15分钟缓存
```

**建议：**
- 历史数据可以缓存更长时间（如1天）
- 只有实时报价需要15分钟刷新

### 3️⃣ 升级到付费版（可选）

| 版本 | 价格/月 | 请求限制 |
|------|---------|----------|
| 免费 | $0 | 25/天 |
| 基础 | $49.99 | 75/分钟 + 无日限制 |
| 高级 | $149.99 | 150/分钟 + 更多功能 |

---

## 修改建议

如果需要更长历史数据用于Strategy Evaluation回测，修改：

```python
# backend/stock_analysis/alpha_vantage_client.py 第175行
'outputsize': 'full'  # 改为full获取完整历史
```

这样可以获取：
- ✅ 20+年历史数据
- ✅ 足够做长期回测
- ⚠️ 仍然只算1次API调用

