#!/usr/bin/env python3
"""检查数据库中实际的strategy_id格式"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "="*80)
print("🔍 检查bbb用户的strategy_id")
print("="*80)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

cur.execute("SELECT accepted_strategies FROM users WHERE username = 'bbb'")
result = cur.fetchone()

if result and result['accepted_strategies']:
    strategies = result['accepted_strategies']
    
    print(f"\n✅ 找到 {len(strategies)} 个策略\n")
    
    for i, s in enumerate(strategies, 1):
        strategy_id = s.get('strategy_id')
        symbol = s.get('symbol')
        
        print(f"[{i}] {symbol}")
        print(f"    strategy_id: '{strategy_id}'")
        print(f"    类型: {type(strategy_id)}")
        print(f"    长度: {len(strategy_id) if strategy_id else 'None'}")
        print(f"    原始: {repr(strategy_id)}")
        print()
else:
    print("❌ 没有找到策略")

cur.close()
conn.close()

print("="*80)
print()


