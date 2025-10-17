import requests

# 测试 Render 后端是否能正确读取环境变量
print("测试 Render 后端环境变量...")

try:
    # 发送一个测试请求
    response = requests.post(
        "https://decision-assistant-backend.onrender.com/api/decisions/chat",
        json={"message": "测试"},
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
    
    # 检查响应是否是智能回复
    response_text = response.json().get("response", "")
    
    if "这是一个很好的问题" in response_text or "让我从不同角度" in response_text:
        print("\n❌ 返回的是随机回复，说明 DeepSeek API 调用失败")
        print("可能原因：")
        print("1. Render 环境变量 DEEPSEEK_API_KEY 未正确设置")
        print("2. Render 环境变量未应用到服务")
        print("3. 代码逻辑有问题")
    else:
        print("\n✅ 返回的是智能回复，说明 DeepSeek API 调用成功")
        
except Exception as e:
    print(f"\n❌ 请求失败: {str(e)}")


