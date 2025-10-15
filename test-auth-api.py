"""
测试认证 API 是否正常工作
"""
import requests
import json

API_URL = "http://127.0.0.1:8000"

def test_api():
    print("="*50)
    print("  测试 Decision Assistant 认证 API")
    print("="*50)
    print()
    
    # 1. 测试服务器是否运行
    print("1️⃣  测试服务器连接...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=3)
        if response.status_code == 200:
            print("   ✅ 服务器运行正常")
        else:
            print(f"   ❌ 服务器响应异常: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("   ❌ 无法连接到服务器")
        print("   💡 请先运行: start-app.bat 或 cd backend && python app.py")
        return
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return
    
    print()
    
    # 2. 测试注册端点
    print("2️⃣  测试注册端点...")
    try:
        test_user = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = requests.post(
            f"{API_URL}/api/auth/register",
            json=test_user,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("   ✅ 注册端点正常")
            data = response.json()
            print(f"   📝 返回: username={data.get('username')}, token已生成")
        elif response.status_code == 400:
            print("   ✅ 注册端点正常（用户已存在）")
        else:
            print(f"   ⚠️  响应码: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 3. 测试登录端点
    print("3️⃣  测试登录端点...")
    try:
        login_data = {
            "username": "testuser",
            "password": "password123"
        }
        response = requests.post(
            f"{API_URL}/api/auth/login",
            json=login_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            print("   ✅ 登录端点正常")
            data = response.json()
            token = data.get('token')
            print(f"   📝 返回: username={data.get('username')}, token已生成")
            print(f"   🔑 Token: {token[:20]}...")
            
            # 4. 测试获取用户信息
            print()
            print("4️⃣  测试获取用户信息...")
            response = requests.get(
                f"{API_URL}/api/auth/me",
                headers={"Authorization": f"Bearer {token}"}
            )
            if response.status_code == 200:
                print("   ✅ 用户信息端点正常")
                data = response.json()
                print(f"   📝 用户: {data.get('username')} ({data.get('email')})")
            else:
                print(f"   ⚠️  响应码: {response.status_code}")
        else:
            print(f"   ⚠️  响应码: {response.status_code}")
            print(f"   响应: {response.text}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    print("="*50)
    print("  测试完成！")
    print("="*50)
    print()
    print("💡 如果所有测试都通过，认证系统已经可以使用了！")
    print("   现在可以：")
    print("   1. 启动前端: cd frontend && npm start")
    print("   2. 访问: http://localhost:3000")
    print()

if __name__ == "__main__":
    test_api()


