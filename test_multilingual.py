#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试多语言股票分析功能
"""

import os
import sys

# 设置环境变量
os.environ['ALPHA_VANTAGE_KEY'] = 'QKO2M2K3LZ58ACO2'
os.environ['DEEPSEEK_API_KEY'] = 'sk-d3196d8e68c44690998d79c715ce715d'

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stock_analysis.alpha_vantage_client import AlphaVantageClient
from stock_analysis.stock_analyzer import StockAnalyzer

def test_chinese_analysis():
    """测试中文分析"""
    print("\n" + "="*60)
    print("🇨🇳 测试中文分析")
    print("="*60)
    
    try:
        # 初始化客户端
        client = AlphaVantageClient()
        analyzer = StockAnalyzer()
        
        # 获取股票数据
        symbol = "AAPL"
        print(f"\n📊 获取 {symbol} 数据...")
        
        quote = client.get_quote(symbol)
        if not quote:
            print("❌ 无法获取股票数据")
            return False
        
        history = client.get_daily_history(symbol, days=30)
        if not history:
            print("❌ 无法获取历史数据")
            return False
        
        closes = [h['close'] for h in history]
        rsi = client.calculate_rsi(closes)
        
        print(f"✅ 数据获取成功: ${quote['price']}")
        print(f"   RSI: {rsi:.2f}")
        
        # 中文分析
        print(f"\n🤖 开始中文AI分析...")
        analysis = analyzer.analyze_stock(
            symbol=symbol,
            current_data=quote,
            history_data=history,
            rsi=rsi,
            risk_preference="balanced",
            language="zh"
        )
        
        if analysis:
            print(f"✅ 中文分析成功!")
            print(f"   评分: {analysis['score']}")
            print(f"   建议: {analysis['recommendation']}")
            print(f"   要点: {analysis['key_points'][0][:30]}...")
            return True
        else:
            print("❌ 中文分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_english_analysis():
    """测试英文分析"""
    print("\n" + "="*60)
    print("🇺🇸 测试英文分析")
    print("="*60)
    
    try:
        # 初始化客户端
        client = AlphaVantageClient()
        analyzer = StockAnalyzer()
        
        # 获取股票数据
        symbol = "MSFT"
        print(f"\n📊 获取 {symbol} 数据...")
        
        quote = client.get_quote(symbol)
        if not quote:
            print("❌ 无法获取股票数据")
            return False
        
        history = client.get_daily_history(symbol, days=30)
        if not history:
            print("❌ 无法获取历史数据")
            return False
        
        closes = [h['close'] for h in history]
        rsi = client.calculate_rsi(closes)
        
        print(f"✅ 数据获取成功: ${quote['price']}")
        print(f"   RSI: {rsi:.2f}")
        
        # 英文分析
        print(f"\n🤖 开始英文AI分析...")
        analysis = analyzer.analyze_stock(
            symbol=symbol,
            current_data=quote,
            history_data=history,
            rsi=rsi,
            risk_preference="balanced",
            language="en"
        )
        
        if analysis:
            print(f"✅ 英文分析成功!")
            print(f"   Score: {analysis['score']}")
            print(f"   Recommendation: {analysis['recommendation']}")
            print(f"   Key Point: {analysis['key_points'][0][:50]}...")
            return True
        else:
            print("❌ 英文分析失败")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "="*60)
    print("🌐 多语言股票分析测试")
    print("="*60)
    
    # 测试中文
    zh_result = test_chinese_analysis()
    
    # 等待一下，避免API限制
    import time
    print("\n⏳ 等待5秒避免API限制...")
    time.sleep(5)
    
    # 测试英文
    en_result = test_english_analysis()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"中文分析: {'✅ 通过' if zh_result else '❌ 失败'}")
    print(f"英文分析: {'✅ 通过' if en_result else '❌ 失败'}")
    
    if zh_result and en_result:
        print("\n🎉 所有测试通过！多语言功能正常工作")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查")
        return 1

if __name__ == "__main__":
    sys.exit(main())

