#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试股票新闻API功能
"""

import os
import sys
import requests

# 设置环境变量
os.environ['ALPHA_VANTAGE_KEY'] = 'QKO2M2K3LZ58ACO2'
os.environ['DEEPSEEK_API_KEY'] = 'sk-d3196d8e68c44690998d79c715ce715d'

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("=" * 70)
print("📰 股票新闻API测试")
print("=" * 70)
print()

# 测试1: 直接测试Alpha Vantage客户端
print("【测试1】直接测试Alpha Vantage新闻客户端")
print("-" * 70)

try:
    from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
    
    client = get_alpha_vantage_client()
    print("✅ 客户端初始化成功")
    print()
    
    # 获取AAPL新闻
    print("📰 获取AAPL新闻...")
    news = client.get_news('AAPL', limit=3)
    
    if news:
        print(f"✅ 成功获取 {len(news)} 条新闻")
        print()
        
        for i, item in enumerate(news, 1):
            print(f"新闻 {i}:")
            print(f"  标题: {item['title']}")
            print(f"  摘要: {item['summary'][:100]}...")
            print(f"  时间: {item['time_published']}")
            print(f"  情绪: {item['sentiment']} ({item['sentiment_score']})")
            print()
    else:
        print("❌ 未获取到新闻")
        
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("【测试2】测试Flask API端点")
print("-" * 70)

# 测试2: 测试Flask API
API_URL = "http://127.0.0.1:8000"

try:
    print(f"📡 测试API: {API_URL}/api/stock/AAPL/news")
    
    response = requests.get(f"{API_URL}/api/stock/AAPL/news?limit=3", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        
        if data['status'] == 'success':
            news_list = data['news']
            print(f"✅ API调用成功，获取 {len(news_list)} 条新闻")
            print()
            
            for i, item in enumerate(news_list, 1):
                print(f"新闻 {i}:")
                print(f"  标题: {item['title']}")
                print(f"  时间: {item['time_published']}")
                print(f"  情绪: {item['sentiment']}")
                print()
        else:
            print(f"❌ API返回错误: {data.get('message')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("⚠️ 无法连接到后端服务器")
    print("   请确保后端正在运行: cd backend && python app.py")
except Exception as e:
    print(f"❌ 测试失败: {e}")

print()
print("=" * 70)
print("【测试3】测试完整流程（股票数据 + 新闻 + AI分析）")
print("-" * 70)

try:
    # 3.1 获取股票数据
    print("📊 1. 获取AAPL股票数据...")
    response = requests.get(f"{API_URL}/api/stock/AAPL", timeout=30)
    if response.status_code == 200:
        stock_data = response.json()
        if stock_data['status'] == 'success':
            price = stock_data['data']['quote']['price']
            print(f"✅ 当前价格: ${price}")
        else:
            print(f"❌ 获取失败: {stock_data.get('message')}")
    
    print()
    
    # 3.2 获取新闻
    print("📰 2. 获取AAPL新闻...")
    response = requests.get(f"{API_URL}/api/stock/AAPL/news?limit=2", timeout=30)
    if response.status_code == 200:
        news_data = response.json()
        if news_data['status'] == 'success':
            print(f"✅ 获取 {len(news_data['news'])} 条新闻")
            if news_data['news']:
                selected_news = news_data['news'][0]
                news_text = f"{selected_news['title']}\n\n{selected_news['summary']}"
                print(f"   选中新闻: {selected_news['title'][:50]}...")
        else:
            print(f"❌ 获取失败: {news_data.get('message')}")
            news_text = ""
    
    print()
    
    # 3.3 AI分析（带新闻和用户观点）
    print("🤖 3. AI分析（包含新闻和用户观点）...")
    analysis_payload = {
        "symbol": "AAPL",
        "risk_preference": "balanced",
        "news_context": news_text if 'news_text' in locals() else "",
        "user_opinion": "我认为苹果公司基本面良好，长期看好"
    }
    
    response = requests.post(
        f"{API_URL}/api/stock/analyze",
        json=analysis_payload,
        timeout=60
    )
    
    if response.status_code == 200:
        analysis_data = response.json()
        if analysis_data['status'] == 'success':
            analysis = analysis_data['analysis']
            print(f"✅ AI分析完成")
            print(f"   综合评分: {analysis['score']}")
            print(f"   操作建议: {analysis['recommendation']}")
            print(f"   建议仓位: {analysis['position_size']}")
            if 'strategy' in analysis:
                print(f"   投资策略: {analysis['strategy'][:100]}...")
        else:
            print(f"❌ 分析失败: {analysis_data.get('message')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("⚠️ 无法连接到后端服务器")
except Exception as e:
    print(f"❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

print()
print("=" * 70)
print("✅ 测试完成！")
print("=" * 70)
print()
print("💡 提示:")
print("   1. 如果测试1成功但测试2失败，请确保后端正在运行")
print("   2. 如果新闻获取失败，可能是API限制，请等待1分钟后重试")
print("   3. Alpha Vantage免费版每天25次请求，请合理使用")
print()

