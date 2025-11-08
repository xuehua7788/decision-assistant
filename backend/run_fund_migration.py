"""
执行资金管理系统数据库迁移
"""
import psycopg2
import os

def migrate():
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l')
    
    print("🔄 开始资金管理系统数据库迁移...")
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 读取SQL文件
        with open('fund_management_migration.sql', 'r', encoding='utf-8') as f:
            sql = f.read()
        
        # 执行迁移
        cur.execute(sql)
        conn.commit()
        
        print("✅ 数据库迁移成功！")
        
        # 验证表是否创建
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('accounts', 'strategies', 'positions', 'transactions')
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        print(f"\n📊 已创建的表：")
        for table in tables:
            print(f"  ✓ {table[0]}")
        
        # 检查accounts表数据
        cur.execute("SELECT COUNT(*) FROM accounts")
        count = cur.fetchone()[0]
        print(f"\n💰 已初始化 {count} 个用户账户（每人10万初始资金）")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    migrate()

