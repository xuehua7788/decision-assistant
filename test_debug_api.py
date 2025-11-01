#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试调试API
"""

import requests
import time
import json

BASE_URL = "https://decision-assistant-backend.onrender.com"

def wait_and_test():
    """等待部署完成并测试"""
    print("=" * 70)
    print("等待Render部署...")
    print("=" * 70)
    print()
    
    max_attempts = 30
    for attempt in range(1, max_attempts + 1):
        print(f"[{attempt}/{max_attempts}] 检查调试API...", end=" ")
        
        try:
            response = requests.get(
                f"{BASE_URL}/api/debug/db-sync-status",
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ API已就绪！")
                print()
                print("=" * 70)
                print("数据库同步状态")
                print("=" * 70)
                print()
                
                data = response.json()
                print(json.dumps(data, indent=2, ensure_ascii=False))
                print()
                
                # 分析结果
                print("=" * 70)
                print("分析")
                print("=" * 70)
                print()
                
                if data.get('db_sync_available'):
                    print("✅ DB_SYNC_AVAILABLE = True")
                else:
                    print("❌ DB_SYNC_AVAILABLE = False")
                
                if data.get('db_connection_available'):
                    print("✅ 数据库连接可用")
                    
                    total = data.get('total_messages_in_db', 0)
                    bbb = data.get('bbb_messages_in_db', 0)
                    
                    print(f"📊 数据库中总消息数: {total}")
                    print(f"📊 bbb用户消息数: {bbb}")
                    print()
                    
                    if bbb == 0:
                        print("❌ bbb用户消息为0！")
                        print()
                        print("问题确认:")
                        print("• 数据库连接正常")
                        print("• 但消息没有同步")
                        print()
                        print("可能原因:")
                        print("1. save_chat_message 中 db_sync.is_available() 返回False")
                        print("2. sync_chat_message 执行时抛出异常")
                        print("3. chat_sessions 或 chat_messages 表不存在")
                    else:
                        print(f"✅ bbb用户有 {bbb} 条消息！")
                        print("数据库同步正常工作！")
                else:
                    print("❌ 数据库连接不可用")
                    
                    if 'db_query_error' in data:
                        print(f"错误: {data['db_query_error']}")
                
                return True
                
            elif response.status_code == 404:
                print("⚠️ API不存在（旧版本）")
            else:
                print(f"⚠️ 状态码: {response.status_code}")
                
        except requests.exceptions.Timeout:
            print("⏱️ 超时")
        except requests.exceptions.ConnectionError:
            print("🔄 连接失败")
        except Exception as e:
            print(f"⚠️ {e}")
        
        if attempt < max_attempts:
            time.sleep(10)
    
    print()
    print("⚠️ 超时：部署时间超过预期")
    return False

if __name__ == "__main__":
    print()
    wait_and_test()







