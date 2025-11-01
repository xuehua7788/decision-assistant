#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
将JSON聊天记录导入数据库
"""

import requests
import json

BASE_URL = "https://decision-assistant-backend.onrender.com"

def import_user_chat(username):
    """导入指定用户的聊天记录到数据库"""
    print("=" * 70)
    print(f"导入用户聊天记录: {username}")
    print("=" * 70)
    print()
    
    # 1. 获取JSON中的聊天记录
    print("1. 获取聊天记录...")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/chats/{username}", timeout=10)
        
        if response.status_code != 200:
            print(f"   ❌ 无法获取聊天记录: {response.status_code}")
            return False
        
        data = response.json()
        messages = data.get('messages', [])
        
        print(f"   ✅ 找到 {len(messages)} 条消息")
        
        if len(messages) == 0:
            print("   ⚠️ 没有消息需要导入")
            return False
        
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False
    
    # 2. 模拟聊天来触发数据库同步
    print()
    print("2. 导入消息到数据库...")
    print("   （通过重新发送消息来触发数据库同步）")
    print()
    
    imported_count = 0
    
    for i, msg in enumerate(messages, 1):
        user_msg = msg.get('user', '')
        assistant_msg = msg.get('assistant', '')
        
        if not user_msg:
            continue
        
        print(f"   导入消息 {i}/{len(messages)}: {user_msg[:50]}...")
        
        try:
            # 通过chat API重新发送，触发数据库同步
            response = requests.post(
                f"{BASE_URL}/api/decisions/chat",
                json={
                    "message": user_msg,
                    "session_id": username
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                imported_count += 1
            else:
                print(f"      ⚠️ 导入失败: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ 错误: {e}")
    
    print()
    print("=" * 70)
    print(f"✅ 导入完成: {imported_count}/{len(messages)} 条消息")
    print("=" * 70)
    print()
    
    if imported_count >= 5:
        print("✅ 消息数量充足，现在可以分析用户画像")
        print(f"   运行: python analyze_user.py {username}")
    else:
        print(f"⚠️ 消息数量不足（需要至少5条，当前{imported_count}条）")
    
    print()
    
    return imported_count > 0

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python import_chat_to_db.py <username>")
        print()
        print("示例:")
        print("  python import_chat_to_db.py bbb")
        sys.exit(1)
    
    username = sys.argv[1]
    
    print()
    print("⚠️ 注意: 这会重新发送用户的历史消息，可能会产生新的AI回复")
    print("         建议仅用于测试或数据迁移")
    print()
    input("按回车继续...")
    print()
    
    success = import_user_chat(username)
    sys.exit(0 if success else 1)




