"""
本地模拟Render环境测试
设置环境变量，测试数据库功能
"""
import os
import sys
import subprocess

def test_local_render():
    """本地测试Render环境"""
    print("=== 本地模拟Render环境测试 ===")
    
    # 设置环境变量（模拟Render环境）
    env_vars = {
        'DATABASE_URL': 'postgresql://decision_user:8P8ZDdFaLp306B0si0ZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.oregon-postgres.render.com:5432/decision_assistant',
        'DB_HOST': 'dpg-d3ot1n3ipnbc739gkn7g-a',
        'DB_PORT': '5432',
        'DB_NAME': 'decision_assistant',
        'DB_USER': 'decision_user',
        'DB_PASSWORD': '8P8ZDdFaLp306B0si0ZTXGScXmrdS9EB',
        'USE_DATABASE': 'true',
        'ENABLE_ANALYTICS': 'false',
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY', 'test-key'),
        'PORT': '8000',
        'FLASK_ENV': 'production'
    }
    
    # 更新环境变量
    for key, value in env_vars.items():
        os.environ[key] = value
    
    print("✅ 环境变量已设置")
    
    # 测试数据库模块导入
    print("\n1. 测试数据库模块导入...")
    try:
        sys.path.append('backend')
        from simple_database import simple_db
        print("✅ 简化数据库模块导入成功")
        
        # 测试数据库配置
        print(f"   数据库可用: {simple_db.is_available()}")
        print(f"   使用数据库: {simple_db.use_database}")
        print(f"   启用分析: {simple_db.enable_analytics}")
        
    except Exception as e:
        print(f"❌ 数据库模块导入失败: {e}")
        return False
    
    # 测试数据库连接
    print("\n2. 测试数据库连接...")
    try:
        connection_test = simple_db.test_connection()
        print(f"   连接状态: {connection_test['status']}")
        print(f"   消息: {connection_test['message']}")
        
        if connection_test['status'] == 'success':
            print("✅ 数据库连接成功！")
        else:
            print("⚠️  数据库连接有问题")
            
    except Exception as e:
        print(f"❌ 数据库连接测试失败: {e}")
    
    # 测试app.py导入
    print("\n3. 测试app.py导入...")
    try:
        from app import DATABASE_AVAILABLE, simple_db as app_db
        print(f"   DATABASE_AVAILABLE: {DATABASE_AVAILABLE}")
        print(f"   app_db: {app_db is not None}")
        print("✅ app.py导入成功")
        
    except Exception as e:
        print(f"❌ app.py导入失败: {e}")
        return False
    
    # 测试Flask应用启动
    print("\n4. 测试Flask应用启动...")
    try:
        from app import app
        print("✅ Flask应用创建成功")
        
        # 测试路由
        with app.test_client() as client:
            # 测试健康检查
            response = client.get('/health')
            print(f"   健康检查: {response.status_code}")
            
            # 测试管理统计
            response = client.get('/api/admin/stats')
            print(f"   管理统计: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   数据库状态: {data.get('database_available', False)}")
            
            # 测试数据库测试接口
            response = client.get('/api/database/test')
            print(f"   数据库测试: {response.status_code}")
            if response.status_code == 200:
                data = response.get_json()
                print(f"   连接测试: {data.get('connection_test', {}).get('status', 'unknown')}")
        
        print("✅ Flask应用测试成功")
        
    except Exception as e:
        print(f"❌ Flask应用测试失败: {e}")
        return False
    
    print("\n🎉 本地测试完成！")
    return True

if __name__ == "__main__":
    test_local_render()
