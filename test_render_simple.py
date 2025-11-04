#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单测试Render Premium功能
"""

import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def test():
    print("🧪 测试 Render Premium AI 分析\n")
    
    payload = {
        "symbol": "AAPL",
        "risk_preference": "balanced",
        "investment_style": "buffett",
        "user_opinion": "我看好苹果的AI战略",
        "language": "zh"
    }
    
    print("📤 发送AI分析请求...")
    print(f"   股票: {payload['symbol']}")
    print(f"   投资风格: {payload['investment_style']}")
    print()
    
    try:
        response = requests.post(
            f"{RENDER_URL}/api/stock/analyze",
            json=payload,
            timeout=60
        )
        
        print(f"📥 响应状态: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ 成功!")
            print(json.dumps(result, indent=2, ensure_ascii=False))
        else:
            print(f"\n❌ 失败:")
            print(response.text[:500])
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")

if __name__ == "__main__":
    test()

