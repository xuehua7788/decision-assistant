#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析指定用户的画像
"""

import requests
import json
import sys
import time

BASE_URL = "https://decision-assistant-backend.onrender.com"

def analyze_user(username):
    """触发用户画像分析"""
    print("=" * 70)
    print(f"分析用户画像: {username}")
    print("=" * 70)
    print()
    
    print("🔄 正在调用AI #3分析用户画像...")
    print("   （这可能需要30-60秒，请耐心等待）")
    print()
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/profile/{username}/analyze",
            json={"days": 30, "force": True},
            headers={"Content-Type": "application/json"},
            timeout=120  # 2分钟超时
        )
        
        print(f"状态码: {response.status_code}")
        print()
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get('profile', {})
            
            print("✅ 分析成功！")
            print()
            print("=" * 70)
            print("用户画像结果")
            print("=" * 70)
            print()
            
            # 投资偏好
            inv_pref = profile.get('investment_preferences', {})
            print("📊 投资偏好:")
            print(f"   风险偏好: {inv_pref.get('risk_tolerance', 'unknown')}")
            print(f"   投资风格: {inv_pref.get('investment_style', 'unknown')}")
            print(f"   时间范围: {inv_pref.get('time_horizon', 'unknown')}")
            print()
            
            # 知识水平
            knowledge = profile.get('knowledge_level', {})
            print("📚 知识水平:")
            print(f"   金融知识: {knowledge.get('financial_knowledge', 'unknown')}")
            print(f"   期权经验: {knowledge.get('option_experience', 'unknown')}")
            print()
            
            # 行为特征
            behav = profile.get('behavioral_traits', {})
            print("🎯 行为特征:")
            print(f"   决策速度: {behav.get('decision_speed', 'unknown')}")
            print(f"   信息深度: {behav.get('information_depth', 'unknown')}")
            print(f"   聊天频率: {behav.get('chat_frequency', 'unknown')} 次/周")
            print()
            
            # 情绪特征
            emotion = profile.get('emotional_traits', {})
            print("💭 情绪特征:")
            print(f"   情绪倾向: {emotion.get('sentiment_tendency', 'unknown')}")
            confidence = emotion.get('confidence_level', 0)
            if isinstance(confidence, (int, float)):
                print(f"   信心水平: {confidence:.1%}")
            else:
                print(f"   信心水平: {confidence}")
            print()
            
            # 关键洞察
            insights = profile.get('key_insights', {})
            if insights:
                print("🔍 关键洞察:")
                if insights.get('key_interests'):
                    print(f"   关注股票: {', '.join(insights.get('key_interests', []))}")
                if insights.get('decision_patterns'):
                    print(f"   决策模式: {insights.get('decision_patterns')}")
                if insights.get('risk_concerns'):
                    print(f"   风险关注: {', '.join(insights.get('risk_concerns', []))}")
                print()
            
            # 推荐参数
            recommendations = profile.get('recommendations', {})
            if recommendations:
                print("💡 个性化建议:")
                if recommendations.get('recommended_strategy_types'):
                    print(f"   推荐策略: {', '.join(recommendations.get('recommended_strategy_types', []))}")
                if recommendations.get('personalization_notes'):
                    print(f"   建议: {recommendations.get('personalization_notes')}")
                print()
            
            # 分析摘要
            print("📝 分析摘要:")
            print(f"   {profile.get('analysis_summary', 'N/A')}")
            print()
            
            # 元数据
            metadata = profile.get('metadata', {})
            print("ℹ️ 分析信息:")
            print(f"   分析时间: {metadata.get('analyzed_at', 'N/A')}")
            print(f"   分析消息数: {metadata.get('total_messages_analyzed', 0)}")
            print(f"   分析周期: {metadata.get('analysis_period_days', 30)} 天")
            print()
            
            print("=" * 70)
            print("✅ 用户画像已保存到数据库")
            print("=" * 70)
            print()
            print("下一步:")
            print("1. 用户下次表达投资意图时，系统会自动应用个性化策略")
            print("2. 查看画像: python check_user_profile.py " + username)
            print()
            
            return True
            
        elif response.status_code == 400:
            data = response.json()
            print(f"❌ {data.get('message', '分析失败')}")
            return False
            
        else:
            print(f"❌ 分析失败: {response.text[:200]}")
            return False
            
    except requests.Timeout:
        print("❌ 请求超时（AI分析时间过长）")
        print("   请稍后重试或检查DEEPSEEK_API_KEY是否有效")
        return False
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("使用方法: python analyze_user.py <username>")
        print()
        print("示例:")
        print("  python analyze_user.py 57e56767-4088-4d2a-9206-64ad27232b15")
        sys.exit(1)
    
    username = sys.argv[1]
    success = analyze_user(username)
    sys.exit(0 if success else 1)


