"""
自动等待Render部署完成并测试
"""
import requests
import time
import sys

BACKEND_URL = 'https://decision-assistant-githubv3.onrender.com'

def check_deployment():
    """检查部署状态"""
    try:
        # 检查新API是否可用
        response = requests.get(f'{BACKEND_URL}/api/fund/account/bbb', timeout=10)
        return response.status_code != 404
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
        
        # 验证表
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name IN ('accounts', 'strategies', 'positions', 'transactions')
        """)
        tables = cur.fetchall()
        print(f"\n📊 已创建的表: {[t[0] for t in tables]}")
        
        cur.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ 迁移失败: {e}")
        return False

def test_apis():
    """测试API"""
    print("\n🧪 测试API端点...")
    
    tests = [
        ('账户查询', 'GET', '/api/fund/account/bbb'),
        ('持仓查询', 'GET', '/api/fund/positions/bbb'),
    ]
    
    results = []
    for name, method, endpoint in tests:
        try:
            url = f'{BACKEND_URL}{endpoint}'
            response = requests.get(url, timeout=10)
            success = response.status_code == 200
            results.append((name, success, response.status_code))
            print(f"  {'✅' if success else '❌'} {name}: {response.status_code}")
        except Exception as e:
            results.append((name, False, str(e)))
            print(f"  ❌ {name}: {e}")
    
    return all(r[1] for r in results)

if __name__ == '__main__':
    print("🚀 等待Render部署并自动测试...")
    print(f"目标: {BACKEND_URL}\n")
    
    # 等待部署（最多10分钟）
    max_attempts = 60
    attempt = 0
    
    while attempt < max_attempts:
        attempt += 1
        print(f"\r尝试 {attempt}/{max_attempts}...", end='', flush=True)
        
        if check_deployment():
            print("\n✅ 后端已部署！")
            break
        
        time.sleep(10)
    
    if attempt >= max_attempts:
        print("\n❌ 部署超时")
        sys.exit(1)
    
    # 执行迁移
    if not run_migration():
        print("\n⚠️ 迁移失败，但继续测试...")
    
    # 测试API
    if test_apis():
        print("\n✅ 所有测试通过！")
        print("\n📱 现在可以刷新前端页面测试完整功能")
    else:
        print("\n⚠️ 部分测试失败")

