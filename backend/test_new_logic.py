#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试新的期权计算逻辑
验证：
1. 期权费 = (名义本金 / 股价) × 期权价格
2. Delta就是单个期权的Delta（无组合概念）
3. 股票名义本金 = 期权名义本金 × Delta
4. 股票保证金 = 股票名义本金 × 10%
"""

import requests
import json

# 测试配置
# BASE_URL = "http://localhost:8000"  # 本地测试
BASE_URL = "https://decision-assistant-backend.onrender.com"  # 生产环境

def test_calculation_logic():
    """测试计算逻辑"""
    
    print("=" * 80)
    print("测试新的期权计算逻辑")
    print("=" * 80)
    
    # 测试用例
    test_cases = [
        {
            "name": "示例1：AMZN ($248.40)",
            "symbol": "AMZN",
            "notional_value": 30000,
            "expected": {
                "equivalent_shares": 120.77,  # 30000 / 248.40
                "premium_min": 1000,  # 期权费应该合理
                "stock_notional": 15801,  # 30000 × 0.5267 (假设Delta=0.5267)
                "stock_margin": 1580  # 15801 × 10%
            }
        },
        {
            "name": "示例2：AAPL ($150)",
            "symbol": "AAPL",
            "notional_value": 30000,
            "expected": {
                "equivalent_shares": 200,  # 30000 / 150
                "premium_min": 1500,
                "stock_notional": 15600,  # 30000 × 0.52 (假设Delta=0.52)
                "stock_margin": 1560
            }
        },
        {
            "name": "示例3：小额资金 - AMZN ($10,000)",
            "symbol": "AMZN",
            "notional_value": 10000,
            "expected": {
                "equivalent_shares": 40.26,  # 10000 / 248.40
                "premium_min": 300,
                "stock_notional": 5267,  # 10000 × 0.5267
                "stock_margin": 526
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"{'='*80}")
        
        try:
            # 调用API
            response = requests.post(
                f"{BASE_URL}/api/dual-strategy/generate",
                json={
                    "symbol": test_case["symbol"],
                    "username": "test_user",
                    "notional_value": test_case["notional_value"],
                    "investment_style": "aggressive"
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ API调用失败: {response.status_code}")
                print(f"   错误信息: {response.text}")
                continue
            
            data = response.json()
            option_strategy = data.get("option_strategy", {})
            stock_strategy = data.get("stock_strategy", {})
            current_price = data.get("current_price")
            
            print(f"\n📊 返回数据:")
            print(f"   股票价格: ${current_price:.2f}")
            print(f"   期权名义本金: ${test_case['notional_value']}")
            
            # ========== 期权策略验证 ==========
            print(f"\n📈 期权策略:")
            print(f"   类型: {option_strategy.get('type')}")
            print(f"   等价股数: {option_strategy.get('equivalent_shares')}股")
            print(f"   执行价: ${option_strategy.get('strike_price')}")
            print(f"   到期日: {option_strategy.get('expiry_date')} ({option_strategy.get('days_to_expiry')}天)")
            print(f"   期权费: ${option_strategy.get('premium'):.2f}")
            print(f"   Delta: {option_strategy.get('delta'):.4f}")
            print(f"   数据来源: {option_strategy.get('data_source')}")
            
            # 验证1：等价股数计算
            expected_shares = test_case["notional_value"] / current_price
            actual_shares = option_strategy.get('equivalent_shares', 0)
            shares_diff = abs(actual_shares - expected_shares)
            
            print(f"\n✅ 验证1：等价股数计算")
            if shares_diff < 0.1:
                print(f"   ✓ 正确: {actual_shares:.2f} ≈ {test_case['notional_value']} / {current_price:.2f} = {expected_shares:.2f}")
            else:
                print(f"   ✗ 错误: {actual_shares:.2f} ≠ {expected_shares:.2f}")
            
            # 验证2：期权费合理性
            premium = option_strategy.get('premium', 0)
            print(f"\n✅ 验证2：期权费合理性")
            if premium >= test_case["expected"]["premium_min"]:
                print(f"   ✓ 合理: ${premium:.2f} >= ${test_case['expected']['premium_min']}")
            else:
                print(f"   ⚠️ 偏低: ${premium:.2f} < ${test_case['expected']['premium_min']}")
            
            # 验证3：期权费计算公式
            if option_strategy.get('data_source') == 'Alpha Vantage Real Data':
                # 无法验证真实期权价格，因为我们不知道Alpha Vantage返回的单股期权价格
                print(f"   ℹ️ 使用真实期权数据，无法验证公式（期权价格由市场决定）")
            else:
                # 简化计算：期权费 = 名义本金 × 4%
                expected_premium = test_case['notional_value'] * 0.04
                if abs(premium - expected_premium) < 10:
                    print(f"   ✓ 简化公式正确: ${premium:.2f} ≈ ${test_case['notional_value']} × 4% = ${expected_premium:.2f}")
            
            # ========== 股票策略验证 ==========
            print(f"\n📊 股票策略:")
            print(f"   类型: {stock_strategy.get('type')}")
            print(f"   股数: {stock_strategy.get('shares')}股")
            print(f"   入场价: ${stock_strategy.get('entry_price'):.2f}")
            print(f"   名义本金: ${stock_strategy.get('notional'):.2f}")
            print(f"   保证金: ${stock_strategy.get('margin'):.2f}")
            print(f"   止损价: ${stock_strategy.get('stop_loss'):.2f}")
            print(f"   止盈价: ${stock_strategy.get('take_profit'):.2f}")
            print(f"   对应Delta: {stock_strategy.get('delta'):.4f}")
            
            # 验证4：股票名义本金 = 期权名义本金 × Delta
            option_delta = option_strategy.get('delta', 0)
            expected_stock_notional = test_case['notional_value'] * abs(option_delta)
            actual_stock_notional = stock_strategy.get('notional', 0)
            notional_diff = abs(actual_stock_notional - expected_stock_notional)
            
            print(f"\n✅ 验证4：股票名义本金计算")
            if notional_diff < 10:
                print(f"   ✓ 正确: ${actual_stock_notional:.2f} ≈ ${test_case['notional_value']} × {option_delta:.4f} = ${expected_stock_notional:.2f}")
            else:
                print(f"   ✗ 错误: ${actual_stock_notional:.2f} ≠ ${expected_stock_notional:.2f}")
            
            # 验证5：股票保证金 = 股票名义本金 × 10%
            expected_margin = actual_stock_notional * 0.1
            actual_margin = stock_strategy.get('margin', 0)
            margin_diff = abs(actual_margin - expected_margin)
            
            print(f"\n✅ 验证5：股票保证金计算")
            if margin_diff < 1:
                print(f"   ✓ 正确: ${actual_margin:.2f} ≈ ${actual_stock_notional:.2f} × 10% = ${expected_margin:.2f}")
            else:
                print(f"   ✗ 错误: ${actual_margin:.2f} ≠ ${expected_margin:.2f}")
            
            # 验证6：风险敞口对等
            option_exposure = test_case['notional_value'] * abs(option_delta)
            stock_exposure = actual_stock_notional * 1.0  # 股票Delta=1
            exposure_diff = abs(option_exposure - stock_exposure)
            
            print(f"\n✅ 验证6：风险敞口对等")
            if exposure_diff < 10:
                print(f"   ✓ 对等: 期权敞口 ${option_exposure:.2f} ≈ 股票敞口 ${stock_exposure:.2f}")
            else:
                print(f"   ✗ 不对等: 期权敞口 ${option_exposure:.2f} ≠ 股票敞口 ${stock_exposure:.2f}")
            
            # 验证7：股票数量计算
            expected_shares_stock = int(actual_stock_notional / current_price)
            actual_shares_stock = stock_strategy.get('shares', 0)
            
            print(f"\n✅ 验证7：股票数量计算")
            if actual_shares_stock == expected_shares_stock:
                print(f"   ✓ 正确: {actual_shares_stock}股 = int(${actual_stock_notional:.2f} / ${current_price:.2f})")
            else:
                print(f"   ⚠️ 差异: {actual_shares_stock}股 ≠ {expected_shares_stock}股")
            
            # 总结
            print(f"\n{'='*80}")
            print(f"✅ 测试用例 {i} 完成")
            print(f"{'='*80}")
            
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时（30秒）")
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败，请确保后端服务正在运行")
            print(f"   提示：运行 'cd backend && python app.py' 启动后端")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*80}")
    print("所有测试完成！")
    print(f"{'='*80}")

if __name__ == "__main__":
    print("\n提示：请确保后端服务正在运行")
    print("本地测试：cd backend && python app.py")
    print("测试URL：", BASE_URL)
    print("\n开始自动化测试...\n")
    
    test_calculation_logic()

