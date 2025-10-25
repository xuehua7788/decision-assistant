#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render后台的用户画像API
"""

import requests
import json

# Render后台地址（请替换为你的实际地址）
BASE_URL = "https://your-app.onrender.com"

def test_profile_stats():
    """测试统计接口"""
    print("=" * 70)
    print("测试1: 获取用户画像统计")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/profile/stats"
        print(f"请求: GET {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_analyze_user(username):
    """测试用户画像分析"""
    print("\n" + "=" * 70)
    print(f"测试2: 分析用户 {username}")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/profile/{username}/analyze"
        print(f"请求: POST {url}")
        
        response = requests.post(
            url,
            json={"days": 30, "force": False},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功!")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return True
        elif response.status_code == 400:
            data = response.json()
            print(f"⚠️ {data.get('message', '数据不足')}")
            return False
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_get_profile(username):
    """测试获取用户画像"""
    print("\n" + "=" * 70)
    print(f"测试3: 获取用户画像 {username}")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/api/profile/{username}"
        print(f"请求: GET {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 成功!")
            
            # 只显示关键信息
            profile = data.get('profile', {})
            inv_pref = profile.get('investment_preferences', {})
            knowledge = profile.get('knowledge_level', {})
            
            print("\n关键信息:")
            print(f"  风险偏好: {inv_pref.get('risk_tolerance')}")
            print(f"  投资风格: {inv_pref.get('investment_style')}")
            print(f"  期权经验: {knowledge.get('option_experience')}")
            print(f"  分析时间: {profile.get('last_analyzed_at')}")
            print(f"  消息数量: {profile.get('total_messages_analyzed')}")
            return True
        elif response.status_code == 404:
            print("⚠️ 用户画像不存在")
            return False
        else:
            print(f"❌ 失败: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


def test_health_check():
    """测试后端健康状态"""
    print("=" * 70)
    print("测试0: 后端健康检查")
    print("=" * 70)
    
    try:
        url = f"{BASE_URL}/health"
        print(f"请求: GET {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 后端正常运行")
            return True
        else:
            print(f"❌ 后端异常: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ 无法连接后端: {e}")
        return False


if __name__ == "__main__":
    print("\n")
    print("=" * 70)
    print("Render后台用户画像API测试")
    print("=" * 70)
    print()
    
    # 提示用户输入URL
    print("请输入你的Render后台URL（例如: https://your-app.onrender.com）")
    print("或直接按回车使用默认值")
    user_input = input("URL: ").strip()
    
    if user_input:
        BASE_URL = user_input.rstrip('/')
    
    print(f"\n使用URL: {BASE_URL}")
    print()
    
    # 运行测试
    results = {}
    
    # 测试0: 健康检查
    results['health'] = test_health_check()
    
    if not results['health']:
        print("\n❌ 后端无法访问，请检查:")
        print("1. Render服务是否正在运行")
        print("2. URL是否正确")
        print("3. 网络连接是否正常")
        exit(1)
    
    # 测试1: 统计接口
    results['stats'] = test_profile_stats()
    
    # 测试2: 分析用户（如果有现有用户）
    print("\n")
    print("是否要测试用户画像分析？(需要有现有用户)")
    test_user = input("输入用户名（或按回车跳过）: ").strip()
    
    if test_user:
        results['analyze'] = test_analyze_user(test_user)
        if results['analyze']:
            results['get_profile'] = test_get_profile(test_user)
    
    # 总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v is True)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status}: {test_name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if results.get('stats'):
        print("\n🎉 用户画像系统已在Render后台正常运行！")
        print("\n下一步:")
        print("1. 用户开始聊天积累数据")
        print("2. 运行定时任务分析用户画像")
        print("3. 在聊天中自动应用个性化策略")
    else:
        print("\n⚠️ 部分测试失败，请检查:")
        print("1. 环境变量是否正确设置")
        print("2. 数据库表是否已创建")
        print("3. Render日志中是否有错误")

