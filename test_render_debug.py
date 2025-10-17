import requests
import json

print("=" * 60)
print("测试 Render 后端 API")
print("=" * 60)

# 测试 1: 健康检查
print("\n1. 测试健康检查...")
try:
    response = requests.get("https://decision-assistant-backend.onrender.com/health", timeout=10)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    if response.status_code == 200:
        print("   ✅ 健康检查通过")
    else:
        print("   ❌ 健康检查失败")
except Exception as e:
    print(f"   ❌ 健康检查失败: {str(e)}")

# 测试 2: 聊天 API
print("\n2. 测试聊天 API...")
try:
    test_message = "给我买房子建议"
    response = requests.post(
        "https://decision-assistant-backend.onrender.com/api/decisions/chat",
        json={"message": test_message, "session_id": "test"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"   状态码: {response.status_code}")
    result = response.json()
    print(f"   响应: {result}")
    
    response_text = result.get("response", "")
    
    # 检查是否是智能回复
    random_responses = [
        "我理解你的问题。让我帮你分析一下...",
        "这是一个很好的问题。从多个角度来看...",
        "基于你提供的信息，我建议...",
        "让我从不同角度帮你分析这个决策..."
    ]
    
    is_random = any(random_resp in response_text for random_resp in random_responses)
    
    if is_random:
        print("   ❌ 返回的是随机回复")
        print("   问题：DeepSeek API 调用失败，回退到了备用回复")
        print("   可能原因：")
        print("   1. Render 环境变量 DEEPSEEK_API_KEY 未设置")
        print("   2. Render 环境变量值不正确")
        print("   3. DeepSeek API 调用失败（网络问题、API Key 无效等）")
    else:
        print("   ✅ 返回的是智能回复")
        print(f"   回复内容: {response_text[:100]}...")
        
except Exception as e:
    print(f"   ❌ 聊天 API 测试失败: {str(e)}")

print("\n" + "=" * 60)
print("测试完成！")
print("=" * 60)
print("\n如果返回的是随机回复，请检查：")
print("1. Render Dashboard -> Settings -> Environment Variables")
print("2. 确认 DEEPSEEK_API_KEY 环境变量存在且值正确")
print("3. 确认环境变量已应用到服务（可能需要重新部署）")
print("4. 查看 Render 日志中的 DEBUG 信息")


