#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试AI+算法集成功能
"""

import requests
import json

# 测试Render线上环境
API_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("🧪 测试 AI + 算法集成")
print("=" * 80)

# 测试1: 正常对话（不触发算法）
print("\n测试1: 正常对话...")
response = requests.post(f"{API_URL}/api/decisions/chat", json={
    "message": "你好，我想咨询一些买房的建议",
    "session_id": "test-ai-algo"
})

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"回复: {data['response'][:100]}...")
    print(f"是否使用算法: {data.get('algorithm_used', False)}")
    print("✅ 正常对话测试通过")
else:
    print(f"❌ 失败: {response.text}")

# 测试2: 触发算法分析
print("\n测试2: 触发算法分析...")
response = requests.post(f"{API_URL}/api/decisions/chat", json={
    "message": "我要买笔记本电脑，MacBook性能10分价格7分，ThinkPad性能8分价格9分，Dell性能7分价格9分",
    "session_id": "test-ai-algo"
})

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"回复: {data['response']}")
    print(f"是否使用算法: {data.get('algorithm_used', False)}")
    
    if data.get('algorithm_used'):
        print("✅ 算法集成测试通过！")
        if 'algorithm_result' in data:
            result = data['algorithm_result']
            print(f"   推荐: {result.get('recommendation')}")
            print(f"   得分: {result.get('scores')}")
    else:
        print("⚠️ 未触发算法（可能AI未识别）")
        print(f"   AI回复: {data['response'][:200]}")
else:
    print(f"❌ 失败: {response.text}")

# 测试3: 另一种表述方式
print("\n测试3: 不同的表述方式...")
response = requests.post(f"{API_URL}/api/decisions/chat", json={
    "message": "帮我选工作，公司A：薪资9分，发展8分，距离7分；公司B：薪资7分，发展9分，距离9分",
    "session_id": "test-ai-algo"
})

print(f"状态码: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    print(f"是否使用算法: {data.get('algorithm_used', False)}")
    print(f"回复: {data['response'][:150]}...")
    
    if data.get('algorithm_used'):
        print("✅ 多样化表述测试通过！")
    else:
        print("⚠️ 未触发算法")
else:
    print(f"❌ 失败: {response.text}")

print("\n" + "=" * 80)
print("测试完成！")
print("=" * 80)

