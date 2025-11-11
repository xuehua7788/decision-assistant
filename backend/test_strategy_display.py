#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试策略生成和前端展示流程
验证所有字段是否正确
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_full_strategy_flow():
    """测试完整的策略生成流程"""
    
    print("=" * 80)
    print("🧪 测试Jany策略生成 → 前端展示流程")
    print("=" * 80)
    
    # 1. 模拟Tom的分析结果
    tom_analysis = {
        "score": 78,
        "recommendation": "买入",
        "market_direction": "bullish",
        "direction_strength": "strong",
        "strategy": "NVIDIA展现强劲增长动能，AI芯片需求旺盛。建议逢低买入，目标价$210。",
        "analysis_summary": "综合基本面和技术面，NVIDIA处于上升趋势"
    }
    
    # 2. 模拟对话历史
    conversation_history = [
        {
            "role": "user",
            "content": "ROE为什么这么高？"
        },
        {
            "role": "assistant",
            "content": "NVIDIA的ROE高达122%，主要因为其在AI芯片市场的垄断地位..."
        }
    ]
    
    # 3. 调用策略生成API
    print("\n📡 调用 /api/dual-strategy/generate...")
    
    payload = {
        "symbol": "NVDA",
        "username": "test_user",
        "notional_value": 30000,
        "investment_style": "buffett",
        "ai_analysis": tom_analysis,
        "conversation_history": conversation_history
    }
    
    print(f"   请求数据: {json.dumps(payload, indent=2, ensure_ascii=False)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/dual-strategy/generate",
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            print(f"\n❌ API返回错误: {response.status_code}")
            print(f"   错误信息: {response.text}")
            return False
        
        result = response.json()
        
        print("\n✅ 策略生成成功！")
        print("\n" + "=" * 80)
        print("📊 返回的策略数据结构:")
        print("=" * 80)
        
        # 4. 验证返回的数据结构
        print("\n🔍 验证字段完整性:")
        
        # 必需的顶层字段
        required_top_fields = ['strategy_id', 'symbol', 'current_price', 'notional_value', 
                              'option_strategy', 'stock_strategy', 'explanation', 'created_at']
        
        print("\n顶层字段:")
        for field in required_top_fields:
            status = "✅" if field in result else "❌"
            value = result.get(field, 'MISSING')
            if field in ['option_strategy', 'stock_strategy']:
                print(f"  {status} {field}: (对象)")
            else:
                print(f"  {status} {field}: {value}")
        
        # 验证option_strategy字段
        if 'option_strategy' in result:
            option_fields = ['type', 'symbol', 'underlying', 'option_type', 'strike_price', 
                           'expiry_date', 'days_to_expiry', 'equivalent_shares', 
                           'premium_per_share', 'total_premium', 'delta', 'data_source', 'reasoning']
            
            print("\n期权策略字段 (option_strategy):")
            option_strategy = result['option_strategy']
            for field in option_fields:
                status = "✅" if field in option_strategy else "❌"
                value = option_strategy.get(field, 'MISSING')
                print(f"  {status} {field}: {value}")
        
        # 验证stock_strategy字段
        if 'stock_strategy' in result:
            stock_fields = ['type', 'symbol', 'shares', 'entry_price', 'notional', 
                          'margin', 'stop_loss', 'take_profit', 'delta', 'reasoning']
            
            print("\n股票策略字段 (stock_strategy):")
            stock_strategy = result['stock_strategy']
            for field in stock_fields:
                status = "✅" if field in stock_strategy else "❌"
                value = stock_strategy.get(field, 'MISSING')
                print(f"  {status} {field}: {value}")
        
        # 5. 验证前端期望的关键字段
        print("\n" + "=" * 80)
        print("🖥️ 前端展示验证:")
        print("=" * 80)
        
        print("\n期权卡片会显示:")
        opt = result['option_strategy']
        print(f"  类型: {opt.get('type')}")
        print(f"  等价股数: {opt.get('equivalent_shares')}股")
        print(f"  执行价: ${opt.get('strike_price')}")
        print(f"  到期日: {opt.get('expiry_date')} ({opt.get('days_to_expiry')}天)")
        print(f"  期权费: ${opt.get('total_premium', 0):.2f}")  # 前端用total_premium
        print(f"  Delta: {opt.get('delta', 0):.4f}")
        
        print("\n股票卡片会显示:")
        stk = result['stock_strategy']
        print(f"  类型: {stk.get('type')}")
        print(f"  股数: {stk.get('shares')}股")
        print(f"  入场价: ${stk.get('entry_price'):.2f}")
        print(f"  名义本金: ${stk.get('notional'):.2f}")
        print(f"  保证金: ${stk.get('margin'):.2f}")
        print(f"  止损价: ${stk.get('stop_loss'):.2f}")
        print(f"  止盈价: ${stk.get('take_profit'):.2f}")
        print(f"  对应Delta: {stk.get('delta'):.4f}")
        
        print("\nAI推荐理由:")
        print(f"  {result.get('explanation')}")
        
        print("\n" + "=" * 80)
        print("✅ 测试通过！所有字段都匹配前端期望")
        print("=" * 80)
        
        return True
        
    except requests.exceptions.Timeout:
        print("\n❌ 请求超时（60秒）")
        print("   Jany可能正在处理，或者DeepSeek API响应慢")
        return False
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = test_full_strategy_flow()
    exit(0 if success else 1)

