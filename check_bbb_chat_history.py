import requests

API_BASE = 'https://decision-assistant-backend.onrender.com'
USERNAME = 'bbb'

print("=" * 60)
print("检查bbb的聊天记录")
print("=" * 60)

# 1. 检查聊天记录API
print("\n1. 从后端API获取聊天记录:")
try:
    r = requests.get(f"{API_BASE}/api/decisions/chat/{USERNAME}", timeout=10)
    print(f"   状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get('messages', [])
        print(f"   ✅ 找到 {len(messages)} 条消息")
        
        if len(messages) > 0:
            print(f"\n   最近3条消息:")
            for i, msg in enumerate(messages[-3:], 1):
                if 'user' in msg:
                    print(f"   [{i}] 用户: {msg['user'][:50]}...")
                if 'assistant' in msg:
                    print(f"   [{i}] AI: {msg['assistant'][:50]}...")
        else:
            print("   ⚠️ 消息列表为空")
    else:
        print(f"   ❌ 失败: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 检查用户画像分析的消息数
print("\n2. 从用户画像查看分析的消息数:")
try:
    r = requests.get(f"{API_BASE}/api/profile/{USERNAME}", timeout=10)
    
    if r.status_code == 200:
        data = r.json()
        profile = data.get('profile', {})
        total_messages = profile.get('metadata', {}).get('total_messages_analyzed', 0)
        print(f"   ✅ 画像分析了 {total_messages} 条消息")
        
        if total_messages > 0:
            print(f"   说明数据库中有聊天记录")
    else:
        print(f"   ❌ 失败")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 60)
print("结论:")
print("如果API返回的消息数 > 0，说明数据在数据库中")
print("如果前端看不到，是前端加载逻辑的问题")
print("=" * 60)






