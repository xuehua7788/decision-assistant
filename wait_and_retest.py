#!/usr/bin/env python3
"""等待Render部署完成后重新测试"""
import time
import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("⏳ 等待Render部署...")
print("=" * 80)

print("\n💡 Render通常需要 1-3 分钟部署")
print("   请稍候...\n")

# 等待2分钟
for i in range(120, 0, -10):
    print(f"   剩余: {i}秒...", end='\r')
    time.sleep(10)

print("\n\n" + "=" * 80)
print("🧪 开始测试")
print("=" * 80)

# 测试新的API端点
print("\n【测试】查询用户策略API")
print("-" * 80)

test_usernames = ["test_1762251403", "bbb", "admin"]

for username in test_usernames:
    print(f"\n🔍 查询用户: {username}")
    
    try:
        response = requests.get(
            f"{RENDER_URL}/api/strategy/user/{username}",
            timeout=15
        )
        
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            count = data.get('count', 0)
            print(f"   ✅ 成功 - 找到 {count} 个策略")
        elif response.status_code == 404:
            print(f"   ⚠️  404 - API路由可能还未部署")
        else:
            print(f"   ❌ 错误: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

print("\n" + "=" * 80)
print("📝 下一步")
print("=" * 80)

print("\n如果看到 404：")
print("  - Render可能还在部署中，再等2分钟")
print("  - 或者需要手动重启Render服务")

print("\n如果看到 200：")
print("  - ✅ API部署成功！")
print("  - 现在需要运行数据库迁移")
print("  - 运行: python migrate_add_user_columns.py")

print("\n" + "=" * 80)


