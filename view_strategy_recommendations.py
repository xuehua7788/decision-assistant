#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看策略推荐表和优化参数
"""

import os
import sys
import json
import psycopg2
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv('backend/.env')
load_dotenv()

def get_db_connection():
    """获取数据库连接"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL 未设置")
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def check_tables_exist(conn):
    """检查表是否存在"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('user_profiles', 'strategy_recommendations')
        ORDER BY table_name;
    """)
    
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    
    return tables


def view_user_profiles(conn, username=None):
    """查看用户画像"""
    cursor = conn.cursor()
    
    if username:
        cursor.execute("""
            SELECT username, risk_tolerance, investment_style, time_horizon,
                   option_experience, confidence_level, 
                   last_analyzed_at, total_messages_analyzed,
                   ai_analysis
            FROM user_profiles
            WHERE username = %s
        """, (username,))
    else:
        cursor.execute("""
            SELECT username, risk_tolerance, investment_style, time_horizon,
                   option_experience, confidence_level, 
                   last_analyzed_at, total_messages_analyzed
            FROM user_profiles
            ORDER BY last_analyzed_at DESC
        """)
    
    results = cursor.fetchall()
    cursor.close()
    
    if not results:
        print("   ⚠️  没有找到用户画像数据")
        return
    
    print("\n" + "=" * 100)
    print("📊 用户画像列表")
    print("=" * 100)
    
    for row in results:
        print(f"\n👤 用户: {row[0]}")
        print(f"   风险偏好: {row[1] or 'N/A'}")
        print(f"   投资风格: {row[2] or 'N/A'}")
        print(f"   时间范围: {row[3] or 'N/A'}")
        print(f"   期权经验: {row[4] or 'N/A'}")
        print(f"   信心水平: {row[5] or 'N/A'}")
        print(f"   最后分析: {row[6] or 'N/A'}")
        print(f"   分析消息数: {row[7] or 0}")
        
        # 如果查询单个用户，显示完整AI分析
        if username and len(row) > 8 and row[8]:
            print("\n   📋 完整AI分析:")
            ai_analysis = row[8] if isinstance(row[8], dict) else json.loads(row[8])
            print(json.dumps(ai_analysis, ensure_ascii=False, indent=6))


def view_strategy_recommendations(conn, username=None, limit=10):
    """查看策略推荐记录"""
    cursor = conn.cursor()
    
    if username:
        cursor.execute("""
            SELECT id, username, strategy_type, strategy_name,
                   strategy_parameters, confidence_score,
                   adjustment_reason, original_parameters, adjusted_parameters,
                   personalization_notes, created_at
            FROM strategy_recommendations
            WHERE username = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (username, limit))
    else:
        cursor.execute("""
            SELECT id, username, strategy_type, strategy_name,
                   strategy_parameters, confidence_score,
                   adjustment_reason, created_at
            FROM strategy_recommendations
            ORDER BY created_at DESC
            LIMIT %s
        """, (limit,))
    
    results = cursor.fetchall()
    cursor.close()
    
    if not results:
        print("   ⚠️  没有找到策略推荐记录")
        return
    
    print("\n" + "=" * 100)
    print("📈 策略推荐历史")
    print("=" * 100)
    
    for row in results:
        print(f"\n🎯 推荐 #{row[0]}")
        print(f"   用户: {row[1]}")
        print(f"   策略类型: {row[2] or 'N/A'}")
        if len(row) > 3:
            print(f"   策略名称: {row[3] or 'N/A'}")
        
        # 策略参数
        if len(row) > 4 and row[4]:
            params = row[4] if isinstance(row[4], dict) else json.loads(row[4])
            print(f"   策略参数: {json.dumps(params, ensure_ascii=False)}")
        
        # 信心分数
        if len(row) > 5:
            print(f"   信心分数: {row[5] or 'N/A'}")
        
        # 调整原因
        if len(row) > 6 and row[6]:
            print(f"   调整原因:")
            for line in row[6].strip().split('\n')[:5]:  # 只显示前5行
                print(f"      {line}")
        
        # 原始参数 vs 调整后参数
        if len(row) > 8 and row[7] and row[8]:
            original = row[7] if isinstance(row[7], dict) else json.loads(row[7])
            adjusted = row[8] if isinstance(row[8], dict) else json.loads(row[8])
            
            print(f"\n   📊 参数对比:")
            print(f"      原始参数: {json.dumps(original, ensure_ascii=False)}")
            print(f"      调整参数: {json.dumps(adjusted, ensure_ascii=False)}")
        
        # 个性化备注
        if len(row) > 9 and row[9]:
            print(f"   💡 个性化备注: {row[9]}")
        
        # 创建时间
        created_at = row[-1] if len(row) > 10 else row[7]
        print(f"   创建时间: {created_at}")


def view_optimization_details(conn, recommendation_id):
    """查看特定推荐的优化详情"""
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT username, user_intent, user_profile_snapshot,
               strategy_type, strategy_name, strategy_parameters,
               confidence_score, adjustment_reason,
               original_parameters, adjusted_parameters,
               personalization_notes, created_at
        FROM strategy_recommendations
        WHERE id = %s
    """, (recommendation_id,))
    
    result = cursor.fetchone()
    cursor.close()
    
    if not result:
        print(f"   ⚠️  未找到推荐 #{recommendation_id}")
        return
    
    print("\n" + "=" * 100)
    print(f"🔍 策略推荐详情 #{recommendation_id}")
    print("=" * 100)
    
    print(f"\n👤 用户: {result[0]}")
    
    # 用户意图
    if result[1]:
        user_intent = result[1] if isinstance(result[1], dict) else json.loads(result[1])
        print(f"\n📝 用户意图:")
        print(json.dumps(user_intent, ensure_ascii=False, indent=3))
    
    # 用户画像快照
    if result[2]:
        profile = result[2] if isinstance(result[2], dict) else json.loads(result[2])
        print(f"\n👤 用户画像快照:")
        print(f"   风险偏好: {profile.get('investment_preferences', {}).get('risk_tolerance', 'N/A')}")
        print(f"   投资风格: {profile.get('investment_preferences', {}).get('investment_style', 'N/A')}")
        print(f"   期权经验: {profile.get('knowledge_level', {}).get('option_experience', 'N/A')}")
        print(f"   信心水平: {profile.get('emotional_traits', {}).get('confidence_level', 'N/A')}")
    
    # 策略信息
    print(f"\n🎯 推荐策略:")
    print(f"   类型: {result[3]}")
    print(f"   名称: {result[4]}")
    
    # 参数对比
    if result[8] and result[9]:
        original = result[8] if isinstance(result[8], dict) else json.loads(result[8])
        adjusted = result[9] if isinstance(result[9], dict) else json.loads(result[9])
        
        print(f"\n📊 参数优化对比:")
        print(f"\n   原始参数:")
        for key, value in original.items():
            print(f"      {key}: {value}")
        
        print(f"\n   优化后参数:")
        for key, value in adjusted.items():
            adj_marker = " ✨" if original.get(key) != value else ""
            print(f"      {key}: {value}{adj_marker}")
    
    # 调整原因
    if result[7]:
        print(f"\n💡 调整原因:")
        for line in result[7].strip().split('\n'):
            print(f"   {line}")
    
    # 个性化备注
    if result[10]:
        print(f"\n📋 个性化备注:")
        print(f"   {result[10]}")
    
    print(f"\n⏰ 创建时间: {result[11]}")


def main():
    print("=" * 100)
    print("🔍 策略推荐和优化参数查看工具")
    print("=" * 100)
    
    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # 检查表是否存在
        print("\n1. 检查数据库表...")
        tables = check_tables_exist(conn)
        print(f"   ✅ 找到表: {', '.join(tables)}")
        
        if 'user_profiles' not in tables:
            print("   ⚠️  user_profiles 表不存在")
        
        if 'strategy_recommendations' not in tables:
            print("   ⚠️  strategy_recommendations 表不存在")
            print("\n   💡 运行以下命令创建表:")
            print("      cd backend && python create_user_profile_tables.py")
            return
        
        # 查看用户画像
        print("\n2. 查看用户画像...")
        view_user_profiles(conn)
        
        # 查看策略推荐
        print("\n3. 查看策略推荐历史...")
        view_strategy_recommendations(conn)
        
        # 如果有推荐记录，询问是否查看详情
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM strategy_recommendations")
        count = cursor.fetchone()[0]
        cursor.close()
        
        if count > 0:
            print(f"\n💡 提示: 共有 {count} 条推荐记录")
            print("   要查看特定推荐的详情，运行:")
            print("   python view_strategy_recommendations.py --detail <推荐ID>")
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == '--detail' and len(sys.argv) > 2:
            # 查看详情
            conn = get_db_connection()
            if conn:
                try:
                    recommendation_id = int(sys.argv[2])
                    view_optimization_details(conn, recommendation_id)
                finally:
                    conn.close()
        elif sys.argv[1] == '--user' and len(sys.argv) > 2:
            # 查看特定用户
            username = sys.argv[2]
            conn = get_db_connection()
            if conn:
                try:
                    print(f"\n查看用户 {username} 的数据...")
                    view_user_profiles(conn, username)
                    view_strategy_recommendations(conn, username)
                finally:
                    conn.close()
        else:
            print("用法:")
            print("  python view_strategy_recommendations.py                    # 查看所有")
            print("  python view_strategy_recommendations.py --user <用户名>     # 查看特定用户")
            print("  python view_strategy_recommendations.py --detail <推荐ID>  # 查看推荐详情")
    else:
        main()








