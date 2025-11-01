#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render上的数据库同步状态
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

def test_db_sync():
    """测试数据库同步"""
    print("=" * 70)
    print("测试Render数据库同步状态")
    print("=" * 70)
    print()
    
    # 发送一条测试消息
    print("1. 发送测试消息...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/decisions/chat",
            json={
                "message": "这是测试消息，用于验证数据库同步",
                "session_id": "test_sync_user"
            },
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 200:
            print("   ✅ 消息发送成功")
        else:
            print(f"   ❌ 发送失败: {response.status_code}")
            return
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return
    
    print()
    
    # 尝试分析用户（会告诉我们数据库中有多少条消息）
    print("2. 检查数据库中的消息...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/profile/test_sync_user/analyze",
            json={},
            timeout=60
        )
        
        if response.status_code == 400:
            data = response.json()
            error = data.get('error', '')
            print(f"   状态: {error}")
            
            if '0 条' in error:
                print()
                print("   ❌ 数据库同步失败！")
                print()
                print("   可能原因:")
                print("   1. database_sync.py 导入失败")
                print("   2. USE_DATABASE 环境变量未设置")
                print("   3. DATABASE_URL 连接失败")
                print("   4. db_sync.is_available() 返回 False")
                print()
                print("   需要检查Render日志中的:")
                print("   • '✅ 数据库同步模块导入成功'")
                print("   • '✅ 数据库连接成功'")
                print("   • '✅ 消息同步到数据库'")
                
            elif '1 条' in error or '2 条' in error:
                print()
                print("   ✅ 数据库同步正常工作！")
                print("   新消息已成功同步到数据库")
                print()
                print("   bbb用户的旧消息丢失是因为:")
                print("   • Render重启清空了JSON文件")
                print("   • 旧消息是在数据库同步功能之前创建的")
                print()
                print("   解决方案:")
                print("   • 让bbb用户重新聊天（新消息会同步）")
                print("   • 或者从本地导入历史数据")
                
        elif response.status_code == 200:
            print("   ✅ 有足够的消息，分析成功")
        else:
            print(f"   ⚠️ 状态码: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    test_db_sync()






