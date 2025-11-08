#!/usr/bin/env python3
import psycopg2
import json

URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

conn = psycopg2.connect(URL)
cur = conn.cursor()

print("1. 添加字段...")
cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS accepted_strategies JSONB DEFAULT '[]'::jsonb")
conn.commit()
print("✅")

print("2. 读取策略...")
cur.execute("SELECT username, json_agg(row_to_json(accepted_strategies)) FROM accepted_strategies WHERE username IS NOT NULL GROUP BY username")
rows = cur.fetchall()
print(f"✅ {len(rows)} 个用户")

print("3. 更新users...")
for username, strategies_json in rows:
    cur.execute("UPDATE users SET accepted_strategies = %s WHERE username = %s", (json.dumps(strategies_json), username))
    print(f"   {username}")
conn.commit()
print("✅")

print("4. 删除旧表...")
cur.execute("DROP TABLE accepted_strategies CASCADE")
conn.commit()
print("✅")

print("5. 验证...")
cur.execute("SELECT username, jsonb_array_length(accepted_strategies) FROM users WHERE accepted_strategies != '[]'::jsonb")
for row in cur.fetchall():
    print(f"   {row[0]}: {row[1]} 个")

cur.close()
conn.close()
print("\n✅ 完成\n")


