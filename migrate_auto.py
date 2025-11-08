#!/usr/bin/env python3
"""自动迁移：将策略合并到users表"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n🔄 开始自动迁移...")

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# 1. 添加字段
print("\n[1/5] 添加 accepted_strategies 字段...")
try:
    cursor.execute("""
        ALTER TABLE users
        ADD COLUMN IF NOT EXISTS accepted_strategies JSONB DEFAULT '[]'::jsonb
    """)
    conn.commit()
    print("✅ 字段已添加")
except Exception as e:
    print(f"ℹ️  {e}")
    conn.rollback()

# 2. 读取策略
print("\n[2/5] 读取现有策略...")
cursor.execute("SELECT * FROM accepted_strategies ORDER BY username, created_at")
all_strategies = cursor.fetchall()
print(f"✅ 找到 {len(all_strategies)} 个策略")

# 3. 按用户分组
print("\n[3/5] 按用户分组...")
strategies_by_user = {}
for s in all_strategies:
    username = s['username'] or 'unknown'
    if username not in strategies_by_user:
        strategies_by_user[username] = []
    
    strategies_by_user[username].append({
        'strategy_id': s['strategy_id'],
        'symbol': s['symbol'],
        'company_name': s['company_name'],
        'investment_style': s['investment_style'],
        'recommendation': s['recommendation'],
        'target_price': float(s['target_price']) if s['target_price'] else None,
        'stop_loss': float(s['stop_loss']) if s['stop_loss'] else None,
        'position_size': s['position_size'],
        'score': s['score'],
        'strategy_text': s['strategy_text'],
        'analysis_summary': s['analysis_summary'],
        'current_price': float(s['current_price']) if s['current_price'] else None,
        'option_strategy': s['option_strategy'],
        'created_at': s['created_at'].isoformat() if s['created_at'] else None,
        'status': s['status']
    })

for username, strategies in strategies_by_user.items():
    print(f"   {username}: {len(strategies)} 个")

# 4. 迁移到users表
print("\n[4/5] 迁移到 users 表...")
for username, strategies in strategies_by_user.items():
    cursor.execute("""
        UPDATE users
        SET accepted_strategies = %s::jsonb
        WHERE username = %s
    """, (json.dumps(strategies, ensure_ascii=False), username))
    print(f"   ✅ {username}")

conn.commit()

# 5. 删除旧表
print("\n[5/5] 删除旧表...")
cursor.execute("DROP TABLE IF EXISTS accepted_strategies CASCADE")
conn.commit()
print("✅ accepted_strategies 表已删除")

# 验证
print("\n📊 验证结果:")
cursor.execute("""
    SELECT username, jsonb_array_length(accepted_strategies) as count
    FROM users
    WHERE jsonb_array_length(accepted_strategies) > 0
""")
for row in cursor.fetchall():
    print(f"   {row['username']}: {row['count']} 个策略")

cursor.close()
conn.close()

print("\n✅ 迁移完成！\n")


