#!/usr/bin/env python3
"""查看注册用户列表"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
import json
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("=" * 60)
        print("📊 需要数据库连接URL")
        print("=" * 60)
        print("\n请输入数据库URL:")
        database_url = input("DATABASE_URL: ").strip()
        
        if not database_url:
            print("\n⚠️  未提供数据库URL")
            return None
    
    try:
        print(f"\n🔌 连接数据库...")
        conn = psycopg2.connect(database_url)
        print("✅ 连接成功！\n")
        return conn
    except Exception as e:
        print(f"❌ 连接失败: {e}\n")
        return None

def list_all_users(conn):
    """列出所有注册用户"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT 
            user_id,
            username,
            email,
            created_at,
            last_login
        FROM users
        ORDER BY created_at DESC
        """
        
        cursor.execute(query)
        users = cursor.fetchall()
        
        cursor.close()
        
        return [dict(u) for u in users]
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
        return []

def get_user_statistics(conn):
    """获取用户统计信息"""
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 总用户数
        cursor.execute("SELECT COUNT(*) as total FROM users")
        total = cursor.fetchone()
        
        # 今天注册的用户
        cursor.execute("""
            SELECT COUNT(*) as today_signups 
            FROM users 
            WHERE DATE(created_at) = CURRENT_DATE
        """)
        today = cursor.fetchone()
        
        # 最近7天注册的用户
        cursor.execute("""
            SELECT COUNT(*) as week_signups 
            FROM users 
            WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'
        """)
        week = cursor.fetchone()
        
        # 最近登录的用户
        cursor.execute("""
            SELECT COUNT(*) as recent_active 
            FROM users 
            WHERE last_login >= CURRENT_DATE - INTERVAL '7 days'
        """)
        active = cursor.fetchone()
        
        cursor.close()
        
        return {
            'total': total['total'],
            'today_signups': today['today_signups'],
            'week_signups': week['week_signups'],
            'recent_active': active['recent_active']
        }
        
    except Exception as e:
        print(f"❌ 统计失败: {e}")
        return None

def display_users(users):
    """显示用户列表"""
    if not users:
        print("⚠️  没有找到任何用户\n")
        return
    
    print("=" * 80)
    print(f"👥 注册用户列表 (共 {len(users)} 人)")
    print("=" * 80)
    print()
    
    for i, u in enumerate(users, 1):
        print(f"[{i}] {'=' * 75}")
        print(f"🆔 用户ID: {u['user_id']}")
        print(f"👤 用户名: {u['username']}")
        print(f"📧 邮箱: {u['email']}")
        print(f"📅 注册时间: {u['created_at']}")
        
        if u.get('last_login'):
            print(f"🕐 最后登录: {u['last_login']}")
        else:
            print(f"🕐 最后登录: 从未登录")
        
        print()

def main():
    """主函数"""
    print()
    print("=" * 80)
    print("👥 用户列表查询工具")
    print("=" * 80)
    
    # 连接数据库
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # 获取统计信息
        stats = get_user_statistics(conn)
        
        if stats:
            print("\n📊 用户统计:")
            print("-" * 80)
            print(f"总用户数: {stats['total']}")
            print(f"今日新增: {stats['today_signups']}")
            print(f"本周新增: {stats['week_signups']}")
            print(f"活跃用户 (7天内): {stats['recent_active']}")
            print()
        
        # 查询所有用户
        print("🔍 正在查询用户列表...")
        users = list_all_users(conn)
        
        # 显示用户列表
        display_users(users)
        
        # 导出选项
        if users:
            print("=" * 80)
            export_choice = input("\n是否导出为JSON文件？(y/n): ").strip().lower()
            if export_choice == 'y':
                filename = f"users_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                
                # 处理datetime对象
                for u in users:
                    if 'created_at' in u and isinstance(u['created_at'], datetime):
                        u['created_at'] = u['created_at'].isoformat()
                    if 'last_login' in u and isinstance(u['last_login'], datetime):
                        u['last_login'] = u['last_login'].isoformat()
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(users, f, ensure_ascii=False, indent=2, default=str)
                
                print(f"✅ 已导出到: {filename}")
        
    finally:
        conn.close()
        print("\n✅ 数据库连接已关闭")
        print()

if __name__ == "__main__":
    main()


