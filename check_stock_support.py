#!/usr/bin/env python3
"""检查股票是否支持"""
import requests
import sys

def check_stock(symbol):
    """检查股票是否可以查询"""
    RENDER_URL = "https://decision-assistant-backend.onrender.com"
    
    print(f"\n🔍 检查股票: {symbol.upper()}")
    print("=" * 60)
    
    try:
        response = requests.get(f"{RENDER_URL}/api/stock/{symbol.upper()}", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('status') == 'success':
                quote = data['data']['quote']
                print(f"✅ 支持！")
                print(f"   公司名: {quote.get('name', 'N/A')}")
                print(f"   当前价: ${quote['price']:.2f}")
                print(f"   涨跌幅: {quote['change_percent']:.2f}%")
                return True
        elif response.status_code == 404:
            print(f"❌ 不支持或股票代码错误")
            print(f"   请检查股票代码是否正确")
        else:
            print(f"⚠️  API错误: {response.status_code}")
            
    except requests.Timeout:
        print(f"⏱️  请求超时（后端可能在冷启动）")
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        symbol = sys.argv[1]
        check_stock(symbol)
    else:
        print("=" * 60)
        print("📊 股票支持检查工具")
        print("=" * 60)
        print("\n用法: python check_stock_support.py SYMBOL")
        print("\n示例:")
        print("  python check_stock_support.py AAPL")
        print("  python check_stock_support.py TSLA")
        print("\n常见股票测试:")
        
        test_stocks = ["AAPL", "TSLA", "NVDA", "BABA", "JD"]
        for stock in test_stocks:
            check_stock(stock)

