#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动更新 StockAnalysis.js 为多语言版本
"""

import re

# 读取原文件
with open('frontend/src/StockAnalysis.js', 'r', encoding='utf-8') as f:
    content = f.read()

# 文本替换映射（中文 -> 多语言函数调用）
replacements = [
    # 标题和按钮
    ('📈 智能股票分析', '{t("searchTitle", language)}'),
    ('输入美股代码（如 AAPL=苹果, TSLA=特斯拉）', '{t("searchPlaceholder", language)}'),
    ('"🔍 搜索中..."', 't("loading", language)'),
    ('"🔍 搜索"', 't("searchButton", language)'),
    ('热门股票:', '{t("hotStocks", language)}'),
    
    # 风险偏好
    ('⚖️ 风险偏好：', '{t("riskPreference", language)}'),
    ("{ value: 'conservative', label: '保守', emoji: '🛡️' }", "{ value: 'conservative', label: t('conservative', language), emoji: '🛡️' }"),
    ("{ value: 'balanced', label: '平衡', emoji: '⚖️' }", "{ value: 'balanced', label: t('balanced', language), emoji: '⚖️' }"),
    ("{ value: 'aggressive', label: '激进', emoji: '🚀' }", "{ value: 'aggressive', label: t('aggressive', language), emoji: '🚀' }"),
    
    # 新闻相关
    ('📰 最新相关新闻（点击选择）：', '{t("latestNews", language)}'),
    ('"🔄 正在加载新闻..."', 't("loadingNews", language)'),
    ('📝 选中的新闻/自定义消息（可选）：', '{t("selectedNews", language)}'),
    ('点击上方新闻自动填充，或手动输入...', '{t("newsPlaceholder", language)}'),
    
    # 用户观点
    ('💭 您的观点/研报（可选）：', '{t("userOpinion", language)}'),
    ('例如：我认为该公司基本面良好，技术创新能力强，长期看好...', '{t("opinionPlaceholder", language)}'),
    
    # AI分析按钮
    ('"🔄 分析中..."', 't("analyzing", language)'),
    ('"🤖 开始AI综合分析"', 't("startAnalysis", language)'),
    ('"✅ 已选择新闻 "', 't("newsSelected", language) + " "'),
    ('"✅ 已输入观点 "', 't("opinionEntered", language) + " "'),
    ('"💡 提示：选择新闻或输入观点可获得更全面的分析"', 't("analysisHint", language)'),
    
    # 错误信息
    ("'请输入股票代码'", "t('errorSearchFirst', language)"),
    ("'请先搜索股票'", "t('errorSearchFirst', language)"),
    ("'未找到该股票'", "t('errorStockNotFound', language)"),
    ("'AI分析失败: '", "t('errorAnalysisFailed', language) + ': '"),
    ("'网络连接失败: '", "t('errorNetwork', language) + ': '"),
    
    # 股票信息
    ('更新时间:', '{t("updatedAt", language)}:'),
    ('📊 推荐期权策略:', '{t("optionStrategy", language)}:'),
    ('风险等级', '{t("riskLevel", language)}'),
    ('当前股价', '{t("currentPrice", language)}'),
    ('策略参数：', '{t("strategyParams", language)}'),
    ('买入执行价:', '{t("buyStrike", language)}:'),
    ('卖出执行价:', '{t("sellStrike", language)}:'),
    ('到期时间:', '{t("expiry", language)}:'),
    ('风险指标：', '{t("riskMetrics", language)}'),
    ('最大收益:', '{t("maxGain", language)}:'),
    ('最大损失:', '{t("maxLoss", language)}:'),
    ('盈亏平衡:', '{t("breakeven", language)}:'),
    ("'无限'", "t('unlimited', language)"),
    
    # K线图和指标
    ('📊 30天价格走势', '{t("priceChart", language)}'),
    ('收盘价', '{t("currentPrice", language)}'),
    ('📋 关键指标', '{t("keyMetrics", language)}'),
    ('今日最高', '{t("high", language)}'),
    ('今日最低', '{t("low", language)}'),
    ('成交量', '{t("volume", language)}'),
    ('30日波动率', '{t("volatility", language)}'),
    
    # AI分析结果
    ('🎯 综合评分', '{t("score", language)}'),
    ('满分100分', '100 pts'),
    ('💡 操作建议', '{t("recommendation", language)}'),
    ('建议仓位:', '{t("positionSize", language)}:'),
    ('目标价:', '{t("targetPrice", language)}:'),
    ('止损价:', '{t("stopLoss", language)}:'),
    ('📌 分析要点', '{t("keyPoints", language)}'),
    ('综合分析:', '{t("summary", language)}:'),
    ('🎯 综合投资策略', '{t("strategy", language)}'),
    
    # 提示信息
    ('输入股票代码开始分析', '{t("searchPlaceholder", language)}'),
    ('支持美股代码，如 AAPL、GOOGL、MSFT 等', 'US stocks like AAPL, GOOGL, MSFT, etc.'),
]

# 执行替换
for old, new in replacements:
    content = content.replace(old, new)

# 特殊处理：热门股票名称
content = re.sub(
    r'title=\{`\$\{stock\.name\} \(\$\{stock\.code\}\)`\}',
    'title={`${language === "zh" ? stock.name_zh : stock.name_en} (${stock.code})`}',
    content
)
content = re.sub(
    r'\{stock\.code\} \{stock\.name\}',
    '{stock.code} {language === "zh" ? stock.name_zh : stock.name_en}',
    content
)

# 写入文件
with open('frontend/src/StockAnalysis.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ StockAnalysis.js 已更新为多语言版本")

