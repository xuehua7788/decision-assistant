#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整AI分析流程（含Premium数据）
"""

import sys
import os
import json

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
from stock_analysis.stock_analyzer import get_stock_analyzer

def test_premium_ai_analysis():
    """测试Premium AI分析"""
    print("=" * 80)
    print("🤖 测试完整AI分析流程 (含Premium数据)")
    print("=" * 80)
    print()
    
    symbol = "AAPL"
    
    # 1. 获取基础数据
    print("📊 步骤1: 获取基础股票数据")
    print("-" * 80)
    client = get_alpha_vantage_client()
    
    quote = client.get_quote(symbol)
    if not quote:
        print(f"❌ 未能获取 {symbol} 报价")
        return
    
    print(f"✅ 当前价格: ${quote['price']:.2f}")
    print(f"   涨跌幅: {quote['change_percent']:.2f}%")
    print()
    
    # 2. 获取历史数据
    print("📈 步骤2: 获取历史数据")
    print("-" * 80)
    history = client.get_daily_history(symbol, days=30)
    if not history:
        print(f"❌ 未能获取历史数据")
        return
    
    print(f"✅ 获取 {len(history)} 天历史数据")
    print()
    
    # 3. 计算RSI
    closes = [h['close'] for h in history]
    rsi = client.calculate_rsi(closes)
    print(f"📊 RSI(14): {rsi:.2f}")
    print()
    
    # 4. 获取Premium数据
    print("💎 步骤3: 获取Premium数据")
    print("-" * 80)
    
    company_overview = client.get_company_overview(symbol)
    print(f"{'✅' if company_overview else '❌'} 公司基本面")
    
    macd_data = client.get_technical_indicator(symbol, 'MACD', interval='daily')
    print(f"{'✅' if macd_data else '❌'} MACD指标")
    
    bbands_data = client.get_technical_indicator(symbol, 'BBANDS', interval='daily', time_period=20)
    print(f"{'✅' if bbands_data else '❌'} 布林带指标")
    
    atr_data = client.get_technical_indicator(symbol, 'ATR', interval='daily', time_period=14)
    print(f"{'✅' if atr_data else '❌'} ATR指标")
    
    cpi_data = client.get_economic_indicator('CPI')
    print(f"{'✅' if cpi_data else '❌'} CPI数据")
    
    unemployment_data = client.get_economic_indicator('UNEMPLOYMENT')
    print(f"{'✅' if unemployment_data else '❌'} 失业率数据")
    
    fed_rate_data = client.get_economic_indicator('FEDERAL_FUNDS_RATE')
    print(f"{'✅' if fed_rate_data else '❌'} 联邦利率数据")
    print()
    
    # 5. 获取新闻
    print("📰 步骤4: 获取新闻")
    print("-" * 80)
    news = client.get_news(symbol, limit=3)
    news_context = ""
    if news:
        print(f"✅ 获取 {len(news)} 条新闻")
        for i, item in enumerate(news[:2], 1):
            print(f"   {i}. {item['title'][:50]}...")
            news_context += f"{item['title']}\n{item.get('summary', '')[:100]}...\n\n"
    else:
        print("❌ 未获取到新闻")
    print()
    
    # 6. AI分析
    print("🤖 步骤5: AI分析 (整合所有数据)")
    print("-" * 80)
    
    analyzer = get_stock_analyzer()
    
    user_opinion = "我看好苹果的AI战略和Vision Pro产品线"
    
    analysis = analyzer.analyze_stock(
        symbol=symbol,
        current_data=quote,
        history_data=history,
        rsi=rsi,
        risk_preference='balanced',
        user_opinion=user_opinion,
        news_context=news_context,
        language='zh',
        investment_style='buffett',  # 使用巴菲特风格
        company_overview=company_overview,
        technical_indicators={
            'macd': macd_data,
            'bbands': bbands_data,
            'atr': atr_data
        },
        economic_data={
            'cpi': cpi_data,
            'unemployment': unemployment_data,
            'fed_rate': fed_rate_data
        }
    )
    
    if not analysis:
        print("❌ AI分析失败")
        return
    
    print("✅ AI分析完成")
    print()
    
    # 7. 展示分析结果
    print("=" * 80)
    print("📋 AI分析结果")
    print("=" * 80)
    print()
    
    print(f"📊 综合评分: {analysis['score']}/100")
    print(f"💡 投资建议: {analysis['recommendation']}")
    print(f"📈 建议仓位: {analysis['position_size']}")
    print(f"🎯 目标价格: ${analysis['target_price']:.2f}")
    print(f"⛔ 止损价格: ${analysis['stop_loss']:.2f}")
    print()
    
    print("🔍 分析要点:")
    for i, point in enumerate(analysis['key_points'], 1):
        print(f"   {i}. {point}")
    print()
    
    print("📝 综合分析:")
    print(f"   {analysis['analysis_summary']}")
    print()
    
    print("💼 投资策略:")
    print(f"   {analysis.get('strategy', 'N/A')}")
    print()
    
    print("=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_premium_ai_analysis()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

