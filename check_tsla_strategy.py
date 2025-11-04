#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查TSLA策略数据
"""

import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("检查TSLA策略数据")
print("=" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    
    if response.status_code == 200:
        result = response.json()
        strategies = result.get('strategies', [])
        
        # 找到TSLA策略
        tsla_strategies = [s for s in strategies if s['symbol'] == 'TSLA']
        
        if not tsla_strategies:
            print("❌ 未找到TSLA策略")
        else:
            print(f"\n找到 {len(tsla_strategies)} 个TSLA策略\n")
            
            for i, strategy in enumerate(tsla_strategies, 1):
                print(f"{'='*80}")
                print(f"TSLA策略 #{i}")
                print(f"{'='*80}")
                print(f"策略ID: {strategy['strategy_id']}")
                print(f"股票: {strategy['symbol']} - {strategy['company_name']}")
                print(f"投资风格: {strategy['investment_style']}")
                print(f"推荐: {strategy['recommendation']}")
                print(f"目标价: ${strategy['target_price']}")
                print(f"当前价: ${strategy['current_price']}")
                print(f"创建时间: {strategy['created_at']}")
                
                # 关键检查：期权策略
                option_strategy = strategy.get('option_strategy')
                print(f"\n期权策略检查:")
                
                if option_strategy is None:
                    print(f"  ❌ option_strategy = None (未保存期权策略)")
                elif option_strategy == {}:
                    print(f"  ⚠️ option_strategy = {{}} (空对象)")
                elif isinstance(option_strategy, dict):
                    print(f"  ✅ option_strategy 存在（dict类型）")
                    print(f"  策略名称: {option_strategy.get('name', 'N/A')}")
                    print(f"  策略类型: {option_strategy.get('type', 'N/A')}")
                    print(f"  数据键: {list(option_strategy.keys())}")
                    
                    # 显示完整数据（前200字符）
                    print(f"\n  完整数据（截断）:")
                    print(f"  {json.dumps(option_strategy, indent=2, ensure_ascii=False)[:300]}")
                else:
                    print(f"  ⚠️ option_strategy 类型: {type(option_strategy)}")
                    print(f"  值: {option_strategy}")
                
                print()
    else:
        print(f"❌ API返回错误: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    import traceback
    traceback.print_exc()

print("=" * 80)

