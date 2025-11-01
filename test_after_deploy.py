import requests
import time

API_BASE = 'https://decision-assistant-githubv3.onrender.com'

print("等待30秒让Render完成部署...")
time.sleep(30)

print("\n测试Profile API...")
try:
    r = requests.get(f"{API_BASE}/api/profile/stats", timeout=10)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        print("✅ Profile API已部署！")
        print(f"响应: {r.json()}")
    else:
        print(f"❌ Profile API未就绪")
        print(f"响应: {r.text[:200]}")
except Exception as e:
    print(f"❌ 错误: {e}")






