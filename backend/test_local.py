"""
本地测试脚本
用于测试后端 API 是否正常工作
"""
import requests
import json
import time

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_USER = {
    "username": "test_user",
    "password": "test_password"
}

def test_health_check():
    """测试健康检查端点"""
    print("🔍 测试健康检查端点...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 健康检查成功: {data}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 健康检查异常: {e}")
        return False

def test_home_endpoint():
    """测试首页端点"""
    print("🔍 测试首页端点...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 首页访问成功: {data['message']}")
            return True
        else:
            print(f"❌ 首页访问失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 首页访问异常: {e}")
        return False

def test_register():
    """测试用户注册"""
    print("🔍 测试用户注册...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 注册成功: {data['message']}")
            return data.get('access_token')
        else:
            data = response.json()
            if "已存在" in data.get('error', ''):
                print("ℹ️ 用户已存在，尝试登录...")
                return test_login()
            else:
                print(f"❌ 注册失败: {data}")
                return None
    except Exception as e:
        print(f"❌ 注册异常: {e}")
        return None

def test_login():
    """测试用户登录"""
    print("🔍 测试用户登录...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json=TEST_USER,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 登录成功: {data['message']}")
            return data.get('access_token')
        else:
            data = response.json()
            print(f"❌ 登录失败: {data}")
            return None
    except Exception as e:
        print(f"❌ 登录异常: {e}")
        return None

def test_user_info(token):
    """测试获取用户信息"""
    print("🔍 测试获取用户信息...")
    try:
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 获取用户信息成功: {data}")
            return True
        else:
            data = response.json()
            print(f"❌ 获取用户信息失败: {data}")
            return False
    except Exception as e:
        print(f"❌ 获取用户信息异常: {e}")
        return False

def test_decision_analysis():
    """测试决策分析"""
    print("🔍 测试决策分析...")
    try:
        test_data = {
            "description": "我应该选择哪个工作机会？",
            "options": ["大公司稳定工作", "创业公司高薪工作", "继续深造学习"]
        }
        response = requests.post(
            f"{BASE_URL}/api/decision",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 决策分析成功")
            print(f"📝 分析结果: {data['analysis'][:200]}...")
            return True
        else:
            data = response.json()
            print(f"❌ 决策分析失败: {data}")
            return False
    except Exception as e:
        print(f"❌ 决策分析异常: {e}")
        return False

def test_chat():
    """测试聊天功能"""
    print("🔍 测试聊天功能...")
    try:
        test_data = {
            "message": "你好，请介绍一下自己",
            "session_id": "test_session"
        }
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json=test_data,
            headers={"Content-Type": "application/json"}
        )
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 聊天成功")
            print(f"💬 回复: {data['response'][:200]}...")
            return True
        else:
            data = response.json()
            print(f"❌ 聊天失败: {data}")
            return False
    except Exception as e:
        print(f"❌ 聊天异常: {e}")
        return False

def main():
    """主测试函数"""
    print("🚀 开始测试决策助手后端 API")
    print("="*50)
    
    # 等待服务器启动
    print("⏳ 等待服务器启动...")
    time.sleep(2)
    
    # 测试结果统计
    results = []
    
    # 基础端点测试
    results.append(("健康检查", test_health_check()))
    results.append(("首页端点", test_home_endpoint()))
    
    # 认证测试
    token = test_register()
    if token:
        results.append(("用户注册/登录", True))
        results.append(("获取用户信息", test_user_info(token)))
    else:
        results.append(("用户注册/登录", False))
        results.append(("获取用户信息", False))
    
    # 功能测试
    results.append(("决策分析", test_decision_analysis()))
    results.append(("聊天功能", test_chat()))
    
    # 输出测试结果
    print("\n" + "="*50)
    print("📊 测试结果汇总:")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name:15} : {status}")
        if result:
            passed += 1
    
    print("="*50)
    print(f"📈 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("🎉 所有测试通过！后端 API 工作正常。")
    else:
        print("⚠️ 部分测试失败，请检查配置和依赖。")
    
    print("="*50)

if __name__ == "__main__":
    main()
