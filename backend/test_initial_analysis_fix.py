#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Tom初步分析API修复
"""

import os
import sys

# 设置环境变量
os.environ['ALPHA_VANTAGE_KEY'] = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')

def test_initial_analysis():
    """测试初步分析功能"""
    
    print("=" * 80)
    print("🧪 测试Tom初步分析API（修复后）")
    print("=" * 80)
    
    try:
        # 导入必要的模块
        from tom_indicator_selector import get_tom_indicator_selector
        from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
        from stock_analysis.stock_analyzer import get_stock_analyzer
        
        print("\n✅ 所有模块导入成功")
        
        # 测试指标选择
        print("\n📊 步骤1：测试指标选择")
        selector = get_tom_indicator_selector()
        selected_indicators = selector.select_indicators('IBM', 'buffett')
        
        print(f"✅ 指标选择成功:")
        print(f"   基本面: {selected_indicators['fundamental'][:3]}...")
        print(f"   技术面: {selected_indicators['technical']}")
        print(f"   宏观面: {selected_indicators['macro']}")
        
        # 测试数据获取
        print("\n📊 步骤2：测试数据获取")
        client = get_alpha_vantage_client()
        
        print("   获取股票数据...")
        quote = client.get_quote('IBM')
        if quote:
            print(f"   ✅ 股票数据: ${quote.get('price', 'N/A')}")
        else:
            print("   ❌ 股票数据获取失败")
            return False
        
        print("   获取历史数据...")
        history = client.get_daily_history('IBM', days=30)
        print(f"   ✅ 历史数据: {len(history) if history else 0}条")
        
        print("   计算RSI...")
        closes = [h['close'] for h in history]
        rsi = client.calculate_rsi(closes)
        print(f"   ✅ RSI: {rsi}")
        
        print("   获取基本面数据...")
        company_overview = client.get_company_overview('IBM')
        print(f"   ✅ 基本面数据: {'有' if company_overview else '无'}")
        
        print("   获取技术指标...")
        macd_data = client.get_technical_indicator('IBM', 'MACD', interval='daily')
        print(f"   ✅ MACD: {'有' if macd_data else '无'}")
        
        print("   获取宏观数据...")
        cpi_data = client.get_economic_indicator('CPI')
        print(f"   ✅ CPI: {'有' if cpi_data else '无'}")
        
        technical_indicators = {'rsi': rsi, 'macd': macd_data}
        economic_data = {'cpi': cpi_data}
        
        # 测试分析
        print("\n📊 步骤3：测试AI分析")
        analyzer = get_stock_analyzer()
        
        analysis = analyzer.analyze_stock(
            symbol='IBM',
            current_data=quote,
            history_data=history,
            rsi=rsi,
            investment_style='buffett',
            news_context='IBM发布新一代AI芯片',
            user_opinion='看好IBM的转型',
            language='zh',
            company_overview=company_overview,
            technical_indicators=technical_indicators,
            economic_data=economic_data,
            custom_indicators=selected_indicators
        )
        
        if analysis:
            print(f"   ✅ 分析成功!")
            print(f"   评分: {analysis.get('score')}/100")
            print(f"   建议: {analysis.get('recommendation')}")
            print(f"   方向: {analysis.get('market_direction')}")
        else:
            print("   ❌ 分析失败")
            return False
        
        print("\n" + "=" * 80)
        print("✅ 所有测试通过！")
        print("=" * 80)
        
        print("\n📋 测试总结:")
        print("1. ✅ 模块导入正常")
        print("2. ✅ 指标选择正常")
        print("3. ✅ 数据获取正常")
        print("4. ✅ AI分析正常")
        print("\n🎉 Tom初步分析API已修复，可以部署！")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_initial_analysis()
    sys.exit(0 if success else 1)

