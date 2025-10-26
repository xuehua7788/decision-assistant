#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查看用户的聊天记录
"""

import requests
import json
import sys

BASE_URL = "https://decision-assistant-backend.onrender.com"

def view_user_chat(username):
    """查看指定用户的聊天记录"""
    print("=" * 70)
    print(f"查看用户聊天记录: {username}")
    print("=" * 70)
    print()
    
    try:
        # 从管理员API获取聊天记录
        response = requests.get(f"{BASE_URL}/api/admin/chats/{username}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            messages = data.get('messages', [])
            
            print(f"✅ 找到 {len(messages)} 条消息")
            print()
            
            if len(messages) == 0:
                print("   暂无聊天记录")
                return
            
            # 显示每条消息
            for i, msg in enumerate(messages, 1):
                print(f"{'='*70}")
                print(f"消息 {i}/{len(messages)}")
                print(f"{'='*70}")
                
                # 用户消息
                if 'user' in msg:
                    print(f"👤 用户: {msg['user']}")
                
                # AI回复
                if 'assistant' in msg:
                    print(f"🤖 AI: {msg['assistant']}")
                
                # 时间戳
                if 'timestamp' in msg:
                    print(f"⏰ 时间: {msg['timestamp']}")
                
                print()
            
            print("=" * 70)
            print("统计信息")
            print("=" * 70)
            print(f"总消息数: {len(messages)}")
            print(f"用户消息: {sum(1 for m in messages if 'user' in m)}")
            print(f"AI回复: {sum(1 for m in messages if 'assistant' in m)}")
            print()
            
            # 检查是否足够分析
            if len(messages) >= 5:
                print("✅ 消息数量充足，可以进行画像分析")
                print(f"   运行: python analyze_user.py {username}")
            else:
                print(f"⚠️ 消息数量不足（需要至少5条，当前{len(messages)}条）")
                print(f"   需要再聊 {5 - len(messages)} 轮对话")
            print()
            
        elif response.status_code == 404:
            print("❌ 用户不存在或没有聊天记录")
        else:
            print(f"❌ 错误: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python view_user_chat.py <username>")
        print()
        print("示例:")
        print("  python view_user_chat.py bbb")
        sys.exit(1)
    
    username = sys.argv[1]
    view_user_chat(username)
