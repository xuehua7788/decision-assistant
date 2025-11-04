#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试本地策略API
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

print("=" * 60)
print("测试本地策略API")
print("=" * 60)

# 1. 测试健康检查
print("\n1️⃣ 测试健康检查...")
try:
    response = requests.get(f"{BASE_URL}/api/stock/health", timeout=5)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        print(f"   ✅ 后端正常运行")
    else:
        print(f"   ❌ 后端异常")
        exit(1)
except Exception as e:
    print(f"   ❌ 后端未运行: {e}")
    print("\n请先启动后端: cd backend && python app.py")
    exit(1)

# 2. 测试策略列表API
print("\n2️⃣ 测试策略列表API...")
try:
    response = requests.get(f"{BASE_URL}/api/strategy/list", timeout=5)
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ API正常工作")
        print(f"   策略数量: {result.get('count', 0)}")
    else:
        print(f"   ❌ API返回错误: {response.status_code}")
        print(f"   响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

# 3. 测试保存策略API
print("\n3️⃣ 测试保存策略API...")
try:
    test_data = {
        "symbol": "TEST",
        "company_name": "Test Company",
        "investment_style": "buffett",
        "recommendation": "买入",
        "target_price": 100.0,
        "stop_loss": 90.0,
        "position_size": "15%",
        "score": 75,
        "strategy_text": "测试策略",
        "analysis_summary": "测试分析",
        "current_price": 95.0,
        "option_strategy": {
            "success": True,
            "strategy": {
                "type": "long_call",
                "name": "买入看涨期权",
                "parameters": {
                    "current_price": 95.0,
                    "buy_strike": 100.0,
                    "premium_paid": 3.0
                }
            }
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/api/strategy/save",
        json=test_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    print(f"   状态码: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ 保存成功")
        print(f"   策略ID: {result.get('strategy_id')}")
    else:
        print(f"   ❌ 保存失败")
        print(f"   响应: {response.text[:200]}")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

# 4. 再次检查列表
print("\n4️⃣ 再次检查策略列表...")
try:
    response = requests.get(f"{BASE_URL}/api/strategy/list", timeout=5)
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ 当前策略数量: {result.get('count', 0)}")
        
        # 显示最新的策略
        strategies = result.get('strategies', [])
        if strategies:
            latest = strategies[0]
            print(f"\n   最新策略:")
            print(f"   - 股票: {latest['symbol']}")
            print(f"   - 推荐: {latest['recommendation']}")
            if latest.get('option_strategy'):
                print(f"   - 期权策略: 已保存 ✅")
            else:
                print(f"   - 期权策略: 未保存 ❌")
except Exception as e:
    print(f"   ❌ 请求失败: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)

