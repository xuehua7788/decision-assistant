#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
等待并验证API密钥更新
"""

import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"
EXPECTED_PREFIX = "OIYWUJE"
MAX_ATTEMPTS = 10

print("=" * 80)
print("等待Render服务重启并验证API密钥")
print("=" * 80)

for attempt in range(1, MAX_ATTEMPTS + 1):
    print(f"\n尝试 {attempt}/{MAX_ATTEMPTS}...")
    
    try:
        response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=10)
        
        if response.status_code == 200:
            health = response.json()
            actual_prefix = health.get('alpha_vantage_key_prefix', '')
            
            print(f"   当前API密钥前缀: {actual_prefix}")
            
            if actual_prefix == EXPECTED_PREFIX:
                print(f"\n✅ API密钥已成功更新！")
                print(f"   新密钥前缀: {actual_prefix}")
                
                # 测试股票数据
                print(f"\n🔍 测试获取股票数据...")
                stock_response = requests.get(f"{RENDER_URL}/api/stock/AAPL", timeout=15)
                
                if stock_response.status_code == 200:
                    data = stock_response.json()
                    if data.get('status') == 'success':
                        quote = data['data']
                        print(f"✅ 股票数据获取成功！")
                        print(f"   {quote['symbol']}: ${quote['price']} ({quote['change_percent']}%)")
                        break
                    else:
                        print(f"⚠️ API返回: {data.get('message')}")
                else:
                    print(f"⚠️ 状态码: {stock_response.status_code}")
                break
            else:
                print(f"   ⏳ 还是旧密钥，等待10秒...")
                time.sleep(10)
        else:
            print(f"   ⚠️ 健康检查失败: {response.status_code}")
            time.sleep(10)
            
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
        time.sleep(10)
else:
    print(f"\n❌ 超时：API密钥未更新")
    print(f"   请检查Render Dashboard环境变量设置")

print("\n" + "=" * 80)

