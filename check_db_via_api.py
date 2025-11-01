#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过API查询数据库中的聊天记录
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

def check_db_messages(username):
    """查询数据库中用户的消息"""
    print("=" * 70)
    print(f"查询数据库中的聊天记录: {username}")
    print("=" * 70)
    print()
    
    try:
        # 调用profile API，它会从数据库读取
        response = requests.get(
            f"{BASE_URL}/api/profile/analyze/{username}",
            params={"days": 30},
            timeout=60
        )
        
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 分析成功！")
            print()
            print("用户画像:")
            print("-" * 70)
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
        elif response.status_code == 400:
            data = response.json()
            error = data.get('error', '')
            
            if '聊天记录不足' in error:
                print("❌ 数据库中没有足够的聊天记录")
                print()
                print("原因分析:")
                print("1. 用户的聊天记录在JSON文件中，但没有同步到数据库")
                print("2. 只有在 USE_DATABASE=true 之后的新消息才会同步")
                print("3. 旧消息（1-8条）不在数据库中")
                print()
                print("解决方案:")
                print("• 让用户继续聊天，新消息会自动同步到数据库")
                print("• 等待5条新消息后再分析")
            else:
                print(f"❌ 错误: {error}")
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text[:200])
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("使用方法: python check_db_via_api.py <username>")
        print()
        print("示例:")
        print("  python check_db_via_api.py bbb")
        sys.exit(1)
    
    username = sys.argv[1]
    check_db_messages(username)




