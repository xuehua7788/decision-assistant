#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试双AI Agent系统
Tom (分析师) + Jany (交易员)
"""

import os
import sys

# 设置环境变量（使用实际的API Key）
if not os.getenv('DEEPSEEK_API_KEY'):
    print("⚠️ 请设置DEEPSEEK_API_KEY环境变量")
    print("   使用: $env:DEEPSEEK_API_KEY='your_key'")
    sys.exit(1)

os.environ['ALPHA_VANTAGE_KEY'] = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')

def test_dual_ai_system():
    """测试双AI系统"""
    
    print("=" * 80)
    print("🧪 测试双AI Agent系统")
    print("=" * 80)
    
    # 模拟Tom的分析结果
    tom_analysis = {
        "score": 78,
        "recommendation": "适度买入",
        "market_direction": "bullish",
        "direction_strength": "moderate",
        "position_size": "18%",
        "target_price": 195.0,
        "stop_loss": 175.0,
        "key_points": [
            "ROE高达147%，远超行业平均",
            "MACD金叉显示上升动能",
            "CPI温和，宏观环境支持"
        ],
        "analysis_summary": "综合来看，苹果基本面优秀，技术面MACD金叉，宏观环境支持。建议适度买入。",
        "strategy": "建议适度买入苹果股票，目标价$195，止损$175。可以分批建仓，先买入15-18%仓位。"
    }
    
    print("\n📊 Tom的分析结果:")
    print(f"   评分: {tom_analysis['score']}/100")
    print(f"   建议: {tom_analysis['recommendation']}")
    print(f"   方向: {tom_analysis['market_direction']} ({tom_analysis['direction_strength']})")
    print(f"   策略: {tom_analysis['strategy'][:50]}...")
    
    # 获取期权链数据
    print("\n📡 获取Alpha Vantage期权数据...")
    from dual_strategy_api import get_option_chain
    
    symbol = 'AAPL'
    option_chain = get_option_chain(symbol)
    
    if not option_chain:
        print("❌ 无法获取期权数据")
        return False
    
    print(f"✅ 获取到 {len(option_chain.get('data', []))} 个期权")
    
    # 显示前3个期权
    print("\n前3个期权示例:")
    for i, opt in enumerate(option_chain['data'][:3], 1):
        print(f"   {i}. {opt.get('contractID')}")
        print(f"      执行价: ${opt.get('strike')}, Delta: {opt.get('delta')}, 期权费: ${opt.get('last')}")
    
    # 调用AI Agent Jany
    print("\n🤖 调用AI Agent Jany生成策略...")
    
    try:
        from ai_strategy_agent import get_ai_strategy_agent
        
        jany = get_ai_strategy_agent()
        
        strategy_result = jany.generate_trading_strategy(
            symbol='AAPL',
            current_price=182.50,
            tom_analysis=tom_analysis,
            option_chain_data=option_chain,
            investment_style='buffett',
            notional_value=30000
        )
        
        if not strategy_result:
            print("❌ AI策略生成失败")
            return False
        
        print("\n✅ AI策略生成成功！")
        print("\n" + "=" * 80)
        print("📊 期权策略:")
        print("=" * 80)
        
        option_strategy = strategy_result.get('option_strategy', {})
        print(f"类型: {option_strategy.get('type')}")
        print(f"标的: {option_strategy.get('underlying')}")
        print(f"期权代码: {option_strategy.get('symbol')}")
        print(f"执行价: ${option_strategy.get('strike_price')}")
        print(f"到期日: {option_strategy.get('expiry_date')} ({option_strategy.get('days_to_expiry')}天)")
        print(f"等价股数: {option_strategy.get('equivalent_shares')}股")
        print(f"期权费: ${option_strategy.get('premium_per_share')}/股")
        print(f"总期权费: ${option_strategy.get('total_premium')}")
        print(f"Delta: {option_strategy.get('delta')}")
        print(f"数据来源: {option_strategy.get('data_source')}")
        print(f"推荐理由: {option_strategy.get('reasoning')}")
        
        print("\n" + "=" * 80)
        print("📈 Delta One股票策略:")
        print("=" * 80)
        
        stock_strategy = strategy_result.get('stock_strategy', {})
        print(f"类型: {stock_strategy.get('type')}")
        print(f"标的: {stock_strategy.get('symbol')}")
        print(f"股数: {stock_strategy.get('shares')}股")
        print(f"入场价: ${stock_strategy.get('entry_price')}")
        print(f"名义本金: ${stock_strategy.get('notional')}")
        print(f"保证金: ${stock_strategy.get('margin')}")
        print(f"止损价: ${stock_strategy.get('stop_loss')}")
        print(f"止盈价: ${stock_strategy.get('take_profit')}")
        print(f"Delta: {stock_strategy.get('delta')}")
        print(f"推荐理由: {stock_strategy.get('reasoning')}")
        
        print("\n" + "=" * 80)
        print("💡 综合说明:")
        print("=" * 80)
        print(strategy_result.get('explanation', ''))
        
        print("\n" + "=" * 80)
        print("⚠️ 风险提示:")
        print("=" * 80)
        print(strategy_result.get('risk_warning', ''))
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_dual_ai_system()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ 双AI系统测试成功！")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ 双AI系统测试失败")
        print("=" * 80)
        sys.exit(1)

