#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待部署并检查状态
"""

import requests
import time

BASE_URL = "https://decision-assistant-backend.onrender.com"

print("等待Render部署...")
time.sleep(120)  # 等待2分钟

print("\n检查数据库状态...")
try:
    response = requests.get(f"{BASE_URL}/api/debug/db-sync-status", timeout=10)
    if response.status_code == 200:
        data = response.json()
        total = data.get('total_messages_in_db', 0)
        bbb = data.get('bbb_messages_in_db', 0)
        
        print(f"✅ 数据库中总消息数: {total}")
        print(f"✅ bbb用户消息数: {bbb}")
        
        if bbb >= 2:
            print(f"\n🎉 数据库同步成功！bbb有{bbb}条消息")
            print(f"还需要 {max(0, 5 - bbb)} 条消息才能分析用户画像")
        else:
            print("\n⚠️ 数据库中没有bbb的消息")
    else:
        print(f"❌ API返回: {response.status_code}")
except Exception as e:
    print(f"❌ 错误: {e}")








