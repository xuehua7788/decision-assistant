#!/usr/bin/env python3
"""列出所有注册用户"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "="*80)
print("👥 所有注册用户列表")
print("="*80)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 查询所有用户
cur.execute("""
    SELECT 
        id,
        username,
        email,
        created_at,
        is_active,
        CASE 
            WHEN accepted_strategies IS NULL THEN 0
            ELSE jsonb_array_length(accepted_strategies)
        END as strategy_count
    FROM users
    ORDER BY created_at DESC
""")

users = cur.fetchall()

print(f"\n✅ 共有 {len(users)} 个注册用户:\n")

for i, user in enumerate(users, 1):
    status = "✅ 活跃" if user['is_active'] else "❌ 停用"
    email = user['email'] or "(无邮箱)"
    
    print(f"[{i}] {user['username']}")
    print(f"    ID: {user['id']}")
    print(f"    邮箱: {email}")
    print(f"    状态: {status}")
    print(f"    策略数: {user['strategy_count']}")
    print(f"    注册时间: {user['created_at']}")
    print()

# 统计
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(CASE WHEN is_active THEN 1 END) as active,
        SUM(CASE 
            WHEN accepted_strategies IS NULL THEN 0
            ELSE jsonb_array_length(accepted_strategies)
        END) as total_strategies
    FROM users
""")

stats = cur.fetchone()

print("="*80)
print("📊 统计信息")
print("-"*80)
print(f"总用户数: {stats['total']}")
print(f"活跃用户: {stats['active']}")
print(f"总策略数: {stats['total_strategies']}")
print("="*80)
print()

cur.close()
conn.close()


