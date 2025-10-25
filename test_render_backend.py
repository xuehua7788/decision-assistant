#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动测试Render后台的用户画像系统
"""

import requests
import json
import sys

# 你的Render后台地址（从你之前的部署信息）
BASE_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 70)
print("Render后台用户画像系统测试")
print("=" * 70)
print(f"测试地址: {BASE_URL}")
print()

def test_1_health():
    """测试1: 后端健康检查"""
    print("测试1: 后端健康检查")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ 后端正常运行")
            return True
        else:
            print(f"   ❌ 后端异常")
            return False
    except Exception as e:
        print(f"   ❌ 连接失败: {e}")
        return False

def test_2_database():
    """测试2: 数据库连接"""
    print("\n测试2: 数据库连接测试")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/database/test", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ 数据库可用: {data.get('database_available')}")
            print(f"   DATABASE_URL: {data.get('environment_variables', {}).get('DATABASE_URL')}")
            return True
        else:
            print(f"   ❌ 测试失败")
            return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def test_3_profile_stats():
    """测试3: 用户画像统计接口"""
    print("\n测试3: 用户画像统计接口")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/profile/stats", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 接口正常")
            print(f"   总用户画像数: {data.get('stats', {}).get('total_profiles', 0)}")
            print(f"   最近分析: {data.get('stats', {}).get('recently_analyzed', 0)}")
            return True
        elif response.status_code == 500:
            print("   ⚠️ 接口存在但数据库表可能未创建")
            print("   需要运行: python backend/create_user_profile_tables.py")
            return False
        else:
            print(f"   ❌ 接口不可用")
            return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def test_4_admin_chats():
    """测试4: 查看现有聊天记录"""
    print("\n测试4: 查看现有聊天记录")
    print("-" * 70)
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/chats", timeout=10)
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            total = data.get('total_sessions', 0)
            print(f"   ✅ 找到 {total} 个用户会话")
            
            if total > 0:
                chats = data.get('chats', {})
                print(f"\n   用户列表:")
                for username, info in list(chats.items())[:5]:  # 只显示前5个
                    print(f"      - {username}: {info.get('total_messages', 0)} 条消息")
                
                # 返回第一个用户名用于后续测试
                return list(chats.keys())[0] if chats else None
            else:
                print("   ℹ️ 暂无用户数据")
                return None
        else:
            print(f"   ❌ 接口不可用")
            return None
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return None

def test_5_analyze_user(username):
    """测试5: 分析用户画像"""
    if not username:
        print("\n测试5: 跳过（无可用用户）")
        return False
    
    print(f"\n测试5: 分析用户画像 - {username}")
    print("-" * 70)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/profile/{username}/analyze",
            json={"days": 30, "force": False},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"   状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ 分析成功")
            
            profile = data.get('profile', {})
            inv_pref = profile.get('investment_preferences', {})
            knowledge = profile.get('knowledge_level', {})
            
            print(f"\n   用户画像:")
            print(f"      风险偏好: {inv_pref.get('risk_tolerance')}")
            print(f"      投资风格: {inv_pref.get('investment_style')}")
            print(f"      期权经验: {knowledge.get('option_experience')}")
            print(f"      分析消息数: {profile.get('metadata', {}).get('total_messages_analyzed')}")
            return True
        elif response.status_code == 400:
            data = response.json()
            print(f"   ⚠️ {data.get('message', '数据不足')}")
            return False
        else:
            print(f"   ❌ 分析失败")
            return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def main():
    results = {}
    test_username = None
    
    # 测试1: 健康检查
    results['health'] = test_1_health()
    if not results['health']:
        print("\n❌ 后端无法访问，请检查Render服务状态")
        return 1
    
    # 测试2: 数据库连接
    results['database'] = test_2_database()
    
    # 测试3: 用户画像统计
    results['profile_stats'] = test_3_profile_stats()
    
    # 测试4: 查看现有用户
    test_username = test_4_admin_chats()
    
    # 测试5: 分析用户（如果有用户）
    if test_username:
        results['analyze_user'] = test_5_analyze_user(test_username)
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅" if result else "❌"
        print(f"   {status} {test_name}")
    
    print(f"\n   通过: {passed}/{total}")
    print()
    
    # 建议
    if not results.get('profile_stats'):
        print("⚠️ 需要创建数据库表:")
        print("   1. 在Render Shell中运行:")
        print("      cd backend && python create_user_profile_tables.py")
        print()
    
    if results.get('health') and results.get('database'):
        print("✅ 基础功能正常")
        
        if test_username:
            print(f"✅ 找到用户数据，可以开始分析")
        else:
            print("ℹ️ 暂无用户数据，用户聊天后即可分析")
    
    return 0 if passed > 0 else 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)

