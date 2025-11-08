#!/usr/bin/env python3
"""查询特定用户策略的示例"""
import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def query_user_strategies(username):
    """
    查询特定用户的策略
    
    Args:
        username: 用户名，如 'bbb', 'danny', 'bruce'
    """
    print(f"\n🔍 查询用户 {username} 的策略...")
    print("-" * 80)
    
    try:
        response = requests.get(
            f"{RENDER_URL}/api/strategy/user/{username}",
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data['status'] == 'success':
                strategies = data.get('strategies', [])
                count = data.get('count', 0)
                
                print(f"✅ 找到 {count} 个策略\n")
                
                if strategies:
                    for i, s in enumerate(strategies, 1):
                        print(f"[{i}] {s['symbol']} - {s['company_name']}")
                        print(f"    投资风格: {s['investment_style']}")
                        print(f"    推荐: {s['recommendation']}")
                        print(f"    评分: {s['score']}")
                        print(f"    当前价: ${s['current_price']}")
                        print(f"    创建时间: {s['created_at']}")
                        print()
                else:
                    print("   该用户还没有保存过策略")
                
                return strategies
            else:
                print(f"❌ 错误: {data.get('message')}")
                return []
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

# ============================================
# 使用示例
# ============================================
print("\n" + "=" * 80)
print("📊 用户策略查询示例")
print("=" * 80)

# 示例1：查询 bbb 的策略
query_user_strategies('bbb')

# 示例2：查询 danny 的策略
query_user_strategies('danny')

# 示例3：查询 bruce 的策略
query_user_strategies('bruce')

print("=" * 80)
print("\n💡 使用方法:")
print("   1. API方式: GET /api/strategy/user/{username}")
print("   2. 数据库方式: SELECT * FROM accepted_strategies WHERE username = 'xxx'")
print("   3. 前端界面: Strategy Evaluation 页面（只显示登录用户自己的）")
print("\n" + "=" * 80)


