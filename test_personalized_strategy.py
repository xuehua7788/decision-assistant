#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试个性化策略推荐
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from option_strategy_handler import OptionStrategyHandler
from profile_based_strategy_optimizer import ProfileBasedStrategyOptimizer
from profile_integration_helpers import load_user_profile_from_db

print("=" * 70)
print("测试个性化策略推荐")
print("=" * 70)
print()

# 1. 加载bbb的用户画像
print("1. 加载用户画像...")
profile = load_user_profile_from_db("bbb")

if not profile:
    print("   ❌ 未找到用户画像")
    sys.exit(1)

print("   ✅ 用户画像加载成功")
print(f"   风险偏好: {profile.get('investment_preferences', {}).get('risk_tolerance')}")
print(f"   期权经验: {profile.get('knowledge_level', {}).get('option_experience')}")
print()

# 2. 模拟用户表达投资意图
print("2. 模拟用户表达投资意图...")
user_input = "我强烈看涨特斯拉"
print(f"   用户输入: \"{user_input}\"")
print()

# 3. 生成基础策略
print("3. 生成基础策略...")
handler = OptionStrategyHandler()
base_result = handler.handle_option_strategy_request(user_input, current_price=250.0)

if base_result.get('status') == 'error':
    print(f"   ❌ 策略生成失败: {base_result.get('message')}")
    sys.exit(1)

base_strategy = base_result['strategy']
print(f"   ✅ 基础策略: {base_strategy['type']}")
print(f"   基础参数:")
print(f"      数量: {base_strategy['parameters']['quantity']}")
print(f"      行权价: ${base_strategy['parameters']['strike_price']}")
print(f"      到期天数: {base_strategy['parameters']['days_to_expiry']}")
print()

# 4. 应用个性化优化
print("4. 应用个性化优化...")
optimizer = ProfileBasedStrategyOptimizer()

# 构造parsed_intent（从base_result中提取）
parsed_intent_dict = {
    'direction': 'bullish',
    'confidence': 'strong',
    'time_horizon': 'short',
    'risk_profile': 'balanced',
    'underlying': 'TSLA'
}

# 创建一个简单的对象来模拟ParsedIntent
class SimpleIntent:
    def __init__(self, data):
        self.direction = data['direction']
        self.confidence = data['confidence']
        self.time_horizon = data['time_horizon']
        self.risk_profile = data['risk_profile']
        self.underlying = data['underlying']

parsed_intent = SimpleIntent(parsed_intent_dict)

# 优化策略
optimized_strategy = optimizer.optimize_strategy(
    base_strategy=base_strategy,
    user_profile=profile,
    parsed_intent=parsed_intent
)

print(f"   ✅ 个性化策略: {optimized_strategy['type']}")
print(f"   优化后参数:")
print(f"      数量: {optimized_strategy['parameters']['quantity']}")
print(f"      行权价: ${optimized_strategy['parameters']['strike_price']}")
print(f"      到期天数: {optimized_strategy['parameters']['days_to_expiry']}")
print()

# 5. 对比调整
print("5. 个性化调整说明:")
print("=" * 70)

adjustments = []

if optimized_strategy['parameters']['quantity'] != base_strategy['parameters']['quantity']:
    adjustments.append(
        f"• 数量调整: {base_strategy['parameters']['quantity']} → "
        f"{optimized_strategy['parameters']['quantity']} "
        f"(根据风险偏好: {profile.get('investment_preferences', {}).get('risk_tolerance')})"
    )

if optimized_strategy['parameters']['strike_price'] != base_strategy['parameters']['strike_price']:
    adjustments.append(
        f"• 行权价调整: ${base_strategy['parameters']['strike_price']} → "
        f"${optimized_strategy['parameters']['strike_price']} "
        f"(根据期权经验: {profile.get('knowledge_level', {}).get('option_experience')})"
    )

if optimized_strategy['parameters']['days_to_expiry'] != base_strategy['parameters']['days_to_expiry']:
    adjustments.append(
        f"• 到期时间调整: {base_strategy['parameters']['days_to_expiry']}天 → "
        f"{optimized_strategy['parameters']['days_to_expiry']}天 "
        f"(根据时间偏好: {profile.get('investment_preferences', {}).get('time_horizon')})"
    )

if adjustments:
    for adj in adjustments:
        print(adj)
else:
    print("• 无调整（基础策略已经适合该用户）")

print()
print("=" * 70)
print("✅ 个性化推荐测试完成")
print("=" * 70)
print()
print("说明:")
print("• 系统根据用户画像自动调整了策略参数")
print("• 激进型投资者 → 增加数量")
print("• 初学者 → 选择更保守的行权价")
print("• 短期偏好 → 缩短到期时间")
print()








