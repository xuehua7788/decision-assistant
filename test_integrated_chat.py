#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试集成后的聊天功能
验证双AI协同工作
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"
SESSION_ID = "test_user_integration"

def test_chat(message, description):
    """测试聊天功能"""
    print(f"\n{'='*80}")
    print(f"测试: {description}")
    print(f"{'='*80}")
    print(f"💬 用户: {message}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/decisions/chat",
            json={
                "message": message,
                "session_id": SESSION_ID
            },
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI回复:")
            print(result.get('response', ''))
            
            if result.get('option_strategy_used'):
                print(f"\n✅ 触发期权策略！")
                strategy = result.get('option_strategy_result', {}).get('strategy', {})
                print(f"   策略名称: {strategy.get('name', 'N/A')}")
                print(f"   风险等级: {strategy.get('risk_level', 'N/A')}")
            else:
                print(f"\n💬 普通聊天（未触发期权策略）")
            
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(response.text)
            return False
            
    except Exception as e:
        print(f"❌ 错误: {str(e)}")
        return False


def main():
    print("🧪 集成测试：双AI协同聊天")
    print("="*80)
    
    # 等待服务器启动
    print("\n等待服务器启动...")
    time.sleep(3)
    
    # 检查服务器是否运行
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"✅ 服务器运行中: {response.json()}")
    except Exception as e:
        print(f"❌ 服务器未启动: {e}")
        print("请先启动后端服务器: cd backend && python app.py")
        return
    
    # 测试1: 普通闲聊
    test_chat(
        message="你好，今天天气怎么样？",
        description="场景1: 普通闲聊（不应触发期权策略）"
    )
    
    time.sleep(2)
    
    # 测试2: 询问股票信息
    test_chat(
        message="特斯拉最近表现怎么样？",
        description="场景2: 询问股票信息（不应触发期权策略）"
    )
    
    time.sleep(2)
    
    # 测试3: 表达对财报的看法
    test_chat(
        message="看起来财报数据不错",
        description="场景3: 讨论财报（不应触发期权策略）"
    )
    
    time.sleep(2)
    
    # 测试4: 基于上下文的投资意图（关键测试）
    test_chat(
        message="我看涨",
        description="场景4: 基于上下文表达投资观点（应触发期权策略，识别TSLA）"
    )
    
    time.sleep(2)
    
    # 测试5: 明确的投资方向
    test_chat(
        message="我看涨苹果股票",
        description="场景5: 明确投资方向（应触发期权策略，识别AAPL）"
    )
    
    time.sleep(2)
    
    # 测试6: 复杂否定场景
    test_chat(
        message="我朋友强烈看涨微软，但我不认同",
        description="场景6: 复杂否定逻辑（应触发期权策略，direction=bearish）"
    )
    
    print("\n" + "="*80)
    print("🎉 测试完成！")
    print("="*80)
    print("\n总结:")
    print("- 场景1-3应该是AI #2的自然聊天回复")
    print("- 场景4应该从上下文识别出TSLA并触发期权策略")
    print("- 场景5应该识别出AAPL并触发期权策略")
    print("- 场景6应该识别出MSFT，direction=bearish")


if __name__ == '__main__':
    main()

