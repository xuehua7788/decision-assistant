#!/usr/bin/env python3
"""验证通过API查询bbb的策略"""
import requests

BACKEND_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("🔍 验证 bbb 用户的策略查询（通过API）")
print("=" * 80)

# ============================================
# 1. 查询所有策略
# ============================================
print("\n【1】查询所有策略")
print("-" * 80)

try:
    response = requests.get(f"{BACKEND_URL}/api/strategy/list", timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        strategies = data.get('strategies', [])
        print(f"✅ 成功获取 {len(strategies)} 个策略")
        
        # 统计按用户分组
        user_counts = {}
        for s in strategies:
            username = s.get('username', '(未分配)')
            user_counts[username] = user_counts.get(username, 0) + 1
        
        print("\n用户策略分布:")
        for username, count in user_counts.items():
            print(f"   {username}: {count} 个")
    else:
        print(f"❌ 请求失败: {response.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")

# ============================================
# 2. 查询 bbb 的策略
# ============================================
print("\n【2】查询 bbb 用户的策略")
print("-" * 80)

try:
    response = requests.get(f"{BACKEND_URL}/api/strategy/user/bbb", timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        strategies = data.get('strategies', [])
        print(f"\n✅ bbb 有 {len(strategies)} 个策略:\n")
        
        for i, s in enumerate(strategies, 1):
            has_option = '✅ 有期权' if s.get('option_strategy') else '❌ 无期权'
            print(f"[{i}] {s['symbol']:6} | {s.get('company_name', 'N/A'):20} | {s['investment_style']:10}")
            print(f"    推荐: {s['recommendation']:8} | 评分: {s.get('score', 'N/A'):3} | {has_option}")
            print(f"    目标价: ${s['target_price']:8.2f} | 当前价: ${s['current_price']:8.2f}")
            
            # 如果有期权策略，显示详情
            if s.get('option_strategy'):
                opt = s['option_strategy']
                opt_name = opt.get('name') or opt.get('strategy', {}).get('name', '未知')
                print(f"    期权策略: {opt_name}")
            
            print()
            
    else:
        print(f"❌ 请求失败: {response.text}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")

print("=" * 80)
print("✅ 验证完成！")
print("=" * 80)
print()


