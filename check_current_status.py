#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查当前状态
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 70)
print("当前聊天记录存储状态")
print("=" * 70)
print()

# 1. 检查JSON中的记录
print("1️⃣ JSON文件存储（临时）:")
try:
    response = requests.get(f"{BASE_URL}/api/admin/chats/bbb", timeout=10)
    if response.status_code == 200:
        data = response.json()
        json_count = len(data.get('messages', []))
        print(f"   ✅ bbb用户有 {json_count} 条消息")
    else:
        print(f"   ❌ 无法获取: {response.status_code}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print()

# 2. 检查数据库中的记录
print("2️⃣ PostgreSQL数据库存储（永久）:")
try:
    response = requests.post(
        f"{BASE_URL}/api/profile/bbb/analyze",
        json={},
        timeout=60
    )
    
    if response.status_code == 400:
        data = response.json()
        error = data.get('error', '')
        
        import re
        match = re.search(r'（(\d+) 条）', error)
        if match:
            db_count = int(match.group(1))
            print(f"   ❌ bbb用户有 {db_count} 条消息")
            
            if db_count == 0:
                print()
                print("   🔍 原因分析:")
                print("   • save_chat_message 被调用了（JSON有记录）")
                print("   • 但 db_sync.is_available() 返回 False")
                print("   • 或者 sync_chat_message 执行失败")
        else:
            print(f"   ⚠️ {error}")
            
    elif response.status_code == 200:
        print(f"   ✅ 有足够的消息，分析成功")
    else:
        print(f"   ❌ 错误: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ 错误: {e}")

print()
print("=" * 70)
print("结论")
print("=" * 70)
print()
print("JSON有记录 + 数据库无记录 = 数据库同步失败")
print()
print("可能原因:")
print("1. db_sync.is_available() 返回 False（连接断开）")
print("2. chat_sessions 或 chat_messages 表不存在")
print("3. sync_chat_message 执行时抛出异常")
print()
print("需要部署调试API来查看详细状态")
print()







