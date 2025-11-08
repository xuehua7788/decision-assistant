#!/usr/bin/env python3
"""查看所有策略详情"""
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "=" * 80)
print("📊 查看所有策略详情")
print("=" * 80)

conn = psycopg2.connect(DATABASE_URL)

try:
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    cursor.execute("""
        SELECT 
            id,
            strategy_id,
            symbol,
            company_name,
            investment_style,
            recommendation,
            score,
            current_price,
            target_price,
            stop_loss,
            username,
            created_at::date as date
        FROM accepted_strategies
        ORDER BY created_at DESC
    """)
    
    strategies = cursor.fetchall()
    
    print(f"\n✅ 找到 {len(strategies)} 个策略\n")
    
    for i, s in enumerate(strategies, 1):
        print(f"[{i}] {'=' * 75}")
        print(f"策略ID: {s['strategy_id']}")
        print(f"股票: {s['symbol']} - {s['company_name'] or 'N/A'}")
        print(f"投资风格: {s['investment_style']}")
        print(f"推荐: {s['recommendation']}")
        print(f"评分: {s['score']}")
        print(f"当前价: ${s['current_price']}")
        if s['target_price']:
            print(f"目标价: ${s['target_price']}")
        if s['stop_loss']:
            print(f"止损价: ${s['stop_loss']}")
        print(f"用户: {s['username'] or '(无用户，旧数据)'}")
        print(f"创建时间: {s['date']}")
        print()
    
    cursor.close()
    
except Exception as e:
    print(f"❌ 查询失败: {e}")

conn.close()

print("=" * 80)


