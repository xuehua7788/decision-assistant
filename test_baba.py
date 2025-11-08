#!/usr/bin/env python3
"""测试BABA股票查询"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 60)
print("🧪 测试 BABA（阿里巴巴）")
print("=" * 60)

# Test 1: 获取BABA股票数据
print("\n1️⃣ 测试 GET /api/stock/BABA")
print("-" * 60)
try:
    response = requests.get(f"{RENDER_URL}/api/stock/BABA", timeout=20)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            quote = data['data']['quote']
            print(f"✅ 成功获取数据")
            print(f"   公司名: {quote.get('name', 'N/A')}")
            print(f"   当前价: ${quote.get('price', 0):.2f}")
            print(f"   涨跌幅: {quote.get('change_percent', 0):.2f}%")
        else:
            print(f"❌ 返回错误: {data}")
    elif response.status_code == 404:
        print(f"❌ 404 Not Found")
        print(f"响应: {response.text}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"响应: {response.text[:300]}")
except requests.Timeout:
    print("⏱️  请求超时")
except Exception as e:
    print(f"❌ 错误: {e}")

# Test 2: 搜索BABA
print("\n2️⃣ 测试搜索 'alibaba'")
print("-" * 60)
try:
    response = requests.get(
        f"{RENDER_URL}/api/stock/search",
        params={'keywords': 'alibaba'},
        timeout=15
    )
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            results = data.get('results', [])
            print(f"✅ 找到 {len(results)} 个结果")
            for i, r in enumerate(results[:5], 1):
                print(f"\n   [{i}] {r['symbol']}")
                print(f"       {r['name']}")
                print(f"       {r['region']}")
        else:
            print(f"⚠️  {data}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"响应: {response.text[:300]}")
except Exception as e:
    print(f"❌ 错误: {e}")

# Test 3: 测试AI分析
print("\n3️⃣ 测试 AI 分析 BABA")
print("-" * 60)
try:
    response = requests.post(
        f"{RENDER_URL}/api/stock/analyze",
        json={
            'symbol': 'BABA',
            'investment_style': 'buffett',
            'language': 'zh'
        },
        timeout=30
    )
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        if data.get('status') == 'success':
            print(f"✅ AI分析成功")
            analysis = data.get('analysis', {})
            print(f"   综合评分: {analysis.get('score', 'N/A')}")
            print(f"   推荐操作: {analysis.get('recommendation', 'N/A')}")
        else:
            print(f"❌ 分析失败: {data}")
    else:
        print(f"❌ HTTP {response.status_code}")
        print(f"响应: {response.text[:300]}")
except requests.Timeout:
    print("⏱️  请求超时（AI分析可能需要更长时间）")
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)


