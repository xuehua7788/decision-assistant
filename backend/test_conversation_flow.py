#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试对话式交互流程
"""

import os
import sys

if not os.getenv('DEEPSEEK_API_KEY'):
    print("⚠️ 请设置DEEPSEEK_API_KEY环境变量")
    sys.exit(1)

os.environ['ALPHA_VANTAGE_KEY'] = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')

def test_conversation_flow():
    """测试完整对话流程"""
    
    print("=" * 80)
    print("🧪 测试对话式交互流程")
    print("=" * 80)
    
    # 步骤1：Tom初步分析（模拟）
    print("\n📊 步骤1：Tom进行初步分析...")
    print("   （实际应用中，这一步会调用 /api/chat/tom/initial-analysis）")
    
    # 模拟Tom的初步分析结果
    initial_analysis = {
        "score": 68,
        "recommendation": "适度买入",
        "market_direction": "bullish",
        "direction_strength": "moderate",
        "position_size": "15%",
        "target_price": 330.0,
        "stop_loss": 300.0,
        "key_points": [
            "ROE高达147%，远超行业平均，显示极强的盈利能力",
            "新AI芯片发布，技术创新推动业务增长",
            "MACD金叉，技术面显示上升动能"
        ],
        "analysis_summary": "IBM基本面稳健，ROE表现优异，新AI芯片发布是重要催化剂。技术面MACD金叉显示上升动能。综合来看，适度看涨。",
        "strategy": "建议适度买入IBM股票，目标价$330，止损$300。可以分批建仓，先买入15%仓位。"
    }
    
    print(f"\n✅ Tom初步分析完成:")
    print(f"   评分: {initial_analysis['score']}/100")
    print(f"   建议: {initial_analysis['recommendation']}")
    print(f"   方向: {initial_analysis['market_direction']}")
    print(f"   关键要点: {', '.join(initial_analysis['key_points'][:2])}")
    
    # 步骤2：用户与Tom对话
    print("\n💬 步骤2：用户与Tom对话...")
    
    from chat_with_tom_api import get_tom_chat_agent
    
    tom = get_tom_chat_agent()
    
    # 构建股票上下文
    stock_context = {
        'symbol': 'IBM',
        'current_price': 182.50,
        'investment_style': 'buffett',
        'initial_analysis': initial_analysis,
        'news_context': 'IBM发布新一代AI芯片，性能提升50%'
    }
    
    conversation_history = []
    
    # 第一轮对话
    user_msg_1 = "ROE为什么这么高？这说明什么？"
    print(f"\n用户: {user_msg_1}")
    
    tom_reply_1 = tom.chat(
        conversation_history=conversation_history,
        stock_context=stock_context,
        user_message=user_msg_1
    )
    
    print(f"Tom: {tom_reply_1[:200]}...")
    
    conversation_history.append({"role": "user", "content": user_msg_1})
    conversation_history.append({"role": "assistant", "content": tom_reply_1})
    
    # 第二轮对话
    user_msg_2 = "这条AI芯片的新闻对股价影响大吗？"
    print(f"\n用户: {user_msg_2}")
    
    tom_reply_2 = tom.chat(
        conversation_history=conversation_history,
        stock_context=stock_context,
        user_message=user_msg_2
    )
    
    print(f"Tom: {tom_reply_2[:200]}...")
    
    conversation_history.append({"role": "user", "content": user_msg_2})
    conversation_history.append({"role": "assistant", "content": tom_reply_2})
    
    print(f"\n✅ 对话完成，共{len(conversation_history)}条消息")
    
    # 步骤3：Jany生成策略（基于对话历史）
    print("\n🤖 步骤3：Jany基于对话历史生成策略...")
    
    from dual_strategy_api import get_option_chain
    from ai_strategy_agent import get_ai_strategy_agent
    
    # 获取期权数据
    option_chain = get_option_chain('IBM')
    
    if not option_chain:
        print("❌ 无法获取期权数据")
        return False
    
    print(f"   期权数据: {len(option_chain.get('data', []))}个期权")
    
    # Jany生成策略
    jany = get_ai_strategy_agent()
    
    strategy_result = jany.generate_trading_strategy(
        symbol='IBM',
        current_price=182.50,
        tom_analysis=initial_analysis,
        option_chain_data=option_chain,
        investment_style='buffett',
        notional_value=30000,
        conversation_history=conversation_history  # 关键：传递对话历史
    )
    
    if not strategy_result:
        print("❌ Jany策略生成失败")
        return False
    
    print("\n✅ Jany策略生成成功！")
    print("\n" + "=" * 80)
    print("📊 期权策略:")
    print("=" * 80)
    
    option_strategy = strategy_result.get('option_strategy', {})
    print(f"类型: {option_strategy.get('type')}")
    print(f"期权代码: {option_strategy.get('symbol')}")
    print(f"执行价: ${option_strategy.get('strike_price')}")
    print(f"总期权费: ${option_strategy.get('total_premium')}")
    print(f"推荐理由: {option_strategy.get('reasoning', '')[:150]}...")
    
    print("\n" + "=" * 80)
    print("📈 Delta One股票策略:")
    print("=" * 80)
    
    stock_strategy = strategy_result.get('stock_strategy', {})
    print(f"类型: {stock_strategy.get('type')}")
    print(f"股数: {stock_strategy.get('shares')}股")
    print(f"名义本金: ${stock_strategy.get('notional')}")
    print(f"保证金: ${stock_strategy.get('margin')}")
    
    print("\n" + "=" * 80)
    print("💡 综合说明:")
    print("=" * 80)
    print(strategy_result.get('explanation', '')[:300])
    
    return True

if __name__ == '__main__':
    success = test_conversation_flow()
    
    if success:
        print("\n" + "=" * 80)
        print("✅ 对话式交互流程测试成功！")
        print("=" * 80)
        print("\n新交互模式特点：")
        print("1. ✅ Tom自主选择指标进行初步分析")
        print("2. ✅ 用户可以与Tom多轮对话讨论")
        print("3. ✅ Jany基于完整对话历史生成策略")
        print("4. ✅ 策略更贴合用户实际需求")
        sys.exit(0)
    else:
        print("\n❌ 测试失败")
        sys.exit(1)

