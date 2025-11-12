"""
测试完整的对话和策略生成流程
验证Tom-用户-Jany共享上下文
"""

import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_full_conversation_flow():
    """测试完整流程"""
    
    symbol = "META"
    username = "test_user"
    
    # 1️⃣ Tom初步分析
    print_section("1️⃣ Tom初步分析")
    
    initial_response = requests.post(
        f"{BASE_URL}/api/chat/tom/initial-analysis",
        json={
            "symbol": symbol,
            "username": username,
            "investment_style": "buffett",
            "news_context": "",
            "user_opinion": ""
        }
    )
    
    initial_data = initial_response.json()
    print(f"✅ Tom初步分析成功")
    print(f"📦 返回数据: {json.dumps(initial_data, indent=2, ensure_ascii=False)[:500]}...")
    
    # 检查返回结构
    if 'analysis' not in initial_data:
        print(f"⚠️  警告: 返回数据中没有'analysis'字段")
        print(f"   实际字段: {list(initial_data.keys())}")
        return
    
    print(f"   推荐: {initial_data['analysis'].get('recommendation', 'N/A')}")
    print(f"   选择的指标: {initial_data['analysis'].get('selected_indicators', {})}")
    
    # 模拟对话历史
    conversation_history = [
        {
            "role": "assistant",
            "content": initial_data['analysis'].get('summary', '初步分析完成'),
            "initial_analysis": True
        }
    ]
    
    # 2️⃣ 用户与Tom对话
    print_section("2️⃣ 用户与Tom对话")
    
    user_questions = [
        "ROE为什么这么高？",
        "能看看价格走势吗？",
        "技术指标怎么样？"
    ]
    
    for i, question in enumerate(user_questions, 1):
        print(f"\n👤 用户问题{i}: {question}")
        
        # 添加用户消息到历史
        conversation_history.append({
            "role": "user",
            "content": question
        })
        
        # Tom回复
        tom_response = requests.post(
            f"{BASE_URL}/api/chat/tom/message",
            json={
                "symbol": symbol,
                "user_message": question,
                "conversation_history": conversation_history[:-1],  # 不包含当前用户消息
                "stock_context": {
                    "symbol": symbol,
                    "investment_style": "buffett",
                    "initial_analysis": initial_data['analysis']
                }
            }
        )
        
        tom_data = tom_response.json()
        if tom_data.get('success'):
            print(f"🤖 Tom回复: {tom_data['tom_reply'][:100]}...")
            print(f"   意图: {tom_data.get('intent', 'general')}")
            
            # 添加Tom回复到历史
            conversation_history.append({
                "role": "assistant",
                "content": tom_data['tom_reply'],
                "intent": tom_data.get('intent'),
                "price_chart_data": tom_data.get('price_chart_data'),
                "indicators_data": tom_data.get('indicators_data')
            })
    
    print(f"\n📊 当前对话历史长度: {len(conversation_history)}")
    
    # 3️⃣ 第一次生成策略
    print_section("3️⃣ Jany第一次生成策略")
    
    strategy1_response = requests.post(
        f"{BASE_URL}/api/dual-strategy/generate",
        json={
            "symbol": symbol,
            "username": username,
            "notional_value": 30000,
            "investment_style": "buffett",
            "ai_analysis": initial_data['analysis'],
            "conversation_history": conversation_history,
            "timestamp": int(datetime.now().timestamp() * 1000)
        }
    )
    
    strategy1_data = strategy1_response.json()
    if strategy1_data.get('option_strategy'):
        print(f"✅ 策略1生成成功")
        print(f"   期权: {strategy1_data['option_strategy']['type']}")
        print(f"   执行价: ${strategy1_data['option_strategy']['strike_price']}")
        print(f"   期权费: ${strategy1_data['option_strategy'].get('total_premium', 0):.2f}")
        print(f"   推荐理由: {strategy1_data.get('explanation', 'N/A')[:100]}...")
        
        # 添加Jany策略到历史
        conversation_history.append({
            "role": "jany",
            "content": f"基于您与Tom的{len(conversation_history)}条对话，我生成了策略",
            "strategy_data": strategy1_data,
            "timestamp": int(datetime.now().timestamp() * 1000)
        })
    else:
        print(f"❌ 策略1生成失败: {strategy1_data.get('error', 'Unknown')}")
        return
    
    # 4️⃣ 用户反馈策略
    print_section("4️⃣ 用户对策略的反馈")
    
    user_feedback = "这个策略太保守了，我想要更激进的策略，能承受更高风险"
    print(f"👤 用户反馈: {user_feedback}")
    
    conversation_history.append({
        "role": "user",
        "content": user_feedback
    })
    
    # Tom回复用户反馈
    tom_feedback_response = requests.post(
        f"{BASE_URL}/api/chat/tom/message",
        json={
            "symbol": symbol,
            "user_message": user_feedback,
            "conversation_history": conversation_history[:-1],
            "stock_context": {
                "symbol": symbol,
                "investment_style": "buffett",
                "initial_analysis": initial_data['analysis']
            }
        }
    )
    
    tom_feedback_data = tom_feedback_response.json()
    if tom_feedback_data.get('success'):
        print(f"🤖 Tom回复: {tom_feedback_data['tom_reply'][:150]}...")
        conversation_history.append({
            "role": "assistant",
            "content": tom_feedback_data['tom_reply']
        })
    
    print(f"\n📊 更新后对话历史长度: {len(conversation_history)}")
    
    # 5️⃣ 重新生成策略（基于反馈）
    print_section("5️⃣ Jany重新生成策略（基于用户反馈）")
    
    strategy2_response = requests.post(
        f"{BASE_URL}/api/dual-strategy/generate",
        json={
            "symbol": symbol,
            "username": username,
            "notional_value": 30000,
            "investment_style": "soros",  # 改为更激进的风格
            "ai_analysis": initial_data['analysis'],
            "conversation_history": conversation_history,  # 包含用户反馈
            "timestamp": int(datetime.now().timestamp() * 1000)  # 新的timestamp
        }
    )
    
    strategy2_data = strategy2_response.json()
    if strategy2_data.get('option_strategy'):
        print(f"✅ 策略2生成成功")
        print(f"   期权: {strategy2_data['option_strategy']['type']}")
        print(f"   执行价: ${strategy2_data['option_strategy']['strike_price']}")
        print(f"   期权费: ${strategy2_data['option_strategy'].get('total_premium', 0):.2f}")
        print(f"   推荐理由: {strategy2_data.get('explanation', 'N/A')[:100]}...")
        
        # 对比两次策略
        print_section("📊 策略对比")
        print(f"策略1（保守）:")
        print(f"  - 类型: {strategy1_data['option_strategy']['type']}")
        print(f"  - 期权费: ${strategy1_data['option_strategy'].get('total_premium', 0):.2f}")
        print(f"\n策略2（激进）:")
        print(f"  - 类型: {strategy2_data['option_strategy']['type']}")
        print(f"  - 期权费: ${strategy2_data['option_strategy'].get('total_premium', 0):.2f}")
        
        if strategy1_data['option_strategy']['type'] != strategy2_data['option_strategy']['type']:
            print(f"\n✅ 策略类型已改变！Jany成功响应了用户反馈")
        else:
            print(f"\n⚠️  策略类型相同，但参数可能不同")
    else:
        print(f"❌ 策略2生成失败: {strategy2_data.get('error', 'Unknown')}")
    
    print_section("✅ 测试完成")
    print(f"最终对话历史长度: {len(conversation_history)}")
    print(f"包含:")
    print(f"  - Tom初步分析: 1条")
    print(f"  - 用户提问: {len([m for m in conversation_history if m['role'] == 'user'])}条")
    print(f"  - Tom回复: {len([m for m in conversation_history if m['role'] == 'assistant'])}条")
    print(f"  - Jany策略: {len([m for m in conversation_history if m['role'] == 'jany'])}条")

if __name__ == "__main__":
    try:
        test_full_conversation_flow()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

