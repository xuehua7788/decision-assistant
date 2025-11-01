import requests
import json

BASE = 'https://decision-assistant-backend.onrender.com'
USERNAME = 'bbb'

print("=" * 70)
print("测试所有Profile功能")
print("=" * 70)

# 1. 查看用户画像
print("\n1. 查看用户画像 (GET /api/profile/bbb)")
try:
    r = requests.get(f"{BASE}/api/profile/{USERNAME}", timeout=10)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        print("   ✅ 成功")
    else:
        print(f"   ❌ 失败: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 查看策略推荐
print("\n2. 查看策略推荐 (GET /api/profile/bbb/recommendations)")
try:
    r = requests.get(f"{BASE}/api/profile/{USERNAME}/recommendations", timeout=10)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ 成功")
        print(f"   推荐数量: {len(data.get('recommendations', []))}")
    else:
        print(f"   ❌ 失败: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 3. 统计信息
print("\n3. 统计信息 (GET /api/profile/stats)")
try:
    r = requests.get(f"{BASE}/api/profile/stats", timeout=10)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        print(f"   ✅ 成功")
        print(f"   总画像数: {data['stats']['total_profiles']}")
        print(f"   最近分析: {data['stats']['recently_analyzed']}")
    else:
        print(f"   ❌ 失败: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 4. 测试旧的聊天API
print("\n4. 测试聊天API (POST /api/decisions/chat)")
try:
    r = requests.post(f"{BASE}/api/decisions/chat", 
                     json={"message": "test", "session_id": "test123"},
                     timeout=10)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        print("   ✅ 聊天功能正常")
    else:
        print(f"   ⚠️ 状态: {r.status_code}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 5. 测试登录API
print("\n5. 测试登录API (POST /api/auth/login)")
try:
    r = requests.post(f"{BASE}/api/auth/login",
                     json={"username": "bbb", "password": "123"},
                     timeout=10)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        print("   ✅ 登录功能正常")
    else:
        print(f"   ⚠️ 状态: {r.status_code}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "=" * 70)
print("测试完成")
print("=" * 70)






