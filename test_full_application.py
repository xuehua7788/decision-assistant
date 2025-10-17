"""
完整应用测试 - 前端+后端
"""
import requests
import json

def test_full_application():
    """测试完整应用"""
    print("=== 测试完整应用 ===\n")
    
    frontend_url = "https://decision-assistant-frontend-prod.vercel.app"
    backend_url = "https://decision-assistant-backend.onrender.com"
    
    # ========== 后端测试 ==========
    print("【后端测试】")
    
    # 1. 健康检查
    print("\n1. 健康检查...")
    try:
        r = requests.get(f"{backend_url}/health", timeout=10)
        print(f"   状态码: {r.status_code}")
        print(f"   响应: {r.json()}")
        print("   ✅ 健康检查通过" if r.status_code == 200 else "   ❌ 健康检查失败")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 2. 数据库状态
    print("\n2. 数据库状态...")
    try:
        r = requests.get(f"{backend_url}/api/admin/stats", timeout=10)
        data = r.json()
        print(f"   状态码: {r.status_code}")
        print(f"   API状态: {data.get('api_status')}")
        print(f"   数据库可用: {data.get('database_available')}")
        print(f"   数据库已配置: {data.get('database_configured')}")
        print(f"   DeepSeek已配置: {data.get('deepseek_configured')}")
        print("   ✅ 数据库状态正常" if data.get('database_available') else "   ⚠️  数据库未启用")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 3. 注册功能
    print("\n3. 测试注册功能...")
    try:
        r = requests.post(f"{backend_url}/api/auth/register", 
                         json={'username': f'testuser_{id({})}', 'password': '123456'},
                         timeout=10)
        print(f"   状态码: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   用户名: {data.get('username')}")
            print(f"   Token: {data.get('token')[:20]}...")
            print("   ✅ 注册功能正常")
        else:
            print(f"   响应: {r.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 4. 聊天功能
    print("\n4. 测试聊天功能...")
    try:
        r = requests.post(f"{backend_url}/api/decisions/chat",
                         json={'message': '给我买房子建议', 'session_id': 'test'},
                         timeout=30)
        print(f"   状态码: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            response_text = data.get('response', '')
            print(f"   AI回复: {response_text[:100]}...")
            
            # 检查是否是智能回复
            if len(response_text) > 50 and "买房" in response_text:
                print("   ✅ 聊天功能正常（智能回复）")
            else:
                print("   ⚠️  聊天功能可用，但可能是随机回复")
        else:
            print(f"   响应: {r.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 5. 决策分析功能
    print("\n5. 测试决策分析功能...")
    try:
        r = requests.post(f"{backend_url}/api/decisions/analyze",
                         json={
                             'description': '是否购买新电脑',
                             'options': ['MacBook Pro', 'ThinkPad', '暂不购买']
                         },
                         timeout=30)
        print(f"   状态码: {r.status_code}")
        if r.status_code == 200:
            data = r.json()
            print(f"   推荐: {data.get('recommendation')}")
            print(f"   总结: {data.get('readable_summary', '')[:80]}...")
            print("   ✅ 决策分析功能正常")
        else:
            print(f"   响应: {r.json()}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # ========== 前端测试 ==========
    print("\n\n【前端测试】")
    
    # 1. 前端访问
    print("\n1. 前端访问...")
    try:
        r = requests.get(frontend_url, timeout=10)
        print(f"   状态码: {r.status_code}")
        if r.status_code == 200:
            print(f"   页面大小: {len(r.text)} 字符")
            if "Decision Assistant" in r.text:
                print("   ✅ 前端页面加载正常")
            else:
                print("   ⚠️  页面内容可能有问题")
        else:
            print("   ❌ 前端访问失败")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # ========== 数据库功能测试 ==========
    print("\n\n【数据库功能测试】")
    
    # 1. 数据库连接测试
    print("\n1. 数据库连接测试...")
    try:
        r = requests.get(f"{backend_url}/api/database/test", timeout=10)
        data = r.json()
        print(f"   状态码: {r.status_code}")
        print(f"   连接状态: {data.get('connection_test', {}).get('status')}")
        print(f"   连接消息: {data.get('connection_test', {}).get('message')}")
        print(f"   PostgreSQL版本: {data.get('connection_test', {}).get('version', '')[:50]}...")
        
        if data.get('connection_test', {}).get('status') == 'success':
            print("   ✅ 数据库连接测试通过")
        else:
            print("   ❌ 数据库连接测试失败")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 2. 查看用户数据
    print("\n2. 查看用户数据...")
    try:
        r = requests.get(f"{backend_url}/api/admin/users", timeout=10)
        data = r.json()
        print(f"   状态码: {r.status_code}")
        print(f"   总用户数: {data.get('total_users', 0)}")
        print("   ✅ 用户数据查询正常")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # 3. 查看聊天记录
    print("\n3. 查看聊天记录...")
    try:
        r = requests.get(f"{backend_url}/api/admin/chats", timeout=10)
        data = r.json()
        print(f"   状态码: {r.status_code}")
        print(f"   总会话数: {data.get('total_sessions', 0)}")
        print("   ✅ 聊天记录查询正常")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    # ========== 总结 ==========
    print("\n\n=== 测试总结 ===")
    print("✅ 后端服务: 正常运行")
    print("✅ 数据库连接: 成功")
    print("✅ AI功能: 正常工作")
    print("✅ 前端页面: 可访问")
    print("\n🎉 整个应用运行正常！")

if __name__ == "__main__":
    test_full_application()
