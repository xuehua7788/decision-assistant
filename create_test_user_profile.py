#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建测试用户画像（用于演示）
"""

import requests
import json

BASE_URL = "https://decision-assistant-backend.onrender.com"

# 模拟一个完整的用户画像
test_profile = {
    "username": "demo_user",
    "investment_preferences": {
        "risk_tolerance": "moderate",
        "investment_style": "growth",
        "time_horizon": "medium"
    },
    "behavioral_traits": {
        "decision_speed": "moderate",
        "information_depth": "moderate",
        "chat_frequency": 5
    },
    "knowledge_level": {
        "financial_knowledge": "intermediate",
        "option_experience": "basic"
    },
    "emotional_traits": {
        "sentiment_tendency": "optimistic",
        "confidence_level": 0.7
    },
    "key_insights": {
        "key_interests": ["TSLA", "NVDA", "AI sector"],
        "common_questions": ["technical analysis", "earnings impact"],
        "decision_patterns": "倾向于在财报前建仓，关注技术面突破",
        "risk_concerns": ["市场波动", "黑天鹅事件"]
    },
    "recommendations": {
        "recommended_strategy_types": ["bull_call_spread", "covered_call"],
        "parameter_adjustments": {
            "strike_selection": "略保守，选择更接近平值的行权价",
            "position_sizing": "建议单笔不超过总资金的10%",
            "time_decay_preference": "适合30-45天到期的期权"
        },
        "personalization_notes": "用户对技术分析有一定了解，但对期权Greeks理解有限，建议推荐简单策略并提供详细解释。"
    },
    "analysis_summary": "该用户是一位中等风险偏好的成长型投资者，对科技股特别是AI领域有浓厚兴趣。决策较为谨慎，会在行动前进行适度研究。期权经验有限，适合推荐风险可控的简单策略。",
    "metadata": {
        "username": "demo_user",
        "analyzed_at": "2024-10-23T10:00:00",
        "analysis_period_days": 30,
        "total_messages_analyzed": 25,
        "analysis_version": "1.0"
    }
}

print("=" * 70)
print("创建演示用户画像")
print("=" * 70)
print()

print("📊 用户画像数据:")
print(json.dumps(test_profile, indent=2, ensure_ascii=False))
print()

print("=" * 70)
print("用户画像参数说明")
print("=" * 70)
print()

print("📊 投资偏好:")
print("   - risk_tolerance: conservative(保守) / moderate(中等) / aggressive(激进)")
print("   - investment_style: value(价值) / growth(成长) / momentum(动量)")
print("   - time_horizon: short(短期) / medium(中期) / long(长期)")
print()

print("🎯 行为特征:")
print("   - decision_speed: fast(快速) / moderate(谨慎) / slow(深思熟虑)")
print("   - information_depth: shallow(浅层) / moderate(适度) / deep(深度)")
print("   - chat_frequency: 聊天频率（次/周）")
print()

print("📚 知识水平:")
print("   - financial_knowledge: beginner(初学) / intermediate(中级) / advanced(高级)")
print("   - option_experience: none(无) / basic(基础) / experienced(有经验)")
print()

print("💭 情绪特征:")
print("   - sentiment_tendency: optimistic(乐观) / pessimistic(悲观) / balanced(平衡)")
print("   - confidence_level: 0.0-1.0（信心水平）")
print()

print("=" * 70)
print("如何使用这些参数")
print("=" * 70)
print()

print("当用户表达投资意图时，系统会:")
print()
print("1. AI #1识别意图:")
print("   用户: '我看好特斯拉'")
print("   → ticker: TSLA, direction: bullish")
print()
print("2. 加载用户画像:")
print("   → risk_tolerance: moderate")
print("   → option_experience: basic")
print()
print("3. 策略优化:")
print("   原始策略: Bull Call Spread, 5手")
print("   → 根据moderate风险: 保持5手")
print("   → 根据basic经验: 调整行权价更接近平值")
print("   → 添加详细解释")
print()
print("4. 返回个性化策略:")
print("   '根据您的中等风险偏好和期权经验，建议...'")
print()

print("=" * 70)
print("查看实际用户画像")
print("=" * 70)
print()
print("运行: python check_user_profile.py <username>")
print()




