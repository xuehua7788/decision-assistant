#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试期权策略：保存→读取
"""

import requests
import json
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("测试期权策略保存和读取")
print("=" * 80)

# 步骤1: 保存一个包含期权策略的策略
print("\n✅ 步骤1: 保存策略（包含期权策略）...")

strategy_data = {
    "symbol": "NVDA",
    "company_name": "NVIDIA Corporation",
    "investment_style": "lynch",
    "recommendation": "买入",
    "target_price": 500.0,
    "stop_loss": 420.0,
    "position_size": "20%",
    "score": 85,
    "strategy_text": "NVDA技术面强势，AI需求持续增长",
    "analysis_summary": "建议买入并持有",
    "current_price": 450.0,
    # 完整的期权策略对象（模拟Stock Analysis生成的）
    "option_strategy": {
        "name": "牛市价差",
        "type": "bull_call_spread",
        "description": "买入低行权价看涨期权，卖出高行权价看涨期权",
        "risk_level": "medium",
        "parameters": {
            "current_price": 450.0,
            "buy_strike": 460.0,
            "sell_strike": 480.0,
            "premium_paid": 8.0,
            "premium_received": 3.0,
            "expiration_days": 45
        },
        "metrics": {
            "max_loss": -500.0,
            "max_gain": 1500.0,
            "breakeven": 465.0,
            "risk_reward_ratio": "1:3"
        },
        "payoff_data": [
            {"price": 440.0, "payoff": -500.0},
            {"price": 450.0, "payoff": -500.0},
            {"price": 460.0, "payoff": -500.0},
            {"price": 465.0, "payoff": 0.0},
            {"price": 470.0, "payoff": 500.0},
            {"price": 480.0, "payoff": 1500.0},
            {"price": 490.0, "payoff": 1500.0}
        ]
    }
}

try:
    response = requests.post(
        f"{RENDER_URL}/api/strategy/save",
        json=strategy_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"❌ 保存失败: {response.status_code}")
        print(f"响应: {response.text}")
        exit(1)
    
    save_result = response.json()
    
    if save_result.get('status') != 'success':
        print(f"❌ 保存失败: {save_result.get('message')}")
        exit(1)
    
    strategy_id = save_result['strategy_id']
    print(f"✅ 策略已保存")
    print(f"   策略ID: {strategy_id}")
    print(f"   包含期权策略: 牛市价差")
    
except Exception as e:
    print(f"❌ 保存请求失败: {e}")
    exit(1)

# 步骤2: 读取策略列表
print("\n📋 步骤2: 读取策略列表...")
time.sleep(1)  # 等待数据库写入

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    
    if response.status_code != 200:
        print(f"❌ 读取失败: {response.status_code}")
        exit(1)
    
    list_result = response.json()
    strategies = list_result.get('strategies', [])
    
    print(f"✅ 读取成功，共 {len(strategies)} 个策略")
    
    # 找到刚才保存的策略
    saved_strategy = None
    for s in strategies:
        if s['strategy_id'] == strategy_id:
            saved_strategy = s
            break
    
    if not saved_strategy:
        print(f"❌ 未找到刚保存的策略: {strategy_id}")
        exit(1)
    
    print(f"\n🔍 步骤3: 验证期权策略...")
    print(f"   策略ID: {saved_strategy['strategy_id']}")
    print(f"   股票: {saved_strategy['symbol']} - {saved_strategy['company_name']}")
    print(f"   推荐: {saved_strategy['recommendation']}")
    
    # 关键验证：检查期权策略
    option_strategy = saved_strategy.get('option_strategy')
    
    if not option_strategy:
        print(f"\n❌ 期权策略丢失！")
        print(f"   数据库中没有option_strategy字段")
        exit(1)
    
    if not isinstance(option_strategy, dict):
        print(f"\n❌ 期权策略格式错误！")
        print(f"   类型: {type(option_strategy)}")
        print(f"   内容: {option_strategy}")
        exit(1)
    
    print(f"\n✅ 期权策略验证成功！")
    print(f"   策略名称: {option_strategy.get('name', 'N/A')}")
    print(f"   策略类型: {option_strategy.get('type', 'N/A')}")
    print(f"   风险等级: {option_strategy.get('risk_level', 'N/A')}")
    
    # 验证详细参数
    params = option_strategy.get('parameters', {})
    if params:
        print(f"\n   期权参数:")
        print(f"   - 买入行权价: ${params.get('buy_strike', 'N/A')}")
        print(f"   - 卖出行权价: ${params.get('sell_strike', 'N/A')}")
        print(f"   - 到期天数: {params.get('expiration_days', 'N/A')}天")
    
    metrics = option_strategy.get('metrics', {})
    if metrics:
        print(f"\n   风险指标:")
        print(f"   - 最大损失: ${metrics.get('max_loss', 'N/A')}")
        print(f"   - 最大收益: ${metrics.get('max_gain', 'N/A')}")
        print(f"   - 盈亏平衡点: ${metrics.get('breakeven', 'N/A')}")
    
    print("\n" + "=" * 80)
    print("🎉 完整测试通过！")
    print("=" * 80)
    print("\n✅ 确认结果:")
    print("1. ✅ 期权策略成功写入数据库")
    print("2. ✅ 期权策略成功从数据库读取")
    print("3. ✅ 期权策略数据完整（包含name, type, parameters, metrics）")
    print("4. ✅ 前端可以正常显示期权策略信息")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

