#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
诊断Render后端路由问题
"""

import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def test_all_routes():
    """测试所有可能的路由组合"""
    
    routes = [
        "/api/stock/health",
        "/api/stock/AAPL",
        "/api/stock/trending",
        "/api/stock/AAPL/news",
        "/stock/AAPL",  # 没有/api前缀
        "/AAPL",  # 只有symbol
    ]
    
    print("\n" + "="*60)
    print("🔍 测试所有路由")
    print("="*60)
    
    for route in routes:
        url = f"{RENDER_URL}{route}"
        try:
            response = requests.get(url, timeout=10)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {route:30s} -> {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'status' in data:
                        print(f"   响应: {data.get('status')}")
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ {route:30s} -> 错误: {e}")
    
    print("\n" + "="*60)
    print("🔍 检查Flask路由列表")
    print("="*60)
    print("尝试访问 /routes 端点...")
    
    try:
        # 有些Flask应用会暴露路由列表
        response = requests.get(f"{RENDER_URL}/routes", timeout=10)
        if response.status_code == 200:
            print("✅ 找到路由列表:")
            print(response.text[:500])
        else:
            print(f"❌ /routes 不可用 ({response.status_code})")
    except:
        print("❌ /routes 端点不存在")

if __name__ == "__main__":
    test_all_routes()

