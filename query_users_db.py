#!/usr/bin/env python3
"""数据库查询用户信息（交互式）"""
import sys

print("\n" + "=" * 80)
print("🗄️  数据库用户查询工具")
print("=" * 80)

# 获取 DATABASE_URL
print("\n请输入 DATABASE_URL:")
print("(格式: postgresql://user:pass@host/db)")
print()

database_url = input("DATABASE_URL: ").strip()

if not database_url:
    print("\n❌ 未提供 DATABASE_URL，退出")
    sys.exit(1)

if not database_url.startswith('postgresql://'):
    print("\n❌ URL 格式错误，应以 postgresql:// 开头")
    sys.exit(1)

# 连接数据库
print("\n🔌 连接数据库...")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    
    conn = psycopg2.connect(database_url)
    print("✅ 连接成功！\n")
    
except ImportError:
    print("\n❌ 缺少 psycopg2 模块")
    print("   请运行: pip install psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ 连接失败: {e}")
    sys.exit(1)

# 查询用户
print("=" * 80)
print("👥 查询所有用户")
print("=" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 查询用户表
    cursor.execute("""
        SELECT 
            user_id,
            username,
            email,
            created_at,
            last_login
        FROM users
        ORDER BY created_at DESC
    """)
    
    users = cursor.fetchall()
    
    if users:
        print(f"\n📊 找到 {len(users)} 个用户\n")
        
        for i, user in enumerate(users, 1):
            print(f"[{i}] {'=' * 75}")
            print(f"🆔 用户ID: {user['user_id']}")
            print(f"👤 用户名: {user['username']}")
            print(f"📧 邮箱: {user['email'] or '(未设置)'}")
            print(f"📅 注册时间: {user['created_at']}")
            
            if user['last_login']:
                print(f"🕐 最后登录: {user['last_login']}")
            else:
                print(f"🕐 最后登录: 从未登录")
            
            print()
    else:
        print("\n⚠️  数据库中没有用户")
    
    cursor.close()
    
except psycopg2.errors.UndefinedTable:
    print("\n❌ users 表不存在")
    print("   数据库可能未初始化")
except Exception as e:
    print(f"\n❌ 查询失败: {e}")
    import traceback
    traceback.print_exc()

# 查询策略
print("=" * 80)
print("📊 查询策略表信息")
print("=" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 统计策略
    cursor.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(DISTINCT symbol) as unique_stocks,
            COUNT(CASE WHEN username IS NOT NULL THEN 1 END) as with_user,
            COUNT(CASE WHEN username IS NULL THEN 1 END) as without_user
        FROM accepted_strategies
    """)
    
    stats = cursor.fetchone()
    
    print(f"\n📈 策略统计:")
    print(f"   总策略数: {stats['total']}")
    print(f"   涉及股票: {stats['unique_stocks']}")
    print(f"   关联用户: {stats['with_user']}")
    print(f"   未关联: {stats['without_user']}")
    
    # 检查是否有 username 列
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='accepted_strategies' 
        AND column_name IN ('user_id', 'username')
    """)
    
    columns = [row['column_name'] for row in cursor.fetchall()]
    
    print(f"\n🔍 用户字段检查:")
    print(f"   user_id 列: {'✅ 存在' if 'user_id' in columns else '❌ 不存在'}")
    print(f"   username 列: {'✅ 存在' if 'username' in columns else '❌ 不存在'}")
    
    if 'user_id' not in columns or 'username' not in columns:
        print(f"\n⚠️  需要运行数据库迁移！")
        print(f"   运行: python migrate_add_user_columns.py")
    
    # 显示最近的策略
    if stats['total'] > 0:
        cursor.execute("""
            SELECT 
                strategy_id,
                symbol,
                username,
                investment_style,
                score,
                created_at
            FROM accepted_strategies
            ORDER BY created_at DESC
            LIMIT 5
        """)
        
        recent = cursor.fetchall()
        
        print(f"\n📋 最近5个策略:")
        for i, s in enumerate(recent, 1):
            username_str = s['username'] if s.get('username') else '(无用户)'
            print(f"   [{i}] {s['symbol']} | {username_str} | {s['investment_style']} | {s['created_at']}")
    
    cursor.close()
    
except Exception as e:
    print(f"\n❌ 查询失败: {e}")

# 专门查询 bbb 用户
print("\n" + "=" * 80)
print("🔍 查询 bbb 用户")
print("=" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("SELECT * FROM users WHERE username = 'bbb'")
    bbb_user = cursor.fetchone()
    
    if bbb_user:
        print("\n✅ 找到 bbb 用户！")
        print(f"   用户ID: {bbb_user['user_id']}")
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
        print("\n❌ 未找到 bbb 用户")
        print("   可能：")
        print("   1. 用户名拼写错误")
        print("   2. 该用户从未注册")
        print("   3. 注册时数据库不可用")
    
    cursor.close()
    
except Exception as e:
    print(f"\n❌ 查询失败: {e}")

# 关闭连接
conn.close()

print("\n" + "=" * 80)
print("✅ 查询完成")
print("=" * 80)
print()


