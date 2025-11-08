#!/usr/bin/env python3
"""唤醒Render后端（处理冷启动）"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("⏰ 唤醒 Render 后端（处理冷启动）")
print("=" * 80)
print("\n💡 Render 免费版闲置后会休眠，首次访问需要等待...")
print()

for i in range(20):  # 最多等待 6-7 分钟
    print(f"尝试 {i+1}/20...", end=' ')
    
    try:
        response = requests.get(
            f"{RENDER_URL}/api/stock/health",
            timeout=30  # 增加超时时间
        )
        
        if response.status_code == 200:
            print("✅ 成功！")
            print(f"\n🎉 后端已唤醒！")
            print(f"响应: {response.json()}")
            
            # 测试登录
            print(f"\n🧪 测试登录...")
            login_response = requests.post(
                f"{RENDER_URL}/api/auth/login",
                json={"username": "admin", "password": "admin123"},
                timeout=15
            )
            
            print(f"登录状态码: {login_response.status_code}")
            
            if login_response.status_code in [200, 401]:
                print("✅ 登录API正常工作！")
            
            break
        else:
            print(f"状态码: {response.status_code}")
            
    except requests.Timeout:
        print("超时...")
    except Exception as e:
        print(f"错误: {str(e)[:50]}")
    
    if i < 19:
        time.sleep(20)  # 等待 20 秒

print("\n" + "=" * 80)


