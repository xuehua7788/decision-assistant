#!/usr/bin/env python3
"""
简化版策略查询工具
直接从数据库查询用户的历史策略
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    # 优先从环境变量获取
    database_url = os.getenv('DATABASE_URL')
    
    # 如果环境变量没有，提示用户输入
    if not database_url:
        print("=" * 60)
        print("📊 需要数据库连接URL")
        print("=" * 60)
        print("\n请输入数据库URL (格式: postgresql://user:pass@host/db)")
        print("或者按Enter跳过，使用默认Render配置\n")
        
        database_url = input("DATABASE_URL: ").strip()
        
        if not database_url:
            print("\n⚠️  未提供数据库URL，无法继续")
            return None
    
    try:
        print(f"\n🔌 正在连接数据库...")
        conn = psycopg2.connect(database_url)
        print("✅ 数据库连接成功！\n")
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}\n")
        return None

def query_all_strategies(conn):
    """查询所有策略"""
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
            current_price,
            created_at,
            status,
            option_strategy
        FROM accepted_strategies
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        strategies = cursor.fetchall()
        
        cursor.close()
        
        return [dict(s) for s in strategies]
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        return []

def display_strategies(strategies):
    """显示策略列表"""
    if not strategies:
        print("⚠️  没有找到任何策略\n")
        return
    
    print("=" * 80)
    print(f"📋 找到 {len(strategies)} 个策略")
    print("=" * 80)
    print()
    
    for i, s in enumerate(strategies, 1):
        print(f"[{i}] {'=' * 75}")
        print(f"📌 策略ID: {s['strategy_id']}")
        print(f"📈 股票: {s['symbol']} - {s['company_name']}")
        print(f"🎯 投资风格: {s['investment_style']}")
        print(f"💡 推荐操作: {s['recommendation']}")
        print(f"⭐ AI评分: {s['score']}/100")
        print(f"💰 接受时价格: ${s['current_price']:.2f}")
        
        if s.get('target_price'):
            print(f"🎯 目标价: ${s['target_price']:.2f}")
        if s.get('stop_loss'):
            print(f"🛑 止损价: ${s['stop_loss']:.2f}")
        if s.get('position_size'):
            print(f"📊 建议仓位: {s['position_size']}%")
        
        print(f"📅 接受时间: {s['created_at']}")
        print(f"📊 状态: {s['status']}")
        
        # 期权策略详情
        if s.get('option_strategy'):
            try:
                opt = s['option_strategy']
                if isinstance(opt, str):
                    opt = json.loads(opt)
                
                print(f"\n🎲 期权策略:")
                print(f"   ├─ 名称: {opt.get('name', 'N/A')}")
                print(f"   ├─ 类型: {opt.get('type', 'N/A')}")
                print(f"   └─ 描述: {opt.get('description', 'N/A')[:60]}...")
                
                if opt.get('parameters'):
                    params = opt['parameters']
                    print(f"   参数:")
                    if params.get('current_price'):
                        print(f"      ├─ 标的价格: ${params['current_price']:.2f}")
                    if params.get('buy_strike'):
                        print(f"      ├─ 买入行权价: ${params['buy_strike']:.2f}")
                    if params.get('sell_strike'):
                        print(f"      ├─ 卖出行权价: ${params['sell_strike']:.2f}")
                    if params.get('expiry_days'):
                        print(f"      └─ 到期天数: {params['expiry_days']}天")
                
                if opt.get('metrics'):
                    metrics = opt['metrics']
                    print(f"   收益风险:")
                    if metrics.get('max_loss'):
                        print(f"      ├─ 最大损失: ${metrics['max_loss']:.2f}")
                    if metrics.get('max_gain'):
                        print(f"      ├─ 最大收益: ${metrics['max_gain']:.2f}")
                    if metrics.get('breakeven'):
                        print(f"      └─ 盈亏平衡: ${metrics['breakeven']:.2f}")
                        
            except Exception as e:
                print(f"   ⚠️  期权策略解析失败: {e}")
        
        print()

def get_statistics(conn):
    """获取策略统计"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 按投资风格统计
        query = """
        SELECT 
            investment_style,
            COUNT(*) as count,
            AVG(score) as avg_score,
            COUNT(DISTINCT symbol) as unique_stocks
        FROM accepted_strategies
        GROUP BY investment_style
        """
        
        cursor.execute(query)
        style_stats = cursor.fetchall()
        
        # 总体统计
        cursor.execute("SELECT COUNT(*) as total FROM accepted_strategies")
        total = cursor.fetchone()
        
        cursor.execute("SELECT COUNT(DISTINCT symbol) as unique_stocks FROM accepted_strategies")
        unique_stocks = cursor.fetchone()
        
        cursor.close()
        
        print("\n" + "=" * 80)
        print("📊 策略统计分析")
        print("=" * 80)
        print()
        
        print(f"📈 总策略数: {total['total']}")
        print(f"📌 涉及股票: {unique_stocks['unique_stocks']} 只")
        print()
        
        print("🎯 按投资风格分布:")
        for stat in style_stats:
            style_name = {
                'buffett': '🏛️  巴菲特（价值投资）',
                'lynch': '🎯 彼得·林奇（成长股）',
                'soros': '🌊 索罗斯（趋势投机）'
            }.get(stat['investment_style'], stat['investment_style'])
            
            print(f"\n  {style_name}")
            print(f"    ├─ 策略数: {stat['count']}")
            print(f"    ├─ 平均评分: {stat['avg_score']:.1f}/100")
            print(f"    └─ 涉及股票: {stat['unique_stocks']} 只")
        
        print()
        
    except Exception as e:
        print(f"❌ 统计失败: {e}")

def export_to_json(strategies):
    """导出为JSON文件"""
    if not strategies:
        print("⚠️  没有数据可导出")
        return
    
    filename = f"strategies_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    # 处理datetime对象
    for s in strategies:
        if 'created_at' in s and isinstance(s['created_at'], datetime):
            s['created_at'] = s['created_at'].isoformat()
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, ensure_ascii=False, indent=2, default=str)
        
        print(f"✅ 数据已导出到: {filename}")
        print(f"📁 文件大小: {os.path.getsize(filename) / 1024:.2f} KB")
    except Exception as e:
        print(f"❌ 导出失败: {e}")

def main():
    """主函数"""
    print()
    print("=" * 80)
    print("🗄️  策略数据库查询工具")
    print("=" * 80)
    
    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # 查询所有策略
        print("🔍 正在查询策略...")
        strategies = query_all_strategies(conn)
        
        # 显示策略列表
        display_strategies(strategies)
        
        # 显示统计信息
        get_statistics(conn)
        
        # 导出选项
        if strategies:
            print("=" * 80)
            export_choice = input("\n是否导出为JSON文件？(y/n): ").strip().lower()
            if export_choice == 'y':
                export_to_json(strategies)
        
    finally:
        conn.close()
        print("\n✅ 数据库连接已关闭")
        print()

if __name__ == "__main__":
    main()


