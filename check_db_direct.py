#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接通过API查询数据库中的消息数量
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

def check_db_messages(username):
    """查询数据库中的消息数量"""
    print("=" * 70)
    print(f"查询数据库中 {username} 的聊天记录")
    print("=" * 70)
    print()
    
    # 创建一个测试端点来查询数据库
    # 我们通过触发分析来看错误消息中的数量
    try:
        response = requests.get(
            f"{BASE_URL}/api/profile/analyze/{username}",
            params={"days": 30},
            timeout=60
        )
        
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 400:
            data = response.json()
            error = data.get('error', '')
            print(f"错误信息: {error}")
            print()
            
            # 从错误信息中提取消息数量
            if '聊天记录不足' in error and '条' in error:
                import re
                match = re.search(r'（(\d+) 条）', error)
                if match:
                    count = int(match.group(1))
                    print(f"📊 数据库中的消息数量: {count}")
                    print()
                    
                    if count == 0:
                        print("❌ 数据库中没有聊天记录")
                        print()
                        print("可能原因:")
                        print("1. save_chat_message 的数据库同步没有执行")
                        print("2. DB_SYNC_AVAILABLE 为 False")
                        print("3. db_sync.is_available() 返回 False")
                        print("4. 数据库连接失败但没有报错")
                        print()
                        print("建议:")
                        print("• 让用户在前端发送新消息")
                        print("• 检查Render日志中的数据库同步信息")
                    else:
                        print(f"✅ 有 {count} 条消息，但不足5条")
                        print(f"   还需要 {5 - count} 条消息")
        
        elif response.status_code == 200:
            print("✅ 分析成功！用户画像已生成")
            data = response.json()
            print()
            import json
            print(json.dumps(data, indent=2, ensure_ascii=False)[:500])
        
        else:
            print(f"❌ 未知错误: {response.text[:200]}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        username = "bbb"
    else:
        username = sys.argv[1]
    
    check_db_messages(username)





