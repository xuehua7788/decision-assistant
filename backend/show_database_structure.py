import psycopg2
import os

# 数据库连接
DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 1. 查询所有表
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")
tables = cur.fetchall()
print('=== 数据库中的所有表 ===')
for t in tables:
    print(f'  - {t[0]}')

print('\n' + '='*80 + '\n')

# 2. 查询每个表的结构
for table in tables:
    table_name = table[0]
    print(f'📊 表名: {table_name}')
    print('-' * 80)
    
    # 查询列信息
    cur.execute(f"""
        SELECT 
            column_name, 
            data_type, 
            character_maximum_length,
            is_nullable,
            column_default
        FROM information_schema.columns 
        WHERE table_name = '{table_name}'
        ORDER BY ordinal_position
    """)
    
    columns = cur.fetchall()
    print(f"{'列名':<25} {'数据类型':<20} {'可空':<8} {'默认值':<30}")
    print('-' * 80)
    for col in columns:
        col_name = col[0]
        data_type = col[1]
        if col[2]:  # 如果有长度限制
            data_type += f'({col[2]})'
        nullable = col[3]
        default_val = col[4] if col[4] else ''
        print(f'{col_name:<25} {data_type:<20} {nullable:<8} {default_val:<30}')
    
    # 查询主键
    cur.execute(f"""
        SELECT a.attname
        FROM pg_index i
        JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = ANY(i.indkey)
        WHERE i.indrelid = '{table_name}'::regclass AND i.indisprimary
    """)
    pks = cur.fetchall()
    if pks:
        print(f"\n🔑 主键: {', '.join([pk[0] for pk in pks])}")
    
    # 查询数据量
    cur.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cur.fetchone()[0]
    print(f'📈 数据量: {count} 条')
    
    # 如果数据量少，显示示例数据
    if count > 0 and count <= 5:
        print(f'\n📝 示例数据:')
        cur.execute(f'SELECT * FROM {table_name} LIMIT 3')
        sample_data = cur.fetchall()
        for row in sample_data:
            print(f'   {row}')
    
    print('\n' + '='*80 + '\n')

conn.close()

