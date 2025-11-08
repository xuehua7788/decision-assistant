#!/usr/bin/env python3
"""测试新的用户策略API"""
import requests
import time

BACKEND_URL = "https://decision-assistant-backend.onrender.com"
USERNAME = "bbb"

print("\n" + "="*80)
print("🧪 测试新的用户策略API")
print("="*80)

# 等待部署
print("\n⏳ 等待Render部署...")
for i in range(60):
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=5)
        if response.status_code == 200:
            print(f"✅ 后端已就绪 (等待了 {i*5}秒)")
            break
    except:
        pass
    
    if i % 6 == 0:
        print(f"   等待中... {i*5}秒")
    time.sleep(5)
else:
    print("⚠️  超时，继续尝试...")

time.sleep(10)  # 额外等待数据库迁移完成

# 1. 测试获取用户策略
print("\n【1】获取 bbb 的策略")
print("-"*80)
try:
    response = requests.get(f"{BACKEND_URL}/api/user/{USERNAME}/strategies", timeout=10)
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 成功获取策略")
        print(f"   用户名: {data['username']}")
        print(f"   策略数: {data['total']}")
        
        if data['total'] > 0:
            print(f"\n   前3个策略:")
            for i, s in enumerate(data['strategies'][:3], 1):
                has_option = '✅' if s.get('option_strategy') else '❌'
                print(f"   [{i}] {s['symbol']:6} | {s['investment_style']:10} | 期权:{has_option}")
        else:
            print("   ⚠️  用户暂无策略")
    else:
        print(f"❌ 失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 2. 测试保存策略
print("\n【2】保存测试策略")
print("-"*80)
try:
    test_strategy = {
        "username": USERNAME,
        "strategy": {
            "strategy_id": f"TEST_{int(time.time())}",
            "symbol": "TEST",
            "company_name": "测试公司",
            "investment_style": "buffett",
            "recommendation": "买入",
            "target_price": 100.0,
            "stop_loss": 90.0,
            "position_size": "10%",
            "score": 85,
            "strategy_text": "测试策略文本",
            "analysis_summary": "测试分析摘要",
            "current_price": 95.0,
            "option_strategy": {
                "name": "测试期权策略",
                "type": "call"
            }
        }
    }
    
    response = requests.post(
        f"{BACKEND_URL}/api/user/save-strategy",
        json=test_strategy,
        timeout=10
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        print(f"   策略总数: {data.get('strategy_count', 'N/A')}")
    else:
        print(f"❌ 失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 3. 再次获取验证
print("\n【3】验证策略已保存")
print("-"*80)
try:
    response = requests.get(f"{BACKEND_URL}/api/user/{USERNAME}/strategies", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ 当前策略总数: {data['total']}")
        
        # 查找刚保存的测试策略
        test_found = False
        for s in data['strategies']:
            if s['symbol'] == 'TEST':
                test_found = True
                print(f"   ✅ 找到测试策略: {s['strategy_id']}")
                break
        
        if not test_found:
            print(f"   ⚠️  未找到测试策略")
    else:
        print(f"❌ 失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 4. 测试删除策略
print("\n【4】删除测试策略")
print("-"*80)
try:
    # 先获取测试策略ID
    response = requests.get(f"{BACKEND_URL}/api/user/{USERNAME}/strategies", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        test_strategy_id = None
        
        for s in data['strategies']:
            if s['symbol'] == 'TEST':
                test_strategy_id = s['strategy_id']
                break
        
        if test_strategy_id:
            # 删除策略
            response = requests.delete(
                f"{BACKEND_URL}/api/user/{USERNAME}/strategies/{test_strategy_id}",
                timeout=10
            )
            
            print(f"状态码: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ {result['message']}")
                print(f"   剩余策略: {result.get('remaining', 'N/A')}")
            else:
                print(f"❌ 删除失败: {response.text}")
        else:
            print("   ℹ️  没有找到测试策略，跳过删除")
    else:
        print(f"❌ 获取策略失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

# 5. 最终验证
print("\n【5】最终验证")
print("-"*80)
try:
    response = requests.get(f"{BACKEND_URL}/api/user/{USERNAME}/strategies", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ bbb 最终策略数: {data['total']}")
        print(f"\n   策略列表:")
        for i, s in enumerate(data['strategies'], 1):
            has_option = '✅ 有期权' if s.get('option_strategy') else '❌ 无期权'
            print(f"   [{i}] {s['symbol']:6} | {s.get('company_name', 'N/A'):20} | {s['investment_style']:10} | {has_option}")
    else:
        print(f"❌ 失败: {response.text}")
except Exception as e:
    print(f"❌ 异常: {e}")

print("\n" + "="*80)
print("✅ 测试完成")
print("="*80)
print()


