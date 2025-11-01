#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的股票分析流程：新闻 + AI分析 + 期权策略
"""

import os
import sys
import requests
import json

# 设置环境变量
os.environ['ALPHA_VANTAGE_KEY'] = 'QKO2M2K3LZ58ACO2'
os.environ['DEEPSEEK_API_KEY'] = 'sk-d3196d8e68c44690998d79c715ce715d'

print("=" * 70)
print("🧪 完整流程测试：股票分析 + 新闻 + 期权策略")
print("=" * 70)
print()

API_URL = "http://127.0.0.1:8000"

try:
    # 步骤1：获取股票数据
    print("【步骤1】获取AAPL股票数据")
    print("-" * 70)
    
    response = requests.get(f"{API_URL}/api/stock/AAPL", timeout=30)
    if response.status_code == 200:
        stock_data = response.json()
        if stock_data['status'] == 'success':
            quote = stock_data['data']['quote']
            print(f"✅ 股票: {quote['name']}")
            print(f"   价格: ${quote['price']}")
            print(f"   涨跌: {quote['change_percent']:.2f}%")
            print(f"   RSI: {stock_data['data']['indicators']['rsi']:.2f}")
            if 'volatility' in stock_data['data']['indicators']:
                print(f"   波动率: {stock_data['data']['indicators']['volatility']:.2f}%")
        else:
            print(f"❌ 失败: {stock_data.get('message')}")
            sys.exit(1)
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        sys.exit(1)
    
    print()
    
    # 步骤2：获取新闻
    print("【步骤2】获取AAPL相关新闻")
    print("-" * 70)
    
    response = requests.get(f"{API_URL}/api/stock/AAPL/news?limit=3", timeout=30)
    if response.status_code == 200:
        news_data = response.json()
        if news_data['status'] == 'success':
            news_list = news_data['news']
            print(f"✅ 获取到 {len(news_list)} 条新闻")
            
            if news_list:
                # 选择第一条新闻
                selected_news = news_list[0]
                print(f"\n📰 选中新闻:")
                print(f"   标题: {selected_news['title'][:60]}...")
                print(f"   情绪: {selected_news['sentiment']} ({selected_news['sentiment_score']})")
                print(f"   时间: {selected_news['time_published']}")
                
                news_text = f"{selected_news['title']}\n\n{selected_news['summary']}"
            else:
                print("⚠️ 未获取到新闻，使用模拟新闻")
                news_text = "苹果公司发布新款iPhone，市场反应积极，预计销量将创新高。"
        else:
            print(f"❌ 失败: {news_data.get('message')}")
            news_text = ""
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        news_text = ""
    
    print()
    
    # 步骤3：AI综合分析（包含新闻和用户观点）
    print("【步骤3】AI综合分析（技术指标 + 新闻 + 用户观点）")
    print("-" * 70)
    
    analysis_payload = {
        "symbol": "AAPL",
        "risk_preference": "balanced",
        "news_context": news_text,
        "user_opinion": "我认为苹果公司基本面良好，技术创新能力强，长期看好"
    }
    
    print(f"📤 发送分析请求...")
    print(f"   包含新闻: {'是' if news_text else '否'}")
    print(f"   包含观点: 是")
    print()
    
    response = requests.post(
        f"{API_URL}/api/stock/analyze",
        json=analysis_payload,
        timeout=60
    )
    
    if response.status_code == 200:
        analysis_data = response.json()
        if analysis_data['status'] == 'success':
            analysis = analysis_data['analysis']
            
            print("✅ AI分析完成")
            print()
            print("📊 分析结果:")
            print(f"   综合评分: {analysis['score']}/100")
            print(f"   操作建议: {analysis['recommendation']}")
            print(f"   建议仓位: {analysis['position_size']}")
            print(f"   目标价: ${analysis['target_price']}")
            print(f"   止损价: ${analysis['stop_loss']}")
            
            if 'market_direction' in analysis:
                direction_map = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '震荡'}
                print(f"   市场方向: {direction_map.get(analysis['market_direction'], analysis['market_direction'])}")
                print(f"   强度: {analysis.get('direction_strength', 'N/A')}")
            
            print()
            print("📌 分析要点:")
            for i, point in enumerate(analysis['key_points'], 1):
                print(f"   {i}. {point}")
            
            if 'analysis_summary' in analysis:
                print()
                print("📝 综合分析:")
                print(f"   {analysis['analysis_summary']}")
            
            if 'strategy' in analysis:
                print()
                print("🎯 投资策略:")
                print(f"   {analysis['strategy']}")
            
            # 步骤4：检查期权策略
            if 'option_strategy' in analysis_data:
                print()
                print("【步骤4】期权策略推荐")
                print("-" * 70)
                
                option = analysis_data['option_strategy']
                print(f"✅ 推荐策略: {option['name']}")
                print(f"   类型: {option['type']}")
                print(f"   风险等级: {option['risk_level']}")
                print(f"   描述: {option['description']}")
                print()
                print("   策略参数:")
                params = option['parameters']
                print(f"   - 当前股价: ${params['current_price']:.2f}")
                if 'buy_strike' in params:
                    print(f"   - 买入执行价: ${params['buy_strike']:.2f}")
                if 'sell_strike' in params:
                    print(f"   - 卖出执行价: ${params['sell_strike']:.2f}")
                print(f"   - 到期时间: {params['expiry']}")
                print()
                print("   风险指标:")
                metrics = option['metrics']
                max_gain = "无限" if metrics['max_gain'] >= 999999 else f"${metrics['max_gain']:.2f}"
                print(f"   - 最大收益: {max_gain}")
                print(f"   - 最大损失: ${metrics['max_loss']:.2f}")
                print(f"   - 盈亏平衡: ${metrics['breakeven']:.2f}")
                print(f"   - 成功概率: {metrics['probability']}")
            else:
                print()
                print("⚠️ 未生成期权策略（可能AI分析结果中缺少market_direction字段）")
        else:
            print(f"❌ 分析失败: {analysis_data.get('message')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        print(f"   响应: {response.text[:200]}")
    
    print()
    print("=" * 70)
    print("✅ 测试完成！")
    print("=" * 70)
    
except requests.exceptions.ConnectionError:
    print()
    print("❌ 无法连接到后端服务器")
    print()
    print("请确保后端正在运行:")
    print("   1. 打开新终端")
    print("   2. cd backend")
    print("   3. $env:ALPHA_VANTAGE_KEY=\"QKO2M2K3LZ58ACO2\"")
    print("   4. $env:DEEPSEEK_API_KEY=\"sk-d3196d8e68c44690998d79c715ce715d\"")
    print("   5. python app.py")
    print()
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

