"""
等待Render部署完成，然后执行数据库迁移
"""
import requests
import time

BACKEND_URL = 'https://decision-assistant-backend.onrender.com'

def check_deployment():
    """检查后端是否部署成功"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/stock/health', timeout=10)
        return response.status_code == 200
    except:
        return False

def run_migration():
    """执行数据库迁移"""
    print("\n🔄 执行数据库迁移...")
    import psycopg2
    
    DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'
    
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        
        # 读取SQL文件
        with open('backend/fund_management_migration.sql', 'r', encoding='utf-8') as f:
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
        print(f"\n💰 已初始化 {count} 个用户账户")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

if __name__ == '__main__':
    print("🚀 等待Render部署...")
    print(f"目标: {BACKEND_URL}")
    
    # 等待部署完成（最多5分钟）
    max_attempts = 30
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\n尝试 {attempt}/{max_attempts}...", end=' ')
        
        if check_deployment():
            print("✅ 后端已启动！")
            break
        else:
            print("⏳ 等待中...")
            time.sleep(10)
    
    if attempt >= max_attempts:
        print("\n❌ 部署超时，请手动检查Render状态")
        exit(1)
    
    # 执行数据库迁移
    if run_migration():
        print("\n✅ 所有步骤完成！")
        print("\n下一步：运行测试脚本")
        print("  cd backend")
        print("  python test_fund_system.py")
    else:
        print("\n❌ 迁移失败，请检查错误信息")

