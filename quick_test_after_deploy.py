#!/usr/bin/env python3
"""快速测试部署后的API"""
import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("🧪 快速测试新API")
print("=" * 80)

# 测试新端点
print("\n【测试】/api/strategy/user/{username} 端点")
print("-" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/user/test", timeout=15)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ API已部署成功！")
        data = response.json()
        print(f"   返回数据: {data.get('status')}")
        print(f"   策略数: {data.get('count', 0)}")
    elif response.status_code == 404:
        print("❌ 404 - Render还未部署新代码")
        print("   请等待2-3分钟后重试")
    else:
        print(f"⚠️  返回: {response.status_code}")
        print(f"   内容: {response.text[:200]}")
        
except requests.Timeout:
    print("⏱️  超时 - Render可能正在冷启动")
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "=" * 80)


