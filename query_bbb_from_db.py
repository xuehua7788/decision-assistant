#!/usr/bin/env python3
"""直接从数据库查询bbb的策略"""
import psycopg2
from psycopg2.extras import RealDictCursor
import json

DATABASE_URL = "postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l"

print("\n" + "="*80)
print("🔍 查询 bbb 用户的策略（从数据库）")
print("="*80)

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor(cursor_factory=RealDictCursor)

# 查询bbb用户的完整信息
cur.execute("""
    SELECT 
        id,
        username,
        email,
        created_at,
        accepted_strategies
    FROM users
    WHERE username = 'bbb'
""")

user = cur.fetchone()

if not user:
    print("❌ 找不到 bbb 用户")
    cur.close()
    conn.close()
    exit(1)

print(f"\n✅ 用户信息:")
print(f"   ID: {user['id']}")
print(f"   用户名: {user['username']}")
print(f"   邮箱: {user['email']}")
print(f"   注册时间: {user['created_at']}")

strategies = user['accepted_strategies']

if not strategies:
    print(f"\n   策略数: 0")
    print("   ⚠️  用户暂无策略")
else:
    print(f"\n   策略数: {len(strategies)}")
    
    print(f"\n{'='*80}")
    print("📊 策略详情")
    print("="*80)
    
    for i, s in enumerate(strategies, 1):
        print(f"\n【策略 {i}】")
        print(f"   策略ID: {s.get('strategy_id', 'N/A')}")
        print(f"   股票代码: {s.get('symbol', 'N/A')}")
        print(f"   公司名称: {s.get('company_name', 'N/A')}")
        print(f"   投资风格: {s.get('investment_style', 'N/A')}")
        print(f"   推荐操作: {s.get('recommendation', 'N/A')}")
        print(f"   目标价: ${s.get('target_price', 0):.2f}")
        print(f"   止损价: ${s.get('stop_loss', 0):.2f}" if s.get('stop_loss') else "   止损价: N/A")
        print(f"   当前价: ${s.get('current_price', 0):.2f}")
        print(f"   评分: {s.get('score', 'N/A')}")
        print(f"   仓位: {s.get('position_size', 'N/A')}")
        print(f"   状态: {s.get('status', 'N/A')}")
        print(f"   创建时间: {s.get('created_at', 'N/A')}")
        
        # 期权策略
        option = s.get('option_strategy')
        if option:
            print(f"\n   ✅ 期权策略:")
            print(f"      名称: {option.get('name', 'N/A')}")
            print(f"      类型: {option.get('type', 'N/A')}")
            
            if 'strategy' in option:
                inner = option['strategy']
                print(f"      策略名: {inner.get('name', 'N/A')}")
                print(f"      描述: {inner.get('description', 'N/A')}")
            
            if 'parameters' in option:
                params = option['parameters']
                print(f"      参数:")
                for k, v in params.items():
                    print(f"         {k}: {v}")
        else:
            print(f"\n   ❌ 无期权策略")
        
        print(f"\n   策略文本预览:")
        strategy_text = s.get('strategy_text', '')
        if strategy_text:
            preview = strategy_text[:150] + "..." if len(strategy_text) > 150 else strategy_text
            print(f"      {preview}")
        else:
            print(f"      (无)")
        
        print("-"*80)

# 统计信息
print(f"\n{'='*80}")
print("📈 统计信息")
print("="*80)

if strategies:
    # 按投资风格分组
    style_counts = {}
    for s in strategies:
        style = s.get('investment_style', 'unknown')
        style_counts[style] = style_counts.get(style, 0) + 1
    
    print(f"\n投资风格分布:")
    for style, count in style_counts.items():
        print(f"   {style}: {count} 个")
    
    # 按股票代码分组
    symbol_counts = {}
    for s in strategies:
        symbol = s.get('symbol', 'unknown')
        symbol_counts[symbol] = symbol_counts.get(symbol, 0) + 1
    
    print(f"\n股票分布:")
    for symbol, count in sorted(symbol_counts.items()):
        print(f"   {symbol}: {count} 个")
    
    # 期权策略统计
    with_option = sum(1 for s in strategies if s.get('option_strategy'))
    without_option = len(strategies) - with_option
    
    print(f"\n期权策略:")
    print(f"   有期权: {with_option} 个")
    print(f"   无期权: {without_option} 个")
    
    # 推荐操作统计
    rec_counts = {}
    for s in strategies:
        rec = s.get('recommendation', 'unknown')
        rec_counts[rec] = rec_counts.get(rec, 0) + 1
    
    print(f"\n推荐操作:")
    for rec, count in rec_counts.items():
        print(f"   {rec}: {count} 个")

cur.close()
conn.close()

print(f"\n{'='*80}")
print("✅ 查询完成")
print("="*80)
print()


