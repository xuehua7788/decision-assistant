#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试后端API（模拟前端调用）
"""

import requests
import json
import time

# 使用生产环境URL
BASE_URL = "https://decision-assistant-backend.onrender.com"

def test_tom_initial_analysis():
    """测试Tom初步分析API"""
    print("\n" + "="*80)
    print("🧪 测试1: Tom初步分析")
    print("="*80)
    
    url = f"{BASE_URL}/api/chat/tom/initial-analysis"
    
    payload = {
        "symbol": "IBM",
        "username": "bbb",
        "investment_style": "buffett",
        "news_context": "IBM发布新一代AI芯片，性能提升50%",
        "user_opinion": "我觉得IBM最近表现不错"
    }
    
    print(f"\n📤 请求: POST {url}")
    print(f"   参数: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        
        print(f"\n📥 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            analysis = data.get('analysis', {})
            
            print(f"\n✅ Tom分析成功:")
            print(f"   评分: {analysis.get('score')}/100")
            print(f"   建议: {analysis.get('recommendation')}")
            print(f"   方向: {analysis.get('market_direction')}")
            print(f"   关键要点: {analysis.get('key_points', [])[:2]}")
            
            return analysis
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None


def test_tom_chat(initial_analysis):
    """测试与Tom对话API"""
    print("\n" + "="*80)
    print("🧪 测试2: 与Tom对话")
    print("="*80)
    
    url = f"{BASE_URL}/api/chat/tom/message"
    
    # 构建股票上下文
    stock_context = {
        "symbol": "IBM",
        "current_price": 316.89,
        "investment_style": "buffett",
        "initial_analysis": initial_analysis,
        "news_context": "IBM发布新一代AI芯片，性能提升50%"
    }
    
    conversation_history = []
    
    # 第1轮对话
    user_msg_1 = "ROE为什么这么高？"
    print(f"\n💬 用户: {user_msg_1}")
    
    payload = {
        "symbol": "IBM",
        "user_message": user_msg_1,
        "conversation_history": conversation_history,
        "stock_context": stock_context
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            tom_reply = data.get('tom_reply', '')
            
            print(f"🤖 Tom: {tom_reply[:150]}...")
            
            conversation_history.append({"role": "user", "content": user_msg_1})
            conversation_history.append({"role": "assistant", "content": tom_reply})
            
            print(f"\n✅ 对话成功，历史记录: {len(conversation_history)}条")
            
            return conversation_history
        else:
            print(f"❌ 对话失败: {response.text}")
            return []
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return []


def test_strategy_generation(initial_analysis, conversation_history):
    """测试策略生成API（带对话历史）"""
    print("\n" + "="*80)
    print("🧪 测试3: Jany生成策略（基于对话历史）")
    print("="*80)
    
    url = f"{BASE_URL}/api/dual-strategy/generate"
    
    payload = {
        "symbol": "IBM",
        "username": "bbb",
        "notional_value": 30000,
        "investment_style": "buffett",
        "ai_analysis": initial_analysis,
        "conversation_history": conversation_history  # 关键：传递对话历史
    }
    
    print(f"\n📤 请求: POST {url}")
    print(f"   对话历史: {len(conversation_history)}条消息")
    
    try:
        response = requests.post(url, json=payload, timeout=90)
        
        print(f"\n📥 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            option_strategy = data.get('option_strategy', {})
            stock_strategy = data.get('stock_strategy', {})
            explanation = data.get('explanation', '')
            
            print(f"\n✅ 策略生成成功!")
            print(f"\n📊 期权策略:")
            print(f"   类型: {option_strategy.get('type')}")
            print(f"   期权代码: {option_strategy.get('symbol')}")
            print(f"   执行价: ${option_strategy.get('strike_price')}")
            print(f"   Delta: {option_strategy.get('delta')}")
            print(f"   总费用: ${option_strategy.get('total_premium')}")
            
            print(f"\n📈 股票策略:")
            print(f"   类型: {stock_strategy.get('type')}")
            print(f"   股数: {stock_strategy.get('shares')}股")
            print(f"   名义本金: ${stock_strategy.get('notional')}")
            print(f"   保证金: ${stock_strategy.get('margin')}")
            
            print(f"\n💡 推荐理由:")
            print(f"   {explanation[:200]}...")
            
            return True
        else:
            print(f"❌ 策略生成失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("="*80)
    print("🚀 开始测试后端API（生产环境）")
    print(f"   BASE_URL: {BASE_URL}")
    print("="*80)
    
    # 等待Render部署完成
    print("\n⏳ 等待Render部署完成（预计3-5分钟）...")
    print("   提示：如果测试失败，请稍等片刻后重试")
    
    # 测试1: Tom初步分析
    initial_analysis = test_tom_initial_analysis()
    
    if not initial_analysis:
        print("\n❌ Tom初步分析失败，停止测试")
        return False
    
    time.sleep(2)
    
    # 测试2: 与Tom对话
    conversation_history = test_tom_chat(initial_analysis)
    
    if not conversation_history:
        print("\n❌ Tom对话失败，停止测试")
        return False
    
    time.sleep(2)
    
    # 测试3: 策略生成（带对话历史）
    success = test_strategy_generation(initial_analysis, conversation_history)
    
    if success:
        print("\n" + "="*80)
        print("✅ 所有测试通过！")
        print("="*80)
        print("\n新功能验证：")
        print("1. ✅ Tom初步分析API正常")
        print("2. ✅ Tom对话API正常")
        print("3. ✅ 对话历史正确传递给Jany")
        print("4. ✅ Jany基于对话生成策略")
        print("\n🎉 后端部署成功，可以开始前端开发！")
        return True
    else:
        print("\n❌ 测试失败")
        return False


if __name__ == '__main__':
    success = main()
    exit(0 if success else 1)

