#!/usr/bin/env python3
"""诊断登录注册问题"""
import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("🔍 诊断登录注册问题")
print("=" * 80)

# 测试1：后端健康检查
print("\n【测试1】后端是否在线？")
print("-" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=15)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 后端在线")
        print(f"响应: {response.json()}")
    else:
        print(f"❌ 后端异常")
        print(f"响应: {response.text[:200]}")
        
except requests.Timeout:
    print("❌ 超时 - 后端可能挂了或正在冷启动")
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试2：注册API
print("\n【测试2】注册API是否工作？")
print("-" * 80)

import time
test_user = f"diagnose_{int(time.time())}"

try:
    response = requests.post(
        f"{RENDER_URL}/api/auth/register",
        json={
            "username": test_user,
            "password": "test123456"
        },
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:300]}")
    
    if response.status_code == 200:
        print("✅ 注册API正常")
    else:
        print("❌ 注册API异常")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试3：登录API
print("\n【测试3】登录API是否工作？")
print("-" * 80)

try:
    response = requests.post(
        f"{RENDER_URL}/api/auth/login",
        json={
            "username": "admin",
            "password": "admin123"
        },
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:300]}")
    
    if response.status_code == 200:
        print("✅ 登录API正常")
    elif response.status_code == 401:
        print("⚠️  密码错误（但API正常）")
    else:
        print("❌ 登录API异常")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试4：CORS预检
print("\n【测试4】CORS预检请求")
print("-" * 80)

try:
    response = requests.options(
        f"{RENDER_URL}/api/auth/register",
        headers={
            'Origin': 'https://decision-assistant-frontend-prod.vercel.app',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'content-type'
        },
        timeout=10
    )
    
    print(f"状态码: {response.status_code}")
    print(f"CORS Headers:")
    for key, value in response.headers.items():
        if 'access-control' in key.lower():
            print(f"  {key}: {value}")
    
    if 'Access-Control-Allow-Origin' in response.headers:
        print("✅ CORS配置正常")
    else:
        print("❌ CORS配置缺失")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 总结
print("\n" + "=" * 80)
print("📋 诊断结果")
print("=" * 80)

print("\n可能的问题：")
print("1. 后端正在冷启动（首次访问需要等待）")
print("2. 后端崩溃（需要查看Render日志）")
print("3. CORS配置问题（新代码未部署）")
print("4. API路由问题")

print("\n建议操作：")
print("1. 等待3分钟让后端冷启动")
print("2. 查看 Render Dashboard 的日志")
print("3. 手动重启 Render 服务")

print("\n" + "=" * 80)


