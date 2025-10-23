#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试双AI协同工作：
AI #1: 意图监听（判断是否需要期权策略）
AI #2: 聊天助手（自然对话）
都带上下文（聊天历史）
"""

import os
import json
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
if not DEEPSEEK_API_KEY:
    print("❌ 错误：未找到 DEEPSEEK_API_KEY")
    exit(1)

print(f"✅ API Key: {DEEPSEEK_API_KEY[:10]}...")


def build_messages_from_history(chat_history):
    """将聊天历史转换为API消息格式"""
    messages = []
    for msg in chat_history:
        if msg['sender'] == 'user':
            messages.append({"role": "user", "content": msg['text']})
        else:
            messages.append({"role": "assistant", "content": msg['text']})
    return messages


def call_ai_for_intent_analysis(message, chat_history):
    """
    AI #1: 意图监听
    分析用户是否想要期权策略推荐
    """
    system_prompt = """你是一个专业的决策助手。分析用户的投资意图并判断是否需要期权策略推荐。

**重要规则**：
1. 仔细分析用户的真实投资观点（不是朋友、他人的观点）
2. 只有当用户明确表达自己对某个股票的投资方向时，才判断为需要期权策略
3. 注意识别否定词：如"不认同"、"不看好"、"但我不是"等，需要反向理解
4. 如果用户只是询问信息、讨论市场、或表达中性观点，则不需要期权策略

**必须返回JSON格式**（不要有任何额外文字）：
{
  "need_option_strategy": true/false,
  "user_intent": {
    "ticker": "股票代码，如TSLA",
    "direction": "bullish/bearish/neutral",
    "strength": "strong/moderate/weak",
    "risk_profile": "aggressive/balanced/conservative"
  },
  "reasoning": "你的分析理由"
}

**示例**：
输入: "我朋友强烈看涨特斯拉，但我不认同"
输出:
{
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

    # 构建消息列表（带聊天历史）
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(build_messages_from_history(chat_history))
    messages.append({"role": "user", "content": message})
    
    print(f"\n{'='*60}")
    print("🤖 AI #1: 意图监听")
    print(f"{'='*60}")
    print(f"📝 发送消息数: {len(messages)}")
    for i, msg in enumerate(messages):
        role = msg['role']
        content = msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']
        print(f"  [{i+1}] {role}: {content}")
    
    # 调用DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ API调用失败: {response.status_code}")
        print(response.text)
        return None
    
    result = response.json()
    ai_response = result["choices"][0]["message"]["content"]
    
    print(f"\n📥 AI #1 返回:")
    print(ai_response)
    
    # 解析JSON
    try:
        intent_analysis = json.loads(ai_response.strip())
        print(f"\n✅ 解析成功:")
        print(f"  - need_option_strategy: {intent_analysis.get('need_option_strategy')}")
        print(f"  - reasoning: {intent_analysis.get('reasoning')}")
        if intent_analysis.get('user_intent'):
            print(f"  - user_intent: {intent_analysis.get('user_intent')}")
        return intent_analysis
    except json.JSONDecodeError as e:
        print(f"❌ JSON解析失败: {e}")
        return None


def call_ai_for_chat(message, chat_history, intent_context=None):
    """
    AI #2: 聊天助手
    自然对话回复
    """
    system_prompt = """你是一个专业、友好的决策助手。

**你的职责**：
- 与用户自然地聊天，回答各种问题
- 如果用户询问投资相关的信息（如股票行情、公司新闻），可以讨论，但不要主动推荐期权策略
- 如果用户明确表达了投资观点，系统会自动触发期权分析，你不需要提及

**回复风格**：
- 自然、友好、专业
- 不要生硬地提示"如果您想要期权策略..."
- 根据上下文理解用户意图

请用中文自然地回复用户。"""

    if intent_context:
        system_prompt += f"\n\n**当前分析**: {intent_context}"
    
    # 构建消息列表（带聊天历史）
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(build_messages_from_history(chat_history))
    messages.append({"role": "user", "content": message})
    
    print(f"\n{'='*60}")
    print("💬 AI #2: 聊天助手")
    print(f"{'='*60}")
    print(f"📝 发送消息数: {len(messages)}")
    for i, msg in enumerate(messages):
        role = msg['role']
        content = msg['content'][:100] + '...' if len(msg['content']) > 100 else msg['content']
        print(f"  [{i+1}] {role}: {content}")
    
    # 调用DeepSeek API
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ API调用失败: {response.status_code}")
        print(response.text)
        return None
    
    result = response.json()
    chat_response = result["choices"][0]["message"]["content"]
    
    print(f"\n📥 AI #2 返回:")
    print(chat_response)
    
    return chat_response


def test_scenario(scenario_name, chat_history, user_message):
    """测试一个场景"""
    print(f"\n\n{'#'*80}")
    print(f"# 测试场景: {scenario_name}")
    print(f"{'#'*80}")
    print(f"\n📜 聊天历史:")
    for msg in chat_history:
        print(f"  {msg['sender']}: {msg['text']}")
    print(f"\n💬 用户新消息: {user_message}")
    
    # 步骤1: AI #1 意图分析
    intent_result = call_ai_for_intent_analysis(user_message, chat_history)
    
    if not intent_result:
        print("\n❌ 意图分析失败")
        return
    
    # 步骤2: 根据意图决定下一步
    if intent_result.get('need_option_strategy'):
        print(f"\n{'='*60}")
        print("🎯 触发期权策略！")
        print(f"{'='*60}")
        print(f"📊 投资意图:")
        print(f"  {json.dumps(intent_result.get('user_intent'), ensure_ascii=False, indent=2)}")
        print(f"\n✅ 应返回: 期权策略 + 图表")
    else:
        print(f"\n{'='*60}")
        print("💬 继续普通聊天")
        print(f"{'='*60}")
        
        # 调用AI #2
        chat_response = call_ai_for_chat(
            message=user_message,
            chat_history=chat_history,
            intent_context=intent_result.get('reasoning')
        )
        
        if chat_response:
            print(f"\n✅ 应返回给用户:")
            print(f"{'='*60}")
            print(chat_response)
            print(f"{'='*60}")


def main():
    print("🧪 双AI协同工作测试")
    print("="*80)
    
    # 测试场景1: 普通聊天（无投资意图）
    test_scenario(
        scenario_name="场景1: 普通闲聊",
        chat_history=[],
        user_message="今天天气怎么样？"
    )
    
    # 测试场景2: 询问股票信息（无明确投资方向）
    test_scenario(
        scenario_name="场景2: 询问股票信息",
        chat_history=[],
        user_message="特斯拉最近表现怎么样？"
    )
    
    # 测试场景3: 基于历史的投资意图
    test_scenario(
        scenario_name="场景3: 基于上下文的投资意图",
        chat_history=[
            {"sender": "user", "text": "特斯拉最近怎么样？"},
            {"sender": "assistant", "text": "特斯拉最近股价表现不错，财报超预期..."},
            {"sender": "user", "text": "财报数据很好"},
            {"sender": "assistant", "text": "是的，Q3营收和利润都超出市场预期..."},
        ],
        user_message="我看涨"
    )
    
    # 测试场景4: 复杂的否定场景
    test_scenario(
        scenario_name="场景4: 朋友看涨但我不认同",
        chat_history=[],
        user_message="我朋友强烈看涨特斯拉，但我不认同"
    )
    
    # 测试场景5: 明确的投资方向
    test_scenario(
        scenario_name="场景5: 明确看涨",
        chat_history=[],
        user_message="我看涨特斯拉"
    )
    
    print("\n\n" + "="*80)
    print("🎉 测试完成！")
    print("="*80)


if __name__ == '__main__':
    main()

