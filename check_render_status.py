#!/usr/bin/env python3
"""检查Render状态"""
import requests

API_URL = "https://decision-assistant-b.onrender.com"

print("检查Render状态...\n")

# 1. 健康检查
print("1. 健康检查")
try:
    r = requests.get(f"{API_URL}/api/health", timeout=10)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ 后端正常运行")
    else:
        print(f"   ❌ 响应: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 检查股票API
print("\n2. 检查股票API")
try:
    r = requests.get(f"{API_URL}/api/stock/AAPL", timeout=30)
    print(f"   状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()
        if data.get('status') == 'success':
            print(f"   ✅ 股票API正常")
        else:
            print(f"   ❌ {data.get('message')}")
    else:
        print(f"   ❌ 响应: {r.text[:100]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 3. 检查ML API
print("\n3. 检查ML顾问API")
try:
    r = requests.options(f"{API_URL}/api/ml/trading/advice", timeout=10)
    print(f"   OPTIONS状态码: {r.status_code}")
    if r.status_code == 200:
        print(f"   ✅ ML API端点存在")
    else:
        print(f"   ❌ ML API可能未注册")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 4. 检查所有路由
print("\n4. 尝试访问根路径")
try:
    r = requests.get(f"{API_URL}/", timeout=10)
    print(f"   状态码: {r.status_code}")
    print(f"   响应: {r.text[:200]}")
except Exception as e:
    print(f"   ❌ 错误: {e}")


