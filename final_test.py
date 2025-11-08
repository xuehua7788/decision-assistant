#!/usr/bin/env python3
"""最终测试 - 2分钟后自动执行"""
import requests
import time

API_URL = "https://decision-assistant-b.onrender.com"

print("=" * 80)
print("⏳ 等待Render重新部署（120秒）...")
print("=" * 80)

for i in range(12, 0, -1):
    print(f"   {i*10} 秒...", flush=True)
    time.sleep(10)

print("\n" + "=" * 80)
print("🧪 开始最终测试")
print("=" * 80)

# 1. 健康检查
print("\n【1】健康检查")
try:
    r = requests.get(f"{API_URL}/api/health", timeout=10)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        print("✅ 后端正常")
    else:
        print(f"❌ 响应: {r.text[:100]}")
        print("\n⚠️  后端可能还在启动，请稍后再试")
        exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    exit(1)

# 2. 测试股票API
print("\n【2】测试股票API")
try:
    r = requests.get(f"{API_URL}/api/stock/AAPL", timeout=30)
    print(f"状态码: {r.status_code}")
    if r.status_code == 200:
        data = r.json()['data']
        print(f"✅ 股票数据正常")
        print(f"   价格: ${data['quote']['price']}")
    else:
        print(f"❌ 失败: {r.text[:100]}")
        exit(1)
except Exception as e:
    print(f"❌ 错误: {e}")
    exit(1)

# 3. 测试ML顾问API
print("\n【3】测试ML顾问API")
try:
    payload = {
        "user_id": "test_user",
        "symbol": "AAPL",
        "stock_data": data,
        "investment_style": "buffett",
        "user_opinion": "我看好苹果的AI战略",
        "news_context": "苹果发布新产品销量超预期"
    }
    
    r = requests.post(f"{API_URL}/api/ml/trading/advice", json=payload, timeout=30)
    print(f"状态码: {r.status_code}")
    
    if r.status_code == 200:
        result = r.json()
        if result.get('status') == 'success':
            advice = result['advice']
            print(f"\n✅✅✅ ML顾问测试成功！✅✅✅")
            print(f"\n{'='*60}")
            print(f"时机: {advice['timing_recommendation']}")
            print(f"信心: {advice['confidence']*100:.0f}%")
            print(f"建议价格: ${advice['suggested_price']:.2f}")
            print(f"价格区间: ${advice['price_range'][0]:.2f} - ${advice['price_range'][1]:.2f}")
            print(f"建议仓位: {advice['suggested_position']*100:.0f}%")
            print(f"风险评分: {advice['risk_score']*100:.0f}%")
            print(f"{'='*60}")
            print(f"\n💡 个性化建议:")
            for insight in advice['personalized_insights']:
                print(f"  • {insight}")
            print(f"\n🛡️ 风险提示:")
            for tip in advice['regret_prevention']:
                print(f"  • {tip}")
            print(f"\n{'='*60}")
            print("✅ 所有测试通过！ML顾问系统部署成功！")
            print("{'='*60}")
        else:
            print(f"❌ ML响应失败: {result.get('message')}")
    elif r.status_code == 503:
        print(f"⚠️  ML模块导入失败")
        print(f"响应: {r.text[:200]}")
    else:
        print(f"❌ HTTP错误: {r.status_code}")
        print(f"响应: {r.text[:200]}")
        
except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)


