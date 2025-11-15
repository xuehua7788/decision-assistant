#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成模拟训练数据
模拟用户的交易决策和结果
"""

import psycopg2
import random
from datetime import datetime, timedelta
import json

DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

def get_db_connection():
    """获取数据库连接"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def generate_mock_positions_for_user(user_id, num_positions=20):
    """为特定用户生成模拟持仓数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 获取或创建策略
        cursor.execute("SELECT strategy_id, option_premium, stock_margin, current_price, volatility, rsi FROM strategies ORDER BY create_time DESC LIMIT 10")
        strategies = cursor.fetchall()
        
        if not strategies:
            print("⚠️ 没有策略数据，先生成策略...")
            generate_mock_strategies(10)
            cursor.execute("SELECT strategy_id, option_premium, stock_margin, current_price, volatility, rsi FROM strategies ORDER BY create_time DESC LIMIT 10")
            strategies = cursor.fetchall()
        
        # 随机用户类型
        user_type = random.choice(['aggressive', 'moderate', 'conservative'])
        user_profiles = {
            'aggressive': {'option_preference': 0.7, 'avg_return': 0.15},
            'moderate': {'option_preference': 0.5, 'avg_return': 0.10},
            'conservative': {'option_preference': 0.3, 'avg_return': 0.08}
        }
        profile = user_profiles[user_type]
        
        print(f"   为用户 {user_id} 生成 {num_positions} 条数据（类型: {user_type}）...")
        
        for i in range(num_positions):
            strategy_id, option_premium, stock_margin, current_price, volatility, rsi = random.choice(strategies)
            
            # 账户状态
            available_cash = random.uniform(30000, 100000)
            total_pnl = random.uniform(-5000, 10000)
            position_count = random.randint(0, 5)
            
            # 决策逻辑
            option_score = profile['option_preference']
            if volatility > 0.5:
                option_score += 0.2
            if rsi > 70 or rsi < 30:
                option_score += 0.15
            if available_cash < 50000:
                option_score += 0.15
            option_score += random.uniform(-0.2, 0.2)
            
            user_choice = 1 if option_score > 0.5 else 2
            
            # 实际和虚拟
            if user_choice == 1:
                actual_type = 'OPTION'
                actual_cost = float(option_premium)
                virtual_type = 'STOCK'
                virtual_cost = float(stock_margin)
            else:
                actual_type = 'STOCK'
                actual_cost = float(stock_margin)
                virtual_type = 'OPTION'
                virtual_cost = float(option_premium)
            
            # 模拟收益
            base_return = profile['avg_return']
            market_factor = (float(volatility) - 0.4) * 0.5
            random_factor = random.uniform(-0.1, 0.15)
            
            actual_return = base_return + market_factor + random_factor
            virtual_return = base_return + market_factor + random.uniform(-0.1, 0.15)
            
            if actual_type == 'OPTION':
                actual_return *= random.uniform(0.8, 2.0)
            
            # 最优选择
            optimal_choice = 1 if actual_return > virtual_return else 2
            
            # 时间
            decision_time = datetime.now() - timedelta(days=random.randint(1, 90))
            close_time = decision_time + timedelta(days=random.randint(1, 30))
            holding_days = (close_time - decision_time).days
            
            # 插入数据
            cursor.execute("""
                INSERT INTO positions (
                    user_id, strategy_id, user_choice, optimal_choice,
                    actual_type, actual_cost, actual_return,
                    virtual_type, virtual_cost, virtual_return,
                    regret_value, holding_days,
                    market_state, account_state,
                    decision_time, close_time, status
                ) VALUES (
                    %s, %s, %s, %s,
                    %s, %s, %s,
                    %s, %s, %s,
                    %s, %s,
                    %s, %s,
                    %s, %s, %s
                )
            """, (
                user_id, strategy_id, user_choice, optimal_choice,
                actual_type, actual_cost, actual_return,
                virtual_type, virtual_cost, virtual_return,
                abs(actual_return - virtual_return), holding_days,
                json.dumps({
                    'current_price': float(current_price),
                    'volatility': float(volatility),
                    'rsi': float(rsi),
                    'volume_ratio': random.uniform(0.5, 2.0)
                }),
                json.dumps({
                    'available_cash': available_cash,
                    'position_count': position_count,
                    'total_pnl': total_pnl
                }),
                decision_time, close_time, 'CLOSED'
            ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"   ✅ 成功为用户 {user_id} 生成 {num_positions} 条模拟数据")
        return True
        
    except Exception as e:
        print(f"   ❌ 生成失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()
        return False


def generate_mock_strategies(num_strategies=30):
    """生成模拟策略数据"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        symbols = ['TSLA', 'AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META']
        
        print(f"\n📊 生成 {num_strategies} 个模拟策略...")
        
        for i in range(num_strategies):
            symbol = random.choice(symbols)
            
            # 随机市场状态
            current_price = random.uniform(100, 300)
            volatility = random.uniform(0.2, 0.7)
            rsi = random.uniform(30, 80)
            volume_ratio = random.uniform(0.5, 2.0)
            
            # 期权策略
            option_type = random.choice(['CALL', 'PUT'])
            strike_price = current_price * random.uniform(0.95, 1.05)
            option_premium = current_price * random.uniform(0.02, 0.05)
            option_delta = random.uniform(0.3, 0.8)
            
            # 股票策略
            notional_value = 30000.0
            stock_amount = notional_value * option_delta
            stock_margin = stock_amount * 0.1
            
            strategy_id = f"{symbol}_{datetime.now().strftime('%Y%m%d')}_{i:04d}"
            
            cursor.execute("""
                INSERT INTO strategies (
                    strategy_id, symbol, company_name, notional_value,
                    option_type, strike_price, option_premium, option_delta,
                    stock_amount, stock_margin,
                    current_price, volatility, rsi, volume_ratio
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (strategy_id) DO NOTHING
            """, (
                strategy_id, symbol, f"{symbol} Inc", notional_value,
                option_type, strike_price, option_premium, option_delta,
                stock_amount, stock_margin,
                current_price, volatility, rsi, volume_ratio
            ))
            
            if (i + 1) % 10 == 0:
                print(f"   已生成 {i + 1}/{num_strategies} 个策略")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 策略生成完成！")
        return True
        
    except Exception as e:
        print(f"❌ 生成策略失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False


def generate_mock_positions(num_positions=50):
    """生成模拟持仓数据（已平仓）"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 获取用户
        cursor.execute("SELECT id, username FROM users LIMIT 5")
        users = cursor.fetchall()
        
        if not users:
            print("❌ 没有用户数据")
            return False
        
        # 获取策略
        cursor.execute("SELECT strategy_id, option_premium, stock_margin, current_price, volatility, rsi FROM strategies ORDER BY create_time DESC LIMIT 30")
        strategies = cursor.fetchall()
        
        if not strategies:
            print("❌ 没有策略数据")
            return False
        
        print(f"\n📈 生成 {num_positions} 个模拟持仓（已平仓）...")
        
        # 定义用户类型（影响决策）
        user_types = {
            'aggressive': {
                'risk_tolerance': 'aggressive',
                'option_preference': 0.7,  # 70%选期权
                'avg_return': 0.15
            },
            'moderate': {
                'risk_tolerance': 'moderate',
                'option_preference': 0.5,  # 50%选期权
                'avg_return': 0.10
            },
            'conservative': {
                'risk_tolerance': 'conservative',
                'option_preference': 0.3,  # 30%选期权
                'avg_return': 0.08
            }
        }
        
        for i in range(num_positions):
            user_id, username = random.choice(users)
            strategy_id, option_premium, stock_margin, current_price, volatility, rsi = random.choice(strategies)
            
            # 随机用户类型
            user_type = random.choice(list(user_types.keys()))
            profile = user_types[user_type]
            
            # 账户状态（随机但合理）
            available_cash = random.uniform(30000, 100000)
            total_pnl = random.uniform(-5000, 10000)
            position_count = random.randint(0, 5)
            margin_occupied = position_count * random.uniform(1000, 3000)
            
            # 决策逻辑：基于市场状态和用户类型
            option_score = 0
            
            # 高波动 → 倾向期权
            if volatility > 0.5:
                option_score += 0.3
            
            # RSI超买/超卖 → 倾向期权
            if rsi > 70 or rsi < 30:
                option_score += 0.2
            
            # 现金不足 → 倾向期权
            if available_cash < 50000:
                option_score += 0.2
            
            # 用户偏好
            option_score += profile['option_preference']
            
            # 随机因素
            option_score += random.uniform(-0.2, 0.2)
            
            # 做决策
            user_choice = 1 if option_score > 0.5 else 2  # 1=期权, 2=股票
            
            # 实际和虚拟
            if user_choice == 1:
                actual_type = 'OPTION'
                actual_cost = float(option_premium)
                virtual_type = 'STOCK'
                virtual_cost = float(stock_margin)
            else:
                actual_type = 'STOCK'
                actual_cost = float(stock_margin)
                virtual_type = 'OPTION'
                virtual_cost = float(option_premium)
            
            # 模拟收益（基于市场和用户类型）
            base_return = profile['avg_return']
            market_factor = (float(volatility) - 0.4) * 0.5  # 波动率影响
            random_factor = random.uniform(-0.1, 0.15)
            
            actual_return = base_return + market_factor + random_factor
            virtual_return = base_return + market_factor + random.uniform(-0.1, 0.15)
            
            # 如果选期权，收益波动更大
            if actual_type == 'OPTION':
                actual_return *= random.uniform(0.8, 2.0)
            
            actual_pnl = actual_cost * actual_return
            virtual_pnl = virtual_cost * virtual_return
            
            actual_current_value = actual_cost + actual_pnl
            virtual_current_value = virtual_cost + virtual_pnl
            
            # 后悔值
            regret_value = virtual_return - actual_return
            optimal_choice = 1 if regret_value <= 0 else 0
            
            # 持有天数
            holding_days = random.randint(1, 30)
            
            # 决策时间和平仓时间
            decision_time = datetime.now() - timedelta(days=holding_days+random.randint(1, 10))
            close_time = decision_time + timedelta(days=holding_days)
            
            # 市场状态快照
            market_state = {
                'current_price': float(current_price),
                'volatility': float(volatility),
                'rsi': float(rsi),
                'volume_ratio': random.uniform(0.8, 1.5)
            }
            
            # 账户状态快照
            account_state = {
                'available_cash': float(available_cash),
                'total_pnl': float(total_pnl),
                'position_count': position_count,
                'margin_occupied': float(margin_occupied)
            }
            
            cursor.execute("""
                INSERT INTO positions (
                    user_id, strategy_id, decision_time, user_choice,
                    actual_type, actual_cost, actual_current_value, actual_pnl,
                    virtual_type, virtual_cost, virtual_current_value, virtual_pnl,
                    status, close_time, close_trigger,
                    market_state, account_state,
                    actual_return, virtual_return, regret_value, optimal_choice, holding_days
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                user_id, strategy_id, decision_time, user_choice,
                actual_type, actual_cost, actual_current_value, actual_pnl,
                virtual_type, virtual_cost, virtual_current_value, virtual_pnl,
                'CLOSED', close_time, 'MANUAL',
                json.dumps(market_state), json.dumps(account_state),
                actual_return, virtual_return, regret_value, optimal_choice, holding_days
            ))
            
            if (i + 1) % 10 == 0:
                print(f"   已生成 {i + 1}/{num_positions} 个持仓")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 持仓生成完成！")
        return True
        
    except Exception as e:
        print(f"❌ 生成持仓失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False


def show_data_summary():
    """显示数据摘要"""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        print(f"\n{'='*60}")
        print(f"📊 数据摘要")
        print(f"{'='*60}")
        
        # 策略数量
        cursor.execute("SELECT COUNT(*) FROM strategies")
        strategy_count = cursor.fetchone()[0]
        print(f"策略总数: {strategy_count}")
        
        # 持仓数量
        cursor.execute("SELECT COUNT(*) FROM positions WHERE status = 'CLOSED'")
        closed_count = cursor.fetchone()[0]
        print(f"已平仓持仓: {closed_count}")
        
        # 选择分布
        cursor.execute("""
            SELECT 
                user_choice,
                COUNT(*) as count,
                ROUND(AVG(actual_return)::numeric, 4) as avg_return
            FROM positions 
            WHERE status = 'CLOSED'
            GROUP BY user_choice
        """)
        
        print(f"\n选择分布:")
        for row in cursor.fetchall():
            choice_label = "期权" if row[0] == 1 else "股票"
            print(f"  {choice_label}: {row[1]} 次 (平均收益率: {float(row[2]):.2%})")
        
        # 最优选择率
        cursor.execute("""
            SELECT 
                ROUND(AVG(optimal_choice::int)::numeric, 4) as optimal_rate
            FROM positions 
            WHERE status = 'CLOSED'
        """)
        optimal_rate = cursor.fetchone()[0]
        print(f"\n最优选择率: {float(optimal_rate):.2%}")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ 获取摘要失败: {e}")
        if conn:
            conn.close()


if __name__ == "__main__":
    print(f"\n{'#'*60}")
    print(f"🎲 生成模拟训练数据")
    print(f"{'#'*60}")
    
    # 1. 生成策略
    if generate_mock_strategies(30):
        print(f"✅ Step 1: 策略生成完成")
    else:
        print(f"❌ Step 1: 策略生成失败")
        exit(1)
    
    # 2. 生成持仓
    if generate_mock_positions(50):
        print(f"✅ Step 2: 持仓生成完成")
    else:
        print(f"❌ Step 2: 持仓生成失败")
        exit(1)
    
    # 3. 显示摘要
    show_data_summary()
    
    print(f"\n{'='*60}")
    print(f"✅ 模拟数据生成完成！")
    print(f"{'='*60}")
    print(f"\n下一步: 运行 python ml_decision_tree.py train")

