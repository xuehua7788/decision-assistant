#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动检测并测试Render后台
"""

import requests
import json
import time

# 可能的Render URL（根据你的项目名）
POSSIBLE_URLS = [
    "https://decision-assistant-backend.onrender.com",
    "https://decision-assistant.onrender.com",
    "https://decision-assistant-githubv3.onrender.com",
]

def find_working_url():
    """自动查找可用的Render URL"""
    print("🔍 正在查找Render后台...")
    print()
    
    for url in POSSIBLE_URLS:
        try:
            print(f"   尝试: {url}")
            response = requests.get(f"{url}/health", timeout=5)
            if response.status_code == 200:
                print(f"   ✅ 找到: {url}")
                return url
        except:
            print(f"   ❌ 不可用")
    
    return None

def test_backend(base_url):
    """自动测试后端所有功能"""
    print("\n" + "=" * 70)
    print("Render后台自动测试")
    print("=" * 70)
    print(f"URL: {base_url}")
    print()
    
    results = {}
    
    # 测试1: 健康检查
    print("测试1: 健康检查")
    print("-" * 70)
    try:
        r = requests.get(f"{base_url}/health", timeout=10)
        if r.status_code == 200:
            print("   ✅ 后端运行正常")
            results['health'] = True
        else:
            print(f"   ❌ 状态码: {r.status_code}")
            results['health'] = False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        results['health'] = False
    
    # 测试2: 数据库状态
    print("\n测试2: 数据库连接")
    print("-" * 70)
    try:
        r = requests.get(f"{base_url}/api/database/test", timeout=10)
        if r.status_code == 200:
            data = r.json()
            db_available = data.get('database_available', False)
            if db_available:
                print("   ✅ 数据库已连接")
                results['database'] = True
            else:
                print("   ⚠️ 数据库未配置")
                results['database'] = False
        else:
            print(f"   ❌ 状态码: {r.status_code}")
            results['database'] = False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        results['database'] = False
    
    # 测试3: 用户画像API
    print("\n测试3: 用户画像API")
    print("-" * 70)
    try:
        r = requests.get(f"{base_url}/api/profile/stats", timeout=10)
        print(f"   状态码: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            stats = data.get('stats', {})
            print("   ✅ 用户画像API正常")
            print(f"      总用户画像: {stats.get('total_profiles', 0)}")
            print(f"      最近分析: {stats.get('recently_analyzed', 0)}")
            results['profile_api'] = True
        elif r.status_code == 500:
            print("   ⚠️ API存在但数据库表未创建")
            print("   需要在Render Shell运行: python backend/create_user_profile_tables.py")
            results['profile_api'] = False
        elif r.status_code == 404:
            print("   ❌ API路由未注册到app.py")
            results['profile_api'] = False
        else:
            print(f"   ❌ 未知错误")
            results['profile_api'] = False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        results['profile_api'] = False
    
    # 测试4: 现有用户数据
    print("\n测试4: 现有用户数据")
    print("-" * 70)
    try:
        r = requests.get(f"{base_url}/api/admin/chats", timeout=10)
        if r.status_code == 200:
            data = r.json()
            total = data.get('total_sessions', 0)
            print(f"   ✅ 找到 {total} 个用户会话")
            
            if total > 0:
                chats = data.get('chats', {})
                print(f"\n   用户列表（前5个）:")
                for username, info in list(chats.items())[:5]:
                    msg_count = info.get('total_messages', 0)
                    print(f"      - {username}: {msg_count} 条消息")
                results['has_users'] = True
                results['first_user'] = list(chats.keys())[0]
            else:
                print("   ℹ️ 暂无用户数据（用户聊天后会自动创建）")
                results['has_users'] = False
        else:
            print(f"   ❌ 状态码: {r.status_code}")
            results['has_users'] = False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        results['has_users'] = False
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    passed = sum(1 for k, v in results.items() if v is True and k != 'first_user')
    total = len([k for k in results.keys() if k != 'first_user'])
    
    print(f"\n通过: {passed}/{total}")
    print()
    
    for key, value in results.items():
        if key == 'first_user':
            continue
        status = "✅" if value else "❌"
        print(f"   {status} {key}")
    
    print()
    
    # 诊断和建议
    if results.get('health') and results.get('database'):
        if results.get('profile_api'):
            print("🎉 用户画像系统已在Render正常运行！")
            print()
            print("✅ 系统状态: 完全就绪")
            print()
            if results.get('has_users'):
                print(f"📊 可以开始分析用户画像")
                print(f"   第一个用户: {results.get('first_user')}")
                print()
                print("下一步:")
                print("1. 在Render Shell运行:")
                print(f"   python backend/scheduled_profile_analysis.py --user {results.get('first_user')}")
            else:
                print("ℹ️ 等待用户开始聊天...")
                print()
                print("用户聊天后会自动:")
                print("1. 保存聊天记录到数据库")
                print("2. 可以运行画像分析")
                print("3. 自动应用个性化策略")
        else:
            print("⚠️ 用户画像API未就绪")
            print()
            print("需要在Render Shell执行:")
            print("1. cd backend")
            print("2. python create_user_profile_tables.py")
            print()
            print("或者等待下次部署时自动创建")
    else:
        print("❌ 基础功能异常")
        print()
        if not results.get('health'):
            print("问题: 后端无法访问")
            print("解决: 检查Render服务是否运行")
        if not results.get('database'):
            print("问题: 数据库未连接")
            print("解决: 检查DATABASE_URL环境变量")
    
    return results

def main():
    print("=" * 70)
    print("Render后台自动检测和测试")
    print("=" * 70)
    print()
    
    # 查找可用URL
    base_url = find_working_url()
    
    if not base_url:
        print()
        print("❌ 无法找到可用的Render后台")
        print()
        print("请提供你的Render URL，或检查:")
        print("1. Render服务是否正在运行")
        print("2. 服务是否已部署成功")
        print("3. URL是否正确")
        return 1
    
    # 运行测试
    print()
    results = test_backend(base_url)
    
    return 0 if results.get('health') else 1

if __name__ == "__main__":
    import sys
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n测试被中断")
        sys.exit(1)

