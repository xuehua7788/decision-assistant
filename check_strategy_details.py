#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查策略详细信息
"""

import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("检查Render数据库中的策略详情")
print("=" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        strategies = result.get('strategies', [])
        
        print(f"\n找到 {len(strategies)} 个策略\n")
        
        for i, strategy in enumerate(strategies, 1):
            print(f"{'='*80}")
            print(f"策略 #{i}")
            print(f"{'='*80}")
            print(f"策略ID: {strategy['strategy_id']}")
            print(f"股票: {strategy['symbol']} - {strategy['company_name']}")
            print(f"投资风格: {strategy['investment_style']}")
            print(f"推荐: {strategy['recommendation']}")
            print(f"目标价: ${strategy['target_price']}")
            print(f"当前价: ${strategy['current_price']}")
            print(f"创建时间: {strategy['created_at']}")
            
            # 检查期权策略
            option_strategy = strategy.get('option_strategy')
            if option_strategy:
                print(f"\n📊 期权策略: ✅ 存在")
                if isinstance(option_strategy, dict):
                    # 可能的格式1: 直接的strategy对象
                    if 'name' in option_strategy:
                        print(f"   策略名称: {option_strategy.get('name')}")
                        print(f"   策略类型: {option_strategy.get('type')}")
                    # 可能的格式2: 完整的result对象
                    elif 'strategy' in option_strategy:
                        print(f"   策略名称: {option_strategy['strategy'].get('name')}")
                        print(f"   策略类型: {option_strategy['strategy'].get('type')}")
                    else:
                        print(f"   数据格式: {json.dumps(option_strategy, indent=2, ensure_ascii=False)[:200]}")
                else:
                    print(f"   数据类型: {type(option_strategy)}")
            else:
                print(f"\n📊 期权策略: ❌ 不存在（这是测试数据）")
            
            print()
    else:
        print(f"❌ API返回错误: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("=" * 80)

