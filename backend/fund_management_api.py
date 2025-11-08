"""
资金管理API
提供账户查询、资金操作等功能
"""
from flask import Blueprint, request, jsonify
import psycopg2
import os
from decimal import Decimal
from datetime import datetime

fund_bp = Blueprint('fund', __name__)

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

# ==================== 账户查询 ====================

@fund_bp.route('/api/fund/account/<username>', methods=['GET'])
def get_account(username):
    """
    获取用户账户信息
    返回：总资金、可用资金、保证金占用、持仓市值、持仓数量
    """
    try:
        user_id = get_user_id(username)
        if not user_id:
            return jsonify({'error': '用户不存在'}), 404
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 查询账户信息
        cur.execute("""
            SELECT 
                total_cash,
                margin_occupied,
                available_cash,
                position_value,
                position_count,
                total_pnl,
                last_update
            FROM accounts
            WHERE user_id = %s
        """, (user_id,))
        
        result = cur.fetchone()
        if not result:
            # 如果账户不存在，创建初始账户
            cur.execute("""
                INSERT INTO accounts (user_id, total_cash, available_cash)
                VALUES (%s, 100000.00, 100000.00)
                RETURNING total_cash, margin_occupied, available_cash, position_value, position_count, total_pnl, last_update
            """, (user_id,))
            result = cur.fetchone()
            conn.commit()
        
        account_data = {
            'username': username,
            'total_cash': float(result[0]),
            'margin_occupied': float(result[1]),
            'available_cash': float(result[2]),
            'position_value': float(result[3]),
            'position_count': result[4],
            'total_pnl': float(result[5]),
            'total_assets': float(result[0]) + float(result[3]),  # 总资产 = 现金 + 持仓市值
            'last_update': result[6].isoformat() if result[6] else None
        }
        
        cur.close()
        conn.close()
        
        return jsonify(account_data), 200
        
    except Exception as e:
        print(f"❌ 获取账户信息失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@fund_bp.route('/api/fund/positions/<username>', methods=['GET'])
def get_positions(username):
    """
    获取用户持仓列表（包含A/B对照组）
    """
    try:
        user_id = get_user_id(username)
        if not user_id:
            return jsonify({'error': '用户不存在'}), 404
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 查询持仓
        cur.execute("""
            SELECT 
                p.position_id,
                p.strategy_id,
                p.decision_time,
                p.user_choice,
                p.actual_type,
                p.actual_cost,
                p.actual_current_value,
                p.actual_pnl,
                p.stop_loss,
                p.take_profit,
                p.virtual_type,
                p.virtual_cost,
                p.virtual_current_value,
                p.virtual_pnl,
                p.status,
                p.close_time,
                p.close_trigger,
                s.symbol,
                s.company_name,
                s.current_price,
                s.option_strategy_detail,
                s.stock_strategy_detail
            FROM positions p
            JOIN strategies s ON p.strategy_id = s.strategy_id
            WHERE p.user_id = %s
            ORDER BY p.decision_time DESC
        """, (user_id,))
        
        positions = []
        for row in cur.fetchall():
            positions.append({
                'position_id': row[0],
                'strategy_id': row[1],
                'decision_time': row[2].isoformat() if row[2] else None,
                'user_choice': row[3],
                'actual': {
                    'type': row[4],
                    'cost': float(row[5]),
                    'current_value': float(row[6]),
                    'pnl': float(row[7]),
                    'return_rate': float(row[7]) / float(row[5]) * 100 if float(row[5]) > 0 else 0,
                    'stop_loss': float(row[8]) if row[8] else None,
                    'take_profit': float(row[9]) if row[9] else None
                },
                'virtual': {
                    'type': row[10],
                    'cost': float(row[11]),
                    'current_value': float(row[12]),
                    'pnl': float(row[13]),
                    'return_rate': float(row[13]) / float(row[11]) * 100 if float(row[11]) > 0 else 0
                },
                'status': row[14],
                'close_time': row[15].isoformat() if row[15] else None,
                'close_trigger': row[16],
                'symbol': row[17],
                'company_name': row[18],
                'current_price': float(row[19]) if row[19] else None,
                'option_strategy_detail': row[20],
                'stock_strategy_detail': row[21]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({'positions': positions}), 200
        
    except Exception as e:
        print(f"❌ 获取持仓列表失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@fund_bp.route('/api/fund/transactions/<username>', methods=['GET'])
def get_transactions(username):
    """
    获取用户资金流水
    """
    try:
        user_id = get_user_id(username)
        if not user_id:
            return jsonify({'error': '用户不存在'}), 404
        
        conn = get_db_connection()
        cur = conn.cursor()
        
        # 查询流水（最近50条）
        cur.execute("""
            SELECT 
                transaction_id,
                position_id,
                type,
                amount,
                balance_after,
                create_time,
                description
            FROM transactions
            WHERE user_id = %s
            ORDER BY create_time DESC
            LIMIT 50
        """, (user_id,))
        
        transactions = []
        for row in cur.fetchall():
            transactions.append({
                'transaction_id': row[0],
                'position_id': row[1],
                'type': row[2],
                'amount': float(row[3]),
                'balance_after': float(row[4]),
                'create_time': row[5].isoformat() if row[5] else None,
                'description': row[6]
            })
        
        cur.close()
        conn.close()
        
        return jsonify({'transactions': transactions}), 200
        
    except Exception as e:
        print(f"❌ 获取流水失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

# ==================== 资金操作 ====================

def record_transaction(conn, user_id, position_id, trans_type, amount, description):
    """
    记录资金流水
    """
    cur = conn.cursor()
    
    # 获取当前余额
    cur.execute("SELECT total_cash FROM accounts WHERE user_id = %s", (user_id,))
    current_balance = cur.fetchone()[0]
    balance_after = current_balance + amount
    
    # 插入流水
    cur.execute("""
        INSERT INTO transactions (user_id, position_id, type, amount, balance_after, description)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (user_id, position_id, trans_type, amount, balance_after, description))
    
    cur.close()

def update_account(conn, user_id, cash_change=0, margin_change=0, position_value_change=0, position_count_change=0):
    """
    更新账户信息
    """
    cur = conn.cursor()
    
    cur.execute("""
        UPDATE accounts
        SET 
            total_cash = total_cash + %s,
            margin_occupied = margin_occupied + %s,
            available_cash = total_cash + %s - (margin_occupied + %s),
            position_value = position_value + %s,
            position_count = position_count + %s
        WHERE user_id = %s
    """, (cash_change, margin_change, cash_change, margin_change, position_value_change, position_count_change, user_id))
    
    cur.close()

if __name__ == '__main__':
    print("资金管理API模块")

