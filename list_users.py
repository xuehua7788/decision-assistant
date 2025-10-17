#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
列出所有用户和会话
"""

import requests
import json

API_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("👥 所有用户")
print("=" * 80)

# 获取用户列表
r = requests.get(f"{API_URL}/api/admin/users")
users = r.json()

print(f"总用户数: {users['total_users']}\n")

for username, info in users['users'].items():
    print(f"📧 {username}")
    print(f"   创建时间: {info.get('created_at', 'N/A')}")
    print(f"   有密码: {'✅' if info.get('has_password') else '❌'}")
    print()

print("=" * 80)
print("💬 所有聊天会话")
print("=" * 80)

# 获取聊天会话列表
r = requests.get(f"{API_URL}/api/admin/chats")
data = r.json()

print(f"总会话数: {data['total_sessions']}\n")

for session_id, chat in data['chats'].items():
    print(f"📝 {session_id}")
    print(f"   消息数: {chat['total_messages']}")
    
    # 显示第一条消息预览
    if chat['last_messages']:
        first_msg = chat['last_messages'][0]
        
        if 'role' in first_msg and first_msg.get('role') == 'user':
            preview = first_msg.get('content', '')[:60]
        elif 'user' in first_msg:
            preview = first_msg.get('user', '')[:60]
        else:
            preview = "N/A"
        
        print(f"   首条消息: {preview}...")
    print()

print("=" * 80)
print("\n💡 提示:")
print("  - 查看特定会话: python quick_view_chat.py <session_id>")
print("  - 查看用户聊天: python quick_view_chat.py <username>")
print("=" * 80)

