#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试所有Profile API端点
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

def test_endpoints():
    """测试所有端点"""
    print("=" * 70)
    print("测试Profile API端点")
    print("=" * 70)
    print()
    
    endpoints = [
        ("GET", "/api/profile/stats", "统计信息"),
        ("GET", "/api/profile/bbb", "获取用户画像"),
        ("GET", "/api/profile/bbb/summary", "用户摘要"),
        ("POST", "/api/profile/bbb/analyze", "分析用户"),
        ("GET", "/api/profile/bbb/recommendations", "推荐策略"),
    ]
    
    for method, path, desc in endpoints:
        print(f"测试: {desc}")
        print(f"  {method} {path}")
        
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{path}", timeout=10)
            else:
                response = requests.post(f"{BASE_URL}{path}", json={}, timeout=10)
            
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                print(f"  ✅ 成功")
            elif response.status_code == 404:
                print(f"  ❌ 404 - API不存在")
            elif response.status_code == 400:
                data = response.json()
                print(f"  ⚠️ {data.get('error', '')[:50]}")
            else:
                print(f"  ⚠️ {response.status_code}")
                
        except Exception as e:
            print(f"  ❌ 错误: {e}")
        
        print()
    
    print("=" * 70)
    print("结论")
    print("=" * 70)
    print()
    print("如果所有端点都返回404:")
    print("  → profile_api_routes 没有注册到Flask app")
    print("  → 需要检查Render部署日志")
    print()
    print("如果返回400（聊天记录不足）:")
    print("  → API已注册，但数据库中没有聊天记录")
    print("  → 需要检查数据库同步逻辑")
    print()

if __name__ == "__main__":
    test_endpoints()





