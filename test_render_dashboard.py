#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render上的数据仪表盘API
"""

import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def test_render_dashboard():
    """测试Render上的数据仪表盘"""
    print("=" * 80)
    print("🌐 测试Render数据仪表盘API")
    print("=" * 80)
    print()
    
    symbol = "AAPL"
    
    print(f"📤 请求: GET {RENDER_URL}/api/stock/{symbol}")
    print("⏳ 等待响应（可能需要10-15秒获取Premium数据）...")
    print()
    
    try:
        response = requests.get(f"{RENDER_URL}/api/stock/{symbol}", timeout=30)
        
        print(f"📥 响应状态: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                stock_data = data['data']
                
                print("✅ 基础数据:")
                print(f"   股票: {stock_data['quote'].get('name', 'N/A')}")
                print(f"   价格: ${stock_data['quote']['price']:.2f}")
                print(f"   RSI: {stock_data['indicators']['rsi']:.2f}")
                print()
                
                # 检查premium_data
                premium_data = stock_data.get('premium_data')
                
                if premium_data:
                    print("✅ Premium数据结构:")
                    has_company = premium_data.get('company_overview') is not None
                    has_technical = premium_data.get('technical') and len(premium_data.get('technical', {})) > 0
                    has_economic = premium_data.get('economic') and len(premium_data.get('economic', {})) > 0
                    
                    print(f"   company_overview: {'✅' if has_company else '❌'}")
                    print(f"   technical: {'✅' if has_technical else '❌'}")
                    print(f"   economic: {'✅' if has_economic else '❌'}")
                    print()
                    
                    # 基本面
                    if has_company:
                        co = premium_data['company_overview']
                        print("📊 基本面数据:")
                        print(f"   公司名: {co.get('Name', 'N/A')}")
                        mc = co.get('MarketCapitalization', 'N/A')
                        if mc != 'N/A':
                            print(f"   市值: ${float(mc)/1e12:.2f}T")
                        print(f"   P/E: {co.get('PERatio', 'N/A')}")
                        print(f"   EPS: ${co.get('EPS', 'N/A')}")
                        roe = co.get('ReturnOnEquityTTM', 'N/A')
                        if roe != 'N/A':
                            print(f"   ROE: {float(roe)*100:.1f}%")
                        margin = co.get('ProfitMargin', 'N/A')
                        if margin != 'N/A':
                            print(f"   利润率: {float(margin)*100:.1f}%")
                        print()
                    
                    # 技术面
                    if has_technical:
                        tech = premium_data['technical']
                        print("📈 技术指标:")
                        print(f"   MACD值: {tech.get('macd_value', 'N/A')}")
                        print(f"   MACD信号: {tech.get('macd_signal', 'N/A')}")
                        print(f"   ATR: ${tech.get('atr', 'N/A')}")
                        print()
                    
                    # 宏观面
                    if has_economic:
                        econ = premium_data['economic']
                        print("🌍 宏观经济:")
                        print(f"   CPI: {econ.get('cpi', 'N/A')}")
                        print(f"   失业率: {econ.get('unemployment', 'N/A')}%")
                        print(f"   联邦利率: {econ.get('fed_rate', 'N/A')}%")
                        print()
                    
                    print("=" * 80)
                    if has_company and has_technical and has_economic:
                        print("✅ 所有Premium数据完整！前端数据仪表盘将正常显示")
                    else:
                        print("⚠️  部分Premium数据缺失，仪表盘可能部分显示")
                    print("=" * 80)
                    
                    # 保存完整JSON
                    with open('render_dashboard_response.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2, ensure_ascii=False)
                    print("\n💾 完整响应已保存到: render_dashboard_response.json")
                    print("\n🎨 现在可以查看前端UI效果！")
                    print(f"   前端URL: https://decision-assistant-three.vercel.app")
                    
                else:
                    print("❌ 没有premium_data！")
                    print("   Render可能还没更新代码，或Premium API调用失败")
            else:
                print(f"❌ API返回错误: {data.get('message', 'Unknown')}")
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(response.text[:500])
    
    except requests.Timeout:
        print("❌ 请求超时")
        print("   Render可能正在冷启动，请稍后重试")
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_render_dashboard()

