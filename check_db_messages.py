#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接查询数据库中的聊天记录
"""

import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from database.connection import get_db_connection

def check_user_messages(username):
    """查询数据库中用户的消息数量"""
    print("=" * 70)
    print(f"查询数据库中的聊天记录: {username}")
    print("=" * 70)
    print()
    
    conn = get_db_connection()
    if not conn:
        print("❌ 无法连接数据库")
        return
    
    try:
        cursor = conn.cursor()
        
        # 1. 获取用户ID
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_row = cursor.fetchone()
        
        if not user_row:
            print(f"❌ 用户 '{username}' 不存在")
            cursor.close()
            conn.close()
            return
        
        user_id = user_row[0]
        print(f"✅ 用户ID: {user_id}")
        print()
        
        # 2. 查询聊天记录数量
        cursor.execute("""
            SELECT COUNT(*) 
            FROM chat_messages 
            WHERE user_id = %s
        """, (user_id,))
        
        count = cursor.fetchone()[0]
        print(f"📊 数据库中的消息数量: {count}")
        print()
        
        # 3. 查询最近的几条消息
        if count > 0:
            cursor.execute("""
                SELECT user_message, assistant_message, created_at
                FROM chat_messages
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT 5
            """, (user_id,))
            
            messages = cursor.fetchall()
            
            print("最近的5条消息:")
            print("-" * 70)
            for i, (user_msg, assistant_msg, created_at) in enumerate(messages, 1):
                print(f"{i}. 用户: {user_msg[:50]}...")
                print(f"   AI: {assistant_msg[:50]}...")
                print(f"   时间: {created_at}")
                print()
        else:
            print("⚠️ 数据库中没有聊天记录")
            print()
            print("可能原因:")
            print("1. 用户的聊天记录还在JSON文件中，没有同步到数据库")
            print("2. USE_DATABASE=true 是最近才设置的")
            print("3. 需要用户发送新消息来触发数据库同步")
            print()
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        if conn:
            conn.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python check_db_messages.py <username>")
        print()
        print("示例:")
        print("  python check_db_messages.py bbb")
        sys.exit(1)
    
    username = sys.argv[1]
    check_user_messages(username)




