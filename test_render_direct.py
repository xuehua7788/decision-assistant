#!/usr/bin/env python3
"""直接测试Render后端的数据"""
import requests
import json

BACKEND_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "="*80)
print("🧪 直接测试Render后端")
print("="*80)

# 1. 获取bbb的策略（从Render）
print("\n【1】从Render获取bbb的策略")
try:
    response = requests.get(f"{BACKEND_URL}/api/user/bbb/strategies", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        strategies = data.get('strategies', [])
        
        print(f"✅ Render返回 {len(strategies)} 个策略")
        
        if strategies:
            first = strategies[0]
            print(f"\n第一个策略（Render）:")
            print(f"   strategy_id: {first.get('strategy_id')}")
            print(f"   symbol: {first.get('symbol')}")
            print(f"   类型: {type(first.get('strategy_id'))}")
            
            # 尝试直接用这个strategy_id评估
            print(f"\n【2】使用这个strategy_id评估")
            
            eval_payload = {
                "strategy_id": first.get('strategy_id'),
                "symbol": first.get('symbol'),
                "username": "bbb"
            }
            
            print(f"请求payload:")
            print(json.dumps(eval_payload, indent=2))
            
            eval_response = requests.post(
                f"{BACKEND_URL}/api/strategy/evaluate",
                json=eval_payload,
                headers={"Content-Type": "application/json"},
                timeout=15
            )
            
            print(f"\n状态码: {eval_response.status_code}")
            print(f"响应: {eval_response.text}")
            
            if eval_response.status_code == 200:
                print("\n✅ 评估成功！")
                result = eval_response.json()
                eval_data = result.get('evaluation', {})
                print(f"   当前价格: ${eval_data.get('current_price', 0):.2f}")
                print(f"   收益率: {eval_data.get('price_change_pct', 0):.2f}%")
            else:
                print(f"\n❌ 评估失败")
                print(f"   错误: {eval_response.text}")
                
    else:
        print(f"❌ 获取策略失败: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ 异常: {e}")

# 2. 比较：本地数据库 vs Render返回的数据
print("\n" + "="*80)
print("【3】对比本地数据库和Render返回")
print("="*80)

import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("SELECT accepted_strategies FROM users WHERE username = 'bbb'")
    result = cur.fetchone()
    
    if result:
        db_strategies = result['accepted_strategies'] or []
        print(f"本地数据库: {len(db_strategies)} 个策略")
        
        if db_strategies:
            print(f"   第一个strategy_id: {db_strategies[0].get('strategy_id')}")
            
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ 数据库查询失败: {e}")

print("\n" + "="*80)
print()


