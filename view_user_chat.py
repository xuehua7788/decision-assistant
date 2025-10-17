#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看用户聊天记录工具
"""

import requests
import json
from datetime import datetime

API_URL = "https://decision-assistant-backend.onrender.com"

def view_all_users():
    """查看所有用户"""
    r = requests.get(f"{API_URL}/api/admin/users")
    users = r.json()
    
    print("=" * 80)
    print("所有用户列表")
    print("=" * 80)
    print(f"总用户数: {users['total_users']}\n")
    
    for username, info in users['users'].items():
        print(f"用户名: {username}")
        print(f"  - 创建时间: {info.get('created_at', 'N/A')}")
        print(f"  - 有密码: {'是' if info.get('has_password') else '否'}")
        print()

def view_all_chats():
    """查看所有聊天会话"""
    r = requests.get(f"{API_URL}/api/admin/chats")
    data = r.json()
    
    print("=" * 80)
    print("所有聊天会话")
    print("=" * 80)
    print(f"总会话数: {data['total_sessions']}\n")
    
    for session_id, chat in data['chats'].items():
        print(f"会话ID: {session_id}")
        print(f"  消息数: {chat['total_messages']}")
        
        if chat['last_messages']:
            print(f"  最后一条消息:")
            last_msg = chat['last_messages'][-1]
            
            # 处理不同格式的消息
            if 'role' in last_msg:
                print(f"    [{last_msg.get('role', 'unknown')}] {last_msg.get('content', '')[:100]}...")
                print(f"    时间: {last_msg.get('timestamp', 'N/A')}")
            elif 'user' in last_msg:
                print(f"    [user] {last_msg.get('user', '')[:100]}...")
                print(f"    [assistant] {last_msg.get('assistant', '')[:100]}...")
        print()

def view_user_chat(username):
    """查看指定用户的聊天记录"""
    r = requests.get(f"{API_URL}/api/admin/chats/{username}")
    
    if r.status_code == 404:
        print(f"用户 {username} 的聊天记录不存在")
        return
    
    data = r.json()
    
    print("=" * 80)
    print(f"用户 {username} 的聊天记录")
    print("=" * 80)
    
    if 'error' in data:
        print(f"错误: {data['error']}")
        return
    
    print(json.dumps(data, indent=2, ensure_ascii=False))

def view_session_detail(session_id):
    """查看指定会话的详细记录"""
    # 先获取所有聊天
    r = requests.get(f"{API_URL}/api/admin/chats")
    data = r.json()
    
    if session_id not in data['chats']:
        print(f"会话 {session_id} 不存在")
        return
    
    chat = data['chats'][session_id]
    
    print("=" * 80)
    print(f"会话详情: {session_id}")
    print("=" * 80)
    print(f"消息总数: {chat['total_messages']}\n")
    
    print("对话内容:")
    print("-" * 80)
    
    for idx, msg in enumerate(chat['last_messages'], 1):
        # 处理不同格式的消息
        if 'role' in msg:
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')
            timestamp = msg.get('timestamp', 'N/A')
            
            print(f"\n[{idx}] {role.upper()} - {timestamp}")
            print(f"{content}\n")
        elif 'user' in msg:
            timestamp = msg.get('timestamp', 'N/A')
            print(f"\n[{idx}] USER - {timestamp}")
            print(f"{msg.get('user', '')}\n")
            print(f"[{idx}] ASSISTANT - {timestamp}")
            print(f"{msg.get('assistant', '')}\n")

def main():
    print("\n🔍 用户聊天记录查看工具\n")
    
    while True:
        print("\n请选择操作:")
        print("1. 查看所有用户")
        print("2. 查看所有聊天会话")
        print("3. 查看指定用户的聊天")
        print("4. 查看指定会话的详细内容")
        print("5. 退出")
        
        choice = input("\n请输入选项 (1-5): ").strip()
        
        if choice == '1':
            view_all_users()
        elif choice == '2':
            view_all_chats()
        elif choice == '3':
            username = input("请输入用户名: ").strip()
            view_user_chat(username)
        elif choice == '4':
            session_id = input("请输入会话ID: ").strip()
            view_session_detail(session_id)
        elif choice == '5':
            print("\n再见！")
            break
        else:
            print("无效选项，请重新选择")

if __name__ == "__main__":
    main()

