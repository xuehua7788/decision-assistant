"""
测试AI意图分析功能
"""
import os
import sys
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_ai_intent_analysis():
    """测试AI意图分析"""
    import requests
    
    deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY not found")
        return
    
    print(f"✅ DEEPSEEK_API_KEY found: {deepseek_api_key[:10]}...")
    
    # 测试用例
    test_cases = [
        {
            "name": "测试1: 我朋友看涨（应该返回false）",
            "message": "我朋友强烈看涨特斯拉",
            "expected": "need_option_strategy: false"
        },
        {
            "name": "测试2: 我自己看涨（应该返回true + bullish）",
            "message": "我强烈看涨特斯拉",
            "expected": "need_option_strategy: true, direction: bullish"
        },
        {
            "name": "测试3: 我不看涨（应该返回true + bearish）",
            "message": "我不看涨特斯拉",
            "expected": "need_option_strategy: true, direction: bearish"
        },
        {
            "name": "测试4: 我看跌（应该返回true + bearish）",
            "message": "我看跌苹果股票",
            "expected": "need_option_strategy: true, direction: bearish"
        },
        {
            "name": "测试5: 普通问题（应该返回false）",
            "message": "什么是期权？",
            "expected": "need_option_strategy: false"
        },
        {
            "name": "测试6: 复杂场景 - 朋友看涨但我不认同（应该返回true + bearish/neutral）",
            "message": "我朋友强烈看涨特斯拉，但我不认同",
            "expected": "need_option_strategy: true, direction: bearish or neutral (用户持相反观点)"
        }
    ]
    
    system_prompt = """你是一个专业的决策助手。分析用户的投资意图并判断是否需要期权策略推荐。

如果用户表达了自己的投资观点（看涨/看跌某只股票），请返回JSON格式：
{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "股票代码",
    "direction": "bullish/bearish/neutral",
    "strength": "strong/moderate/slight",
    "risk_profile": "aggressive/balanced/conservative"
  },
  "reasoning": "简短解释用户的意图"
}

重要规则：
1. 只有当用户明确表达**自己**的投资观点时才返回期权策略
2. 如果用户仅描述他人观点（"我朋友看涨"、"他人认为"），没有表达自己态度，返回need_option_strategy: false
3. 如果用户表达了与他人相反的观点（"我朋友看涨，但我不认同"、"他看涨但我不同意"），这是用户的投资观点，返回need_option_strategy: true，direction为相反方向
4. 如果用户说"我不看涨"、"我不认为会涨"，direction应该是bearish或neutral
5. 否则，正常对话

示例1：
用户："我朋友强烈看涨特斯拉"
回复：{
  "need_option_strategy": false,
  "reasoning": "这是朋友的观点，不是用户自己的投资意图"
}

示例2：
用户："我强烈看涨特斯拉"
回复：{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "TSLA",
    "direction": "bullish",
    "strength": "strong",
    "risk_profile": "balanced"
  },
  "reasoning": "用户明确表达了看涨TSLA的观点"
}

示例3：
用户："我不看涨特斯拉"
回复：{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "TSLA",
    "direction": "bearish",
    "strength": "moderate",
    "risk_profile": "balanced"
  },
  "reasoning": "用户表达了不看涨，即看跌或中性的观点"
}

示例4：
用户："我朋友强烈看涨特斯拉，但我不认同"
回复：{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "TSLA",
    "direction": "bearish",
    "strength": "moderate",
    "risk_profile": "balanced"
  },
  "reasoning": "用户明确表示不认同朋友的看涨观点，表达了自己看跌或中性的立场"
}

用中文回复，JSON格式要完整。"""
    
    headers = {
        "Authorization": f"Bearer {deepseek_api_key}",
        "Content-Type": "application/json",
    }
    
    print("\n" + "="*80)
    print("开始测试AI意图分析")
    print("="*80 + "\n")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"{test_case['name']}")
        print(f"{'='*80}")
        print(f"用户输入: {test_case['message']}")
        print(f"期望结果: {test_case['expected']}")
        print(f"{'-'*80}")
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": test_case['message']}
            ],
            "temperature": 0.7,
            "max_tokens": 500,
        }
        
        try:
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                
                print(f"AI原始响应:\n{ai_response}")
                print(f"{'-'*80}")
                
                # 尝试解析JSON
                try:
                    intent = json.loads(ai_response.strip())
                    print(f"\n✅ JSON解析成功:")
                    print(f"   - need_option_strategy: {intent.get('need_option_strategy')}")
                    
                    if intent.get('need_option_strategy'):
                        user_intent = intent.get('user_intent', {})
                        print(f"   - ticker: {user_intent.get('ticker')}")
                        print(f"   - direction: {user_intent.get('direction')}")
                        print(f"   - strength: {user_intent.get('strength')}")
                        print(f"   - risk_profile: {user_intent.get('risk_profile')}")
                    
                    print(f"   - reasoning: {intent.get('reasoning')}")
                    
                except json.JSONDecodeError as e:
                    print(f"\n❌ JSON解析失败: {e}")
                    
            else:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"   {response.text}")
                
        except Exception as e:
            print(f"❌ 测试失败: {e}")
        
        print()


def test_option_strategy_mapping():
    """测试AI提取的意图能否正确映射到期权策略"""
    from algorithms.option_nlp_parser import ParsedIntent
    from algorithms.option_strategy_mapper import StrategyMapper
    
    print("\n" + "="*80)
    print("测试期权策略映射")
    print("="*80 + "\n")
    
    # 模拟AI提取的意图
    test_intents = [
        {
            "name": "强烈看涨 + 平衡风险",
            "intent": ParsedIntent(
                ticker="TSLA",
                direction="bullish",
                strength="strong",
                timeframe="short",
                risk_profile="balanced",
                confidence=0.9,
                raw_text="我强烈看涨特斯拉"
            ),
            "price": 250.0
        },
        {
            "name": "看跌 + 保守风险",
            "intent": ParsedIntent(
                ticker="AAPL",
                direction="bearish",
                strength="moderate",
                timeframe="medium",
                risk_profile="conservative",
                confidence=0.9,
                raw_text="我不看涨苹果"
            ),
            "price": 180.0
        }
    ]
    
    mapper = StrategyMapper()
    
    for test in test_intents:
        print(f"\n{'='*80}")
        print(f"测试: {test['name']}")
        print(f"{'='*80}")
        print(f"原始输入: {test['intent'].raw_text}")
        print(f"\n提取的意图:")
        print(f"  - ticker: {test['intent'].ticker}")
        print(f"  - direction: {test['intent'].direction}")
        print(f"  - strength: {test['intent'].strength}")
        print(f"  - risk_profile: {test['intent'].risk_profile}")
        print(f"  - 当前价格: ${test['price']}")
        
        try:
            strategy = mapper.map_strategy(test['intent'], test['price'])
            
            print(f"\n✅ 策略映射成功:")
            print(f"   策略名称: {strategy.name}")
            print(f"   策略类型: {strategy.type}")
            print(f"   风险等级: {strategy.risk_level}")
            print(f"   描述: {strategy.description}")
            print(f"\n   参数:")
            print(f"   - 买入执行价: ${strategy.parameters.get('buy_strike', 'N/A')}")
            print(f"   - 卖出执行价: ${strategy.parameters.get('sell_strike', 'N/A')}")
            print(f"   - 支付权利金: ${strategy.parameters.get('premium_paid', 'N/A')}")
            print(f"   - 收到权利金: ${strategy.parameters.get('premium_received', 'N/A')}")
            print(f"\n   风险指标:")
            print(f"   - 最大收益: ${strategy.metrics.get('max_gain', 'N/A')}")
            print(f"   - 最大损失: ${strategy.metrics.get('max_loss', 'N/A')}")
            print(f"   - 盈亏平衡: ${strategy.metrics.get('breakeven', 'N/A')}")
            print(f"   - Payoff数据点: {len(strategy.payoff_data)} 个")
            
        except Exception as e:
            print(f"\n❌ 策略映射失败: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    print("\n" + "🔬 "*20)
    print("期权策略AI意图分析测试")
    print("🔬 "*20 + "\n")
    
    # 测试1: AI意图分析
    test_ai_intent_analysis()
    
    # 测试2: 策略映射
    test_option_strategy_mapping()
    
    print("\n" + "="*80)
    print("测试完成！")
    print("="*80 + "\n")

