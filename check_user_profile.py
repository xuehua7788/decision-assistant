#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询用户画像参数
"""

import requests
import json
import sys

BASE_URL = "https://decision-assistant-backend.onrender.com"

def check_user_profile(username):
    """查询指定用户的画像"""
    print("=" * 70)
    print(f"查询用户画像: {username}")
    print("=" * 70)
    print()
    
    # 1. 获取用户画像
    print("1. 获取用户画像...")
    try:
        response = requests.get(f"{BASE_URL}/api/profile/{username}", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            profile = data.get('profile', {})
            
            print("✅ 找到用户画像")
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
            print(f"   信心水平: {emotion.get('confidence_level', 'unknown')}")
            print()
            
            # 分析摘要
            print("📝 分析摘要:")
            print(f"   {profile.get('analysis_summary', 'N/A')}")
            print()
            
            # 元数据
            metadata = profile.get('metadata', {})
            print("ℹ️ 元数据:")
            print(f"   分析时间: {profile.get('last_analyzed_at', 'N/A')}")
            print(f"   分析消息数: {metadata.get('total_messages_analyzed', 0)}")
            print()
            
            return True
            
        elif response.status_code == 404:
            print("❌ 用户画像不存在")
            print()
            print("可能原因:")
            print("1. 用户还没有被分析")
            print("2. 用户聊天记录不足（需要至少5条）")
            print()
            print("解决方法:")
            print(f"   python analyze_user.py {username}")
            return False
            
        else:
            print(f"❌ 错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


def list_all_users():
    """列出所有有聊天记录的用户"""
    print("=" * 70)
    print("查询所有用户")
    print("=" * 70)
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/api/admin/chats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            chats = data.get('chats', {})
            
            if chats:
                print(f"找到 {len(chats)} 个用户:\n")
                
                for username, info in chats.items():
                    msg_count = info.get('total_messages', 0)
                    print(f"  - {username}: {msg_count} 条消息")
                
                print()
                return list(chats.keys())
            else:
                print("暂无用户数据")
                return []
        else:
            print(f"❌ 错误: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []


def get_profile_stats():
    """获取用户画像统计"""
    print("=" * 70)
    print("用户画像统计")
    print("=" * 70)
    print()
    
    try:
        response = requests.get(f"{BASE_URL}/api/profile/stats", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            stats = data.get('stats', {})
            
            print(f"总用户画像数: {stats.get('total_profiles', 0)}")
            print(f"最近分析: {stats.get('recently_analyzed', 0)}")
            print()
            
            # 风险分布
            risk_dist = stats.get('risk_distribution', {})
            if risk_dist:
                print("风险偏好分布:")
                for risk, count in risk_dist.items():
                    print(f"  {risk}: {count}")
                print()
            
            # 经验分布
            exp_dist = stats.get('experience_distribution', {})
            if exp_dist:
                print("期权经验分布:")
                for exp, count in exp_dist.items():
                    print(f"  {exp}: {count}")
                print()
            
            return True
        else:
            print(f"❌ API错误: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 查询指定用户
        username = sys.argv[1]
        check_user_profile(username)
    else:
        # 显示所有用户和统计
        print()
        
        # 统计信息
        get_profile_stats()
        
        # 用户列表
        users = list_all_users()
        
        if users:
            print("=" * 70)
            print("查询用户画像")
            print("=" * 70)
            print()
            print("使用方法:")
            print(f"  python check_user_profile.py {users[0]}")
            print()


