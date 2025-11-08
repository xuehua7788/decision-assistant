#!/usr/bin/env python3
"""快速测试ML顾问"""
import requests

API_URL = "https://decision-assistant-b.onrender.com"

print("测试ML顾问API...")

# 1. 获取AAPL数据
print("\n1. 获取股票数据...")
r = requests.get(f"{API_URL}/api/stock/AAPL", timeout=30)
if r.status_code == 200:
    stock_data = r.json()['data']
    print(f"✅ 价格: ${stock_data['quote']['price']}")
    
    # 2. 测试ML顾问
    print("\n2. 测试ML顾问...")
    ml_r = requests.post(
        f"{API_URL}/api/ml/trading/advice",
        json={
            "user_id": "bbb",
            "symbol": "AAPL",
            "stock_data": stock_data,
            "investment_style": "buffett",
            "user_opinion": "我看好苹果",
            "news_context": "苹果新产品发布"
        },
        timeout=30
    )
    
    print(f"状态码: {ml_r.status_code}")
    
    if ml_r.status_code == 200:
        advice = ml_r.json()['advice']
        print(f"\n✅ ML建议成功！")
        print(f"时机: {advice['timing_recommendation']}")
        print(f"信心: {advice['confidence']*100:.0f}%")
        print(f"建议价格: ${advice['suggested_price']:.2f}")
        print(f"建议仓位: {advice['suggested_position']*100:.0f}%")
    elif ml_r.status_code == 503:
        print(f"⚠️  ML模块未加载")
    else:
        print(f"❌ 错误: {ml_r.text[:200]}")
else:
    print(f"❌ 股票数据获取失败: {r.status_code}")


