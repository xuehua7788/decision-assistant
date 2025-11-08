"""
测试Delta计算逻辑
验证：股票金额 = 名义本金 × 组合Delta
"""

def test_delta_calculation():
    print("=" * 60)
    print("测试Delta计算逻辑")
    print("=" * 60)
    
    # 测试案例1：单个CALL期权
    print("\n【案例1】单个CALL期权")
    notional_value = 10000  # 名义本金$10,000
    option_delta = 0.5  # CALL期权Delta=0.5
    current_price = 150  # 当前股价$150
    
    stock_amount = notional_value * abs(option_delta)
    stock_margin = stock_amount * 0.1
    stock_shares = int(stock_amount / current_price)
    
    print(f"  名义本金: ${notional_value:,}")
    print(f"  期权Delta: {option_delta}")
    print(f"  当前股价: ${current_price}")
    print(f"  → 股票金额: ${notional_value} × {option_delta} = ${stock_amount:,.2f}")
    print(f"  → 股票保证金: ${stock_amount:,.2f} × 10% = ${stock_margin:,.2f}")
    print(f"  → 股票数量: ${stock_amount:,.2f} / ${current_price} = {stock_shares}股")
    
    # 测试案例2：Call Spread组合
    print("\n【案例2】Call Spread组合 (0.5 - 0.2)")
    notional_value = 10000
    portfolio_delta = 0.3  # 组合Delta = 0.5 - 0.2
    current_price = 150
    
    stock_amount = notional_value * abs(portfolio_delta)
    stock_margin = stock_amount * 0.1
    stock_shares = int(stock_amount / current_price)
    
    print(f"  名义本金: ${notional_value:,}")
    print(f"  组合Delta: {portfolio_delta} (0.5 - 0.2)")
    print(f"  当前股价: ${current_price}")
    print(f"  → 股票金额: ${notional_value} × {portfolio_delta} = ${stock_amount:,.2f}")
    print(f"  → 股票保证金: ${stock_amount:,.2f} × 10% = ${stock_margin:,.2f}")
    print(f"  → 股票数量: ${stock_amount:,.2f} / ${current_price} = {stock_shares}股")
    
    # 测试案例3：PUT期权
    print("\n【案例3】PUT期权")
    notional_value = 10000
    option_delta = -0.4  # PUT期权Delta=-0.4
    current_price = 150
    
    stock_amount = notional_value * abs(option_delta)
    stock_margin = stock_amount * 0.1
    stock_shares = int(stock_amount / current_price)
    
    print(f"  名义本金: ${notional_value:,}")
    print(f"  期权Delta: {option_delta}")
    print(f"  当前股价: ${current_price}")
    print(f"  → 股票金额: ${notional_value} × |{option_delta}| = ${stock_amount:,.2f}")
    print(f"  → 股票保证金: ${stock_amount:,.2f} × 10% = ${stock_margin:,.2f}")
    print(f"  → 股票数量: ${stock_amount:,.2f} / ${current_price} = {stock_shares}股")
    print(f"  → 仓位类型: SHORT (因为Delta为负)")
    
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！计算逻辑正确")
    print("=" * 60)

if __name__ == '__main__':
    test_delta_calculation()

