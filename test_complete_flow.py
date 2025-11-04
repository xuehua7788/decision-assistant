#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整的用户流程：Stock Analysis → 接受策略 → Strategy Evaluation
"""

import requests
import json
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("测试完整用户流程")
print("=" * 80)

# 步骤1: 获取股票分析（模拟Stock Analysis）
print("\n📊 步骤1: 获取TSLA股票分析...")
try:
    # 1.1 获取股票数据
    response = requests.get(f"{RENDER_URL}/api/stock/TSLA", timeout=15)
    if response.status_code != 200:
        print(f"❌ 获取股票数据失败: {response.status_code}")
        exit(1)
    
    stock_data = response.json()
    print(f"✅ 股票数据获取成功")
    print(f"   当前价格: ${stock_data['data']['price']}")
    
    # 1.2 AI分析
    print("\n🤖 步骤2: 请求AI分析...")
    analysis_request = {
        "symbol": "TSLA",
        "risk_preference": "balanced",
        "language": "zh",
        "investment_style": "lynch"
    }
    
    response = requests.post(
        f"{RENDER_URL}/api/stock/analyze",
        json=analysis_request,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    if response.status_code != 200:
        print(f"❌ AI分析失败: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        exit(1)
    
    analysis_result = response.json()
    
    if analysis_result.get('status') != 'success':
        print(f"❌ 分析返回错误: {analysis_result.get('message')}")
        exit(1)
    
    analysis = analysis_result['analysis']
    option_strategy = analysis_result.get('option_strategy')
    
    print(f"✅ AI分析完成")
    print(f"   推荐: {analysis['recommendation']}")
    print(f"   评分: {analysis['score']}")
    print(f"   目标价: ${analysis['target_price']}")
    
    if option_strategy:
        print(f"\n📊 期权策略生成成功:")
        print(f"   策略名称: {option_strategy['name']}")
        print(f"   策略类型: {option_strategy['type']}")
        print(f"   风险等级: {option_strategy.get('risk_level', 'N/A')}")
    else:
        print(f"\n⚠️  没有生成期权策略")
        print("   这可能是因为AI分析结果不包含market_direction")
        exit(1)
    
    # 步骤3: 模拟用户点击"接受此策略"
    print("\n✅ 步骤3: 用户点击'接受此策略'...")
    
    strategy_data = {
        "symbol": "TSLA",
        "company_name": "Tesla Inc.",
        "investment_style": "lynch",
        "recommendation": analysis['recommendation'],
        "target_price": analysis['target_price'],
        "stop_loss": analysis.get('stop_loss', 0),
        "position_size": analysis.get('position_size', '15%'),
        "score": analysis['score'],
        "strategy_text": analysis.get('strategy', ''),
        "analysis_summary": analysis.get('analysis_summary', ''),
        "current_price": stock_data['data']['price'],
        "option_strategy": option_strategy  # 关键：包含期权策略
    }
    
    response = requests.post(
        f"{RENDER_URL}/api/strategy/save",
        json=strategy_data,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    if response.status_code != 200:
        print(f"❌ 保存策略失败: {response.status_code}")
        print(f"响应: {response.text[:500]}")
        exit(1)
    
    save_result = response.json()
    
    if save_result.get('status') != 'success':
        print(f"❌ 保存失败: {save_result.get('message')}")
        exit(1)
    
    strategy_id = save_result['strategy_id']
    print(f"✅ 策略已保存")
    print(f"   策略ID: {strategy_id}")
    
    # 步骤4: 从Strategy Evaluation读取
    print("\n📋 步骤4: 从Strategy Evaluation读取策略列表...")
    time.sleep(1)  # 等待数据库写入
    
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    
    if response.status_code != 200:
        print(f"❌ 读取策略列表失败: {response.status_code}")
        exit(1)
    
    list_result = response.json()
    strategies = list_result.get('strategies', [])
    
    # 找到刚才保存的策略
    saved_strategy = None
    for s in strategies:
        if s['strategy_id'] == strategy_id:
            saved_strategy = s
            break
    
    if not saved_strategy:
        print(f"❌ 未找到刚保存的策略: {strategy_id}")
        exit(1)
    
    print(f"✅ 找到保存的策略")
    print(f"   股票: {saved_strategy['symbol']}")
    print(f"   推荐: {saved_strategy['recommendation']}")
    
    # 关键检查：期权策略是否保存
    if saved_strategy.get('option_strategy'):
        opt = saved_strategy['option_strategy']
        print(f"\n🎉 期权策略已成功保存到数据库!")
        print(f"   策略名称: {opt.get('name', 'N/A')}")
        print(f"   策略类型: {opt.get('type', 'N/A')}")
    else:
        print(f"\n❌ 期权策略未保存到数据库")
        exit(1)
    
    print("\n" + "=" * 80)
    print("✅ 完整流程测试通过！")
    print("=" * 80)
    print("\n总结:")
    print("1. ✅ Stock Analysis生成期权策略")
    print("2. ✅ 用户接受策略后成功保存")
    print("3. ✅ Strategy Evaluation可以读取期权策略")
    print("4. ✅ 整个数据流畅通无阻")
    
except Exception as e:
    print(f"\n❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()
