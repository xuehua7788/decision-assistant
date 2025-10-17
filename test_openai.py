import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 设置 OpenAI API Key
api_key = os.getenv('OPENAI_API_KEY')

print(f"OpenAI API Key: {api_key[:10]}..." if api_key else "OpenAI API Key: NOT SET")

try:
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "你是一个专业的决策助手，帮助用户做出明智的决策。请用中文回复，简洁明了。"},
            {"role": "user", "content": "给我买房子建议"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    ai_response = response.choices[0].message.content
    print(f"\n✅ OpenAI API 调用成功！")
    print(f"回复内容: {ai_response}")
    
except Exception as e:
    print(f"\n❌ OpenAI API 调用失败！")
    print(f"错误信息: {str(e)}")

