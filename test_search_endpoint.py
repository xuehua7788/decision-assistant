#!/usr/bin/env python3
"""直接测试搜索端点"""
import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

# Test 1: 检查路由是否存在
print("1️⃣ 检查路由...")
try:
    response = requests.options(f"{RENDER_URL}/api/stock/search", timeout=10)
    print(f"   OPTIONS /api/stock/search: {response.status_code}")
    print(f"   允许的方法: {response.headers.get('Allow', 'N/A')}")
except Exception as e:
    print(f"   ❌ {e}")

# Test 2: 直接访问
print("\n2️⃣ GET /api/stock/search...")
try:
    response = requests.get(f"{RENDER_URL}/api/stock/search", timeout=10)
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ {e}")

# Test 3: 带参数访问
print("\n3️⃣ GET /api/stock/search?keywords=apple...")
try:
    response = requests.get(
        f"{RENDER_URL}/api/stock/search",
        params={'keywords': 'apple'},
        timeout=10
    )
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.text[:500]}")
except Exception as e:
    print(f"   ❌ {e}")


