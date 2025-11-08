#!/usr/bin/env python3
"""直接检查Render数据库的实际状态"""
import psycopg2
from psycopg2.extras import RealDictCursor

# Render数据库URL
DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "="*80)
print("🔍 直接检查Render数据库")
print("="*80)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 1. 检查accepted_strategies表是否还存在
print("\n【1】检查旧表accepted_strategies是否存在")
cur.execute("""
    SELECT EXISTS (
        SELECT FROM information_schema.tables 
        WHERE table_name = 'accepted_strategies'
    )
""")
result = cur.fetchone()
table_exists = list(result.values())[0] if result else False
print(f"   accepted_strategies表存在: {table_exists}")

if table_exists:
    print("   ⚠️  旧表还在！迁移可能没有完成")
else:
    print("   ✅ 旧表已删除，迁移完成")

# 2. 检查users表的accepted_strategies字段
print("\n【2】检查users表结构")
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'users' AND column_name = 'accepted_strategies'
""")
column = cur.fetchone()
if column:
    print(f"   ✅ accepted_strategies字段存在")
    print(f"      类型: {column['data_type']}")
else:
    print(f"   ❌ accepted_strategies字段不存在！")

# 3. 检查bbb用户的数据
print("\n【3】检查bbb用户的策略数据")
cur.execute("SELECT username, accepted_strategies FROM users WHERE username = 'bbb'")
result = cur.fetchone()

if result:
    print(f"   ✅ 找到用户 bbb")
    strategies = result['accepted_strategies']
    
    if strategies:
        print(f"   策略数据类型: {type(strategies)}")
        print(f"   策略数量: {len(strategies) if isinstance(strategies, list) else 'N/A'}")
        
        if isinstance(strategies, list) and len(strategies) > 0:
            first = strategies[0]
            print(f"\n   第一个策略:")
            print(f"      strategy_id: {first.get('strategy_id')}")
            print(f"      symbol: {first.get('symbol')}")
        else:
            print(f"   ⚠️  策略数据为空或格式错误")
            print(f"   原始数据: {strategies}")
    else:
        print(f"   ❌ accepted_strategies为NULL或空")
else:
    print(f"   ❌ 未找到用户 bbb")

cur.close()
conn.close()

print("\n" + "="*80)
print()

