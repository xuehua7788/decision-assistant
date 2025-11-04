#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待Render部署完成并测试
"""

import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("⏳ 等待Render部署完成...")
print("   预计需要2-3分钟")
print()

# 等待2分钟
for i in range(12):
    print(f"   等待中... {i*10}秒/{120}秒", end='\r')
    time.sleep(10)

print("\n\n" + "=" * 60)
print("开始测试Render后端")
print("=" * 60)

# 测试策略API
print("\n🔍 测试策略API...")
try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ 策略API正常工作！")
        print(f"策略数量: {result.get('count', 0)}")
    elif response.status_code == 404:
        print(f"❌ 仍然是404错误")
        print(f"可能需要更多时间部署，或者需要在Render Dashboard手动触发部署")
    else:
        print(f"⚠️ 返回状态码: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 60)

