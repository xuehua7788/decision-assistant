#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
直接测试Alpha Vantage API
"""

import requests
import time

API_KEY = "QKO2M2K3LZ58ACO2"
BASE_URL = "https://www.alphavantage.co/query"

def test_api_call(symbol):
    """测试单个API调用"""
    print(f"\n{'='*60}")
    print(f"测试 {symbol}")
    print('='*60)
    
    params = {
        'function': 'GLOBAL_QUOTE',
        'symbol': symbol,
        'apikey': API_KEY
    }
    
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"响应: {data}")
            
            if 'Note' in data:
                print(f"\n⚠️ API限制！")
                print(f"消息: {data['Note']}")
                return False
            elif 'Global Quote' in data:
                quote = data['Global Quote']
                if quote:
                    print(f"\n✅ 成功获取数据")
                    print(f"价格: ${quote.get('05. price', 'N/A')}")
                    return True
                else:
                    print(f"\n❌ 返回空数据")
                    return False
            else:
                print(f"\n❌ 未知响应格式")
                return False
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 Alpha Vantage API 直接测试")
    print("="*60)
    print(f"API Key: {API_KEY[:10]}...")
    
    symbols = ['AAPL', 'NVDA', 'TSLA', 'MSFT']
    
    for i, symbol in enumerate(symbols):
        if i > 0:
            print(f"\n⏳ 等待15秒避免API限制...")
            time.sleep(15)
        
        test_api_call(symbol)
    
    print("\n" + "="*60)
    print("测试完成")
    print("="*60)

if __name__ == "__main__":
    main()


