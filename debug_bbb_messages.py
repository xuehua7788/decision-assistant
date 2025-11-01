import requests

API_BASE = 'https://decision-assistant-backend.onrender.com'
USERNAME = 'bbb'

print("=" * 70)
print("调试bbb的消息同步问题")
print("=" * 70)

# 1. 检查数据库中的消息
print("\n1. 检查后端API返回的消息:")
try:
    r = requests.get(f"{API_BASE}/api/decisions/chat/{USERNAME}", timeout=10)
    
    if r.status_code == 200:
        data = r.json()
        messages = data.get('messages', [])
        print(f"   API返回: {len(messages)} 条消息")
        
        print(f"\n   所有消息:")
        for i, msg in enumerate(messages, 1):
            print(f"\n   消息 {i}:")
            if 'user' in msg:
                print(f"      用户: {msg['user']}")
            if 'assistant' in msg:
                print(f"      AI: {msg['assistant'][:100]}...")
    else:
        print(f"   ❌ API失败: {r.status_code}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 检查用户画像分析的消息数
print("\n" + "=" * 70)
print("2. 用户画像分析的消息数:")
try:
    r = requests.get(f"{API_BASE}/api/profile/{USERNAME}", timeout=10)
    
    if r.status_code == 200:
        data = r.json()
        profile = data.get('profile', {})
        metadata = profile.get('metadata', {})
        
        print(f"   总消息数: {metadata.get('total_messages_analyzed', 0)}")
        print(f"   分析时间: {metadata.get('analyzed_at', 'N/A')}")
        print(f"   分析周期: {metadata.get('analysis_period_days', 0)} 天")
        
        # 显示关键洞察中提到的问题
        insights = profile.get('key_insights', {})
        common_questions = insights.get('common_questions', [])
        print(f"\n   常见问题: {common_questions}")
        
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 70)
print("分析:")
print("如果画像分析了14条消息，但API只返回3条")
print("说明有11条旧消息在画像分析时存在，但现在已经丢失")
print("可能原因:")
print("1. 旧消息只在JSON文件中，Render重启后丢失")
print("2. 数据库同步在某个时间点才开始工作")
print("3. 画像分析时读取的是JSON文件，而不是数据库")
print("=" * 70)






