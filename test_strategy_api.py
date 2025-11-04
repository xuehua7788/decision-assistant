#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试策略API
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_save_strategy():
    """测试保存策略"""
    print("=" * 60)
    print("测试：保存策略")
    print("=" * 60)
    
    strategy_data = {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "investment_style": "buffett",
        "recommendation": "买入",
        "target_price": 200.0,
        "stop_loss": 175.0,
        "position_size": "15%",
        "score": 75,
        "strategy_text": "巴菲特认为苹果有深厚的护城河，建议长期持有",
        "analysis_summary": "苹果品牌价值高，现金流充沛，值得投资",
        "current_price": 180.5
    }
    
    response = requests.post(
        f"{API_URL}/api/strategy/save",
        json=strategy_data
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    print(f"响应: {json.dumps(result, indent=2, ensure_ascii=False)}")
    
    if result['status'] == 'success':
        print(f"\n✅ 策略已保存: {result['strategy_id']}")
        return result['strategy_id']
    else:
        print(f"\n❌ 保存失败: {result['message']}")
        return None

def test_list_strategies():
    """测试获取策略列表"""
    print("\n" + "=" * 60)
    print("测试：获取策略列表")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/api/strategy/list")
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if result['status'] == 'success':
        print(f"\n✅ 找到 {result['count']} 个策略:")
        for strategy in result['strategies']:
            print(f"  • {strategy['symbol']} - {strategy['investment_style']} - {strategy['recommendation']}")
        return result['strategies']
    else:
        print(f"\n❌ 获取失败: {result['message']}")
        return []

def test_evaluate_strategy(strategy_id):
    """测试评估策略"""
    print("\n" + "=" * 60)
    print("测试：评估策略")
    print("=" * 60)
    
    response = requests.post(
        f"{API_URL}/api/strategy/evaluate",
        json={
            "strategy_id": strategy_id,
            "symbol": "AAPL"
        }
    )
    
    print(f"状态码: {response.status_code}")
    result = response.json()
    
    if result['status'] == 'success':
        print(f"\n✅ 评估完成:")
        backtest = result['evaluation']['backtest']
        print(f"  策略收益: {backtest['strategy_return']}%")
        print(f"  实际涨幅: {backtest['actual_return']}%")
        print(f"  超额收益: {backtest['outperformance']}%")
        print(f"\n  结论: {result['evaluation']['conclusion']}")
    else:
        print(f"\n❌ 评估失败: {result['message']}")

if __name__ == "__main__":
    print("\n🧪 策略API测试\n")
    
    try:
        # 1. 保存策略
        strategy_id = test_save_strategy()
        
        # 2. 获取策略列表
        strategies = test_list_strategies()
        
        # 3. 评估策略
        if strategy_id:
            test_evaluate_strategy(strategy_id)
        elif strategies:
            test_evaluate_strategy(strategies[0]['strategy_id'])
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


