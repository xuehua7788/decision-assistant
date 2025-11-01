#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试bbb用户的消息存储
"""

import requests
import time

BASE_URL = "https://decision-assistant-backend.onrender.com"

def send_and_check():
    """发送消息并检查"""
    print("=" * 70)
    print("快速测试bbb用户")
    print("=" * 70)
    print()
    
    # 测试消息
    messages = [
        "我想投资特斯拉",
        "有什么期权策略推荐？",
        "我看好特斯拉长期发展",
        "但担心短期波动"
    ]
    
    print("📤 发送测试消息...")
    print()
    
    for i, msg in enumerate(messages, 1):
        print(f"[{i}/4] {msg}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/decisions/chat",
                json={
                    "message": msg,
                    "session_id": "bbb"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                reply = data.get('response', '')[:60]
                print(f"    AI: {reply}...")
            else:
                print(f"    ❌ 错误: {response.status_code}")
                
        except Exception as e:
            print(f"    ❌ 异常: {e}")
        
        time.sleep(1)
    
    print()
    print("=" * 70)
    print("📊 检查消息数量")
    print("=" * 70)
    print()
    
    # 检查JSON中的消息
    print("1. JSON存储（通过/api/admin/chats）:")
    try:
        response = requests.get(f"{BASE_URL}/api/admin/chats/bbb", timeout=10)
        if response.status_code == 200:
            data = response.json()
            json_count = len(data.get('messages', []))
            print(f"   ✅ JSON中有 {json_count} 条消息")
        else:
            print(f"   ❌ 无法获取: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 检查数据库中的消息
    print("2. 数据库存储（通过/api/profile/analyze）:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/profile/bbb/analyze",
            json={},
            timeout=60
        )
        
        if response.status_code == 400:
            data = response.json()
            error = data.get('error', '')
            print(f"   状态: {error}")
            
            import re
            match = re.search(r'（(\d+) 条）', error)
            if match:
                db_count = int(match.group(1))
                print(f"   📊 数据库中有 {db_count} 条消息")
                
                if db_count == 0:
                    print()
                    print("   ❌ 数据库同步未工作")
                    print("   原因: USE_DATABASE 可能未设置为 true")
                elif db_count < json_count:
                    print()
                    print("   ⚠️ 数据库消息少于JSON")
                    print(f"   可能有 {json_count - db_count} 条消息未同步")
                else:
                    print()
                    print("   ✅ 数据库同步正常")
                    
        elif response.status_code == 200:
            print("   ✅ 消息充足，分析成功！")
            data = response.json()
            profile = data.get('profile', {})
            print()
            print("   用户画像摘要:")
            inv_pref = profile.get('investment_preferences', {})
            print(f"   • 风险偏好: {inv_pref.get('risk_tolerance', 'N/A')}")
            print(f"   • 投资风格: {inv_pref.get('investment_style', 'N/A')}")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    send_and_check()






