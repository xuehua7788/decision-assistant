#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试期权策略保存功能
"""

import requests
import json

# 测试Render后端
BASE_URL = "https://decision-assistant-backend.onrender.com"

def test_save_option_strategy():
    """测试保存期权策略"""
    print("\n=== 测试保存期权策略 ===\n")
    
    # 模拟前端发送的数据
    strategy_data = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "investment_style": "buffett",
        "recommendation": "买入",
        "target_price": 200.0,
        "stop_loss": 175.0,
        "position_size": "15%",
        "score": 75,
        "strategy_text": "基于技术面和基本面分析，建议买入",
        "analysis_summary": "AAPL技术面强势，建议买入",
        "current_price": 180.5,
        # 期权策略（完整的期权策略对象）
        "option_strategy": {
            "success": True,
            "parsed_intent": {
                "ticker": "AAPL",
                "direction": "bullish",
                "strength": "strong",
                "time_horizon": "medium"
            },
            "strategy": {
                "type": "long_call",
                "name": "买入看涨期权",
                "description": "买入虚值看涨期权，适合强烈看涨的情况",
                "parameters": {
                    "current_price": 180.5,
                    "buy_strike": 185.0,
                    "premium_paid": 3.5,
                    "expiration_days": 30
                },
                "metrics": {
                    "max_loss": -350.0,
                    "max_gain": 999999,
                    "breakeven": 188.5,
                    "risk_reward_ratio": "1:无限"
                },
                "payoff_data": [
                    {"price": 170.0, "payoff": -350.0},
                    {"price": 180.0, "payoff": -350.0},
                    {"price": 185.0, "payoff": -350.0},
                    {"price": 188.5, "payoff": 0.0},
                    {"price": 190.0, "payoff": 150.0},
                    {"price": 200.0, "payoff": 1150.0}
                ]
            }
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/strategy/save",
            json=strategy_data,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        if result.get('status') == 'success':
            print(f"\n✅ 策略保存成功！")
            print(f"策略ID: {result.get('strategy_id')}")
            return result.get('strategy_id')
        else:
            print(f"\n❌ 保存失败: {result.get('message')}")
            return None
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_list_strategies():
    """测试获取策略列表"""
    print("\n=== 测试获取策略列表 ===\n")
    
    try:
        response = requests.get(f"{BASE_URL}/api/strategy/list")
        
        print(f"状态码: {response.status_code}")
        result = response.json()
        
        if result.get('status') == 'success':
            strategies = result.get('strategies', [])
            print(f"\n✅ 找到 {len(strategies)} 个策略\n")
            
            for strategy in strategies[:3]:  # 只显示前3个
                print(f"策略ID: {strategy['strategy_id']}")
                print(f"股票: {strategy['symbol']} - {strategy['company_name']}")
                print(f"推荐: {strategy['recommendation']}")
                
                # 检查是否有期权策略
                if strategy.get('option_strategy'):
                    opt = strategy['option_strategy']
                    if isinstance(opt, dict) and 'strategy' in opt:
                        print(f"期权策略: {opt['strategy'].get('name', 'N/A')}")
                    else:
                        print(f"期权策略: {opt}")
                else:
                    print("期权策略: 无")
                print("-" * 50)
        else:
            print(f"❌ 获取失败: {result.get('message')}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    # 测试保存
    strategy_id = test_save_option_strategy()
    
    # 测试列表
    test_list_strategies()

