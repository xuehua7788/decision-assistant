#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地股票API
"""

import requests
import time

LOCAL_URL = "http://127.0.0.1:8000"

def test_routes():
    """测试所有路由"""
    print("\n" + "="*60)
    print("🔍 测试本地股票API")
    print("="*60)
    
    routes = [
        ("/api/stock/health", "GET"),
        ("/api/stock/AAPL", "GET"),
        ("/api/stock/trending", "GET"),
        ("/api/stock/AAPL/news", "GET"),
    ]
    
    for route, method in routes:
        url = f"{LOCAL_URL}{route}"
        try:
            if method == "GET":
                response = requests.get(url, timeout=10)
            
            status = "✅" if response.status_code == 200 else "❌"
            print(f"{status} {route:35s} -> {response.status_code}")
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    if 'status' in data:
                        print(f"   状态: {data.get('status')}")
                    if 'version' in data:
                        print(f"   版本: {data.get('version')}")
                except:
                    pass
        except Exception as e:
            print(f"❌ {route:35s} -> 错误: {e}")
        
        time.sleep(0.5)

if __name__ == "__main__":
    test_routes()


