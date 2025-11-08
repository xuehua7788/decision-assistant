#!/usr/bin/env python3
"""
完整测试双策略系统
"""
import requests
import json

BASE_URL = "http://localhost:8000"
USERNAME = "test_user"

def test_dual_strategy_flow():
    """测试完整的双策略流程"""
    print("=" * 60)
    print("🧪 测试双策略系统完整流程")
    print("=" * 60)
    
    # 1. 生成双策略
    print("\n【步骤1】生成双策略（期权+股票）")
    print("-" * 60)
    
    generate_data = {
        "symbol": "AAPL",
        "username": USERNAME,
        "notional_value": 10000,
        "investment_style": "balanced"
    }
    
    print(f"请求: POST {BASE_URL}/api/dual-strategy/generate")
    print(f"参数: {json.dumps(generate_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/dual-strategy/generate",
            json=generate_data,
            timeout=30
        )
        
        print(f"\n响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 双策略生成成功！")
            print(f"\n策略ID: {data['strategy_id']}")
            print(f"股票代码: {data['symbol']}")
            print(f"当前股价: ${data['current_price']}")
            print(f"名义本金: ${data['notional_value']}")
            
            # 期权策略
            option = data['option_strategy']
            print(f"\n📊 期权策略:")
            print(f"  类型: {option['type']}")
            print(f"  合约数: {option['contracts']}手")
            print(f"  执行价: ${option['strike_price']}")
            print(f"  到期日: {option['expiry_date']} ({option['days_to_expiry']}天)")
            print(f"  期权费: ${option['premium']:.2f}")
            print(f"  Delta: {option['delta']:.4f}")
            print(f"  组合Delta: {option['portfolio_delta']:.4f}")
            print(f"  数据源: {option.get('data_source', 'N/A')}")
            
            # 股票策略
            stock = data['stock_strategy']
            print(f"\n📈 股票策略:")
            print(f"  类型: {stock['type']}")
            print(f"  股数: {stock['shares']}股")
            print(f"  入场价: ${stock['entry_price']:.2f}")
            print(f"  总金额: ${stock['amount']:.2f}")
            print(f"  保证金: ${stock['margin']:.2f}")
            print(f"  止损价: ${stock['stop_loss']:.2f}")
            print(f"  止盈价: ${stock['take_profit']:.2f}")
            print(f"  组合Delta: {stock['portfolio_delta']:.4f}")
            
            # 验证计算
            print(f"\n🔍 验证计算:")
            expected_stock_amount = data['notional_value'] * abs(option['portfolio_delta'])
            print(f"  预期股票金额: ${data['notional_value']} × {abs(option['portfolio_delta']):.4f} = ${expected_stock_amount:.2f}")
            print(f"  实际股票金额: ${stock['amount']:.2f}")
            print(f"  {'✅ 计算正确' if abs(expected_stock_amount - stock['amount']) < 1 else '❌ 计算错误'}")
            
            expected_margin = stock['amount'] * 0.1
            print(f"  预期保证金: ${stock['amount']:.2f} × 10% = ${expected_margin:.2f}")
            print(f"  实际保证金: ${stock['margin']:.2f}")
            print(f"  {'✅ 计算正确' if abs(expected_margin - stock['margin']) < 0.1 else '❌ 计算错误'}")
            
            return data['strategy_id']
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return None

def test_account_balance():
    """测试账户余额查询"""
    print("\n" + "=" * 60)
    print("【步骤2】查询账户余额")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/fund/account/{USERNAME}")
        print(f"请求: GET {BASE_URL}/api/fund/account/{USERNAME}")
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 账户信息:")
            print(f"  总现金: ${data['total_cash']:,.2f}")
            print(f"  可用现金: ${data['available_cash']:,.2f}")
            print(f"  保证金占用: ${data['margin_occupied']:,.2f}")
            print(f"  持仓价值: ${data['position_value']:,.2f}")
            print(f"  持仓数量: {data['position_count']}")
            return data
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_accept_strategy(strategy_id, choice):
    """测试接受策略"""
    print("\n" + "=" * 60)
    print(f"【步骤3】接受策略 (选择: {'期权' if choice == 1 else '股票'})")
    print("-" * 60)
    
    accept_data = {
        "username": USERNAME,
        "strategy_id": strategy_id,
        "choice": choice
    }
    
    print(f"请求: POST {BASE_URL}/api/dual-strategy/accept")
    print(f"参数: {json.dumps(accept_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/dual-strategy/accept",
            json=accept_data
        )
        
        print(f"\n响应状态: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ 策略接受成功！")
                print(f"\n持仓ID: {data['position_id']}")
                print(f"实盘类型: {data['actual_type']}")
                print(f"实盘成本: ${data['actual_cost']:.2f}")
                print(f"虚拟类型: {data['virtual_type']}")
                print(f"账户余额: ${data['balance_after']:.2f}")
                return data
            else:
                print(f"❌ 接受失败: {data.get('error', '未知错误')}")
                return None
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def test_positions():
    """测试持仓查询"""
    print("\n" + "=" * 60)
    print("【步骤4】查询持仓（A/B对照组）")
    print("-" * 60)
    
    try:
        response = requests.get(f"{BASE_URL}/api/fund/positions/{USERNAME}")
        print(f"请求: GET {BASE_URL}/api/fund/positions/{USERNAME}")
        print(f"响应状态: {response.status_code}")
        
        if response.status_code == 200:
            positions = response.json()
            print(f"✅ 找到 {len(positions)} 个持仓")
            
            for i, pos in enumerate(positions, 1):
                print(f"\n持仓 #{i}:")
                print(f"  策略ID: {pos['strategy_id']}")
                print(f"  用户选择: {'期权' if pos['user_choice'] == 1 else '股票'}")
                print(f"  A组(实盘): {pos['actual_type']} - 成本${pos['actual_cost']:.2f}, 盈亏${pos['actual_pnl']:.2f}")
                print(f"  B组(虚拟): {pos['virtual_type']} - 成本${pos['virtual_cost']:.2f}, 盈亏${pos['virtual_pnl']:.2f}")
                print(f"  状态: {pos['status']}")
            
            return positions
        else:
            print(f"❌ 请求失败: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

if __name__ == '__main__':
    print("\n🚀 开始测试...")
    print(f"后端地址: {BASE_URL}")
    print(f"测试用户: {USERNAME}")
    
    # 测试流程
    strategy_id = test_dual_strategy_flow()
    
    if strategy_id:
        test_account_balance()
        
        # 测试接受期权策略
        result = test_accept_strategy(strategy_id, choice=1)
        
        if result:
            test_account_balance()
            test_positions()
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

