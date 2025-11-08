#!/usr/bin/env python3
"""
数据库迁移：将策略从 accepted_strategies 表迁移到 users 表
1. 在 users 表添加 accepted_strategies JSONB 字段
2. 将现有策略迁移到对应用户
3. 备份后删除 accepted_strategies 表
"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "=" * 80)
print("🔄 数据库迁移：策略数据合并到 users 表")
print("=" * 80)

conn = psycopg2.connect(DATABASE_URL)
cursor = conn.cursor(cursor_factory=RealDictCursor)

# ============================================
# 步骤1: 检查 users 表当前结构
# ============================================
print("\n【步骤1】检查 users 表当前结构")
print("-" * 80)

cursor.execute("""
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_name = 'users'
    ORDER BY ordinal_position
""")

columns = cursor.fetchall()
print("当前列:")
for col in columns:
    print(f"   - {col['column_name']:25} {col['data_type']}")

has_strategies_column = any(col['column_name'] == 'accepted_strategies' for col in columns)

# ============================================
# 步骤2: 添加 accepted_strategies 字段
# ============================================
print("\n【步骤2】添加 accepted_strategies 字段")
print("-" * 80)

try:
    if not has_strategies_column:
        cursor.execute("""
            ALTER TABLE users
            ADD COLUMN accepted_strategies JSONB DEFAULT '[]'::jsonb
        """)
        conn.commit()
        print("✅ 成功添加 accepted_strategies 字段 (JSONB类型)")
    else:
        print("ℹ️  accepted_strategies 字段已存在")
except Exception as e:
    print(f"❌ 添加字段失败: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# ============================================
# 步骤3: 读取所有现有策略
# ============================================
print("\n【步骤3】读取 accepted_strategies 表的数据")
print("-" * 80)

cursor.execute("""
    SELECT 
        id,
        strategy_id,
        username,
        user_id,
        symbol,
        company_name,
        investment_style,
        recommendation,
        target_price,
        stop_loss,
        position_size,
        score,
        strategy_text,
        analysis_summary,
        current_price,
        option_strategy,
        created_at,
        status
    FROM accepted_strategies
    ORDER BY username, created_at
""")

all_strategies = cursor.fetchall()
print(f"✅ 读取到 {len(all_strategies)} 个策略")

# 按用户分组
strategies_by_user = {}
for s in all_strategies:
    username = s['username'] or 'unknown'
    if username not in strategies_by_user:
        strategies_by_user[username] = []
    
    # 转换为前端需要的格式
    strategy_obj = {
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
    }
    
    strategies_by_user[username].append(strategy_obj)

print(f"\n策略分布:")
for username, strategies in strategies_by_user.items():
    print(f"   {username}: {len(strategies)} 个策略")

# ============================================
# 步骤4: 迁移策略到 users 表
# ============================================
print("\n【步骤4】迁移策略到 users 表")
print("-" * 80)

try:
    for username, strategies in strategies_by_user.items():
        # 转换为JSON字符串
        strategies_json = json.dumps(strategies, ensure_ascii=False)
        
        cursor.execute("""
            UPDATE users
            SET accepted_strategies = %s::jsonb
            WHERE username = %s
            RETURNING id, username
        """, (strategies_json, username))
        
        result = cursor.fetchone()
        
        if result:
            print(f"✅ {username}: 迁移了 {len(strategies)} 个策略")
        else:
            print(f"⚠️  {username}: 用户不存在，跳过")
    
    conn.commit()
    print("\n✅ 策略迁移完成！")
    
except Exception as e:
    print(f"❌ 迁移失败: {e}")
    conn.rollback()
    conn.close()
    exit(1)

# ============================================
# 步骤5: 验证迁移结果
# ============================================
print("\n【步骤5】验证迁移结果")
print("-" * 80)

cursor.execute("""
    SELECT 
        id,
        username,
        jsonb_array_length(accepted_strategies) as strategy_count
    FROM users
    WHERE jsonb_array_length(accepted_strategies) > 0
    ORDER BY username
""")

users_with_strategies = cursor.fetchall()

print(f"\n✅ 有策略的用户 ({len(users_with_strategies)} 个):\n")
for user in users_with_strategies:
    print(f"   {user['username']:15} - {user['strategy_count']} 个策略")

# ============================================
# 步骤6: 备份并删除 accepted_strategies 表
# ============================================
print("\n【步骤6】删除 accepted_strategies 表")
print("-" * 80)

user_input = input("⚠️  确认删除 accepted_strategies 表？数据已迁移。(yes/no): ")

if user_input.lower() == 'yes':
    try:
        # 先备份到一个临时表（可选）
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accepted_strategies_backup AS
            SELECT * FROM accepted_strategies
        """)
        print("✅ 已创建备份表: accepted_strategies_backup")
        
        # 删除原表
        cursor.execute("DROP TABLE IF EXISTS accepted_strategies CASCADE")
        conn.commit()
        print("✅ 已删除 accepted_strategies 表")
        
    except Exception as e:
        print(f"❌ 删除失败: {e}")
        conn.rollback()
else:
    print("ℹ️  已取消删除操作")

# ============================================
# 步骤7: 显示最终的 users 表结构
# ============================================
print("\n【步骤7】最终的 users 表结构")
print("-" * 80)

cursor.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = 'users'
    ORDER BY ordinal_position
""")

final_columns = cursor.fetchall()
print("\n✅ users 表字段:")
for col in final_columns:
    nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
    print(f"   - {col['column_name']:25} {col['data_type']:20} {nullable}")

# ============================================
# 步骤8: 查看 bbb 的策略示例
# ============================================
print("\n【步骤8】查看 bbb 用户的策略")
print("-" * 80)

cursor.execute("""
    SELECT 
        username,
        accepted_strategies
    FROM users
    WHERE username = 'bbb'
""")

bbb_data = cursor.fetchone()

if bbb_data:
    strategies = bbb_data['accepted_strategies']
    print(f"\n✅ bbb 有 {len(strategies)} 个策略:\n")
    
    for i, s in enumerate(strategies[:3], 1):  # 只显示前3个
        print(f"[{i}] {s['symbol']} - {s['investment_style']}")
        print(f"    推荐: {s['recommendation']} | 评分: {s.get('score', 'N/A')}")
        if i < 3 and len(strategies) > 3:
            print()
    
    if len(strategies) > 3:
        print(f"... 还有 {len(strategies) - 3} 个策略")
else:
    print("❌ 找不到 bbb 用户")

cursor.close()
conn.close()

print("\n" + "=" * 80)
print("✅ 迁移完成！")
print("=" * 80)
print()


