#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI分析一致性
验证：AI文字描述和market_direction字段是否一致
"""

# 模拟测试用例
test_cases = [
    {
        "name": "案例1：AI说谨慎但direction=bullish（需要修正）",
        "ai_analysis": {
            "score": 65,
            "recommendation": "买入",
            "market_direction": "bullish",  # 不一致
            "direction_strength": "moderate",
            "strategy": "现在不是大举买入的时候，如果你真的看好，可以小仓位试探"  # 谨慎
        },
        "expected_corrected_direction": "neutral",
        "expected_strategy_type": "Long Call（观望为主）"
    },
    {
        "name": "案例2：AI明确看涨（一致）",
        "ai_analysis": {
            "score": 85,
            "recommendation": "买入",
            "market_direction": "bullish",
            "direction_strength": "strong",
            "strategy": "技术面强势，建议积极买入"
        },
        "expected_corrected_direction": "bullish",
        "expected_strategy_type": "Long Call（略虚值）"
    },
    {
        "name": "案例3：AI说观望（一致）",
        "ai_analysis": {
            "score": 50,
            "recommendation": "观望",
            "market_direction": "neutral",
            "direction_strength": "weak",
            "strategy": "信号不明确，建议观望等待更好时机"
        },
        "expected_corrected_direction": "neutral",
        "expected_strategy_type": "Long Call（观望为主）"
    }
]

def test_consistency():
    """测试一致性修正逻辑"""
    
    print("=" * 80)
    print("测试AI分析一致性修正")
    print("=" * 80)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"{'='*80}")
        
        ai_analysis = test_case['ai_analysis']
        
        print(f"\n原始AI分析:")
        print(f"  score: {ai_analysis['score']}")
        print(f"  market_direction: {ai_analysis['market_direction']}")
        print(f"  direction_strength: {ai_analysis['direction_strength']}")
        print(f"  strategy: {ai_analysis['strategy']}")
        
        # 模拟修正逻辑
        market_direction = ai_analysis['market_direction']
        direction_strength = ai_analysis['direction_strength']
        score = ai_analysis['score']
        strategy_text = ai_analysis['strategy']
        
        # 检查谨慎关键词
        caution_keywords = ['不是', '观望', '谨慎', '小仓位', '等待', '不建议', '避免']
        has_caution = any(keyword in strategy_text for keyword in caution_keywords)
        
        if has_caution and market_direction == 'bullish' and score < 70:
            print(f"\n⚠️ 检测到不一致：")
            print(f"  文字谨慎（包含关键词）但direction=bullish")
            print(f"  修正: direction → neutral, strength → weak")
            market_direction = 'neutral'
            direction_strength = 'weak'
        
        print(f"\n修正后:")
        print(f"  market_direction: {market_direction}")
        print(f"  direction_strength: {direction_strength}")
        
        # 验证
        expected = test_case['expected_corrected_direction']
        if market_direction == expected:
            print(f"\n✅ 验证通过: {market_direction} = {expected}")
        else:
            print(f"\n❌ 验证失败: {market_direction} ≠ {expected}")
    
    print(f"\n{'='*80}")
    print("测试完成")
    print(f"{'='*80}")

if __name__ == "__main__":
    test_consistency()

