#!/usr/bin/env python3
"""测试策略数据结构"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "="*80)
print("🔍 测试策略数据结构和匹配逻辑")
print("="*80)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. 获取用户策略
cur.execute("SELECT accepted_strategies FROM users WHERE username = 'bbb'")
result = cur.fetchone()

if not result:
    print("❌ 用户不存在")
    exit(1)

strategies = result['accepted_strategies'] if result['accepted_strategies'] else []

print(f"\n✅ 用户有 {len(strategies)} 个策略")

# 2. 测试匹配逻辑
test_strategy_id = "NVDA_20251104_060307_lynch"

print(f"\n🔍 测试匹配: {test_strategy_id}")

found = False
for i, s in enumerate(strategies):
    s_id = s.get('strategy_id')
    matches = (s_id == test_strategy_id)
    
    if i < 3:  # 只显示前3个
        print(f"   [{i}] {s_id}")
        print(f"       == {test_strategy_id} ? {matches}")
        print(f"       类型对比: {type(s_id)} vs {type(test_strategy_id)}")
    
    if matches:
        found = True
        print(f"\n   ✅ 找到匹配！索引: {i}")
        print(f"   完整策略数据:")
        print(json.dumps(s, indent=2, ensure_ascii=False))
        break

if not found:
    print(f"\n   ❌ 未找到匹配")
    print(f"\n   所有可用的strategy_id:")
    for s in strategies:
        print(f"      - {s.get('strategy_id')}")

# 3. 测试后端的查找逻辑（模拟）
print(f"\n" + "="*80)
print("🔬 模拟后端查找逻辑")
print("="*80)

def find_strategy(strategies, strategy_id):
    """模拟后端的查找逻辑"""
    for s in strategies:
        if s.get('strategy_id') == strategy_id:
            return s
    return None

test_result = find_strategy(strategies, test_strategy_id)

if test_result:
    print(f"✅ 模拟查找成功")
    print(f"   symbol: {test_result.get('symbol')}")
    print(f"   current_price: {test_result.get('current_price')}")
else:
    print(f"❌ 模拟查找失败")

cur.close()
conn.close()

print("\n" + "="*80)
print()


