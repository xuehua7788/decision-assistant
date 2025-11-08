#!/usr/bin/env python3
"""手动部署后测试"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("🧪 测试手动部署后的后端")
print("=" * 80)

# 测试1：健康检查
print("\n【测试1】健康检查")
print("-" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 后端在线")
        print(f"   状态: {data.get('status')}")
        print(f"   版本: {data.get('version', 'N/A')}")
    else:
        print(f"❌ 状态码: {response.status_code}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试2：CORS预检
print("\n【测试2】CORS配置")
print("-" * 80)

try:
    response = requests.options(
        f"{RENDER_URL}/api/auth/login",
        headers={
            'Origin': 'https://decision-assistant-frontend-prod.vercel.app',
            'Access-Control-Request-Method': 'POST'
        },
        timeout=10
    )
    
    print(f"状态码: {response.status_code}")
    
    cors_headers = {k: v for k, v in response.headers.items() 
                   if 'access-control' in k.lower()}
    
    if cors_headers:
        print("✅ CORS响应头:")
        for k, v in cors_headers.items():
            print(f"   {k}: {v}")
    else:
        print("❌ 缺少CORS响应头")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试3：登录API
print("\n【测试3】登录API")
print("-" * 80)

try:
    response = requests.post(
        f"{RENDER_URL}/api/auth/login",
        json={"username": "admin", "password": "admin123"},
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.text[:200]}")
    
    if response.status_code in [200, 401]:
        print("✅ 登录API正常工作")
    else:
        print("❌ 登录API异常")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试4：注册API
print("\n【测试4】注册API")
print("-" * 80)

test_user = f"test_{int(time.time())}"

try:
    response = requests.post(
        f"{RENDER_URL}/api/auth/register",
        json={"username": test_user, "password": "test123"},
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 注册成功")
        print(f"   用户名: {data.get('username')}")
    else:
        print(f"响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 测试5：新API端点
print("\n【测试5】用户策略查询API")
print("-" * 80)

try:
    response = requests.get(
        f"{RENDER_URL}/api/strategy/user/test",
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ 新API已部署")
        data = response.json()
        print(f"   返回: {data.get('status')}")
    elif response.status_code == 404:
        print("❌ 新API还未部署")
    else:
        print(f"响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 总结
print("\n" + "=" * 80)
print("📊 测试总结")
print("=" * 80)

print("\n✅ 如果所有测试通过：")
print("   1. 前端应该可以正常登录注册了")
print("   2. 可以运行完整测试: python test_user_fix.py")
print("   3. 需要运行数据库迁移: python migrate_add_user_columns.py")

print("\n❌ 如果还有问题：")
print("   1. 检查Render部署日志")
print("   2. 确认部署状态为 'Live'")
print("   3. 尝试在Render Dashboard重启服务")

print("\n" + "=" * 80)


