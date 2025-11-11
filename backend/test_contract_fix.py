#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试期权合约数修复
验证：
1. 名义本金$30,000能否购买至少1手期权
2. 小数手期权计算是否正确
3. 组合Delta计算是否正确
"""

import requests
import json

# 测试配置
BASE_URL = "http://localhost:8000"  # 本地测试
# BASE_URL = "https://decision-assistant-backend.onrender.com"  # 生产环境

def test_dual_strategy_generation():
    """测试双策略生成"""
    
    print("=" * 60)
    print("测试：期权合约数修复")
    print("=" * 60)
    
    # 测试用例
    test_cases = [
        {
            "name": "高价股票 - AMZN ($248)",
            "symbol": "AMZN",
            "notional_value": 30000,
            "expected_contracts_min": 1.0,  # 至少1手
            "expected_premium_min": 500  # 期权费至少$500
        },
        {
            "name": "中价股票 - AAPL ($150)",
            "symbol": "AAPL",
            "notional_value": 30000,
            "expected_contracts_min": 2.0,  # 至少2手
            "expected_premium_min": 800
        },
        {
            "name": "低价股票 - F ($12)",
            "symbol": "F",
            "notional_value": 30000,
            "expected_contracts_min": 20.0,  # 至少20手
            "expected_premium_min": 200
        },
        {
            "name": "小额资金 - AMZN ($10,000)",
            "symbol": "AMZN",
            "notional_value": 10000,
            "expected_contracts_min": 0.3,  # 小数手
            "expected_premium_min": 100,
            "is_fractional": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*60}")
        print(f"测试用例 {i}: {test_case['name']}")
        print(f"{'='*60}")
        
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
            
            # 验证期权策略
            print(f"\n📊 期权策略:")
            print(f"   类型: {option_strategy.get('type')}")
            print(f"   合约数: {option_strategy.get('contracts')}手")
            print(f"   执行价: ${option_strategy.get('strike_price')}")
            print(f"   到期日: {option_strategy.get('expiry_date')} ({option_strategy.get('days_to_expiry')}天)")
            print(f"   期权费: ${option_strategy.get('premium'):.2f}")
            print(f"   单个Delta: {option_strategy.get('delta'):.4f}")
            print(f"   组合Delta: {option_strategy.get('portfolio_delta'):.4f}")
            print(f"   数据来源: {option_strategy.get('data_source')}")
            
            # 验证股票策略
            print(f"\n📈 股票策略:")
            print(f"   类型: {stock_strategy.get('type')}")
            print(f"   股数: {stock_strategy.get('shares')}股")
            print(f"   入场价: ${stock_strategy.get('entry_price'):.2f}")
            print(f"   总金额: ${stock_strategy.get('amount'):.2f}")
            print(f"   保证金: ${stock_strategy.get('margin'):.2f}")
            print(f"   止损价: ${stock_strategy.get('stop_loss'):.2f}")
            print(f"   止盈价: ${stock_strategy.get('take_profit'):.2f}")
            
            # 验证结果
            contracts = option_strategy.get('contracts', 0)
            premium = option_strategy.get('premium', 0)
            portfolio_delta = option_strategy.get('portfolio_delta', 0)
            single_delta = option_strategy.get('delta', 0)
            
            print(f"\n✅ 验证结果:")
            
            # 检查1：合约数
            if contracts >= test_case["expected_contracts_min"]:
                print(f"   ✓ 合约数合格: {contracts} >= {test_case['expected_contracts_min']}")
            else:
                print(f"   ✗ 合约数不足: {contracts} < {test_case['expected_contracts_min']}")
            
            # 检查2：期权费
            if premium >= test_case["expected_premium_min"]:
                print(f"   ✓ 期权费合理: ${premium:.2f} >= ${test_case['expected_premium_min']}")
            else:
                print(f"   ✗ 期权费过低: ${premium:.2f} < ${test_case['expected_premium_min']}")
            
            # 检查3：小数手标识
            if test_case.get("is_fractional"):
                if contracts < 1:
                    print(f"   ✓ 小数手正确: {contracts}手 < 1")
                else:
                    print(f"   ✗ 应该是小数手但显示整数: {contracts}手")
            
            # 检查4：组合Delta计算
            expected_portfolio_delta = single_delta * contracts
            delta_diff = abs(portfolio_delta - expected_portfolio_delta)
            if delta_diff < 0.01:  # 允许0.01的误差
                print(f"   ✓ 组合Delta计算正确: {portfolio_delta:.4f} ≈ {single_delta:.4f} × {contracts}")
            else:
                print(f"   ✗ 组合Delta计算错误: {portfolio_delta:.4f} ≠ {single_delta:.4f} × {contracts}")
            
            # 检查5：股票金额基于Delta
            expected_stock_amount = test_case["notional_value"] * abs(portfolio_delta)
            actual_stock_amount = stock_strategy.get('amount', 0)
            amount_diff = abs(actual_stock_amount - expected_stock_amount)
            if amount_diff / expected_stock_amount < 0.05:  # 允许5%误差
                print(f"   ✓ 股票金额计算正确: ${actual_stock_amount:.2f} ≈ ${test_case['notional_value']} × {abs(portfolio_delta):.4f}")
            else:
                print(f"   ✗ 股票金额计算错误: ${actual_stock_amount:.2f} ≠ ${expected_stock_amount:.2f}")
            
        except requests.exceptions.Timeout:
            print(f"❌ 请求超时（30秒）")
        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败，请确保后端服务正在运行")
        except Exception as e:
            print(f"❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}")

if __name__ == "__main__":
    test_dual_strategy_generation()

