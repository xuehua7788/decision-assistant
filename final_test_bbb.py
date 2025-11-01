#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最终测试：验证数据库同步是否工作
"""

import requests
import time

BASE_URL = "https://decision-assistant-backend.onrender.com"

def final_test():
    """最终测试"""
    print("=" * 70)
    print("最终测试：验证数据库同步")
    print("=" * 70)
    print()
    
    # 1. 发送5条测试消息
    print("📤 发送5条测试消息到bbb用户...")
    print()
    
    messages = [
        "我想了解期权投资",
        "特斯拉股票最近怎么样？",
        "我看好科技股长期发展",
        "但担心短期市场波动",
        "有什么保守的投资策略吗？"
    ]
    
    for i, msg in enumerate(messages, 1):
        print(f"[{i}/5] 发送: {msg}")
        try:
            response = requests.post(
                f"{BASE_URL}/api/decisions/chat",
                json={
                    "message": msg,
                    "session_id": "bbb"
                },
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 200:
                print(f"      ✅ 成功")
            else:
                print(f"      ❌ 失败: {response.status_code}")
                
        except Exception as e:
            print(f"      ❌ 错误: {e}")
        
        time.sleep(1)
    
    print()
    print("=" * 70)
    print("📊 等待3秒后检查数据库...")
    print("=" * 70)
    time.sleep(3)
    print()
    
    # 2. 分析用户画像（会显示数据库中的消息数量）
    print("🔍 分析bbb用户画像...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/profile/bbb/analyze",
            json={},
            timeout=60
        )
        
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            print("🎉 成功！用户画像已生成！")
            print()
            data = response.json()
            profile = data.get('profile', {})
            
            print("📊 用户画像摘要:")
            print("-" * 70)
            
            inv_pref = profile.get('investment_preferences', {})
            knowledge = profile.get('knowledge_level', {})
            emotion = profile.get('emotional_traits', {})
            
            print(f"• 风险偏好: {inv_pref.get('risk_tolerance', 'N/A')}")
            print(f"• 投资风格: {inv_pref.get('investment_style', 'N/A')}")
            print(f"• 时间范围: {inv_pref.get('time_horizon', 'N/A')}")
            print(f"• 期权经验: {knowledge.get('option_experience', 'N/A')}")
            print(f"• 信心水平: {emotion.get('confidence_level', 'N/A')}")
            print()
            print(f"📝 分析摘要:")
            print(profile.get('analysis_summary', 'N/A'))
            print()
            
        elif response.status_code == 400:
            data = response.json()
            error = data.get('error', '')
            print(f"❌ {error}")
            print()
            
            import re
            match = re.search(r'（(\d+) 条）', error)
            if match:
                count = int(match.group(1))
                if count == 0:
                    print("❌ 数据库同步仍然失败！")
                    print("   请检查Render日志中是否有:")
                    print("   '⚠️ 数据库不可用，消息只保存到JSON'")
                else:
                    print(f"⚠️ 数据库中有 {count} 条消息，但不足5条")
                    print(f"   还需要 {5 - count} 条消息")
        else:
            print(f"❌ 未知错误: {response.status_code}")
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
    
    print()
    print("=" * 70)

if __name__ == "__main__":
    final_test()







