#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试策略数据库存储和评估
"""

import requests
import json
from datetime import datetime

API_URL = "http://127.0.0.1:8000"

def test_save_strategy():
    """测试保存策略到数据库"""
    print("\n" + "="*60)
    print("测试1: 保存策略到数据库")
    print("="*60)
    
    strategy_data = {
        "symbol": "TSLA",
        "company_name": "Tesla Inc.",
        "investment_style": "lynch",
        "recommendation": "买入",
        "target_price": 280.00,
        "stop_loss": 200.00,
        "position_size": "15%",
        "score": 85,
        "strategy_text": "彼得·林奇风格：Tesla是快速增长型公司，电动车市场份额持续扩大...",
        "analysis_summary": "Tesla符合林奇的成长股标准，PEG合理，建议买入",
        "current_price": 242.50
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/strategy/save",
            json=strategy_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 策略保存成功！")
            print(f"   Strategy ID: {result['strategy_id']}")
            return result['strategy_id']
        else:
            print(f"❌ 保存失败: {response.status_code}")
            print(f"   {response.text}")
            return None
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return None

def test_list_strategies():
    """测试获取策略列表"""
    print("\n" + "="*60)
    print("测试2: 获取策略列表")
    print("="*60)
    
    try:
        response = requests.get(f"{API_URL}/api/strategy/list")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 获取成功！共 {result['count']} 条策略")
            
            for i, strategy in enumerate(result['strategies'][:3], 1):
                print(f"\n策略 {i}:")
                print(f"  ID: {strategy['strategy_id']}")
                print(f"  股票: {strategy['symbol']} - {strategy['company_name']}")
                print(f"  风格: {strategy['investment_style']}")
                print(f"  建议: {strategy['recommendation']}")
                print(f"  当前价: ${strategy['current_price']}")
                print(f"  目标价: ${strategy['target_price']}")
            
            return result['strategies']
        else:
            print(f"❌ 获取失败: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def test_evaluate_strategy(strategy_id):
    """测试策略评估"""
    print("\n" + "="*60)
    print("测试3: 评估策略表现")
    print("="*60)
    
    try:
        response = requests.post(
            f"{API_URL}/api/strategy/evaluate",
            json={"strategy_id": strategy_id},
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"📥 API返回: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if result['status'] == 'success':
                eval_data = result['evaluation']
                
                print(f"✅ 评估成功！")
                print(f"\n策略ID: {eval_data['strategy_id']}")
                print(f"股票: {eval_data['symbol']} - {eval_data['company_name']}")
                print(f"投资风格: {eval_data['investment_style']}")
                print(f"\n📊 回测结果:")
                print(f"  建议买入价: ${eval_data['backtest']['strategy_buy_price']}")
                print(f"  当前真实价: ${eval_data['backtest']['current_real_price']}")
                print(f"  策略预期收益: {eval_data['backtest']['strategy_return']}%")
                print(f"  实际持有收益: {eval_data['backtest']['actual_return']}%")
                print(f"  策略表现: {eval_data['backtest']['outperformance']}%")
                print(f"\n💡 结论: {eval_data['conclusion']}")
                
                return True
            else:
                print(f"❌ 评估失败: {result.get('message', '未知错误')}")
                return False
        else:
            print(f"❌ 评估失败: {response.status_code}")
            print(f"   {response.text}")
            return False
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

if __name__ == "__main__":
    print("🚀 开始测试策略数据库存储和评估功能")
    print(f"API地址: {API_URL}")
    
    # 测试1: 保存策略
    strategy_id = test_save_strategy()
    
    # 测试2: 获取列表
    strategies = test_list_strategies()
    
    # 测试3: 评估策略
    if strategy_id:
        test_evaluate_strategy(strategy_id)
    elif strategies:
        # 如果新保存失败，用现有的策略测试
        test_evaluate_strategy(strategies[0]['strategy_id'])
    
    print("\n" + "="*60)
    print("✅ 测试完成！")
    print("="*60)

