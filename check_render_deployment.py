#!/usr/bin/env python3
"""检查 Render 部署状态"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("🔍 检查 Render 部署状态")
print("=" * 80)

for i in range(10):
    print(f"\n尝试 {i+1}/10...")
    
    try:
        response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 后端在线")
            print(f"   状态: {data.get('status')}")
            print(f"   版本: {data.get('version', 'N/A')}")
            
            # 测试新的 API
            print(f"\n🧪 测试新 API...")
            test_response = requests.get(
                f"{RENDER_URL}/api/strategy/user/test",
                timeout=10
            )
            
            if test_response.status_code == 200:
                print(f"   ✅ 新 API 已部署！")
                print(f"\n🎉 部署成功！可以测试了")
                break
            elif test_response.status_code == 404:
                print(f"   ⚠️  新 API 还未部署")
            else:
                print(f"   状态码: {test_response.status_code}")
                
        else:
            print(f"⚠️  状态码: {response.status_code}")
            
    except requests.Timeout:
        print(f"⏱️  超时...")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    if i < 9:
        print(f"   等待 20 秒...")
        time.sleep(20)

print("\n" + "=" * 80)


