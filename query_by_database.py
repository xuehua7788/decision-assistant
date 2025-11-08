#!/usr/bin/env python3
"""通过数据库直接查询用户策略"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

def query_user_strategies_from_db(username):
    """从数据库查询用户策略"""
    print(f"\n🔍 从数据库查询 {username} 的策略...")
    print("-" * 80)
    
    conn = psycopg2.connect(DATABASE_URL)
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute("""
            SELECT 
                strategy_id,
                symbol,
                company_name,
                investment_style,
                recommendation,
                score,
                current_price,
                target_price,
                created_at
            FROM accepted_strategies
            WHERE username = %s
            ORDER BY created_at DESC
        """, (username,))
        
        strategies = cursor.fetchall()
        
        print(f"✅ 找到 {len(strategies)} 个策略\n")
        
        if strategies:
            for i, s in enumerate(strategies, 1):
                print(f"[{i}] {s['symbol']} - {s['company_name']}")
                print(f"    风格: {s['investment_style']}")
                print(f"    推荐: {s['recommendation']}")
                print(f"    评分: {s['score']}")
                print(f"    创建: {s['created_at']}")
                print()
        else:
            print("   该用户还没有保存过策略")
        
        cursor.close()
        conn.close()
        
        return strategies
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        conn.close()
        return []

# 使用示例
print("\n" + "=" * 80)
print("📊 数据库直查示例")
print("=" * 80)

# 查询几个用户
for username in ['bbb', 'danny', 'bruce']:
    query_user_strategies_from_db(username)

print("=" * 80)


