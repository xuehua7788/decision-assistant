#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断Render数据库连接问题
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

def diagnose():
    """诊断数据库连接"""
    print("=" * 70)
    print("诊断Render数据库连接")
    print("=" * 70)
    print()
    
    # 1. 检查数据库状态API
    print("1. 检查数据库状态API...")
    try:
        response = requests.get(f"{BASE_URL}/api/db/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ API响应成功")
            print(f"   DATABASE_AVAILABLE: {data.get('database_available', False)}")
            print(f"   USE_DATABASE: {data.get('use_database', False)}")
            print(f"   DB_SYNC_AVAILABLE: {data.get('db_sync_available', False)}")
        elif response.status_code == 404:
            print(f"   ⚠️ API不存在（可能是旧版本代码）")
        else:
            print(f"   ⚠️ 状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 2. 检查数据库表是否存在
    print("2. 检查数据库表...")
    try:
        response = requests.get(f"{BASE_URL}/api/db/init/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get('tables', {})
            print(f"   ✅ 表状态:")
            for table, exists in tables.items():
                status = "✅" if exists else "❌"
                print(f"      {status} {table}")
        elif response.status_code == 404:
            print(f"   ⚠️ API不存在")
        else:
            print(f"   ⚠️ 状态码: {response.status_code}")
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    
    # 3. 尝试手动触发一次数据库同步测试
    print("3. 测试数据库写入...")
    print("   发送测试消息...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/decisions/chat",
            json={
                "message": "数据库连接测试",
                "session_id": "db_test_user"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print(f"   ✅ 消息发送成功")
            
            # 立即检查数据库
            print("   检查数据库中是否有记录...")
            response2 = requests.post(
                f"{BASE_URL}/api/profile/db_test_user/analyze",
                json={},
                timeout=60
            )
            
            if response2.status_code == 400:
                data = response2.json()
                error = data.get('error', '')
                
                import re
                match = re.search(r'（(\d+) 条）', error)
                if match:
                    count = int(match.group(1))
                    if count > 0:
                        print(f"   ✅ 数据库同步成功！有 {count} 条记录")
                    else:
                        print(f"   ❌ 数据库同步失败！仍然是 0 条")
                        print()
                        print("   可能原因:")
                        print("   • database_sync.py 导入失败")
                        print("   • psycopg2 连接失败但没有报错")
                        print("   • chat_messages 表不存在")
                        print("   • save_chat_message 中的同步代码没有执行")
        else:
            print(f"   ❌ 发送失败: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    print("=" * 70)
    print("建议")
    print("=" * 70)
    print()
    print("如果数据库同步失败，需要:")
    print("1. 查看Render部署日志，搜索:")
    print("   • '✅ 数据库同步模块导入成功'")
    print("   • '✅ 数据库连接成功'")
    print("   • '❌ 数据库连接失败'")
    print()
    print("2. 如果看到连接失败，检查:")
    print("   • DATABASE_URL 格式是否正确")
    print("   • PostgreSQL 服务是否运行")
    print()
    print("3. 如果导入失败，检查:")
    print("   • psycopg2 是否在 requirements.txt 中")
    print("   • Render 构建日志是否有错误")
    print()

if __name__ == "__main__":
    diagnose()






