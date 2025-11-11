#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试双AI Agent系统 - 看跌场景
"""

import os
import sys

if not os.getenv('DEEPSEEK_API_KEY'):
    print("⚠️ 请设置DEEPSEEK_API_KEY环境变量")
    sys.exit(1)

os.environ['ALPHA_VANTAGE_KEY'] = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')

def test_bearish_scenario():
    """测试看跌场景"""
    
    print("=" * 80)
    print("🧪 测试双AI系统 - 看跌场景 + 激进风格")
    print("=" * 80)
    
    # 模拟Tom的看跌分析
    tom_analysis = {
        "score": 35,
        "recommendation": "卖出",
        "market_direction": "bearish",
        "direction_strength": "strong",
        "position_size": "0%",
        "target_price": 160.0,
        "stop_loss": 190.0,
        "key_points": [
            "PE比率过高，估值泡沫明显",
            "MACD死叉，技术面走弱",
            "失业率上升，宏观环境恶化"
        ],
        "analysis_summary": "综合来看，苹果估值过高，技术面走弱，宏观环境不利。建议卖出或做空。",
        "strategy": "强烈建议卖出或做空苹果股票，目标价$160，止损$190。可以考虑买入看跌期权。"
    }
    
    print("\n📊 Tom的分析结果:")
    print(f"   评分: {tom_analysis['score']}/100")
    print(f"   建议: {tom_analysis['recommendation']}")
    print(f"   方向: {tom_analysis['market_direction']} ({tom_analysis['direction_strength']})")
    
    # 获取期权数据
    from dual_strategy_api import get_option_chain
    
    symbol = 'AAPL'
    option_chain = get_option_chain(symbol)
    
    if not option_chain:
        print("❌ 无法获取期权数据")
        return False
    
    print(f"\n✅ 获取到 {len(option_chain.get('data', []))} 个期权")
    
    # 调用AI Agent Jany（激进风格）
    print("\n🤖 调用AI Agent Jany生成策略（激进风格）...")
    
    try:
        from ai_strategy_agent import get_ai_strategy_agent
        
        jany = get_ai_strategy_agent()
        
        strategy_result = jany.generate_trading_strategy(
            symbol='AAPL',
            current_price=182.50,
            tom_analysis=tom_analysis,
            option_chain_data=option_chain,
            investment_style='soros',  # 索罗斯激进风格
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
        print(f"期权代码: {option_strategy.get('symbol')}")
        print(f"执行价: ${option_strategy.get('strike_price')}")
        print(f"到期日: {option_strategy.get('expiry_date')}")
        print(f"等价股数: {option_strategy.get('equivalent_shares')}股")
        print(f"总期权费: ${option_strategy.get('total_premium')}")
        print(f"Delta: {option_strategy.get('delta')}")
        print(f"推荐理由: {option_strategy.get('reasoning')}")
        
        print("\n" + "=" * 80)
        print("📈 Delta One股票策略:")
        print("=" * 80)
        
        stock_strategy = strategy_result.get('stock_strategy', {})
        print(f"类型: {stock_strategy.get('type')}")
        print(f"股数: {stock_strategy.get('shares')}股")
        print(f"名义本金: ${stock_strategy.get('notional')}")
        print(f"保证金: ${stock_strategy.get('margin')}")
        print(f"推荐理由: {stock_strategy.get('reasoning')}")
        
        print("\n" + "=" * 80)
        print("💡 综合说明:")
        print("=" * 80)
        print(strategy_result.get('explanation', ''))
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_bearish_scenario()
    
    if success:
        print("\n✅ 看跌场景测试成功！")
        sys.exit(0)
    else:
        print("\n❌ 看跌场景测试失败")
        sys.exit(1)

