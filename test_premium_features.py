#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Alpha Vantage Premium功能
"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stock_analysis.alpha_vantage_client import get_alpha_vantage_client

def test_premium_features():
    """测试Premium功能"""
    print("=" * 80)
    print("🧪 测试 Alpha Vantage Premium 功能")
    print("=" * 80)
    print()
    
    client = get_alpha_vantage_client()
    symbol = "AAPL"
    
    # 1. 测试公司基本面
    print("📊 测试1: 公司基本面数据")
    print("-" * 80)
    company_overview = client.get_company_overview(symbol)
    if company_overview:
        print(f"✅ 成功获取 {symbol} 公司数据")
        print(f"   公司名: {company_overview.get('Name', 'N/A')}")
        print(f"   市值: ${company_overview.get('MarketCapitalization', 'N/A')}")
        print(f"   市盈率: {company_overview.get('PERatio', 'N/A')}")
        print(f"   每股收益(EPS): ${company_overview.get('EPS', 'N/A')}")
        print(f"   ROE: {company_overview.get('ReturnOnEquityTTM', 'N/A')}")
        print(f"   利润率: {company_overview.get('ProfitMargin', 'N/A')}")
    else:
        print(f"❌ 未能获取公司数据")
    print()
    
    # 2. 测试MACD
    print("📈 测试2: MACD指标")
    print("-" * 80)
    macd_data = client.get_technical_indicator(symbol, 'MACD', interval='daily')
    if macd_data and 'Technical Analysis: MACD' in macd_data:
        print(f"✅ 成功获取 {symbol} MACD数据")
        latest_date = list(macd_data['Technical Analysis: MACD'].keys())[0]
        latest_macd = macd_data['Technical Analysis: MACD'][latest_date]
        print(f"   日期: {latest_date}")
        print(f"   MACD: {latest_macd.get('MACD', 'N/A')}")
        print(f"   MACD信号线: {latest_macd.get('MACD_Signal', 'N/A')}")
        print(f"   MACD柱状图: {latest_macd.get('MACD_Hist', 'N/A')}")
    else:
        print(f"❌ 未能获取MACD数据")
        if macd_data:
            print(f"   响应: {macd_data}")
    print()
    
    # 3. 测试布林带
    print("📉 测试3: 布林带指标")
    print("-" * 80)
    bbands_data = client.get_technical_indicator(symbol, 'BBANDS', interval='daily', time_period=20)
    if bbands_data and 'Technical Analysis: BBANDS' in bbands_data:
        print(f"✅ 成功获取 {symbol} 布林带数据")
        latest_date = list(bbands_data['Technical Analysis: BBANDS'].keys())[0]
        latest_bb = bbands_data['Technical Analysis: BBANDS'][latest_date]
        print(f"   日期: {latest_date}")
        print(f"   上轨: ${latest_bb.get('Real Upper Band', 'N/A')}")
        print(f"   中轨: ${latest_bb.get('Real Middle Band', 'N/A')}")
        print(f"   下轨: ${latest_bb.get('Real Lower Band', 'N/A')}")
    else:
        print(f"❌ 未能获取布林带数据")
    print()
    
    # 4. 测试ATR
    print("📊 测试4: ATR指标")
    print("-" * 80)
    atr_data = client.get_technical_indicator(symbol, 'ATR', interval='daily', time_period=14)
    if atr_data and 'Technical Analysis: ATR' in atr_data:
        print(f"✅ 成功获取 {symbol} ATR数据")
        latest_date = list(atr_data['Technical Analysis: ATR'].keys())[0]
        latest_atr = atr_data['Technical Analysis: ATR'][latest_date]
        print(f"   日期: {latest_date}")
        print(f"   ATR(14): ${latest_atr.get('ATR', 'N/A')}")
    else:
        print(f"❌ 未能获取ATR数据")
    print()
    
    # 5. 测试CPI
    print("🌍 测试5: CPI经济指标")
    print("-" * 80)
    cpi_data = client.get_economic_indicator('CPI')
    if cpi_data and 'data' in cpi_data:
        print(f"✅ 成功获取CPI数据")
        if len(cpi_data['data']) > 0:
            latest_cpi = cpi_data['data'][0]
            print(f"   日期: {latest_cpi.get('date', 'N/A')}")
            print(f"   CPI值: {latest_cpi.get('value', 'N/A')}")
    else:
        print(f"❌ 未能获取CPI数据")
        if cpi_data:
            print(f"   响应: {list(cpi_data.keys())}")
    print()
    
    # 6. 测试失业率
    print("💼 测试6: 失业率")
    print("-" * 80)
    unemployment_data = client.get_economic_indicator('UNEMPLOYMENT')
    if unemployment_data and 'data' in unemployment_data:
        print(f"✅ 成功获取失业率数据")
        if len(unemployment_data['data']) > 0:
            latest_unemployment = unemployment_data['data'][0]
            print(f"   日期: {latest_unemployment.get('date', 'N/A')}")
            print(f"   失业率: {latest_unemployment.get('value', 'N/A')}%")
    else:
        print(f"❌ 未能获取失业率数据")
    print()
    
    # 7. 测试联邦利率
    print("💵 测试7: 联邦基金利率")
    print("-" * 80)
    fed_rate_data = client.get_economic_indicator('FEDERAL_FUNDS_RATE')
    if fed_rate_data and 'data' in fed_rate_data:
        print(f"✅ 成功获取联邦利率数据")
        if len(fed_rate_data['data']) > 0:
            latest_fed_rate = fed_rate_data['data'][0]
            print(f"   日期: {latest_fed_rate.get('date', 'N/A')}")
            print(f"   利率: {latest_fed_rate.get('value', 'N/A')}%")
    else:
        print(f"❌ 未能获取联邦利率数据")
    print()
    
    print("=" * 80)
    print("✅ Premium功能测试完成")
    print("=" * 80)

if __name__ == "__main__":
    try:
        test_premium_features()
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

