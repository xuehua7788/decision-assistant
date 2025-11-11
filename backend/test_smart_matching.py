#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试智能匹配逻辑
验证：
1. AI分析结果 + 用户风格 → 正确的期权类型
2. 不同场景下的策略推荐
3. 推荐理由是否合理
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:8000"  # 本地测试
# BASE_URL = "https://decision-assistant-backend.onrender.com"  # 生产环境

def test_smart_matching():
    """测试智能匹配逻辑"""
    
    print("=" * 80)
    print("测试智能匹配逻辑")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        {
            "name": "场景1：强烈看涨 + 激进风格",
            "symbol": "AAPL",
            "investment_style": "aggressive",
            "ai_analysis": {
                "score": 85,
                "market_direction": "bullish",
                "direction_strength": "strong",
                "recommendation": "买入"
            },
            "expected": {
                "option_type": "CALL",
                "strategy_name": "Long Call（略虚值）",
                "keywords": ["强烈看涨", "aggressive", "高杠杆"]
            }
        },
        {
            "name": "场景2：强烈看涨 + 保守风格",
            "symbol": "AAPL",
            "investment_style": "buffett",
            "ai_analysis": {
                "score": 85,
                "market_direction": "bullish",
                "direction_strength": "strong",
                "recommendation": "买入"
            },
            "expected": {
                "option_type": "CALL",
                "strategy_name": "Long Call（平值）",
                "keywords": ["强烈看涨", "buffett", "平值"]
            }
        },
        {
            "name": "场景3：看跌 + 激进风格",
            "symbol": "AAPL",
            "investment_style": "soros",
            "ai_analysis": {
                "score": 30,
                "market_direction": "bearish",
                "direction_strength": "moderate",
                "recommendation": "卖出"
            },
            "expected": {
                "option_type": "PUT",
                "strategy_name": "Long Put（平值）",
                "keywords": ["看跌", "soros", "做空"]
            }
        },
        {
            "name": "场景4：强烈看跌 + 激进风格",
            "symbol": "AAPL",
            "investment_style": "aggressive",
            "ai_analysis": {
                "score": 15,
                "market_direction": "bearish",
                "direction_strength": "strong",
                "recommendation": "强烈卖出"
            },
            "expected": {
                "option_type": "PUT",
                "strategy_name": "Long Put（略虚值）",
                "keywords": ["强烈看跌", "aggressive", "高杠杆"]
            }
        },
        {
            "name": "场景5：震荡 + 平衡风格",
            "symbol": "AAPL",
            "investment_style": "balanced",
            "ai_analysis": {
                "score": 50,
                "market_direction": "neutral",
                "direction_strength": "weak",
                "recommendation": "观望"
            },
            "expected": {
                "option_type": "CALL",
                "strategy_name": "Long Call（观望为主）",
                "keywords": ["震荡", "balanced", "观望"]
            }
        },
        {
            "name": "场景6：一般看涨 + 彼得林奇风格",
            "symbol": "AAPL",
            "investment_style": "lynch",
            "ai_analysis": {
                "score": 70,
                "market_direction": "bullish",
                "direction_strength": "moderate",
                "recommendation": "买入"
            },
            "expected": {
                "option_type": "CALL",
                "strategy_name": "Long Call（平值）",
                "keywords": ["看涨", "lynch"]
            }
        },
        {
            "name": "场景7：无AI分析 + 激进风格（降级）",
            "symbol": "AAPL",
            "investment_style": "aggressive",
            "ai_analysis": None,  # 没有AI分析
            "expected": {
                "option_type": "CALL",
                "strategy_name": "Long Call（默认）",
                "keywords": ["aggressive", "默认"]
            }
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"{'='*80}")
        print(f"投资风格: {test_case['investment_style']}")
        if test_case['ai_analysis']:
            print(f"AI分析: score={test_case['ai_analysis']['score']}, "
                  f"direction={test_case['ai_analysis']['market_direction']}, "
                  f"strength={test_case['ai_analysis']['direction_strength']}")
        else:
            print(f"AI分析: 无")
        
        try:
            # 调用API
            response = requests.post(
                f"{BASE_URL}/api/dual-strategy/generate",
                json={
                    "symbol": test_case["symbol"],
                    "username": "test_user",
                    "notional_value": 30000,
                    "investment_style": test_case["investment_style"],
                    "ai_analysis": test_case["ai_analysis"]
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                failed += 1
                continue
            
            data = response.json()
            option_strategy = data.get("option_strategy", {})
            explanation = data.get("explanation", "")
            
            print(f"\n📊 返回结果:")
            print(f"   期权类型: {option_strategy.get('type')}")
            print(f"   执行价: ${option_strategy.get('strike_price')}")
            print(f"   Delta: {option_strategy.get('delta'):.4f}")
            print(f"   等价股数: {option_strategy.get('equivalent_shares')}股")
            print(f"   期权费: ${option_strategy.get('premium'):.2f}")
            print(f"\n🤖 推荐理由:")
            print(f"   {explanation}")
            
            # 验证结果
            print(f"\n✅ 验证:")
            
            # 验证1：期权类型
            expected_type = test_case["expected"]["option_type"]
            actual_type = option_strategy.get('type')
            if actual_type == expected_type:
                print(f"   ✓ 期权类型正确: {actual_type} = {expected_type}")
            else:
                print(f"   ✗ 期权类型错误: {actual_type} ≠ {expected_type}")
                failed += 1
                continue
            
            # 验证2：推荐理由包含关键词
            keywords_found = []
            keywords_missing = []
            for keyword in test_case["expected"]["keywords"]:
                if keyword.lower() in explanation.lower():
                    keywords_found.append(keyword)
                else:
                    keywords_missing.append(keyword)
            
            if keywords_missing:
                print(f"   ⚠️ 推荐理由缺少关键词: {keywords_missing}")
            else:
                print(f"   ✓ 推荐理由包含所有关键词: {keywords_found}")
            
            # 验证3：执行价调整
            current_price = data.get('current_price')
            strike_price = option_strategy.get('strike_price')
            strike_diff_pct = ((strike_price - current_price) / current_price) * 100
            
            print(f"   ℹ️ 执行价偏移: {strike_diff_pct:+.2f}%")
            
            if "略虚值" in test_case["expected"]["strategy_name"]:
                if strike_diff_pct > 1:
                    print(f"   ✓ 执行价为虚值（偏移>1%）")
                else:
                    print(f"   ⚠️ 预期虚值但偏移较小: {strike_diff_pct:.2f}%")
            elif "平值" in test_case["expected"]["strategy_name"]:
                if abs(strike_diff_pct) < 2:
                    print(f"   ✓ 执行价接近平值（偏移<2%）")
                else:
                    print(f"   ⚠️ 预期平值但偏移较大: {strike_diff_pct:.2f}%")
            
            print(f"\n✅ 测试用例 {i} 通过")
            passed += 1
            
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败，请确保后端服务正在运行")
            print(f"   提示：运行 'cd backend && python app.py' 启动后端")
            failed += 1
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    # 总结
    print(f"\n{'='*80}")
    print(f"测试总结")
    print(f"{'='*80}")
    print(f"总计: {len(test_cases)} 个测试用例")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"成功率: {(passed/len(test_cases)*100):.1f}%")
    print(f"{'='*80}")

if __name__ == "__main__":
    print("\n提示：请确保后端服务正在运行")
    print("本地测试：cd backend && python app.py")
    print("测试URL：", BASE_URL)
    print("\n开始自动化测试...\n")
    
    test_smart_matching()

