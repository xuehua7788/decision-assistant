#!/usr/bin/env python3
"""将所有策略分配给bbb用户"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "=" * 80)
print("🔄 将策略分配给 bbb 用户")
print("=" * 80)

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# ============================================
# 1. 查找 bbb 用户的 ID
# ============================================
print("\n【1】查找 bbb 用户")
print("-" * 80)

cursor.execute("""
    SELECT id, username, created_at
    FROM users
    WHERE username = 'bbb'
""")

bbb_user = cursor.fetchone()

if not bbb_user:
    print("❌ 找不到 bbb 用户！")
    conn.close()
    exit(1)

print(f"✅ 找到用户:")
print(f"   ID: {bbb_user['id']}")
print(f"   用户名: {bbb_user['username']}")
print(f"   注册时间: {bbb_user['created_at']}")

bbb_user_id = bbb_user['id']

# ============================================
# 2. 查看当前策略状态
# ============================================
print("\n【2】当前策略状态")
print("-" * 80)

cursor.execute("""
    SELECT 
        id,
        strategy_id,
        symbol,
        investment_style,
        username,
        user_id,
        created_at
    FROM accepted_strategies
    ORDER BY created_at
""")

strategies = cursor.fetchall()

print(f"✅ 找到 {len(strategies)} 个策略:\n")

for i, s in enumerate(strategies, 1):
    username = s['username'] or '(未分配)'
    user_id = s['user_id'] or '(空)'
    print(f"[{i}] {s['symbol']:6} | {s['investment_style']:10} | user_id: {user_id:4} | username: {username}")

# ============================================
# 3. 更新所有策略到 bbb
# ============================================
print("\n【3】更新策略归属")
print("-" * 80)

try:
    # 更新所有策略
    cursor.execute("""
        UPDATE accepted_strategies
        SET 
            username = 'bbb',
            user_id = %s
        WHERE username IS NULL OR username != 'bbb'
        RETURNING id, symbol, investment_style
    """, (str(bbb_user_id),))
    
    updated = cursor.fetchall()
    
    if updated:
        print(f"✅ 成功更新 {len(updated)} 个策略:")
        for s in updated:
            print(f"   - {s['symbol']:6} ({s['investment_style']})")
    else:
        print("ℹ️  没有需要更新的策略（可能已经是 bbb 的了）")
    
    # 提交事务
    conn.commit()
    print("\n✅ 数据库事务已提交")
    
except Exception as e:
    print(f"❌ 更新失败: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# ============================================
# 4. 验证更新结果
# ============================================
print("\n【4】验证更新结果")
print("-" * 80)

cursor.execute("""
    SELECT 
        COUNT(*) as total_strategies,
        COUNT(CASE WHEN username = 'bbb' THEN 1 END) as bbb_strategies
    FROM accepted_strategies
""")

result = cursor.fetchone()

print(f"✅ 策略统计:")
print(f"   总策略数: {result['total_strategies']}")
print(f"   bbb的策略: {result['bbb_strategies']}")

if result['total_strategies'] == result['bbb_strategies']:
    print("\n🎉 完美！所有策略都已分配给 bbb！")
else:
    print(f"\n⚠️  还有 {result['total_strategies'] - result['bbb_strategies']} 个策略未分配")

# ============================================
# 5. 显示 bbb 的所有策略
# ============================================
print("\n【5】bbb 的所有策略")
print("-" * 80)

cursor.execute("""
    SELECT 
        id,
        symbol,
        company_name,
        investment_style,
        recommendation,
        target_price,
        current_price,
        score,
        created_at,
        option_strategy
    FROM accepted_strategies
    WHERE username = 'bbb'
    ORDER BY created_at DESC
""")

bbb_strategies = cursor.fetchall()

print(f"\n📊 bbb 共有 {len(bbb_strategies)} 个策略:\n")

for i, s in enumerate(bbb_strategies, 1):
    has_option = '✅ 有期权' if s['option_strategy'] else '❌ 无期权'
    print(f"[{i}] {s['symbol']:6} | {s['company_name'] or '(无名称)':20} | {s['investment_style']:10}")
    print(f"    推荐: {s['recommendation']:8} | 评分: {s['score'] or 'N/A':3} | {has_option}")
    print(f"    目标价: ${s['target_price']:8.2f} | 当前价: ${s['current_price']:8.2f}")
    print(f"    创建时间: {s['created_at']}")
    print()

cursor.close()
conn.close()

print("=" * 80)
print("✅ 操作完成！")
print("=" * 80)
print()


