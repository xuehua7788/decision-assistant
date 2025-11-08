#!/usr/bin/env python3
"""等待Render部署并测试修复"""

import requests
import time
import json

RENDER_URL = "https://decision-assistant-b.onrender.com"

print("=" * 80)
print("⏳ 等待Render部署并测试修复...")
print("=" * 80)

# 等待90秒让Render部署
print("\n等待90秒让Render完成部署...", flush=True)
for i in range(90, 0, -10):
    print(f"  还有 {i} 秒...", flush=True)
    time.sleep(10)

print("\n" + "=" * 80)
print("🧪 开始测试")
print("=" * 80)

# 1. 健康检查
print("\n【1】健康检查")
try:
    r = requests.get(f"{RENDER_URL}/api/health", timeout=30)
    print(f"✅ 后端状态: {r.status_code}")
except Exception as e:
    print(f"❌ 后端无响应: {e}")
    exit(1)

# 2. 获取bbb的策略
print("\n【2】获取bbb的策略")
try:
    r = requests.get(f"{RENDER_URL}/api/user/bbb/strategies", timeout=30)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        data = r.json()
        if data.get('status') == 'success' and data.get('strategies'):
            strategies = data['strategies']
            print(f"✅ 找到 {len(strategies)} 个策略\n")
            
            # 使用第一个策略进行测试
            test_strategy = strategies[0]
            print(f"测试策略:")
            print(f"   strategy_id: {test_strategy['strategy_id']}")
            print(f"   symbol: {test_strategy['symbol']}")
            print(f"   investment_style: {test_strategy.get('investment_style', 'N/A')}")
            
            # 3. 测试评估API
            print("\n【3】测试策略评估API")
            
            # 3.1 OPTIONS预检
            print("\n  [3.1] OPTIONS预检请求")
            r_options = requests.options(
                f"{RENDER_URL}/api/strategy/evaluate",
                headers={
                    'Origin': 'https://decision-assistant-frontend-prod.vercel.app',
                    'Access-Control-Request-Method': 'POST'
                },
                timeout=30
            )
            print(f"  状态码: {r_options.status_code}")
            if r_options.status_code == 200:
                print(f"  ✅ CORS配置正确")
            
            # 3.2 POST评估请求
            print("\n  [3.2] POST评估请求")
            eval_payload = {
                "strategy_id": test_strategy['strategy_id'],
                "symbol": test_strategy['symbol'],
                "username": "bbb"
            }
            print(f"  请求数据: {json.dumps(eval_payload, indent=2, ensure_ascii=False)}")
            
            r_eval = requests.post(
                f"{RENDER_URL}/api/strategy/evaluate",
                json=eval_payload,
                timeout=30
            )
            print(f"\n  状态码: {r_eval.status_code}")
            
            if r_eval.status_code == 200:
                result = r_eval.json()
                if result.get('status') == 'success':
                    print(f"  ✅ 评估成功！")
                    eval_data = result['evaluation']
                    print(f"\n  评估结果:")
                    print(f"    当前价格: ${eval_data.get('current_price', 'N/A')}")
                    print(f"    原始价格: ${eval_data.get('original_price', 'N/A')}")
                    print(f"    收益率: {eval_data.get('return_pct', 'N/A')}%")
                    print(f"    表现: {eval_data.get('performance', 'N/A')}")
                else:
                    print(f"  ❌ 评估失败: {result.get('message', 'Unknown error')}")
            else:
                print(f"  ❌ 请求失败: {r_eval.text}")
        else:
            print(f"❌ 没有找到策略")
    else:
        print(f"❌ 请求失败: {r.text}")
        
except Exception as e:
    print(f"❌ 测试出错: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("✅ 测试完成")
print("=" * 80)


