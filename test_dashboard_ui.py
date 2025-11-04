#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据仪表盘API
"""

import requests
import json

# 测试本地
BACKEND_URL = "http://localhost:5000"

def test_stock_data_with_premium():
    """测试股票数据API是否返回premium_data"""
    print("=" * 80)
    print("📊 测试股票数据API（含Premium数据）")
    print("=" * 80)
    print()
    
    symbol = "AAPL"
    
    print(f"📤 请求: GET {BACKEND_URL}/api/stock/{symbol}")
    print()
    
    try:
        response = requests.get(f"{BACKEND_URL}/api/stock/{symbol}", timeout=30)
        
        print(f"📥 响应状态: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                stock_data = data['data']
                
                print("✅ 基础数据:")
                print(f"   股票: {stock_data['quote']['name']}")
                print(f"   价格: ${stock_data['quote']['price']:.2f}")
                print(f"   RSI: {stock_data['indicators']['rsi']:.2f}")
                print()
                
                # 检查premium_data
                premium_data = stock_data.get('premium_data')
                
                if premium_data:
                    print("✅ Premium数据结构:")
                    print(f"   company_overview: {'✅' if premium_data.get('company_overview') else '❌'}")
                    print(f"   technical: {'✅' if premium_data.get('technical') else '❌'}")
                    print(f"   economic: {'✅' if premium_data.get('economic') else '❌'}")
                    print()
                    
                    # 基本面
                    if premium_data.get('company_overview'):
                        co = premium_data['company_overview']
                        print("📊 基本面数据:")
                        print(f"   公司名: {co.get('Name', 'N/A')}")
                        print(f"   市值: {co.get('MarketCapitalization', 'N/A')}")
                        print(f"   P/E: {co.get('PERatio', 'N/A')}")
                        print(f"   EPS: {co.get('EPS', 'N/A')}")
                        print(f"   ROE: {co.get('ReturnOnEquityTTM', 'N/A')}")
                        print(f"   利润率: {co.get('ProfitMargin', 'N/A')}")
                        print()
                    
                    # 技术面
                    if premium_data.get('technical'):
                        tech = premium_data['technical']
                        print("📈 技术指标:")
                        print(f"   MACD值: {tech.get('macd_value', 'N/A')}")
                        print(f"   MACD信号: {tech.get('macd_signal', 'N/A')}")
                        print(f"   ATR: {tech.get('atr', 'N/A')}")
                        print()
                    
                    # 宏观面
                    if premium_data.get('economic'):
                        econ = premium_data['economic']
                        print("🌍 宏观经济:")
                        print(f"   CPI: {econ.get('cpi', 'N/A')}")
                        print(f"   失业率: {econ.get('unemployment', 'N/A')}")
                        print(f"   联邦利率: {econ.get('fed_rate', 'N/A')}")
                        print()
                    
                    print("=" * 80)
                    print("✅ 数据结构完整！前端可以正常显示数据仪表盘")
                    print("=" * 80)
                    
                    # 保存完整JSON供前端参考
                    with open('test_dashboard_response.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print("\n💾 完整响应已保存到: test_dashboard_response.json")
                    
                else:
                    print("❌ 没有premium_data！")
                    print("   后端可能没有获取到Premium数据")
            else:
                print(f"❌ API返回错误: {data.get('message', 'Unknown')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text[:500])
    
    except requests.ConnectionError:
        print("❌ 无法连接到后端")
        print("   请确保后端正在运行: python backend/app.py")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_stock_data_with_premium()

