#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render上的Premium功能
"""

import requests
import json
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def test_render_premium():
    """测试Render上的Premium功能"""
    print("=" * 80)
    print("🌐 测试 Render Premium 功能")
    print(f"🔗 URL: {RENDER_URL}")
    print("=" * 80)
    print()
    
    # 1. 健康检查
    print("🏥 步骤1: 健康检查")
    print("-" * 80)
    try:
        response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=10)
        if response.status_code == 200:
            health = response.json()
            print(f"✅ 后端在线")
            print(f"   版本: {health.get('version', 'N/A')}")
            print(f"   Alpha Vantage: {'✅' if health.get('alpha_vantage_key_set') else '❌'}")
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ 无法连接: {e}")
        return
    print()
    
    # 2. 测试股票数据获取（会用到Premium的历史数据）
    print("📊 步骤2: 获取股票数据")
    print("-" * 80)
    try:
        symbol = "AAPL"
        response = requests.get(f"{RENDER_URL}/api/stock/{symbol}", timeout=15)
        if response.status_code == 200:
            stock_data = response.json()
            print(f"✅ 成功获取 {symbol} 数据")
            if 'data' in stock_data:
                current_price = stock_data['data'].get('price', stock_data['data'].get('current', {}).get('price', 0))
                change_pct = stock_data['data'].get('change_percent', stock_data['data'].get('current', {}).get('change_percent', 0))
                print(f"   当前价格: ${current_price:.2f}")
                print(f"   涨跌幅: {change_pct:.2f}%")
        else:
            print(f"❌ 获取失败: {response.status_code}")
            print(f"   {response.text}")
            return
    except Exception as e:
        print(f"❌ 错误: {e}")
        return
    print()
    
    # 3. 测试AI分析（会用到所有Premium数据）
    print("🤖 步骤3: AI分析 (含Premium数据)")
    print("-" * 80)
    print("⏳ 这可能需要10-15秒（正在获取Premium数据）...")
    
    try:
        payload = {
            "symbol": "AAPL",
            "risk_preference": "balanced",
            "investment_style": "buffett",
            "user_opinion": "我看好苹果的AI战略和Vision Pro产品线",
            "news_context": "",  # 留空，让后端自动获取
            "language": "zh"
        }
        
        response = requests.post(
            f"{RENDER_URL}/api/stock/analyze",
            json=payload,
            timeout=60  # AI分析需要更长时间
        )
        
        if response.status_code == 200:
            analysis = response.json()
            
            if analysis.get('status') == 'success':
                result = analysis['data']
                print("✅ AI分析成功")
                print()
                print("📋 分析结果:")
                print("-" * 80)
                print(f"📊 综合评分: {result['score']}/100")
                print(f"💡 投资建议: {result['recommendation']}")
                print(f"📈 建议仓位: {result['position_size']}")
                print(f"🎯 目标价格: ${result['target_price']:.2f}")
                print(f"⛔ 止损价格: ${result['stop_loss']:.2f}")
                print()
                
                print("🔍 分析要点:")
                for i, point in enumerate(result['key_points'], 1):
                    print(f"   {i}. {point}")
                print()
                
                print("📝 综合分析:")
                summary = result['analysis_summary']
                # 分行显示
                lines = summary.split('。')
                for line in lines:
                    if line.strip():
                        print(f"   {line.strip()}。")
                print()
                
                print("💼 投资策略:")
                strategy = result.get('strategy', 'N/A')
                lines = strategy.split('。')
                for line in lines:
                    if line.strip():
                        print(f"   {line.strip()}。")
                print()
                
                # 检查是否提到了Premium数据
                combined_text = f"{' '.join(result['key_points'])} {summary} {strategy}"
                
                print("✅ Premium数据验证:")
                print("-" * 80)
                
                checks = {
                    "基本面数据": ["市盈率", "ROE", "利润率", "P/E", "EPS"],
                    "技术指标": ["MACD", "布林带", "ATR", "超买", "超卖"],
                    "宏观经济": ["CPI", "通胀", "失业", "利率", "联邦"],
                    "新闻整合": ["新闻", "AI", "市场"],
                    "用户观点": ["Vision Pro", "AI战略", "观点", "看好"]
                }
                
                for category, keywords in checks.items():
                    found = any(kw in combined_text for kw in keywords)
                    print(f"   {'✅' if found else '⚠️'} {category}: {'已整合' if found else '未明确提及'}")
                
            else:
                print(f"❌ 分析失败: {analysis.get('message', 'Unknown error')}")
        else:
            print(f"❌ API调用失败: {response.status_code}")
            print(f"   {response.text[:200]}")
    
    except requests.Timeout:
        print("❌ 请求超时（可能是后端正在冷启动）")
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("✅ 测试完成")
    print("=" * 80)

if __name__ == "__main__":
    # 等待一会儿让Render部署
    print("⏳ 等待30秒让Render完成部署...")
    for i in range(30, 0, -1):
        print(f"\r   倒计时: {i}秒 ", end='', flush=True)
        time.sleep(1)
    print("\r   开始测试...      ")
    print()
    
    test_render_premium()

