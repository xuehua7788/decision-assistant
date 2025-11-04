#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断策略API问题
"""

import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 60)
print("诊断策略API问题")
print("=" * 60)

# 1. 测试健康检查
print("\n1️⃣ 测试健康检查...")
try:
    response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=10)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ 后端正常运行")
        print(f"   响应: {response.json()}")
    else:
        print(f"   ❌ 后端异常")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

# 2. 测试策略列表API
print("\n2️⃣ 测试策略列表API (GET /api/strategy/list)...")
try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    print(f"   状态码: {response.status_code}")
    print(f"   响应头: {dict(response.headers)}")
    if response.status_code == 200:
        print(f"   ✅ API存在且正常")
        result = response.json()
        print(f"   策略数量: {result.get('count', 0)}")
    elif response.status_code == 404:
        print(f"   ❌ API不存在 (404)")
        print(f"   响应内容: {response.text[:200]}")
    else:
        print(f"   ⚠️ API存在但返回错误")
        print(f"   响应内容: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

# 3. 测试OPTIONS预检请求
print("\n3️⃣ 测试CORS预检请求 (OPTIONS /api/strategy/save)...")
try:
    response = requests.options(
        f"{RENDER_URL}/api/strategy/save",
        headers={
            "Origin": "https://decision-assistant-frontend-prod.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        },
        timeout=10
    )
    print(f"   状态码: {response.status_code}")
    print(f"   CORS头:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"     {key}: {value}")
    
    if response.status_code == 200:
        print(f"   ✅ CORS预检通过")
    elif response.status_code == 404:
        print(f"   ❌ 路由不存在 (404)")
    else:
        print(f"   ⚠️ CORS预检失败")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

# 4. 测试POST保存API
print("\n4️⃣ 测试保存API (POST /api/strategy/save)...")
try:
    test_data = {
        "symbol": "TEST",
        "company_name": "Test Company",
        "investment_style": "buffett",
        "recommendation": "买入",
        "target_price": 100.0,
        "current_price": 90.0
    }
    response = requests.post(
        f"{RENDER_URL}/api/strategy/save",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ API正常工作")
        print(f"   响应: {response.json()}")
    elif response.status_code == 404:
        print(f"   ❌ API不存在 (404)")
        print(f"   响应内容: {response.text[:200]}")
    else:
        print(f"   ⚠️ API存在但返回错误")
        print(f"   响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")
print("=" * 60)

