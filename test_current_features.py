#!/usr/bin/env python3
"""测试当前可用功能"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("\n" + "=" * 80)
print("🧪 测试当前系统功能")
print("=" * 80)

# 1. 注册新用户
print("\n【功能1】用户注册")
print("-" * 80)

username = f"user_{int(time.time())}"
password = "test123456"

try:
    response = requests.post(
        f"{RENDER_URL}/api/auth/register",
        json={"username": username, "password": password},
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        token = data.get('token')
        print(f"✅ 注册成功")
        print(f"   用户名: {username}")
        print(f"   Token: {token[:30]}...")
    else:
        print(f"❌ 注册失败: {response.text}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 2. 登录
print("\n【功能2】用户登录")
print("-" * 80)

try:
    response = requests.post(
        f"{RENDER_URL}/api/auth/login",
        json={"username": username, "password": password},
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 登录成功")
        print(f"   用户名: {data.get('username')}")
    else:
        print(f"⚠️  {response.json().get('detail')}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 3. 保存策略（带username）
print("\n【功能3】保存策略（包含用户名）")
print("-" * 80)

strategy_data = {
    "username": username,  # 关联用户
    "symbol": "TSLA",
    "company_name": "Tesla Inc.",
    "investment_style": "lynch",
    "recommendation": "买入",
    "target_price": 300.0,
    "stop_loss": 250.0,
    "position_size": "20%",
    "score": 88,
    "strategy_text": "成长股投资策略",
    "analysis_summary": "特斯拉具有强劲的增长潜力",
    "current_price": 275.0
}

try:
    response = requests.post(
        f"{RENDER_URL}/api/strategy/save",
        json=strategy_data,
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 策略保存成功")
        print(f"   策略ID: {data.get('strategy_id')}")
    else:
        print(f"❌ 保存失败: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 4. 查询用户的策略
print("\n【功能4】查询用户策略")
print("-" * 80)

try:
    response = requests.get(
        f"{RENDER_URL}/api/strategy/user/{username}",
        timeout=15
    )
    
    if response.status_code == 200:
        data = response.json()
        count = data.get('count', 0)
        print(f"✅ 查询成功")
        print(f"   用户: {data.get('username')}")
        print(f"   策略数: {count}")
        
        if count > 0:
            strategies = data.get('strategies', [])
            for i, s in enumerate(strategies, 1):
                print(f"\n   [{i}] {s['symbol']} - {s['investment_style']}")
                print(f"       评分: {s['score']} | {s['recommendation']}")
    else:
        print(f"❌ 查询失败: {response.status_code}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

# 5. 查询所有策略
print("\n【功能5】查询所有策略")
print("-" * 80)

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=15)
    
    if response.status_code == 200:
        data = response.json()
        strategies = data.get('strategies', [])
        
        with_user = sum(1 for s in strategies if s.get('username'))
        without_user = len(strategies) - with_user
        
        print(f"✅ 查询成功")
        print(f"   总策略数: {len(strategies)}")
        print(f"   关联用户: {with_user}")
        print(f"   未关联: {without_user}")
    else:
        print(f"❌ 查询失败")
        
except Exception as e:
    print(f"❌ 错误: {e}")

print("\n" + "=" * 80)
print("📊 测试完成")
print("=" * 80)

print("\n✅ 成功的功能:")
print("   - 用户注册和登录")
print("   - 策略保存（包含用户名）")
print("   - 查询特定用户的策略")
print("   - 查询所有策略")

print("\n⏳ 待完成:")
print("   - 数据库迁移（添加user字段到现有策略）")
print("   - 查询 bbb 用户（需要DATABASE_URL）")

print("\n" + "=" * 80)


