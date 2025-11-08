#!/usr/bin/env python3
"""测试用户和策略关联修复"""
import requests
import json
import time

# 测试环境
RENDER_URL = "https://decision-assistant-backend.onrender.com"
LOCAL_URL = "http://localhost:5000"

# 使用Render（如果本地后端没运行）
API_URL = RENDER_URL

print("\n" + "=" * 80)
print("🧪 测试用户和策略关联修复")
print("=" * 80)

# ========================================
# 测试1：注册新用户
# ========================================
print("\n【测试1】注册新用户")
print("-" * 80)

test_username = f"test_{int(time.time())}"
test_password = "test123456"

try:
    response = requests.post(
        f"{API_URL}/api/auth/register",
        json={
            "username": test_username,
            "password": test_password
        },
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 注册成功")
        print(f"   用户名: {data.get('username')}")
        print(f"   Token: {data.get('token', 'N/A')[:20]}...")
        token = data.get('token')
    else:
        print(f"❌ 注册失败")
        print(f"   响应: {response.text}")
        test_username = "bbb"  # 使用已存在的用户继续测试
        token = None
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    test_username = "bbb"
    token = None

# ========================================
# 测试2：保存策略（带username）
# ========================================
print("\n【测试2】保存策略（包含username）")
print("-" * 80)

strategy_data = {
    "username": test_username,  # 🆕 关键：包含username
    "symbol": "AAPL",
    "company_name": "Apple Inc.",
    "investment_style": "buffett",
    "recommendation": "买入",
    "target_price": 200.0,
    "stop_loss": 175.0,
    "position_size": "15%",
    "score": 85,
    "strategy_text": "测试策略",
    "analysis_summary": "这是测试用的策略摘要",
    "current_price": 180.5
}

try:
    response = requests.post(
        f"{API_URL}/api/strategy/save",
        json=strategy_data,
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 策略保存成功")
        print(f"   策略ID: {data.get('strategy_id')}")
        strategy_id = data.get('strategy_id')
    else:
        print(f"❌ 保存失败")
        print(f"   响应: {response.text[:200]}")
        strategy_id = None
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    strategy_id = None

# ========================================
# 测试3：查询用户的策略
# ========================================
print("\n【测试3】查询用户的策略列表")
print("-" * 80)

try:
    response = requests.get(
        f"{API_URL}/api/strategy/user/{test_username}",
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('status') == 'success':
            strategies = data.get('strategies', [])
            count = data.get('count', 0)
            
            print(f"✅ 查询成功")
            print(f"   用户: {data.get('username')}")
            print(f"   策略数: {count}")
            
            if strategies:
                print(f"\n   最近的策略:")
                for i, s in enumerate(strategies[:3], 1):
                    print(f"   [{i}] {s['symbol']} - {s['investment_style']}")
                    print(f"       评分: {s['score']} | 推荐: {s['recommendation']}")
                    print(f"       创建: {s['created_at']}")
            else:
                print(f"   ⚠️  暂无策略")
        else:
            print(f"❌ 查询失败: {data.get('message')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        print(f"   响应: {response.text[:200]}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# ========================================
# 测试4：查询所有策略（检查是否有username）
# ========================================
print("\n【测试4】检查所有策略的username字段")
print("-" * 80)

try:
    response = requests.get(
        f"{API_URL}/api/strategy/list",
        timeout=15
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('status') == 'success':
            strategies = data.get('strategies', [])
            
            print(f"✅ 查询成功")
            print(f"   总策略数: {len(strategies)}")
            
            # 统计有username的策略
            with_username = sum(1 for s in strategies if s.get('username'))
            without_username = len(strategies) - with_username
            
            print(f"   有username: {with_username}")
            print(f"   无username: {without_username}")
            
            # 显示最近的几个策略
            if strategies:
                print(f"\n   最近的策略:")
                for i, s in enumerate(strategies[:5], 1):
                    username_info = s.get('username', '(无用户)')
                    print(f"   [{i}] {s['symbol']} | 用户: {username_info} | {s.get('created_at', 'N/A')[:10]}")
        else:
            print(f"❌ 查询失败: {data.get('message')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求失败: {e}")

# ========================================
# 测试总结
# ========================================
print("\n" + "=" * 80)
print("📊 测试总结")
print("=" * 80)

print("\n✅ 如果看到以上所有测试通过，说明修复成功：")
print("   1. 用户注册功能正常")
print("   2. 策略可以关联username")
print("   3. 可以查询特定用户的策略")
print("   4. 策略表包含username字段")

print("\n⚠️  如果有测试失败：")
print("   - 可能需要先运行数据库迁移")
print("   - 或者后端代码还未部署")

print("\n💡 下一步：")
print("   1. 如果本地测试通过 → 部署到Render")
print("   2. 运行迁移脚本: python migrate_add_user_columns.py")
print("   3. 在Render上重新测试")

print("\n" + "=" * 80)


