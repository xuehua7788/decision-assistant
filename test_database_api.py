"""
测试Render后端数据库API
"""
import requests
import json

def test_database_api():
    """测试数据库API接口"""
    base_url = "https://decision-assistant-backend.onrender.com"
    
    print("=== 测试Render后端数据库API ===")
    
    # 测试健康检查
    print("\n1. 测试健康检查...")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   状态码: {response.status_code}")
        print(f"   响应: {response.json()}")
    except Exception as e:
        print(f"   ❌ 健康检查失败: {e}")
        return False
    
    # 测试数据库状态
    print("\n2. 测试数据库状态...")
    try:
        response = requests.get(f"{base_url}/api/database/status", timeout=10)
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   数据库配置: {data.get('database_configured', False)}")
        print(f"   使用数据库: {data.get('use_database', False)}")
        print(f"   启用分析: {data.get('enable_analytics', False)}")
        
        if data.get('status') == 'success':
            print("   ✅ 数据库连接成功！")
        else:
            print(f"   ⚠️  数据库状态: {data.get('message', 'unknown')}")
            
    except Exception as e:
        print(f"   ❌ 数据库状态检查失败: {e}")
    
    # 测试数据库连接
    print("\n3. 测试数据库连接...")
    try:
        response = requests.get(f"{base_url}/api/database/test-connection", timeout=15)
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   连接状态: {data.get('status', 'unknown')}")
        print(f"   消息: {data.get('message', 'no message')}")
        
        if data.get('status') == 'success':
            print("   ✅ 数据库连接测试成功！")
        else:
            print(f"   ❌ 数据库连接测试失败: {data.get('message', 'unknown')}")
            
    except Exception as e:
        print(f"   ❌ 数据库连接测试失败: {e}")
    
    # 测试配置信息
    print("\n4. 测试配置信息...")
    try:
        response = requests.get(f"{base_url}/api/database/config", timeout=10)
        print(f"   状态码: {response.status_code}")
        data = response.json()
        print(f"   配置信息: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except Exception as e:
        print(f"   ❌ 配置信息获取失败: {e}")
    
    print("\n=== 测试完成 ===")
    return True

if __name__ == "__main__":
    test_database_api()
