#!/usr/bin/env python3
"""等待Render完全部署并测试"""
import requests
import time

BACKEND_URL = "https://decision-assistant-backend.onrender.com"

print("\n🔄 等待Render完全部署...")
print("="*80)

for i in range(120):  # 最多等待10分钟
    try:
        # 测试新的API路由
        response = requests.get(f"{BACKEND_URL}/api/user/bbb/strategies", timeout=5)
        
        if response.status_code in [200, 404]:  # 404表示用户不存在，但路由存在
            if response.status_code == 200:
                print(f"\n✅ 部署完成！ (等待了 {i*5}秒)")
                data = response.json()
                print(f"   状态: {data.get('status')}")
                print(f"   用户: {data.get('username')}")
                print(f"   策略数: {data.get('total')}")
                break
            elif response.status_code == 404:
                try:
                    data = response.json()
                    if 'status' in data:  # 是我们的API返回的404
                        print(f"\n✅ 部署完成！ (等待了 {i*5}秒)")
                        print(f"   API已就绪，但用户不存在（可能迁移未完成）")
                        break
                except:
                    pass
        
    except requests.exceptions.RequestException:
        pass
    
    if i % 6 == 0:
        print(f"   等待中... {i*5}秒 / 600秒")
    
    time.sleep(5)
else:
    print("\n⚠️  超时，但继续测试...")

print("\n" + "="*80)
print("开始完整测试...")
print("="*80)

# 执行完整测试
import subprocess
subprocess.run(["python", "test_new_apis.py"])


