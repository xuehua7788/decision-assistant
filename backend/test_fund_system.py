"""
测试资金管理系统完整流程
"""
import requests
import json

# BASE_URL = 'http://localhost:5000'  # 本地测试
BASE_URL = 'https://decision-assistant-backend.onrender.com'  # 生产环境

def test_account():
    """测试账户查询"""
    print("\n=== 测试1: 查询账户信息 ===")
    response = requests.get(f'{BASE_URL}/api/fund/account/bbb')
    print(f"状态码: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"总资产: ${data['total_assets']:.2f}")
        print(f"现金: ${data['total_cash']:.2f}")
        print(f"可用资金: ${data['available_cash']:.2f}")
        print(f"保证金占用: ${data['margin_occupied']:.2f}")
        print(f"持仓数量: {data['position_count']}")
        return True
    else:
        print(f"❌ 失败: {response.text}")
        return False

def test_generate_strategy():
    """测试生成双策略"""
    print("\n=== 测试2: 生成双策略 ===")
    payload = {
        "symbol": "AAPL",
        "username": "bbb",
        "notional_value": 10000,
        "investment_style": "aggressive"
    }
    response = requests.post(
        f'{BASE_URL}/api/dual-strategy/generate',
        json=payload
    )
    print(f"状态码: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"策略ID: {data['strategy_id']}")
        print(f"当前股价: ${data['current_price']:.2f}")
        print(f"\n期权策略:")
        print(f"  类型: {data['option_strategy']['type']}")
        print(f"  执行价: ${data['option_strategy']['strike_price']:.2f}")
        print(f"  期权费: ${data['option_strategy']['premium']:.2f}")
        print(f"  Delta: {data['option_strategy']['delta']}")
        print(f"\n股票策略:")
        print(f"  类型: {data['stock_strategy']['type']}")
        print(f"  金额: ${data['stock_strategy']['amount']:.2f}")
        print(f"  保证金: ${data['stock_strategy']['margin']:.2f}")
        print(f"  股数: {data['stock_strategy']['shares']}")
        return data['strategy_id']
    else:
        print(f"❌ 失败: {response.text}")
        return None

def test_accept_strategy(strategy_id, choice):
    """测试接受策略"""
    print(f"\n=== 测试3: 接受策略 (选择{choice}) ===")
    payload = {
        "username": "bbb",
        "strategy_id": strategy_id,
        "choice": choice  # 1=期权, 2=股票
    }
    response = requests.post(
        f'{BASE_URL}/api/dual-strategy/accept',
        json=payload
    )
    print(f"状态码: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"✅ 开仓成功!")
        print(f"持仓ID: {data['position_id']}")
        print(f"实盘类型: {data['actual_type']}")
        print(f"实盘成本: ${data['actual_cost']:.2f}")
        print(f"虚拟类型: {data['virtual_type']}")
        print(f"账户余额: ${data['balance_after']:.2f}")
        return data['position_id']
    else:
        print(f"❌ 失败: {response.text}")
        return None

def test_get_positions():
    """测试查询持仓"""
    print("\n=== 测试4: 查询持仓列表 ===")
    response = requests.get(f'{BASE_URL}/api/fund/positions/bbb')
    print(f"状态码: {response.status_code}")
    if response.ok:
        data = response.json()
        positions = data['positions']
        print(f"持仓数量: {len(positions)}")
        for i, pos in enumerate(positions, 1):
            print(f"\n持仓 #{i}:")
            print(f"  状态: {pos['status']}")
            print(f"  股票: {pos['symbol']}")
            print(f"  A组({pos['actual']['type']}): 成本${pos['actual']['cost']:.2f}, 盈亏${pos['actual']['pnl']:.2f}")
            print(f"  B组({pos['virtual']['type']}): 成本${pos['virtual']['cost']:.2f}, 盈亏${pos['virtual']['pnl']:.2f}")
        return True
    else:
        print(f"❌ 失败: {response.text}")
        return False

def test_close_position(position_id):
    """测试平仓"""
    print(f"\n=== 测试5: 平仓 (ID={position_id}) ===")
    payload = {
        "username": "bbb",
        "position_id": position_id,
        "trigger": "MANUAL"
    }
    response = requests.post(
        f'{BASE_URL}/api/position/close',
        json=payload
    )
    print(f"状态码: {response.status_code}")
    if response.ok:
        data = response.json()
        print(f"✅ 平仓成功!")
        print(f"实际收益: ${data['actual_pnl']:.2f} ({data['actual_return']})")
        print(f"虚拟收益: ${data['virtual_pnl']:.2f} ({data['virtual_return']})")
        print(f"后悔值: {data['regret_value']}")
        print(f"是否最优: {'是' if data['optimal_choice'] else '否'}")
        print(f"持有天数: {data['holding_days']}")
        print(f"账户余额: ${data['balance_after']:.2f}")
        return True
    else:
        print(f"❌ 失败: {response.text}")
        return False

def test_transactions():
    """测试查询流水"""
    print("\n=== 测试6: 查询资金流水 ===")
    response = requests.get(f'{BASE_URL}/api/fund/transactions/bbb')
    print(f"状态码: {response.status_code}")
    if response.ok:
        data = response.json()
        transactions = data['transactions']
        print(f"流水记录: {len(transactions)}条")
        for i, trans in enumerate(transactions[:5], 1):  # 只显示前5条
            print(f"\n记录 #{i}:")
            print(f"  类型: {trans['type']}")
            print(f"  金额: ${trans['amount']:.2f}")
            print(f"  余额: ${trans['balance_after']:.2f}")
            print(f"  说明: {trans['description']}")
        return True
    else:
        print(f"❌ 失败: {response.text}")
        return False

if __name__ == '__main__':
    print("🚀 开始测试资金管理系统...")
    print(f"测试环境: {BASE_URL}")
    
    # 测试1: 查询账户
    if not test_account():
        print("\n❌ 账户查询失败，停止测试")
        exit(1)
    
    # 测试2: 生成策略
    strategy_id = test_generate_strategy()
    if not strategy_id:
        print("\n❌ 策略生成失败，停止测试")
        exit(1)
    
    # 测试3: 接受策略（选择期权）
    position_id = test_accept_strategy(strategy_id, choice=1)
    if not position_id:
        print("\n❌ 接受策略失败，停止测试")
        exit(1)
    
    # 测试4: 查询持仓
    if not test_get_positions():
        print("\n❌ 查询持仓失败")
    
    # 测试5: 平仓
    if not test_close_position(position_id):
        print("\n❌ 平仓失败")
    
    # 测试6: 查询流水
    if not test_transactions():
        print("\n❌ 查询流水失败")
    
    # 最终账户状态
    print("\n=== 最终账户状态 ===")
    test_account()
    
    print("\n✅ 所有测试完成！")

