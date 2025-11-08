import psycopg2
import json

# 数据库连接
DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

# 查询bbb用户的策略
cur.execute("""
    SELECT username, accepted_strategies 
    FROM users 
    WHERE username = 'bbb'
""")

result = cur.fetchone()
if result:
    username = result[0]
    strategies = result[1]
    
    print(f'用户: {username}')
    print(f'策略数量: {len(strategies) if strategies else 0}')
    print('\n' + '='*80 + '\n')
    
    if strategies:
        for i, strategy in enumerate(strategies, 1):
            print(f'策略 #{i}')
            print('-' * 80)
            print(json.dumps(strategy, indent=2, ensure_ascii=False))
            print('\n' + '='*80 + '\n')
else:
    print('未找到bbb用户')

conn.close()

