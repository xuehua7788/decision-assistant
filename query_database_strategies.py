#!/usr/bin/env python3
"""直接从数据库查询策略"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ 未设置 DATABASE_URL 环境变量")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        print("✅ 数据库连接成功")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def query_all_strategies():
    """查询所有策略"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            strategy_id,
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
            created_at,
            status,
            option_strategy
        FROM accepted_strategies
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        strategies = cursor.fetchall()
        
        print(f"✅ 查询到 {len(strategies)} 个策略")
        
        cursor.close()
        conn.close()
        
        return [dict(s) for s in strategies]
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        if conn:
            conn.close()
        return []

def query_strategies_by_symbol(symbol):
    """按股票代码查询"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT * FROM accepted_strategies
        WHERE symbol = %s
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, (symbol,))
        strategies = cursor.fetchall()
        
        print(f"✅ {symbol} 有 {len(strategies)} 个策略")
        
        cursor.close()
        conn.close()
        
        return [dict(s) for s in strategies]
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        if conn:
            conn.close()
        return []

def query_strategies_by_style(investment_style):
    """按投资风格查询"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT * FROM accepted_strategies
        WHERE investment_style = %s
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, (investment_style,))
        strategies = cursor.fetchall()
        
        print(f"✅ {investment_style} 风格有 {len(strategies)} 个策略")
        
        cursor.close()
        conn.close()
        
        return [dict(s) for s in strategies]
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        if conn:
            conn.close()
        return []

def query_strategies_by_date_range(start_date, end_date):
    """按时间范围查询"""
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT * FROM accepted_strategies
        WHERE created_at BETWEEN %s AND %s
        ORDER BY created_at DESC
        """
        
        cursor.execute(query, (start_date, end_date))
        strategies = cursor.fetchall()
        
        print(f"✅ 时间范围内有 {len(strategies)} 个策略")
        
        cursor.close()
        conn.close()
        
        return [dict(s) for s in strategies]
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        if conn:
            conn.close()
        return []

def get_strategy_statistics():
    """获取策略统计信息"""
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 总体统计
        query = """
        SELECT 
            COUNT(*) as total_strategies,
            COUNT(DISTINCT symbol) as unique_stocks,
            AVG(score) as avg_score,
            investment_style,
            COUNT(*) as count_by_style
        FROM accepted_strategies
        GROUP BY investment_style
        """
        
        cursor.execute(query)
        stats = cursor.fetchall()
        
        print("\n📊 策略统计:")
        print("=" * 60)
        
        for stat in stats:
            print(f"\n🎯 {stat['investment_style']} 风格:")
            print(f"   策略数量: {stat['count_by_style']}")
            print(f"   平均评分: {stat['avg_score']:.1f}")
        
        # 总计
        cursor.execute("SELECT COUNT(*) as total FROM accepted_strategies")
        total = cursor.fetchone()
        print(f"\n📈 总计: {total['total']} 个策略")
        
        cursor.close()
        conn.close()
        
        return stats
        
    except Exception as e:
        print(f"❌ 统计失败: {e}")
        if conn:
            conn.close()
        return None

def main():
    """主函数"""
    print("=" * 60)
    print("📊 数据库策略查询工具")
    print("=" * 60)
    
    print("\n选择查询方式:")
    print("1. 查询所有策略")
    print("2. 按股票代码查询")
    print("3. 按投资风格查询")
    print("4. 按时间范围查询")
    print("5. 查看统计信息")
    
    choice = input("\n请选择 (1-5): ").strip()
    
    strategies = []
    
    if choice == '1':
        strategies = query_all_strategies()
    
    elif choice == '2':
        symbol = input("输入股票代码 (如 AAPL): ").strip().upper()
        strategies = query_strategies_by_symbol(symbol)
    
    elif choice == '3':
        print("\n投资风格:")
        print("  buffett - 巴菲特")
        print("  lynch - 彼得·林奇")
        print("  soros - 索罗斯")
        style = input("选择风格: ").strip().lower()
        strategies = query_strategies_by_style(style)
    
    elif choice == '4':
        start = input("开始日期 (YYYY-MM-DD): ").strip()
        end = input("结束日期 (YYYY-MM-DD): ").strip()
        strategies = query_strategies_by_date_range(start, end)
    
    elif choice == '5':
        get_strategy_statistics()
        return
    
    else:
        print("❌ 无效选择")
        return
    
    # 显示结果
    if strategies:
        print(f"\n📋 找到 {len(strategies)} 个策略\n")
        
        for i, s in enumerate(strategies, 1):
            print(f"[{i}] {s['symbol']} - {s['company_name']}")
            print(f"    风格: {s['investment_style']} | 评分: {s['score']}")
            print(f"    推荐: {s['recommendation']} | 时间: {s['created_at']}")
            
            if s.get('option_strategy'):
                opt = s['option_strategy']
                if isinstance(opt, str):
                    opt = json.loads(opt)
                print(f"    期权: {opt.get('name', 'N/A')}")
            
            print()
        
        # 导出选项
        export = input("是否导出为JSON? (y/n): ").strip().lower()
        if export == 'y':
            filename = f"strategies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            # 处理datetime对象
            for s in strategies:
                if 'created_at' in s and isinstance(s['created_at'], datetime):
                    s['created_at'] = s['created_at'].isoformat()
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(strategies, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"✅ 已导出到: {filename}")
    
    else:
        print("\n⚠️  没有找到匹配的策略")

if __name__ == "__main__":
    main()


