#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票分析API
"""

import os
import sys

# 设置环境变量
os.environ['ALPHA_VANTAGE_KEY'] = 'QKO2M2K3LZ58ACO2'
os.environ['DEEPSEEK_API_KEY'] = 'sk-d3196d8e68c44690998d79c715ce715d'

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 60)
print("测试股票分析API")
print("=" * 60)
print()

# 测试1: 导入模块
print("📦 测试1: 导入模块...")
try:
    from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
    from stock_analysis.stock_analyzer import get_stock_analyzer
    print("✅ 模块导入成功")
except Exception as e:
    print(f"❌ 模块导入失败: {e}")
    sys.exit(1)

print()

# 测试2: 获取股票数据
print("📊 测试2: 获取AAPL股票数据...")
try:
    client = get_alpha_vantage_client()
    quote = client.get_quote('AAPL')
    if quote:
        print(f"✅ 报价获取成功: ${quote['price']:.2f}")
    else:
        print("❌ 报价获取失败")
        sys.exit(1)
    
    history = client.get_daily_history('AAPL', days=30)
    if history:
        print(f"✅ 历史数据获取成功: {len(history)}条")
    else:
        print("❌ 历史数据获取失败")
        sys.exit(1)
    
    closes = [h['close'] for h in history]
    rsi = client.calculate_rsi(closes)
    print(f"✅ RSI计算成功: {rsi:.2f}")
    
except Exception as e:
    print(f"❌ 数据获取失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()

# 测试3: AI分析
print("🤖 测试3: AI分析股票...")
try:
    analyzer = get_stock_analyzer()
    analysis = analyzer.analyze_stock(
        symbol='AAPL',
        current_data=quote,
        history_data=history,
        rsi=rsi,
        risk_preference='balanced'
    )
    
    if analysis:
        print(f"✅ AI分析成功")
        print(f"   评分: {analysis['score']}")
        print(f"   建议: {analysis['recommendation']}")
        print(f"   仓位: {analysis['position_size']}")
        print(f"   目标价: ${analysis['target_price']:.2f}")
        print(f"   止损价: ${analysis['stop_loss']:.2f}")
    else:
        print("❌ AI分析失败")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ AI分析失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print()
print("=" * 60)
print("✅ 所有测试通过！")
print("=" * 60)

