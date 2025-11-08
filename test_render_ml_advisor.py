#!/usr/bin/env python3
"""
测试Render上的ML交易顾问API
"""

import requests
import json
import time

# Render API配置
API_URL = "https://decision-assistant-b.onrender.com"

def wait_for_deployment():
    """等待Render部署"""
    print("⏳ 等待Render部署（90秒）...")
    for i in range(90, 0, -10):
        print(f"   还有 {i} 秒...", flush=True)
        time.sleep(10)
    print("✅ 等待完成，开始测试\n")

def test_ml_advisor():
    """测试ML交易顾问"""
    
    print("=" * 80)
    print("🧪 测试Render上的ML交易顾问API")
    print("=" * 80)
    
    # 1. 健康检查
    print("\n【1】健康检查")
    try:
        r = requests.get(f"{API_URL}/api/health", timeout=30)
        print(f"✅ 后端状态: {r.status_code}")
    except Exception as e:
        print(f"❌ 后端无响应: {e}")
        return
    
    # 2. 获取股票数据
    print("\n【2】获取股票数据: AAPL")
    try:
        r = requests.get(f"{API_URL}/api/stock/AAPL", timeout=30)
        if r.status_code == 200:
            result = r.json()
            if result.get('status') == 'success':
                stock_data = result['data']
                print(f"✅ 股票数据获取成功")
                print(f"   价格: ${stock_data['quote']['price']}")
                print(f"   RSI: {stock_data['indicators']['rsi']:.2f}")
            else:
                print(f"❌ 获取失败: {result.get('message')}")
                return
        else:
            print(f"❌ HTTP错误: {r.status_code}")
            return
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    
    # 3. 测试ML顾问API
    print("\n【3】测试ML交易顾问")
    try:
        payload = {
            "user_id": "bbb",
            "symbol": "AAPL",
            "stock_data": stock_data,
            "investment_style": "buffett",
            "user_opinion": "我看好苹果公司的AI战略和Vision Pro产品线",
            "news_context": "苹果推出新款iPhone 16销量超预期，市场份额增长"
        }
        
        print(f"\n📤 发送请求...")
        r = requests.post(
            f"{API_URL}/api/ml/trading/advice",
            json=payload,
            timeout=30
        )
        
        print(f"📥 状态码: {r.status_code}")
        
        if r.status_code == 200:
            result = r.json()
            
            if result.get('status') == 'success':
                advice = result['advice']
                
                print(f"\n✅ ML建议生成成功！")
                print(f"\n" + "="*60)
                print(f"📊 交易建议")
                print(f"="*60)
                print(f"⏰ 时机: {advice['timing_recommendation']}")
                print(f"📊 信心: {advice['confidence']*100:.0f}%")
                print(f"💰 建议价格: ${advice['suggested_price']:.2f}")
                print(f"📍 价格区间: ${advice['price_range'][0]:.2f} - ${advice['price_range'][1]:.2f}")
                print(f"📦 建议仓位: {advice['suggested_position']*100:.0f}%")
                print(f"⚠️  风险评分: {advice['risk_score']*100:.0f}%")
                
                print(f"\n" + "="*60)
                print(f"💡 个性化建议")
                print(f"="*60)
                for insight in advice['personalized_insights']:
                    print(f"• {insight}")
                
                print(f"\n" + "="*60)
                print(f"🛡️ 风险提示")
                print(f"="*60)
                for prevention in advice['regret_prevention']:
                    print(f"• {prevention}")
                
                print(f"\n" + "="*60)
                print(f"📋 执行计划")
                print(f"="*60)
                plan = advice['execution_plan']['primary_strategy']
                print(f"动作: {plan['action']}")
                print(f"订单类型: {plan['order_type']}")
                print(f"目标价: ${plan['target_price']:.2f}")
                print(f"仓位: {plan['position_percent']:.0f}%")
                
                risk_mgmt = advice['execution_plan']['risk_management']
                print(f"\n止损: ${risk_mgmt['stop_loss']:.2f}")
                print(f"止盈: ${risk_mgmt['take_profit_levels'][0]:.2f} / ${risk_mgmt['take_profit_levels'][1]:.2f} / ${risk_mgmt['take_profit_levels'][2]:.2f}")
                
                print(f"\n" + "="*60)
                
            else:
                print(f"❌ 失败: {result.get('message')}")
        
        elif r.status_code == 503:
            print(f"⚠️  ML功能暂不可用（模块未加载）")
            print(f"   响应: {r.text[:200]}")
        else:
            print(f"❌ 请求失败: {r.status_code}")
            print(f"   响应: {r.text[:200]}")
    
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == '__main__':
    wait_for_deployment()
    test_ml_advisor()


