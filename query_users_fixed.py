#!/usr/bin/env python3
"""修复后的用户查询"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "=" * 80)
print("🔍 查询用户和策略")
print("=" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ 数据库连接成功\n")
except Exception as e:
    print(f"❌ 连接失败: {e}")
    exit(1)

# ============================================
# 1. 检查 users 表结构
# ============================================
print("【1】检查 users 表结构...")
print("-" * 80)

try:
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='users'
        ORDER BY ordinal_position
    """)
    
    columns = [row[0] for row in cursor.fetchall()]
    print(f"users 表的列:")
    for col in columns:
        print(f"   - {col}")
    
    cursor.close()
    print()
    
except Exception as e:
    print(f"❌ 检查失败: {e}\n")

# ============================================
# 2. 查询所有用户（适配实际表结构）
# ============================================
print("【2】查询所有用户...")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 使用实际存在的列
    cursor.execute("""
        SELECT * FROM users 
        ORDER BY created_at DESC 
        LIMIT 20
    """)
    
    users = cursor.fetchall()
    
    print(f"✅ 找到 {len(users)} 个用户:\n")
    
    for i, user in enumerate(users, 1):
        print(f"[{i}] 用户名: {user.get('username', 'N/A')}")
        for key, value in user.items():
            if key != 'password_hash' and key != 'password':  # 不显示密码
                print(f"    {key}: {value}")
        print()
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 查询失败: {e}\n")
    conn.rollback()

# ============================================
# 3. 专门查找 bbb 用户
# ============================================
print("【3】查找 bbb 用户...")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE username = 'bbb'")
    bbb_user = cursor.fetchone()
    
    if bbb_user:
        print("✅ 找到 bbb 用户！\n")
        for key, value in bbb_user.items():
            if key != 'password_hash' and key != 'password':
                print(f"   {key}: {value}")
        
        # 查询 bbb 的策略
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM accepted_strategies 
            WHERE username = 'bbb'
        """)
        
        strategy_count = cursor.fetchone()['count']
        print(f"\n   关联的策略数: {strategy_count}")
        
    else:
        print("❌ 未找到 bbb 用户")
        print("\n可能的原因:")
        print("   1. 用户名是 'bx' 不是 'bbb'（你记错了）")
        print("   2. bbb 从未成功注册到数据库")
        print("   3. 注册时数据库不可用，只保存到了临时文件")
    
    cursor.close()
    print()
    
except Exception as e:
    print(f"❌ 查询失败: {e}\n")
    conn.rollback()

# ============================================
# 4. 策略表统计
# ============================================
print("【4】策略表统计...")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN username IS NOT NULL AND username != '' THEN 1 END) as with_user,
            COUNT(DISTINCT symbol) as unique_stocks
        FROM accepted_strategies
    """)
    
    stats = cursor.fetchone()
    
    print(f"✅ 策略统计:")
    print(f"   总策略数: {stats['total']}")
    print(f"   关联用户: {stats['with_user']}")
    print(f"   未关联: {stats['total'] - stats['with_user']}")
    print(f"   涉及股票: {stats['unique_stocks']}")
    
    # 显示最近的策略
    cursor.execute("""
        SELECT strategy_id, symbol, username, investment_style, 
               created_at::date as date
        FROM accepted_strategies
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    
    if recent:
        print(f"\n   最近5个策略:")
        for i, s in enumerate(recent, 1):
            username_str = s['username'] if s['username'] else '(无用户)'
            print(f"   [{i}] {s['symbol']} | {username_str} | {s['investment_style']} | {s['date']}")
    
    cursor.close()
    print()
    
except Exception as e:
    print(f"❌ 统计失败: {e}\n")
    conn.rollback()

# ============================================
# 5. 测试新功能
# ============================================
print("【5】验证迁移是否成功...")
print("-" * 80)

try:
    cursor = conn.cursor()
    
    # 检查新列是否真的存在
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='accepted_strategies' 
        AND column_name IN ('username', 'user_id')
    """)
    
    new_columns = [row[0] for row in cursor.fetchall()]
    
    if 'username' in new_columns and 'user_id' in new_columns:
        print("✅ 迁移成功！新列已添加:")
        print("   - username ✅")
        print("   - user_id ✅")
        print("\n💡 现在保存的新策略将包含用户信息")
    else:
        print("⚠️  部分列缺失")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 验证失败: {e}")

conn.close()

print("\n" + "=" * 80)
print("✅ 查询完成")
print("=" * 80)
print()


