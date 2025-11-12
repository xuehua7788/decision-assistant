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
    import urllib.parse
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        # 本地测试时使用Render数据库（使用解析后的连接参数避免编码问题）
        DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'
    
    # 统一使用解析后的连接参数，避免Windows上的UnicodeDecodeError
    result = urllib.parse.urlparse(DATABASE_URL)
    return psycopg2.connect(
        database=result.path[1:],
        user=result.username,
        password=result.password,
        host=result.hostname,
        port=result.port
    )

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

def get_option_chain(symbol):
    """
    获取期权链数据（Alpha Vantage HISTORICAL_OPTIONS）
    """
    API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')
    url = f'https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol={symbol}&apikey={API_KEY}'
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'data' in data and len(data['data']) > 0:
            print(f"✅ 获取到 {len(data['data'])} 个期权")
            return data
        else:
            print(f"⚠️ Alpha Vantage返回空数据")
            return None
            
    except Exception as e:
        print(f"❌ 获取期权链失败: {e}")
        return None

def get_option_data(symbol, current_price, option_type='call', days_to_expiry=90):
    """
    从Alpha Vantage获取真实期权数据（包括Delta）
    
    参数:
    - symbol: 股票代码
    - current_price: 当前股价
    - option_type: 'call' 或 'put'
    - days_to_expiry: 目标到期天数（默认90天）
    
    返回:
    - 最接近平值的期权合约数据，包含真实Delta
    """
    API_KEY = os.getenv('ALPHA_VANTAGE_KEY', 'OIYWUJEPSR9RQAGU')
    url = f'https://www.alphavantage.co/query?function=HISTORICAL_OPTIONS&symbol={symbol}&apikey={API_KEY}'
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if 'data' not in data or not data['data']:
            print(f"⚠️ 未获取到期权数据，使用简化Delta计算")
            return None
        
        # 计算目标到期日期
        target_expiry = (datetime.now() + timedelta(days=days_to_expiry)).date()
        
        # 筛选符合条件的期权
        candidates = []
        for option in data['data']:
            if option['type'] != option_type:
                continue
            
            expiry_date = datetime.strptime(option['expiration'], '%Y-%m-%d').date()
            strike = float(option['strike'])
            delta = float(option.get('delta', 0))
            
            # 筛选条件：
            # 1. 到期日在60-120天之间
            # 2. 执行价接近当前价格（±20%）
            days_diff = abs((expiry_date - target_expiry).days)
            strike_diff = abs(strike - current_price) / current_price
            
            if days_diff <= 30 and strike_diff <= 0.2:
                candidates.append({
                    'contractID': option['contractID'],
                    'strike': strike,
                    'expiry': expiry_date,
                    'delta': delta,
                    'gamma': float(option.get('gamma', 0)),
                    'theta': float(option.get('theta', 0)),
                    'vega': float(option.get('vega', 0)),
                    'implied_volatility': float(option.get('implied_volatility', 0)),
                    'premium': float(option.get('mark', 0)),  # 使用mark价格
                    'days_to_expiry': (expiry_date - datetime.now().date()).days,
                    'strike_diff': strike_diff
                })
        
        if not candidates:
            print(f"⚠️ 未找到合适的期权合约，使用简化Delta计算")
            return None
        
        # 选择最接近平值的期权（strike_diff最小）
        best_option = min(candidates, key=lambda x: x['strike_diff'])
        print(f"✅ 找到真实期权: {best_option['contractID']}, Delta={best_option['delta']:.4f}")
        return best_option
        
    except Exception as e:
        print(f"❌ 获取期权数据失败: {e}")
        import traceback
        traceback.print_exc()
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

def smart_strategy_matching(ai_analysis, investment_style, current_price):
    """
    智能策略匹配：根据AI分析结果和用户风格推荐最优策略
    
    参数:
    - ai_analysis: AI分析结果 {score, market_direction, direction_strength, ...}
    - investment_style: 用户投资风格 (aggressive/balanced/conservative/buffett/lynch/soros)
    - current_price: 当前股价
    
    返回:
    - option_type: 'call' / 'put' / 'none'
    - strike_offset: 执行价偏移（0=平值，正数=虚值，负数=实值）
    - strategy_name: 策略名称
    - explanation: 推荐理由
    """
    
    # 提取AI分析结果
    score = ai_analysis.get('score', 50) if ai_analysis else 50
    market_direction = ai_analysis.get('market_direction', 'neutral') if ai_analysis else 'neutral'
    direction_strength = ai_analysis.get('direction_strength', 'moderate') if ai_analysis else 'moderate'
    recommendation = ai_analysis.get('recommendation', '观望') if ai_analysis else '观望'
    strategy_text = ai_analysis.get('strategy', '') if ai_analysis else ''
    
    # ✅ 增强：检查AI文字内容，识别犹豫/谨慎态度
    # 如果AI文字说"不是买入时候"、"观望"、"谨慎"、"选择一个"等，修正为neutral
    caution_keywords = ['不是', '观望', '谨慎', '小仓位', '等待', '不建议', '避免', '选择', '犹豫', '不确定', '风险', '回调']
    hesitation_detected = False
    
    if strategy_text:
        # 检查是否有谨慎关键词
        caution_count = sum(1 for keyword in caution_keywords if keyword in strategy_text)
        
        # 如果有2个以上谨慎关键词，或者明确说"不是买入时候"
        if caution_count >= 2 or '不是' in strategy_text or '选择' in strategy_text:
            hesitation_detected = True
            print(f"⚠️ AI表达犹豫/谨慎（关键词数：{caution_count}），文字内容：{strategy_text[:100]}...")
            
            # 如果market_direction与文字不一致，修正为neutral
            if market_direction in ['bullish', 'bearish']:
                print(f"   修正：{market_direction} → neutral")
                market_direction = 'neutral'
                direction_strength = 'weak'
                recommendation = '观望'
    
    print(f"🧠 智能匹配: score={score}, direction={market_direction}, strength={direction_strength}, style={investment_style}, recommendation={recommendation}")
    
    # ========== 强烈看涨 ==========
    if market_direction == 'bullish' and direction_strength == 'strong' and score > 80:
        if investment_style in ['aggressive', 'momentum', 'soros']:
            return {
                'option_type': 'call',
                'strike_offset': 0.03,  # 虚值3%
                'strategy_name': 'Long Call（略虚值）',
                'explanation': f'AI强烈看涨（评分{score}），{investment_style}风格适合高杠杆Call期权，执行价略高于当前价3%'
            }
        elif investment_style in ['conservative', 'value', 'buffett']:
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（平值）',
                'explanation': f'AI强烈看涨（评分{score}），{investment_style}风格建议平值Call期权，风险适中'
            }
        else:  # balanced, lynch
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（平值）',
                'explanation': f'AI强烈看涨（评分{score}），{investment_style}风格适合平值Call期权'
            }
    
    # ========== 一般看涨 ==========
    elif market_direction == 'bullish' and score >= 60:
        if investment_style in ['aggressive', 'momentum', 'soros']:
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（平值）',
                'explanation': f'AI看涨（评分{score}），{investment_style}风格适合Call期权'
            }
        elif investment_style in ['conservative', 'value', 'buffett']:
            return {
                'option_type': 'call',
                'strike_offset': -0.02,  # 略实值
                'strategy_name': 'Long Call（略实值）',
                'explanation': f'AI看涨（评分{score}），{investment_style}风格建议略实值Call，更稳健'
            }
        else:  # balanced, lynch
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（平值）',
                'explanation': f'AI看涨（评分{score}），{investment_style}风格适度参与'
            }
    
    # ========== 震荡/不确定 ==========
    elif market_direction == 'neutral' or (40 <= score <= 60):
        if investment_style in ['aggressive', 'momentum', 'soros']:
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（谨慎）',
                'explanation': f'AI判断震荡（评分{score}），方向不明确，{investment_style}风格可谨慎参与，建议小仓位'
            }
        else:
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（观望为主）',
                'explanation': f'AI判断震荡（评分{score}），信号不明确，{investment_style}风格建议观望或小仓位'
            }
    
    # ========== 一般看跌 ==========
    elif market_direction == 'bearish' and score >= 20:
        if investment_style in ['aggressive', 'momentum', 'soros']:
            return {
                'option_type': 'put',
                'strike_offset': 0,
                'strategy_name': 'Long Put（平值）',
                'explanation': f'AI看跌（评分{score}），{investment_style}风格适合Put期权做空'
            }
        elif investment_style in ['conservative', 'value', 'buffett']:
            return {
                'option_type': 'put',
                'strike_offset': -0.05,  # 虚值5%（Put的虚值是执行价更低）
                'strategy_name': 'Long Put（略虚值）',
                'explanation': f'AI看跌（评分{score}），{investment_style}风格建议略虚值Put作为对冲'
            }
        else:  # balanced, lynch
            return {
                'option_type': 'put',
                'strike_offset': 0,
                'strategy_name': 'Long Put（平值）',
                'explanation': f'AI看跌（评分{score}），{investment_style}风格适度做空'
            }
    
    # ========== 强烈看跌 ==========
    elif market_direction == 'bearish' and direction_strength == 'strong' and score < 20:
        if investment_style in ['aggressive', 'momentum', 'soros']:
            return {
                'option_type': 'put',
                'strike_offset': -0.03,  # 虚值3%
                'strategy_name': 'Long Put（略虚值）',
                'explanation': f'AI强烈看跌（评分{score}），{investment_style}风格适合高杠杆Put期权'
            }
        elif investment_style in ['conservative', 'value', 'buffett']:
            return {
                'option_type': 'put',
                'strike_offset': 0,
                'strategy_name': 'Long Put（平值）',
                'explanation': f'AI强烈看跌（评分{score}），{investment_style}风格建议平值Put避险'
            }
        else:  # balanced, lynch
            return {
                'option_type': 'put',
                'strike_offset': 0,
                'strategy_name': 'Long Put（平值）',
                'explanation': f'AI强烈看跌（评分{score}），{investment_style}风格适度做空'
            }
    
    # ========== 默认（降级：只根据投资风格） ==========
    else:
        print(f"⚠️ AI分析不明确，降级到投资风格匹配")
        if investment_style in ['aggressive', 'momentum']:
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（默认）',
                'explanation': f'{investment_style}风格默认看涨策略'
            }
        elif investment_style in ['conservative', 'value', 'buffett']:
            return {
                'option_type': 'call',
                'strike_offset': -0.02,
                'strategy_name': 'Long Call（略实值）',
                'explanation': f'{investment_style}风格默认稳健策略'
            }
        else:
            return {
                'option_type': 'call',
                'strike_offset': 0,
                'strategy_name': 'Long Call（默认）',
                'explanation': f'{investment_style}风格默认平衡策略'
            }

def generate_dual_strategy(symbol, current_price, notional_value, investment_style='balanced', ai_analysis=None):
    """
    生成双策略：期权 + Delta One股票（智能匹配版）
    
    参数：
    - symbol: 股票代码
    - current_price: 当前股价
    - notional_value: 名义本金（两策略相同）
    - investment_style: 投资风格（影响期权选择）
    - ai_analysis: AI分析结果（可选，用于智能匹配）
    
    返回：
    - option_strategy: 期权策略详情（使用Alpha Vantage真实数据）
    - stock_strategy: 股票策略详情（基于期权Delta计算）
    - explanation: 策略推荐理由
    """
    
    # 1. 智能匹配策略
    strategy_match = smart_strategy_matching(ai_analysis, investment_style, current_price)
    
    option_type = strategy_match['option_type']
    strike_offset = strategy_match['strike_offset']
    strategy_name = strategy_match['strategy_name']
    explanation = strategy_match['explanation']
    
    print(f"✅ 智能匹配结果: {strategy_name}")
    print(f"   推荐理由: {explanation}")
    print(f"   期权类型: {option_type}, 执行价偏移: {strike_offset*100:.1f}%")
    
    # 2. 从Alpha Vantage获取真实期权数据
    real_option = get_option_data(symbol, current_price, option_type=option_type, days_to_expiry=90)
    
    if real_option:
        # 使用真实期权数据
        strike_price = real_option['strike']
        expiry_date = real_option['expiry']
        days_to_expiry = real_option['days_to_expiry']
        option_delta = real_option['delta']  # 单个期权的Delta
        implied_volatility = real_option['implied_volatility']
        
        # ✅ 正确的期权费计算逻辑：
        # 期权费 = (名义本金 / 股价) × 期权价格
        equivalent_shares = notional_value / current_price  # 等价股数
        option_price_per_share = real_option['premium']  # Alpha Vantage返回的单股期权价格
        total_premium = equivalent_shares * option_price_per_share
        
        # Delta就是单个期权的Delta（不需要组合计算）
        # Alpha Vantage返回的是单股期权的Delta
        
        option_strategy = {
            'type': option_type.upper(),
            'contractID': real_option['contractID'],
            'strike_price': round(strike_price, 2),
            'expiry_date': expiry_date.isoformat(),
            'days_to_expiry': days_to_expiry,
            'premium': round(total_premium, 2),
            'equivalent_shares': round(equivalent_shares, 2),  # 等价股数
            'delta': option_delta,  # 单个期权的Delta
            'gamma': real_option['gamma'],
            'theta': real_option['theta'],
            'vega': real_option['vega'],
            'implied_volatility': round(implied_volatility, 4),
            'notional_value': notional_value,
            'data_source': 'Alpha Vantage Real Data',
            'description': f"{option_type.upper()} 期权，等价{equivalent_shares:.2f}股，执行价 ${strike_price:.2f}，{days_to_expiry}天到期，Delta={option_delta:.4f}"
        }
        
        print(f"✅ 使用真实期权: Delta={option_delta:.4f}, 名义本金=${notional_value}")
        
    else:
        # 降级：使用简化计算
        print("⚠️ Alpha Vantage期权数据不可用，使用简化计算")
        days_to_expiry = 90
        expiry_date = (datetime.now() + timedelta(days=days_to_expiry)).date()
        
        # 根据strike_offset调整执行价
        strike_price = current_price * (1 + strike_offset)
        
        option_delta = calculate_option_delta(option_type.upper(), strike_price, current_price, days_to_expiry)
        
        # 简化计算
        equivalent_shares = notional_value / current_price
        option_premium = notional_value * 0.04  # 简化：期权费为名义本金的4%
        
        option_strategy = {
            'type': option_type.upper(),
            'contractID': 'SIMULATED',
            'strike_price': round(strike_price, 2),
            'expiry_date': expiry_date.isoformat(),
            'days_to_expiry': days_to_expiry,
            'premium': round(option_premium, 2),
            'equivalent_shares': round(equivalent_shares, 2),
            'delta': option_delta,
            'notional_value': notional_value,
            'data_source': 'Simplified Calculation',
            'description': f"{option_type.upper()} 期权（简化），等价{equivalent_shares:.2f}股，执行价 ${strike_price:.2f}"
        }
    
    # 3. 生成Delta One股票策略
    # ✅ 正确公式：股票名义本金 = 期权名义本金 × Delta
    # 股票保证金 = 股票名义本金 × 10%
    option_delta_value = option_strategy['delta']
    stock_notional = notional_value * abs(option_delta_value)  # 股票名义本金 = 期权名义本金 × Delta
    stock_margin = stock_notional * 0.1  # 10%保证金
    stock_shares = int(stock_notional / current_price)  # 股票数量
    
    # 设置止盈止损
    if option_type == 'call':
        stop_loss = current_price * 0.9  # -10%止损
        take_profit = current_price * 1.2  # +20%止盈
        position_type = 'LONG'
    else:
        stop_loss = current_price * 1.1  # +10%止损（做空）
        take_profit = current_price * 0.8  # -20%止盈（做空）
        position_type = 'SHORT'
    
    stock_strategy = {
        'type': position_type,
        'notional': round(stock_notional, 2),  # 股票名义本金
        'margin': round(stock_margin, 2),
        'shares': stock_shares,
        'entry_price': current_price,
        'stop_loss': round(stop_loss, 2),
        'take_profit': round(take_profit, 2),
        'delta': option_delta_value,  # 对应的Delta
        'description': f"{position_type} {stock_shares}股，名义本金 ${stock_notional:.2f}（期权本金${notional_value} × Delta{option_delta_value:.4f}），保证金 ${stock_margin:.2f}"
    }
    
    return option_strategy, stock_strategy, explanation

@dual_strategy_bp.route('/api/dual-strategy/generate', methods=['POST'])
def generate_strategy():
    """
    生成双策略推荐（使用AI Agent Jany）
    
    请求体：
    {
        "symbol": "AAPL",
        "username": "bbb",
        "notional_value": 10000,  // 名义本金
        "investment_style": "aggressive",  // 可选
        "ai_analysis": {...}  // Tom的分析结果
    }
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        username = data.get('username')
        notional_value = float(data.get('notional_value', 30000))  # 默认$30,000
        investment_style = data.get('investment_style', 'balanced')
        ai_analysis = data.get('ai_analysis')  # Tom的分析结果
        conversation_history = data.get('conversation_history', [])  # 新增：对话历史
        
        if not symbol or not username:
            return jsonify({'error': '缺少必要参数'}), 400
        
        if not ai_analysis:
            return jsonify({'error': '缺少AI分析结果'}), 400
        
        print(f"🎯 开始生成策略: {symbol}, 风格: {investment_style}, 名义本金: ${notional_value}")
        
        # 获取实时股价
        stock_data = get_stock_data(symbol)
        if not stock_data:
            return jsonify({'error': '无法获取股票数据'}), 500
        
        current_price = stock_data['price']
        print(f"   当前价格: ${current_price}")
        
        # 🆕 获取selected_symbols并推断目标股票
        selected_symbols = data.get('selected_symbols', [symbol])
        target_symbol = symbol
        
        # 如果有多个股票，先推断用户选择
        if selected_symbols and len(selected_symbols) > 1:
            from ai_strategy_agent import get_ai_strategy_agent
            jany = get_ai_strategy_agent()
            
            target_symbol = jany.infer_target_symbol_from_conversation(
                conversation_history, 
                selected_symbols
            )
            
            if target_symbol != symbol:
                print(f"📊 Jany推断用户选择: {target_symbol}（原始为 {symbol}）")
                symbol = target_symbol
                
                # 🔄 重新获取推断出的股票价格
                from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
                client = get_alpha_vantage_client()
                quote = client.get_quote(symbol)
                if quote:
                    current_price = quote['price']
                    print(f"   更新价格: {symbol} = ${current_price}")
        
        # 获取Alpha Vantage期权链数据（使用推断后的股票）
        option_chain_data = get_option_chain(symbol)
        if not option_chain_data:
            return jsonify({'error': f'无法获取{symbol}的期权数据'}), 500
        
        print(f"   期权数据: {len(option_chain_data.get('data', []))}个期权")
        
        # 🤖 使用AI Agent Jany生成策略（替代硬编码逻辑）
        try:
            from ai_strategy_agent import get_ai_strategy_agent
            
            jany = get_ai_strategy_agent()
            
            print(f"🤖 调用Jany生成策略...")
            print(f"   对话历史: {len(conversation_history)}条")
            
            strategy_result = jany.generate_trading_strategy(
                symbol=symbol,  # 使用推断后的股票
                current_price=current_price,  # 使用推断后的价格
                tom_analysis=ai_analysis,
                option_chain_data=option_chain_data,
                investment_style=investment_style,
                notional_value=notional_value,
                conversation_history=conversation_history,
                selected_symbols=selected_symbols
            )
            
            if not strategy_result:
                print(f"❌ Jany返回None，降级到传统逻辑")
                # 降级：使用原来的逻辑
                option_strategy, stock_strategy, explanation = generate_dual_strategy(
                    symbol, current_price, notional_value, investment_style, ai_analysis
                )
            else:
                # 提取策略
                option_strategy = strategy_result.get('option_strategy')
                stock_strategy = strategy_result.get('stock_strategy')
                explanation = strategy_result.get('explanation', '')
                
                print(f"✅ AI策略生成成功")
                print(f"   期权: {option_strategy.get('type')} @ ${option_strategy.get('strike_price')}")
                print(f"   股票: {stock_strategy.get('shares')}股 @ ${stock_strategy.get('entry_price')}")
            
        except Exception as e:
            print(f"❌ AI策略Agent出错，降级到传统逻辑: {e}")
            import traceback
            traceback.print_exc()
            # 降级：使用原来的逻辑
            option_strategy, stock_strategy, explanation = generate_dual_strategy(
                symbol, current_price, notional_value, investment_style, ai_analysis
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
            option_strategy['expiry_date'], option_strategy.get('total_premium', option_strategy.get('premium', 0)), 
            option_strategy['delta'],  # 单个期权的Delta
            stock_strategy['notional'], stock_strategy['margin'],  # 股票名义本金和保证金
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
            'explanation': explanation,  # 新增：策略推荐理由
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

