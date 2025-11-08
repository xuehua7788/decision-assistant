"""
双策略推荐API（期权 + Delta One股票）
"""
from flask import Blueprint, request, jsonify
import psycopg2
import os
import json
from datetime import datetime, timedelta
from decimal import Decimal
import requests

dual_strategy_bp = Blueprint('dual_strategy', __name__)

def get_db_connection():
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l')
    return psycopg2.connect(DATABASE_URL)

def get_user_id(username):
    """根据用户名获取user_id"""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM users WHERE username = %s", (username,))
    result = cur.fetchone()
    cur.close()
    conn.close()
    return result[0] if result else None

def get_stock_data(symbol):
    """
    从Alpha Vantage获取股票实时数据
    """
    API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')
    url = f'https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={API_KEY}'
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if 'Global Quote' in data and data['Global Quote']:
            quote = data['Global Quote']
            return {
                'price': float(quote.get('05. price', 0)),
                'change_percent': float(quote.get('10. change percent', '0').replace('%', '')),
                'volume': int(quote.get('06. volume', 0))
            }
    except Exception as e:
        print(f"❌ 获取股票数据失败: {e}")
    
    return None

def calculate_option_delta(option_type, strike_price, current_price, days_to_expiry):
    """
    简化的Delta计算（实际应使用Black-Scholes模型）
    这里用近似公式：
    - CALL: Delta ≈ 0.5 + (current_price - strike_price) / (2 * strike_price) * (90 / days_to_expiry)
    - PUT: Delta ≈ -0.5 + (strike_price - current_price) / (2 * strike_price) * (90 / days_to_expiry)
    """
    if option_type == 'CALL':
        if current_price >= strike_price:
            # 实值期权
            delta = 0.5 + min(0.4, (current_price - strike_price) / strike_price * 0.5)
        else:
            # 虚值期权
            delta = 0.5 - min(0.4, (strike_price - current_price) / strike_price * 0.5)
    else:  # PUT
        if current_price <= strike_price:
            # 实值期权
            delta = -0.5 - min(0.4, (strike_price - current_price) / strike_price * 0.5)
        else:
            # 虚值期权
            delta = -0.5 + min(0.4, (current_price - strike_price) / strike_price * 0.5)
    
    # 时间衰减影响
    time_factor = min(1.0, days_to_expiry / 90)
    delta = delta * time_factor
    
    return round(delta, 4)

def generate_dual_strategy(symbol, current_price, notional_value, investment_style='balanced'):
    """
    生成双策略：期权 + Delta One股票
    
    参数：
    - symbol: 股票代码
    - current_price: 当前股价
    - notional_value: 名义本金（两策略相同）
    - investment_style: 投资风格（影响期权选择）
    
    返回：
    - option_strategy: 期权策略详情
    - stock_strategy: 股票策略详情
    """
    
    # 1. 生成期权策略（3个月平值期权）
    days_to_expiry = 90
    expiry_date = (datetime.now() + timedelta(days=days_to_expiry)).date()
    
    # 根据投资风格选择期权类型和执行价
    if investment_style in ['aggressive', 'momentum']:
        option_type = 'CALL'
        strike_price = current_price * 1.05  # 5%虚值看涨
    elif investment_style in ['conservative', 'value']:
        option_type = 'PUT'
        strike_price = current_price * 0.95  # 5%虚值看跌
    else:  # balanced
        option_type = 'CALL'
        strike_price = current_price  # 平值
    
    # 计算期权费（简化：约为名义本金的3-5%）
    option_premium = notional_value * 0.04  # 4%
    
    # 计算Delta
    option_delta = calculate_option_delta(option_type, strike_price, current_price, days_to_expiry)
    
    option_strategy = {
        'type': option_type,
        'strike_price': round(strike_price, 2),
        'expiry_date': expiry_date.isoformat(),
        'days_to_expiry': days_to_expiry,
        'premium': round(option_premium, 2),
        'delta': option_delta,
        'notional_value': notional_value,
        'contracts': int(notional_value / (current_price * 100)),  # 假设1手=100股
        'description': f"{option_type} 期权，执行价 ${strike_price:.2f}，{days_to_expiry}天到期"
    }
    
    # 2. 生成Delta One股票策略
    stock_amount = abs(option_delta) * notional_value  # Delta × 名义本金
    stock_margin = stock_amount * 0.1  # 10%保证金
    stock_shares = int(stock_amount / current_price)
    
    # 设置止盈止损
    if option_type == 'CALL':
        stop_loss = current_price * 0.9  # -10%止损
        take_profit = current_price * 1.2  # +20%止盈
    else:
        stop_loss = current_price * 1.1  # +10%止损（做空）
        take_profit = current_price * 0.8  # -20%止盈（做空）
    
    stock_strategy = {
        'type': 'LONG' if option_delta > 0 else 'SHORT',
        'amount': round(stock_amount, 2),
        'margin': round(stock_margin, 2),
        'shares': stock_shares,
        'entry_price': current_price,
        'stop_loss': round(stop_loss, 2),
        'take_profit': round(take_profit, 2),
        'delta': option_delta,
        'notional_value': notional_value,
        'description': f"{'做多' if option_delta > 0 else '做空'} {stock_shares}股，保证金 ${stock_margin:.2f}"
    }
    
    return option_strategy, stock_strategy

@dual_strategy_bp.route('/api/dual-strategy/generate', methods=['POST'])
def generate_strategy():
    """
    生成双策略推荐
    
    请求体：
    {
        "symbol": "AAPL",
        "username": "bbb",
        "notional_value": 10000,  // 名义本金
        "investment_style": "aggressive"  // 可选
    }
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        username = data.get('username')
        notional_value = float(data.get('notional_value', 10000))
        investment_style = data.get('investment_style', 'balanced')
        
        if not symbol or not username:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 获取实时股价
        stock_data = get_stock_data(symbol)
        if not stock_data:
            return jsonify({'error': '无法获取股票数据'}), 500
        
        current_price = stock_data['price']
        
        # 生成双策略
        option_strategy, stock_strategy = generate_dual_strategy(
            symbol, current_price, notional_value, investment_style
        )
        
        # 生成策略ID
        strategy_id = f"{symbol}_{int(datetime.now().timestamp())}_{investment_style}"
        
        # 保存到数据库
        conn = get_db_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO strategies (
                strategy_id, symbol, notional_value,
                option_type, strike_price, expiry_date, option_premium, option_delta,
                stock_amount, stock_margin,
                current_price, option_strategy_detail, stock_strategy_detail
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            strategy_id, symbol, notional_value,
            option_strategy['type'], option_strategy['strike_price'], 
            option_strategy['expiry_date'], option_strategy['premium'], option_strategy['delta'],
            stock_strategy['amount'], stock_strategy['margin'],
            current_price, json.dumps(option_strategy), json.dumps(stock_strategy)
        ))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'strategy_id': strategy_id,
            'symbol': symbol,
            'current_price': current_price,
            'notional_value': notional_value,
            'option_strategy': option_strategy,
            'stock_strategy': stock_strategy,
            'created_at': datetime.now().isoformat()
        }), 200
        
    except Exception as e:
        print(f"❌ 生成策略失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@dual_strategy_bp.route('/api/dual-strategy/accept', methods=['POST'])
def accept_strategy():
    """
    接受策略（实际下单）
    
    请求体：
    {
        "username": "bbb",
        "strategy_id": "AAPL_1234567890_aggressive",
        "choice": 1  // 1=期权, 2=股票
    }
    """
    try:
        data = request.json
        username = data.get('username')
        strategy_id = data.get('strategy_id')
        choice = int(data.get('choice'))  # 1=期权, 2=股票
        
        if not username or not strategy_id or choice not in [1, 2]:
            return jsonify({'error': '参数错误'}), 400
        
        user_id = get_user_id(username)
        if not user_id:
            return jsonify({'error': '用户不存在'}), 404
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. 获取策略详情
        cur.execute("""
            SELECT 
                option_premium, option_delta, stock_amount, stock_margin,
                option_strategy_detail, stock_strategy_detail, current_price, symbol
            FROM strategies
            WHERE strategy_id = %s
        """, (strategy_id,))
        
        strategy = cur.fetchone()
        if not strategy:
            return jsonify({'error': '策略不存在'}), 404
        
        option_premium = float(strategy[0])
        option_delta = float(strategy[1])
        stock_amount = float(strategy[2])
        stock_margin = float(strategy[3])
        option_detail = strategy[4]
        stock_detail = strategy[5]
        current_price = float(strategy[6])
        symbol = strategy[7]
        
        # 2. 检查账户余额
        cur.execute("SELECT available_cash FROM accounts WHERE user_id = %s", (user_id,))
        available_cash = float(cur.fetchone()[0])
        
        if choice == 1:
            # 选择期权：需要支付期权费
            required_cash = option_premium
            actual_type = 'OPTION'
            actual_cost = option_premium
            virtual_type = 'STOCK'
            virtual_cost = stock_margin
        else:
            # 选择股票：需要保证金
            required_cash = stock_margin
            actual_type = 'STOCK'
            actual_cost = stock_margin
            virtual_type = 'OPTION'
            virtual_cost = option_premium
        
        if available_cash < required_cash:
            return jsonify({
                'error': '资金不足',
                'required': required_cash,
                'available': available_cash
            }), 400
        
        # 3. 创建持仓记录（A/B对照组）
        cur.execute("""
            INSERT INTO positions (
                user_id, strategy_id, user_choice,
                actual_type, actual_cost, actual_current_value,
                virtual_type, virtual_cost, virtual_current_value,
                stop_loss, take_profit, status
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'OPEN')
            RETURNING position_id
        """, (
            user_id, strategy_id, choice,
            actual_type, actual_cost, actual_cost,
            virtual_type, virtual_cost, virtual_cost,
            stock_detail.get('stop_loss') if choice == 2 else None,
            stock_detail.get('take_profit') if choice == 2 else None
        ))
        
        position_id = cur.fetchone()[0]
        
        # 4. 扣除资金
        if choice == 1:
            # 期权：扣除期权费
            cur.execute("""
                UPDATE accounts
                SET total_cash = total_cash - %s,
                    available_cash = available_cash - %s,
                    position_count = position_count + 1
                WHERE user_id = %s
            """, (option_premium, option_premium, user_id))
            
            description = f"开仓期权 {symbol}，支付期权费 ${option_premium:.2f}"
            
        else:
            # 股票：扣除保证金
            cur.execute("""
                UPDATE accounts
                SET margin_occupied = margin_occupied + %s,
                    available_cash = available_cash - %s,
                    position_value = position_value + %s,
                    position_count = position_count + 1
                WHERE user_id = %s
            """, (stock_margin, stock_margin, stock_amount, user_id))
            
            description = f"开仓股票 {symbol}，占用保证金 ${stock_margin:.2f}"
        
        # 5. 记录流水
        cur.execute("SELECT total_cash FROM accounts WHERE user_id = %s", (user_id,))
        balance_after = float(cur.fetchone()[0])
        
        cur.execute("""
            INSERT INTO transactions (user_id, position_id, type, amount, balance_after, description)
            VALUES (%s, %s, 'OPEN', %s, %s, %s)
        """, (user_id, position_id, -required_cash, balance_after, description))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'position_id': position_id,
            'actual_type': actual_type,
            'actual_cost': actual_cost,
            'virtual_type': virtual_type,
            'balance_after': balance_after,
            'message': f"成功开仓{actual_type}策略"
        }), 200
        
    except Exception as e:
        print(f"❌ 接受策略失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("双策略API模块")

