"""
本地Flask测试服务器
模拟Render环境，测试所有功能
"""
import os
import sys
import threading
import time
import requests

def start_local_server():
    """启动本地测试服务器"""
    # 设置环境变量
    os.environ['DATABASE_URL'] = 'postgresql://decision_user:8P8ZDdFaLp306B0si0ZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.oregon-postgres.render.com:5432/decision_assistant'
    os.environ['USE_DATABASE'] = 'true'
    os.environ['ENABLE_ANALYTICS'] = 'false'
    os.environ['DEEPSEEK_API_KEY'] = os.getenv('DEEPSEEK_API_KEY', 'test-key')
    os.environ['PORT'] = '5000'
    os.environ['FLASK_ENV'] = 'production'
    
    # 启动Flask应用
    sys.path.append('backend')
    from app import app
    
    print("🚀 启动本地测试服务器...")
    app.run(host='0.0.0.0', port=5000, debug=False)

def test_endpoints():
    """测试所有端点"""
    time.sleep(3)  # 等待服务器启动
    
    base_url = "http://localhost:5000"
    
    print("\n=== 测试端点 ===")
    
    # 测试健康检查
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"✅ 健康检查: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
    
    # 测试管理统计
    try:
        response = requests.get(f"{base_url}/api/admin/stats", timeout=5)
        print(f"✅ 管理统计: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   数据库状态: {data.get('database_available', False)}")
    except Exception as e:
        print(f"❌ 管理统计失败: {e}")
    
    # 测试数据库测试
    try:
        response = requests.get(f"{base_url}/api/database/test", timeout=5)
        print(f"✅ 数据库测试: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   连接状态: {data.get('connection_test', {}).get('status', 'unknown')}")
    except Exception as e:
        print(f"❌ 数据库测试失败: {e}")
    
    # 测试聊天功能
    try:
        response = requests.post(f"{base_url}/api/decisions/chat", 
                               json={'message': '测试', 'session_id': 'test'}, 
                               timeout=5)
        print(f"✅ 聊天功能: {response.status_code}")
    except Exception as e:
        print(f"❌ 聊天功能失败: {e}")
    
    print("\n🎉 本地测试完成！")

if __name__ == "__main__":
    # 在后台启动服务器
    server_thread = threading.Thread(target=start_local_server)
    server_thread.daemon = True
    server_thread.start()
    
    # 测试端点
    test_endpoints()
