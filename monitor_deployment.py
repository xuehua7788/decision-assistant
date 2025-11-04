#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
监控Render部署状态
"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("Monitoring Render deployment...")
print("Checking every 10 seconds...\n")

for i in range(20):  # 检查20次（约3分钟）
    try:
        # Test strategy list endpoint
        response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=5)
        
        if response.status_code == 200:
            print(f"✅ [{time.strftime('%H:%M:%S')}] Deployment SUCCESS! Strategy API is working!")
            data = response.json()
            print(f"   Strategies count: {data.get('count', 0)}")
            break
        elif response.status_code == 404:
            print(f"⏳ [{time.strftime('%H:%M:%S')}] Still deploying... (404)")
        else:
            print(f"⚠️  [{time.strftime('%H:%M:%S')}] Status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⏳ [{time.strftime('%H:%M:%S')}] Waiting for server... ({str(e)[:50]})")
    
    if i < 19:
        time.sleep(10)

print("\nMonitoring complete!")


