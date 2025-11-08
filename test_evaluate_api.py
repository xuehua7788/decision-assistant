#!/usr/bin/env python3
"""测试策略评估API"""
import requests
import json

BACKEND_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "="*80)
print("🧪 测试策略评估API")
print("="*80)

# 1. 测试健康检查
print("\n【1】健康检查")
try:
    response = requests.get(f"{BACKEND_URL}/health", timeout=5)
    print(f"✅ 后端状态: {response.status_code}")
except Exception as e:
    print(f"❌ 后端无响应: {e}")

# 2. 获取bbb的策略
print("\n【2】获取bbb的策略")
try:
    response = requests.get(f"{BACKEND_URL}/api/user/bbb/strategies", timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        strategies = data.get('strategies', [])
        print(f"✅ 找到 {len(strategies)} 个策略")
        
        if strategies:
            first_strategy = strategies[0]
            print(f"\n第一个策略:")
            print(f"   strategy_id: {first_strategy.get('strategy_id')}")
            print(f"   symbol: {first_strategy.get('symbol')}")
            print(f"   investment_style: {first_strategy.get('investment_style')}")
except Exception as e:
    print(f"❌ 错误: {e}")

# 3. 测试评估API（OPTIONS预检）
print("\n【3】测试OPTIONS预检请求")
try:
    response = requests.options(
        f"{BACKEND_URL}/api/strategy/evaluate",
        headers={
            "Origin": "https://decision-assistant-frontend-prod.vercel.app",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type"
        },
        timeout=10
    )
    print(f"状态码: {response.status_code}")
    print(f"CORS头:")
    for header, value in response.headers.items():
        if 'access-control' in header.lower():
            print(f"   {header}: {value}")
except Exception as e:
    print(f"❌ 错误: {e}")

# 4. 测试评估API（POST）
print("\n【4】测试POST评估请求")
try:
    # 使用第一个策略
    if strategies and len(strategies) > 0:
        test_strategy = strategies[0]
        
        payload = {
            "strategy_id": test_strategy.get('strategy_id'),
            "symbol": test_strategy.get('symbol'),
            "username": "bbb"
        }
        
        print(f"请求数据:")
        print(json.dumps(payload, indent=2))
        
        response = requests.post(
            f"{BACKEND_URL}/api/strategy/evaluate",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=15
        )
        
        print(f"\n状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ 评估成功!")
            
            evaluation = data.get('evaluation', {})
            print(f"\n评估结果:")
            print(f"   保存时价格: ${evaluation.get('saved_price', 0):.2f}")
            print(f"   当前价格: ${evaluation.get('current_price', 0):.2f}")
            print(f"   价格变化: {evaluation.get('price_change_pct', 0):.2f}%")
            print(f"   状态: {evaluation.get('status')}")
        else:
            print(f"❌ 失败: {response.text}")
    else:
        print("⚠️  没有策略可测试")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 5. 检查所有策略相关的路由
print("\n【5】检查所有可用的策略路由")
routes_to_test = [
    "/api/user/bbb/strategies",
    "/api/strategy/evaluate",
    "/api/user/save-strategy"
]

for route in routes_to_test:
    try:
        # 尝试OPTIONS
        response = requests.options(f"{BACKEND_URL}{route}", timeout=5)
        status = "✅" if response.status_code in [200, 204] else "❌"
        print(f"{status} {route} - OPTIONS: {response.status_code}")
    except Exception as e:
        print(f"❌ {route} - 无响应")

print("\n" + "="*80)
print("✅ 测试完成")
print("="*80)
print()


