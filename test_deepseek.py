import os
import requests
from dotenv import load_dotenv

load_dotenv()

# 设置 DeepSeek API Key
api_key = os.getenv('DEEPSEEK_API_KEY')

print(f"DeepSeek API Key: {api_key[:10]}..." if api_key else "DeepSeek API Key: NOT SET")

try:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是一个专业的决策助手，帮助用户做出明智的决策。请用中文回复，简洁明了。"},
            {"role": "user", "content": "给我买房子建议"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    print(f"\n响应状态码: {response.status_code}")
    print(f"响应内容: {response.text[:500]}")
    
    if response.status_code == 200:
        result = response.json()
        ai_response = result["choices"][0]["message"]["content"]
        print(f"\n✅ DeepSeek API 调用成功！")
        print(f"回复内容: {ai_response}")
    else:
        print(f"\n❌ DeepSeek API 调用失败！")
        print(f"错误信息: {response.text}")
    
except Exception as e:
    print(f"\n❌ DeepSeek API 调用失败！")
    print(f"错误信息: {str(e)}")


