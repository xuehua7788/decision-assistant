#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Alpha Vantage API密钥
"""

import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("测试 Alpha Vantage API 密钥")
print("=" * 80)

# 1. 检查健康状态
print("\n1️⃣ 检查后端健康状态...")
try:
    response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=10)
    
    if response.status_code == 200:
        health = response.json()
        print(f"✅ 后端正常运行")
        print(f"   API密钥前缀: {health.get('alpha_vantage_key_prefix', 'N/A')}")
        print(f"   API密钥已设置: {health.get('alpha_vantage_key_set', False)}")
        
        # 验证密钥前缀
        expected_prefix = "OIYWUJE"
        actual_prefix = health.get('alpha_vantage_key_prefix', '')
        
        if actual_prefix == expected_prefix:
            print(f"✅ API密钥已更新为新密钥")
        else:
            print(f"⚠️ API密钥可能未更新")
            print(f"   期望前缀: {expected_prefix}")
            print(f"   实际前缀: {actual_prefix}")
    else:
        print(f"❌ 健康检查失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# 2. 测试获取股票数据
print("\n2️⃣ 测试获取股票数据（AAPL）...")
try:
    response = requests.get(f"{RENDER_URL}/api/stock/AAPL", timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('status') == 'success':
            quote = data['data']
            print(f"✅ 股票数据获取成功")
            print(f"   股票: {quote.get('symbol')} - {quote.get('name')}")
            print(f"   价格: ${quote.get('price')}")
            print(f"   涨跌: {quote.get('change_percent')}%")
            print(f"\n🎉 Alpha Vantage API 工作正常！")
        else:
            print(f"⚠️ API返回错误: {data.get('message')}")
            
    elif response.status_code == 404:
        print(f"❌ 股票数据未找到（可能是API限制）")
    else:
        print(f"❌ 请求失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)
print("\n💡 提示:")
print("   如果API密钥前缀不是 'OIYWUJE'，请在Render Dashboard更新环境变量")
print("   路径: Dashboard → Backend Service → Environment → ALPHA_VANTAGE_KEY")

