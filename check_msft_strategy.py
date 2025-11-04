#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查MSFT策略详情
"""

import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("检查MSFT策略详情")
print("=" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list?symbol=MSFT", timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        strategies = result.get('strategies', [])
        
        if not strategies:
            print("❌ 未找到MSFT策略")
        else:
            for strategy in strategies:
                print(f"\n策略ID: {strategy['strategy_id']}")
                print(f"股票: {strategy['symbol']} - {strategy['company_name']}")
                print(f"推荐: {strategy['recommendation']}")
                print(f"目标价: ${strategy['target_price']}")
                print(f"创建时间: {strategy['created_at']}")
                
                # 关键检查
                option_strategy = strategy.get('option_strategy')
                print(f"\n期权策略数据:")
                if option_strategy:
                    print(f"  类型: {type(option_strategy)}")
                    print(f"  内容: {json.dumps(option_strategy, indent=2, ensure_ascii=False)[:500]}")
                else:
                    print(f"  ❌ 无期权策略")
    else:
        print(f"❌ API返回错误: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

