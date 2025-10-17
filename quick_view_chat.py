#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速查看聊天记录
"""

import requests
import json
import sys

API_URL = "https://decision-assistant-backend.onrender.com"

def view_session(session_id):
    """查看指定会话"""
    r = requests.get(f"{API_URL}/api/admin/chats")
    data = r.json()
    
    if session_id not in data['chats']:
        print(f"❌ 会话 '{session_id}' 不存在")
        print(f"\n可用的会话ID:")
        for sid in data['chats'].keys():
            print(f"  - {sid}")
        return
    
    chat = data['chats'][session_id]
    
    print("=" * 80)
    print(f"📝 会话ID: {session_id}")
    print("=" * 80)
    print(f"消息总数: {chat['total_messages']}\n")
    
    for idx, msg in enumerate(chat['last_messages'], 1):
        print("-" * 80)
        
        if 'role' in msg:
            # 新格式
            role = msg.get('role', 'unknown').upper()
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 'N/A')
            
            print(f"[{idx}] {role} - {timestamp}")
            print(f"\n{content}\n")
        elif 'user' in msg:
            # 旧格式
            print(f"[{idx}] USER")
            print(f"\n{msg.get('user', '')}\n")
            print(f"[{idx}] ASSISTANT")
            print(f"\n{msg.get('assistant', '')}\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("📋 使用方法: python quick_view_chat.py <session_id>")
        print("\n示例:")
        print("  python quick_view_chat.py test")
        print("  python quick_view_chat.py 4e37bb85-c3a6-4eaf-9ec7-b81ce6ca5d5f")
        
        # 显示可用的会话
        r = requests.get(f"{API_URL}/api/admin/chats")
        data = r.json()
        print(f"\n📝 当前可用的 {data['total_sessions']} 个会话:")
        for sid in data['chats'].keys():
            print(f"  - {sid}")
        sys.exit(1)
    
    session_id = sys.argv[1]
    view_session(session_id)

