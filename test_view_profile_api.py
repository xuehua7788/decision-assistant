#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试用户画像API - 查看优化参数
"""

import requests
import json

API_BASE = 'https://decision-assistant-githubv3.onrender.com'
USERNAME = 'bbb'

print("=" * 80)
print("🔍 测试用户画像和策略推荐API")
print("=" * 80)

# 1. 获取用户画像
print(f"\n1. 获取用户 {USERNAME} 的画像...")
try:
    response = requests.get(f"{API_BASE}/api/profile/{USERNAME}", timeout=30)
    
    if response.status_code == 200:
        profile = response.json()
        print("   ✅ 用户画像获取成功\n")
        
        inv_pref = profile.get('investment_preferences', {})
        knowledge = profile.get('knowledge_level', {})
        emotion = profile.get('emotional_traits', {})
        
        print("   📊 关键特征:")
        print(f"      • 风险偏好: {inv_pref.get('risk_tolerance', 'N/A')}")
        print(f"      • 投资风格: {inv_pref.get('investment_style', 'N/A')}")
        print(f"      • 时间范围: {inv_pref.get('time_horizon', 'N/A')}")
        print(f"      • 期权经验: {knowledge.get('option_experience', 'N/A')}")
        print(f"      • 信心水平: {emotion.get('confidence_level', 'N/A')}")
        
        print("\n   📝 分析摘要:")
        print(f"      {profile.get('analysis_summary', 'N/A')}")
        
    elif response.status_code == 404:
        print(f"   ⚠️  用户 {USERNAME} 的画像不存在")
        print("   💡 可能需要先触发画像分析")
    else:
        print(f"   ❌ 请求失败: {response.status_code}")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 2. 获取策略推荐历史
print(f"\n2. 获取用户 {USERNAME} 的策略推荐历史...")
try:
    response = requests.get(f"{API_BASE}/api/profile/{USERNAME}/recommendations", timeout=30)
    
    if response.status_code == 200:
        data = response.json()
        recommendations = data.get('recommendations', [])
        
        if recommendations:
            print(f"   ✅ 找到 {len(recommendations)} 条推荐记录\n")
            
            for i, rec in enumerate(recommendations[:3], 1):  # 只显示前3条
                print(f"   📈 推荐 #{rec.get('id', i)}:")
                print(f"      策略类型: {rec.get('strategy_type', 'N/A')}")
                print(f"      策略名称: {rec.get('strategy_name', 'N/A')}")
                print(f"      信心分数: {rec.get('confidence_score', 0) * 100:.0f}%")
                
                # 显示参数对比
                original = rec.get('original_parameters', {})
                adjusted = rec.get('adjusted_parameters', {})
                
                if original and adjusted:
                    print(f"\n      📊 参数对比:")
                    for key in original.keys():
                        orig_val = original.get(key, 'N/A')
                        adj_val = adjusted.get(key, 'N/A')
                        changed = " ✨" if orig_val != adj_val else ""
                        print(f"         {key}: {orig_val} → {adj_val}{changed}")
                
                # 显示调整原因
                if rec.get('adjustment_reason'):
                    print(f"\n      💡 调整原因:")
                    reasons = rec['adjustment_reason'].strip().split('\n')
                    for reason in reasons[:3]:  # 只显示前3条
                        if reason.strip():
                            print(f"         • {reason.strip()}")
                
                print()
        else:
            print("   ⚠️  暂无推荐记录")
            
    elif response.status_code == 404:
        print(f"   ⚠️  用户 {USERNAME} 没有推荐记录")
    else:
        print(f"   ❌ 请求失败: {response.status_code}")
        print(f"   {response.text}")
        
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 3. 显示如何触发画像分析
print("\n3. 如何触发画像分析:")
print(f"   POST {API_BASE}/api/profile/{USERNAME}/analyze")
print("\n   示例代码:")
print(f"""
   import requests
   response = requests.post(
       '{API_BASE}/api/profile/{USERNAME}/analyze',
       timeout=60
   )
   print(response.json())
""")

print("\n" + "=" * 80)
print("测试完成")
print("=" * 80)

print("\n💡 提示:")
print("   • 打开 view_optimizer_web.html 查看可视化界面")
print("   • 运行 python check_strategy_optimizer_status.py 查看集成状态")








