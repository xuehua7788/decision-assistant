"""
平仓API
处理手动平仓、止盈止损、到期平仓
"""
from flask import Blueprint, request, jsonify
import psycopg2
import os
from datetime import datetime
from decimal import Decimal

close_bp = Blueprint('close', __name__)

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

@close_bp.route('/api/position/close', methods=['POST'])
def close_position():
    """
    平仓
    
    请求体：
    {
        "username": "bbb",
        "position_id": 123,
        "trigger": "MANUAL"  // MANUAL/STOP_LOSS/TAKE_PROFIT/EXPIRY
    }
    """
    try:
        data = request.json
        username = data.get('username')
        position_id = int(data.get('position_id'))
        trigger = data.get('trigger', 'MANUAL')
        
        if not username or not position_id:
            return jsonify({'error': '参数错误'}), 400
        
        user_id = get_user_id(username)
        if not user_id:
            return jsonify({'error': '用户不存在'}), 404
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 1. 获取持仓信息
        cur.execute("""
            SELECT 
                p.user_id, p.strategy_id, p.user_choice, p.decision_time,
                p.actual_type, p.actual_cost, p.actual_current_value, p.actual_pnl,
                p.virtual_type, p.virtual_cost, p.virtual_current_value, p.virtual_pnl,
                p.status,
                s.stock_margin, s.symbol
            FROM positions p
            JOIN strategies s ON p.strategy_id = s.strategy_id
            WHERE p.position_id = %s AND p.user_id = %s
        """, (position_id, user_id))
        
        position = cur.fetchone()
        if not position:
            return jsonify({'error': '持仓不存在'}), 404
        
        if position[12] == 'CLOSED':
            return jsonify({'error': '持仓已平仓'}), 400
        
        pos_user_id = position[0]
        strategy_id = position[1]
        user_choice = position[2]
        decision_time = position[3]
        actual_type = position[4]
        actual_cost = float(position[5])
        actual_current_value = float(position[6])
        actual_pnl = float(position[7])
        virtual_type = position[8]
        virtual_cost = float(position[9])
        virtual_current_value = float(position[10])
        virtual_pnl = float(position[11])
        stock_margin = float(position[13]) if position[13] else 0
        symbol = position[14]
        
        # 2. 计算收益率和后悔值
        actual_return = actual_pnl / actual_cost if actual_cost > 0 else 0
        virtual_return = virtual_pnl / virtual_cost if virtual_cost > 0 else 0
        regret_value = virtual_return - actual_return  # 正值=选错了
        optimal_choice = 1 if regret_value <= 0 else 0  # 1=最优选择
        
        # 计算持有天数
        holding_days = (datetime.now() - decision_time).days
        
        # 3. 更新持仓状态
        cur.execute("""
            UPDATE positions
            SET 
                status = 'CLOSED',
                close_time = CURRENT_TIMESTAMP,
                close_trigger = %s,
                actual_return = %s,
                virtual_return = %s,
                regret_value = %s,
                optimal_choice = %s,
                holding_days = %s
            WHERE position_id = %s
        """, (trigger, actual_return, virtual_return, regret_value, optimal_choice, holding_days, position_id))
        
        # 4. 返还资金
        if actual_type == 'OPTION':
            # 期权平仓：返还期权当前价值
            cash_return = actual_current_value
            margin_return = 0
            
            cur.execute("""
                UPDATE accounts
                SET 
                    total_cash = total_cash + %s,
                    available_cash = available_cash + %s,
                    position_count = position_count - 1,
                    total_pnl = total_pnl + %s
                WHERE user_id = %s
            """, (cash_return, cash_return, actual_pnl, user_id))
            
            description = f"平仓期权 {symbol}，收益 ${actual_pnl:.2f}"
            
        else:  # STOCK
            # 股票平仓：返还保证金 + 盈亏
            cash_return = actual_pnl
            margin_return = stock_margin
            
            cur.execute("""
                UPDATE accounts
                SET 
                    total_cash = total_cash + %s,
                    margin_occupied = margin_occupied - %s,
                    available_cash = available_cash + %s + %s,
                    position_value = position_value - %s,
                    position_count = position_count - 1,
                    total_pnl = total_pnl + %s
                WHERE user_id = %s
            """, (cash_return, margin_return, cash_return, margin_return, actual_cost, actual_pnl, user_id))
            
            description = f"平仓股票 {symbol}，返还保证金 ${margin_return:.2f}，收益 ${actual_pnl:.2f}"
        
        # 5. 记录流水
        cur.execute("SELECT total_cash FROM accounts WHERE user_id = %s", (user_id,))
        balance_after = float(cur.fetchone()[0])
        
        cur.execute("""
            INSERT INTO transactions (user_id, position_id, type, amount, balance_after, description)
            VALUES (%s, %s, 'CLOSE', %s, %s, %s)
        """, (user_id, position_id, cash_return, balance_after, description))
        
        if margin_return > 0:
            cur.execute("""
                INSERT INTO transactions (user_id, position_id, type, amount, balance_after, description)
                VALUES (%s, %s, 'MARGIN_RETURN', %s, %s, %s)
            """, (user_id, position_id, margin_return, balance_after, f"返还保证金 ${margin_return:.2f}"))
        
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'position_id': position_id,
            'actual_pnl': actual_pnl,
            'actual_return': f"{actual_return * 100:.2f}%",
            'virtual_pnl': virtual_pnl,
            'virtual_return': f"{virtual_return * 100:.2f}%",
            'regret_value': f"{regret_value * 100:.2f}%",
            'optimal_choice': optimal_choice == 1,
            'holding_days': holding_days,
            'balance_after': balance_after,
            'message': f"平仓成功，{'选择正确' if optimal_choice == 1 else '选择错误'}！"
        }), 200
        
    except Exception as e:
        print(f"❌ 平仓失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@close_bp.route('/api/position/update', methods=['POST'])
def update_position_value():
    """
    更新持仓价值（实时计算浮动盈亏）
    
    请求体：
    {
        "position_id": 123,
        "current_price": 150.5
    }
    """
    try:
        data = request.json
        position_id = int(data.get('position_id'))
        current_price = float(data.get('current_price'))
        
        if not position_id or not current_price:
            return jsonify({'error': '参数错误'}), 400
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 获取持仓信息
        cur.execute("""
            SELECT 
                p.actual_type, p.actual_cost, p.user_choice,
                p.virtual_type, p.virtual_cost,
                p.stop_loss, p.take_profit,
                s.option_delta, s.stock_amount, s.option_premium, s.current_price as entry_price
            FROM positions p
            JOIN strategies s ON p.strategy_id = s.strategy_id
            WHERE p.position_id = %s AND p.status = 'OPEN'
        """, (position_id,))
        
        position = cur.fetchone()
        if not position:
            return jsonify({'error': '持仓不存在或已平仓'}), 404
        
        actual_type = position[0]
        actual_cost = float(position[1])
        user_choice = position[2]
        virtual_type = position[3]
        virtual_cost = float(position[4])
        stop_loss = float(position[5]) if position[5] else None
        take_profit = float(position[6]) if position[6] else None
        option_delta = float(position[7])
        stock_amount = float(position[8])
        option_premium = float(position[9])
        entry_price = float(position[10])
        
        # 计算实际持仓价值
        if actual_type == 'OPTION':
            # 期权价值 = 内在价值 + 时间价值（简化）
            intrinsic_value = max(0, (current_price - entry_price) * abs(option_delta) * stock_amount / current_price)
            time_value = option_premium * 0.5  # 假设时间价值衰减50%
            actual_current_value = intrinsic_value + time_value
        else:  # STOCK
            # 股票价值 = 价格变动 × 股数
            price_change = current_price - entry_price
            actual_current_value = actual_cost + (price_change * stock_amount / entry_price)
        
        actual_pnl = actual_current_value - actual_cost
        
        # 计算虚拟持仓价值
        if virtual_type == 'OPTION':
            intrinsic_value = max(0, (current_price - entry_price) * abs(option_delta) * stock_amount / current_price)
            time_value = option_premium * 0.5
            virtual_current_value = intrinsic_value + time_value
        else:  # STOCK
            price_change = current_price - entry_price
            virtual_current_value = virtual_cost + (price_change * stock_amount / entry_price)
        
        virtual_pnl = virtual_current_value - virtual_cost
        
        # 更新持仓
        cur.execute("""
            UPDATE positions
            SET 
                actual_current_value = %s,
                actual_pnl = %s,
                virtual_current_value = %s,
                virtual_pnl = %s
            WHERE position_id = %s
        """, (actual_current_value, actual_pnl, virtual_current_value, virtual_pnl, position_id))
        
        conn.commit()
        
        # 检查止盈止损触发
        trigger = None
        if actual_type == 'STOCK':
            if stop_loss and current_price <= stop_loss:
                trigger = 'STOP_LOSS'
            elif take_profit and current_price >= take_profit:
                trigger = 'TAKE_PROFIT'
        
        cur.close()
        conn.close()
        
        result = {
            'success': True,
            'position_id': position_id,
            'current_price': current_price,
            'actual_pnl': actual_pnl,
            'virtual_pnl': virtual_pnl,
            'trigger': trigger
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ 更新持仓失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("平仓API模块")

