#!/usr/bin/env python3
"""立即运行数据库迁移和查询"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "=" * 80)
print("🔧 数据库操作执行中...")
print("=" * 80)

# ============================================
# 步骤1：连接数据库
# ============================================
print("\n【步骤1】连接数据库...")
print("-" * 80)

try:
    conn = psycopg2.connect(DATABASE_URL)
    print("✅ 数据库连接成功")
except Exception as e:
    print(f"❌ 连接失败: {e}")
    exit(1)

# ============================================
# 步骤2：检查现有表结构
# ============================================
print("\n【步骤2】检查表结构...")
print("-" * 80)

try:
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='accepted_strategies'
        ORDER BY ordinal_position
    """)
    
    columns = [row[0] for row in cursor.fetchall()]
    print(f"✅ accepted_strategies 表现有列:")
    for col in columns:
        print(f"   - {col}")
    
    has_username = 'username' in columns
    has_user_id = 'user_id' in columns
    
    print(f"\n   username 列: {'✅ 存在' if has_username else '❌ 不存在'}")
    print(f"   user_id 列: {'✅ 存在' if has_user_id else '❌ 不存在'}")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 检查失败: {e}")
    conn.close()
    exit(1)

# ============================================
# 步骤3：添加缺失的列
# ============================================
if not has_username or not has_user_id:
    print("\n【步骤3】添加缺失的列...")
    print("-" * 80)
    
    try:
        cursor = conn.cursor()
        
        if not has_user_id:
            print("   添加 user_id 列...")
            cursor.execute("""
                ALTER TABLE accepted_strategies 
                ADD COLUMN IF NOT EXISTS user_id VARCHAR(50)
            """)
            print("   ✅ user_id 列已添加")
        
        if not has_username:
            print("   添加 username 列...")
            cursor.execute("""
                ALTER TABLE accepted_strategies 
                ADD COLUMN IF NOT EXISTS username VARCHAR(50)
            """)
            print("   ✅ username 列已添加")
        
        # 创建索引
        print("   创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_strategy_username 
            ON accepted_strategies(username)
        """)
        print("   ✅ 索引已创建")
        
        conn.commit()
        cursor.close()
        
        print("\n✅ 数据库迁移完成！")
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        conn.rollback()
        conn.close()
        exit(1)
else:
    print("\n【步骤3】跳过 - 列已存在")

# ============================================
# 步骤4：查询所有用户
# ============================================
print("\n【步骤4】查询所有注册用户...")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT user_id, username, email, created_at 
        FROM users 
        ORDER BY created_at DESC
        LIMIT 20
    """)
    
    users = cursor.fetchall()
    
    print(f"✅ 找到 {len(users)} 个用户:\n")
    
    for i, user in enumerate(users, 1):
        print(f"[{i}] {user['username']}")
        print(f"    ID: {user['user_id']}")
        print(f"    邮箱: {user['email'] or '(无)'}")
        print(f"    注册: {user['created_at']}")
        print()
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 查询用户失败: {e}")

# ============================================
# 步骤5：查找 bbb 用户
# ============================================
print("【步骤5】查找 bbb 用户...")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE username = 'bbb'")
    bbb_user = cursor.fetchone()
    
    if bbb_user:
        print("✅ 找到 bbb 用户！")
        print(f"   用户ID: {bbb_user['user_id']}")
        print(f"   用户名: {bbb_user['username']}")
        print(f"   注册时间: {bbb_user['created_at']}")
        
        # 查询 bbb 的策略
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM accepted_strategies 
            WHERE username = 'bbb'
        """)
        
        strategy_count = cursor.fetchone()['count']
        print(f"   策略数量: {strategy_count}")
        
    else:
        print("❌ 未找到 bbb 用户")
        print("   可能原因：")
        print("   1. 用户名拼写错误")
        print("   2. 该用户从未成功注册")
        print("   3. 注册时数据库不可用，只保存到了临时文件")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 查询失败: {e}")

# ============================================
# 步骤6：查询策略统计
# ============================================
print("\n【步骤6】策略统计...")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(CASE WHEN username IS NOT NULL THEN 1 END) as with_user,
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
        SELECT strategy_id, symbol, username, investment_style, created_at
        FROM accepted_strategies
        ORDER BY created_at DESC
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    
    if recent:
        print(f"\n   最近5个策略:")
        for i, s in enumerate(recent, 1):
            username_str = s['username'] if s['username'] else '(无用户)'
            print(f"   [{i}] {s['symbol']} | {username_str} | {s['created_at']}")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 统计失败: {e}")

# ============================================
# 关闭连接
# ============================================
conn.close()

print("\n" + "=" * 80)
print("✅ 所有操作完成")
print("=" * 80)
print()


