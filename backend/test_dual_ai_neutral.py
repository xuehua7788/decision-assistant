#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试双AI Agent系统 - 观望场景
"""

import os
import sys

if not os.getenv('DEEPSEEK_API_KEY'):
    print("⚠️ 请设置DEEPSEEK_API_KEY环境变量")
    sys.exit(1)

os.environ['ALPHA_VANTAGE_KEY'] = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')

def test_neutral_scenario():
    """测试观望场景"""
    
    print("=" * 80)
    print("🧪 测试双AI系统 - 观望场景")
    print("=" * 80)
    
    # 模拟Tom的观望分析
    tom_analysis = {
        "score": 55,
        "recommendation": "观望",
        "market_direction": "neutral",
        "direction_strength": "weak",
        "position_size": "0%",
        "target_price": 185.0,
        "stop_loss": 180.0,
        "key_points": [
            "基本面稳定，但无明显亮点",
            "技术面震荡，方向不明",
            "宏观环境不确定性较大"
        ],
        "analysis_summary": "综合来看，苹果基本面稳定，但技术面方向不明，宏观环境不确定。建议观望等待更好机会。",
        "strategy": "当前不是大举买入的时候，建议观望。如果一定要参与，可以小仓位试探，等待明确信号。"
    }
    
    print("\n📊 Tom的分析结果:")
    print(f"   评分: {tom_analysis['score']}/100")
    print(f"   建议: {tom_analysis['recommendation']}")
    print(f"   方向: {tom_analysis['market_direction']} ({tom_analysis['direction_strength']})")
    print(f"   策略: {tom_analysis['strategy']}")
    
    # 获取期权数据
    from dual_strategy_api import get_option_chain
    
    symbol = 'AAPL'
    option_chain = get_option_chain(symbol)
    
    if not option_chain:
        print("❌ 无法获取期权数据")
        return False
    
    print(f"\n✅ 获取到 {len(option_chain.get('data', []))} 个期权")
    
    # 调用AI Agent Jany（平衡风格）
    print("\n🤖 调用AI Agent Jany生成策略（平衡风格）...")
    
    try:
        from ai_strategy_agent import get_ai_strategy_agent
        
        jany = get_ai_strategy_agent()
        
        strategy_result = jany.generate_trading_strategy(
            symbol='AAPL',
            current_price=182.50,
            tom_analysis=tom_analysis,
            option_chain_data=option_chain,
            investment_style='balanced',
            notional_value=30000
        )
        
        if not strategy_result:
            print("❌ AI策略生成失败")
            return False
        
        print("\n✅ AI策略生成成功！")
        
        # 检查是否是观望建议
        if 'recommendation' in strategy_result and strategy_result['recommendation'] == '观望':
            print("\n" + "=" * 80)
            print("💡 AI建议:")
            print("=" * 80)
            print(f"建议: {strategy_result['recommendation']}")
            print(f"说明: {strategy_result.get('explanation', '')}")
            return True
        
        # 如果有具体策略
        print("\n" + "=" * 80)
        print("📊 期权策略:")
        print("=" * 80)
        
        option_strategy = strategy_result.get('option_strategy', {})
        print(f"类型: {option_strategy.get('type')}")
        print(f"期权代码: {option_strategy.get('symbol')}")
        print(f"执行价: ${option_strategy.get('strike_price')}")
        print(f"推荐理由: {option_strategy.get('reasoning')}")
        
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
    success = test_neutral_scenario()
    
    if success:
        print("\n✅ 观望场景测试成功！")
        sys.exit(0)
    else:
        print("\n❌ 观望场景测试失败")
        sys.exit(1)

