#!/usr/bin/env python3
"""查看数据库中的所有表"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "=" * 80)
print("🗄️  数据库表结构概览")
print("=" * 80)

conn = psycopg2.connect(DATABASE_URL)

# ============================================
# 1. 列出所有表
# ============================================
print("\n【1】所有表列表")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            table_name,
            (SELECT COUNT(*) 
             FROM information_schema.columns 
             WHERE table_name = t.table_name) as column_count
        FROM information_schema.tables t
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    tables = cursor.fetchall()
    
    print(f"✅ 找到 {len(tables)} 个表:\n")
    
    for i, table in enumerate(tables, 1):
        print(f"[{i}] {table['table_name']}")
        print(f"    列数: {table['column_count']}")
    
    cursor.close()
    print()
    
except Exception as e:
    print(f"❌ 查询失败: {e}")

# ============================================
# 2. 每个表的详细结构
# ============================================
print("【2】表结构详情")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    # 获取所有表名
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_type = 'BASE TABLE'
        ORDER BY table_name
    """)
    
    table_names = [row['table_name'] for row in cursor.fetchall()]
    
    for table_name in table_names:
        print(f"\n📊 表: {table_name}")
        print("   " + "-" * 76)
        
        # 获取该表的列信息
        cursor.execute("""
            SELECT 
                column_name,
                data_type,
                character_maximum_length,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        
        columns = cursor.fetchall()
        
        for col in columns:
            col_type = col['data_type']
            if col['character_maximum_length']:
                col_type += f"({col['character_maximum_length']})"
            
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            default = f" DEFAULT {col['column_default']}" if col['column_default'] else ""
            
            print(f"   - {col['column_name']:<25} {col_type:<20} {nullable}{default}")
        
        # 获取该表的行数
        try:
            cursor.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cursor.fetchone()['count']
            print(f"\n   📈 数据行数: {count}")
        except:
            pass
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 查询失败: {e}")

# ============================================
# 3. 表关系和索引
# ============================================
print("\n" + "=" * 80)
print("【3】索引信息")
print("-" * 80)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname
    """)
    
    indexes = cursor.fetchall()
    
    if indexes:
        current_table = None
        for idx in indexes:
            if idx['tablename'] != current_table:
                current_table = idx['tablename']
                print(f"\n📊 表: {current_table}")
            
            print(f"   索引: {idx['indexname']}")
    else:
        print("   无索引")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 查询失败: {e}")

conn.close()

print("\n" + "=" * 80)
print("✅ 查询完成")
print("=" * 80)
print()


