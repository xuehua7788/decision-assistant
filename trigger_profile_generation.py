#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
触发用户画像生成并验证
"""

import requests
import json
import time

API_BASE = 'https://decision-assistant-githubv3.onrender.com'
USERNAME = 'bbb'

def check_chat_messages(username):
    """检查用户是否有聊天记录"""
    print(f"\n📝 检查用户 {username} 的聊天记录...")
    try:
        # 这里需要一个API来查询聊天记录数量
        # 暂时我们假设用户已经有聊天记录
        print("   ℹ️  无法直接查询聊天记录，假设用户已有对话")
        return True
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def trigger_profile_analysis(username):
    """触发用户画像分析"""
    print(f"\n🔄 触发用户 {username} 的画像分析...")
    try:
        response = requests.post(
            f"{API_BASE}/api/profile/{username}/analyze",
            timeout=120  # AI分析可能需要较长时间
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 画像分析成功！")
            print(f"\n   📊 分析结果:")
            
            if result.get('status') == 'success':
                profile = result.get('profile', {})
                inv_pref = profile.get('investment_preferences', {})
                knowledge = profile.get('knowledge_level', {})
                
                print(f"      • 风险偏好: {inv_pref.get('risk_tolerance', 'N/A')}")
                print(f"      • 投资风格: {inv_pref.get('investment_style', 'N/A')}")
                print(f"      • 期权经验: {knowledge.get('option_experience', 'N/A')}")
                print(f"      • 分析消息数: {profile.get('metadata', {}).get('total_messages_analyzed', 0)}")
                return True
            else:
                print(f"   ⚠️  状态: {result.get('status')}")
                print(f"   消息: {result.get('message', 'N/A')}")
                return False
                
        elif response.status_code == 400:
            error = response.json()
            print(f"   ⚠️  {error.get('error', '请求失败')}")
            return False
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            print(f"   {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("   ⏱️  请求超时（AI分析可能需要1-2分钟）")
        print("   💡 请稍后使用 GET /api/profile/{username} 查看结果")
        return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def verify_profile_exists(username):
    """验证用户画像是否存在"""
    print(f"\n🔍 验证用户 {username} 的画像...")
    try:
        response = requests.get(f"{API_BASE}/api/profile/{username}", timeout=30)
        
        if response.status_code == 200:
            profile = response.json()
            print("   ✅ 用户画像存在！")
            
            # 显示关键信息
            inv_pref = profile.get('investment_preferences', {})
            knowledge = profile.get('knowledge_level', {})
            emotion = profile.get('emotional_traits', {})
            
            print(f"\n   📊 画像摘要:")
            print(f"      • 风险偏好: {inv_pref.get('risk_tolerance', 'N/A')}")
            print(f"      • 投资风格: {inv_pref.get('investment_style', 'N/A')}")
            print(f"      • 时间范围: {inv_pref.get('time_horizon', 'N/A')}")
            print(f"      • 期权经验: {knowledge.get('option_experience', 'N/A')}")
            print(f"      • 信心水平: {emotion.get('confidence_level', 0) * 100:.0f}%")
            
            metadata = profile.get('metadata', {})
            print(f"\n   📅 元数据:")
            print(f"      • 最后分析: {metadata.get('analyzed_at', 'N/A')}")
            print(f"      • 分析消息数: {metadata.get('total_messages_analyzed', 0)}")
            
            return True
            
        elif response.status_code == 404:
            print("   ⚠️  用户画像不存在")
            return False
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def send_test_message(username, message):
    """发送测试消息（模拟聊天）"""
    print(f"\n💬 发送测试消息...")
    try:
        response = requests.post(
            f"{API_BASE}/api/chat",
            json={
                "message": message,
                "session_id": username
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("   ✅ 消息发送成功")
            
            # 检查是否触发了策略生成
            if result.get('need_option_strategy'):
                print("   🎯 触发了期权策略生成！")
                strategy = result.get('option_strategy', {})
                print(f"      策略类型: {strategy.get('type', 'N/A')}")
                
                # 检查是否有优化标记
                if 'optimization_metadata' in strategy:
                    opt_meta = strategy['optimization_metadata']
                    print(f"      ✨ 策略已优化: {opt_meta.get('optimized', False)}")
                    print(f"      调整次数: {opt_meta.get('adjustment_count', 0)}")
                else:
                    print("      ⚠️  策略未经过优化（优化器未集成）")
                    
                return True
            else:
                print("   💭 普通聊天回复（未触发策略）")
                return False
                
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def check_recommendations(username):
    """检查策略推荐记录"""
    print(f"\n📈 检查用户 {username} 的策略推荐...")
    try:
        response = requests.get(
            f"{API_BASE}/api/profile/{username}/recommendations",
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            recommendations = data.get('recommendations', [])
            
            if recommendations:
                print(f"   ✅ 找到 {len(recommendations)} 条推荐记录")
                
                # 显示最新的一条
                latest = recommendations[0]
                print(f"\n   📊 最新推荐:")
                print(f"      ID: {latest.get('id')}")
                print(f"      策略类型: {latest.get('strategy_type', 'N/A')}")
                print(f"      信心分数: {latest.get('confidence_score', 0) * 100:.0f}%")
                print(f"      创建时间: {latest.get('created_at', 'N/A')}")
                
                # 检查是否有参数调整
                original = latest.get('original_parameters', {})
                adjusted = latest.get('adjusted_parameters', {})
                
                if original and adjusted:
                    changes = sum(1 for k in original if original.get(k) != adjusted.get(k))
                    if changes > 0:
                        print(f"      ✨ 参数已优化 ({changes} 项调整)")
                    else:
                        print(f"      ℹ️  使用标准参数")
                
                return True
            else:
                print("   ⚠️  暂无推荐记录")
                return False
                
        elif response.status_code == 404:
            print("   ⚠️  用户没有推荐记录")
            return False
        else:
            print(f"   ❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False


def main():
    print("=" * 80)
    print("🚀 用户画像和策略优化 - 完整测试流程")
    print("=" * 80)
    
    # 步骤1: 检查用户画像是否存在
    profile_exists = verify_profile_exists(USERNAME)
    
    if not profile_exists:
        print("\n" + "=" * 80)
        print("📋 用户画像不存在，需要生成")
        print("=" * 80)
        
        # 步骤2: 检查聊天记录
        has_messages = check_chat_messages(USERNAME)
        
        if not has_messages:
            print("\n⚠️  用户需要先进行一些对话才能生成画像")
            print("💡 建议:")
            print("   1. 使用前端聊天界面与AI对话（至少5条消息）")
            print("   2. 或运行以下命令发送测试消息:")
            print(f"      python send_test_messages.py {USERNAME}")
            return
        
        # 步骤3: 触发画像分析
        print("\n" + "=" * 80)
        print("🔄 开始生成用户画像")
        print("=" * 80)
        
        success = trigger_profile_analysis(USERNAME)
        
        if success:
            print("\n⏱️  等待3秒后验证...")
            time.sleep(3)
            verify_profile_exists(USERNAME)
    
    # 步骤4: 测试策略生成（如果画像存在）
    if profile_exists or success:
        print("\n" + "=" * 80)
        print("🎯 测试策略生成和优化")
        print("=" * 80)
        
        test_messages = [
            "我看好特斯拉，想要激进的期权策略",
            "NVDA最近涨得不错，我想做个看涨策略"
        ]
        
        for msg in test_messages:
            print(f"\n测试消息: \"{msg}\"")
            send_test_message(USERNAME, msg)
            time.sleep(2)
    
    # 步骤5: 检查推荐记录
    print("\n" + "=" * 80)
    print("📊 检查生成结果")
    print("=" * 80)
    
    check_recommendations(USERNAME)
    
    # 总结
    print("\n" + "=" * 80)
    print("📋 测试总结")
    print("=" * 80)
    
    profile_exists_now = verify_profile_exists(USERNAME)
    has_recommendations = check_recommendations(USERNAME)
    
    print("\n✅ 成功指标:")
    print(f"   {'✅' if profile_exists_now else '❌'} 用户画像已生成")
    print(f"   {'✅' if has_recommendations else '❌'} 策略推荐已保存")
    
    if profile_exists_now and has_recommendations:
        print("\n🎉 恭喜！用户画像系统运行正常")
        print("💡 现在可以打开 view_optimizer_web.html 查看可视化结果")
    elif profile_exists_now:
        print("\n⚠️  用户画像已生成，但没有策略推荐记录")
        print("💡 可能原因:")
        print("   1. 策略优化器未集成到 app.py")
        print("   2. 用户没有触发过策略生成")
        print("   3. 数据库保存失败")
    else:
        print("\n⚠️  用户画像生成失败")
        print("💡 可能原因:")
        print("   1. 用户聊天记录不足（需要至少5条）")
        print("   2. DeepSeek API调用失败")
        print("   3. 数据库连接问题")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    main()







