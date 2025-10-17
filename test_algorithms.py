#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试算法分析API
"""

import requests
import json

API_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("🧮 测试算法分析API")
print("=" * 80)

# 测试1: 列出所有算法
print("\n1. 列出所有可用算法...")
r = requests.get(f"{API_URL}/api/algorithms/list")
print(f"   状态码: {r.status_code}")

if r.status_code == 200:
    data = r.json()
    print(f"   可用算法数: {data['total']}")
    for algo in data['algorithms']:
        print(f"     - {algo['id']}: {algo['name']} (v{algo['version']})")
    print("   ✅ 算法列表获取成功")
else:
    print(f"   ❌ 失败: {r.text}")

# 测试2: 使用加权评分法
print("\n2. 测试加权评分法...")
test_data = {
    "algorithm_id": "weighted_scoring",
    "question": "选择哪款笔记本电脑？",
    "options": [
        {"name": "MacBook Pro", "价格": 7, "性能": 10, "便携性": 8, "续航": 9},
        {"name": "ThinkPad X1", "价格": 8, "性能": 8, "便携性": 9, "续航": 8},
        {"name": "Dell XPS 13", "价格": 9, "性能": 7, "便携性": 10, "续航": 7}
    ],
    "criteria": ["价格", "性能", "便携性", "续航"]
}

r = requests.post(f"{API_URL}/api/algorithms/analyze", json=test_data)
print(f"   状态码: {r.status_code}")

if r.status_code == 200:
    result = r.json()['result']
    print(f"   推荐: {result['recommendation']}")
    print(f"   得分:")
    for option, score in result['scores'].items():
        print(f"     - {option}: {score:.2f}")
    print("   ✅ 加权评分法测试成功")
else:
    print(f"   ❌ 失败: {r.text}")

# 测试3: 使用优劣势分析法
print("\n3. 测试优劣势分析法...")
test_data = {
    "algorithm_id": "pros_cons",
    "question": "远程工作 vs 办公室工作",
    "options": [
        {
            "name": "远程工作",
            "pros": ["灵活的工作时间", "节省通勤时间", "舒适的工作环境", "更好的工作生活平衡"],
            "cons": ["社交机会减少", "沟通成本增加"]
        },
        {
            "name": "办公室工作",
            "pros": ["面对面沟通", "团队协作更容易", "明确的工作边界"],
            "cons": ["通勤时间长", "固定的工作时间", "办公环境噪音"]
        }
    ]
}

r = requests.post(f"{API_URL}/api/algorithms/analyze", json=test_data)
print(f"   状态码: {r.status_code}")

if r.status_code == 200:
    result = r.json()['result']
    print(f"   推荐: {result['recommendation']}")
    print(f"   净得分:")
    for option, score in result['scores'].items():
        print(f"     - {option}: {score}")
    print("   ✅ 优劣势分析法测试成功")
else:
    print(f"   ❌ 失败: {r.text}")

# 测试4: 对比多个算法
print("\n4. 对比多个算法...")
test_data = {
    "question": "选择投资方案",
    "options": [
        {"name": "股票", "收益": 9, "风险": 8, "流动性": 10},
        {"name": "房产", "收益": 7, "风险": 5, "流动性": 3},
        {"name": "基金", "收益": 8, "风险": 6, "流动性": 8}
    ],
    "algorithms": ["weighted_scoring"]
}

r = requests.post(f"{API_URL}/api/algorithms/compare", json=test_data)
print(f"   状态码: {r.status_code}")

if r.status_code == 200:
    results = r.json()['results']
    print(f"   算法数: {len(results)}")
    for algo_id, result in results.items():
        if 'error' not in result:
            print(f"     - {algo_id}: 推荐 {result['recommendation']}")
    print("   ✅ 算法对比测试成功")
else:
    print(f"   ❌ 失败: {r.text}")

print("\n" + "=" * 80)
print("🎉 算法测试完成！")
print("=" * 80)

