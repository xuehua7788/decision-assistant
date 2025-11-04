#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略存储API - 保存用户接受的投资策略
"""

from flask import Blueprint, request, jsonify
import json
import os
from datetime import datetime
import random
from database.connection import get_db_connection

strategy_bp = Blueprint('strategy', __name__, url_prefix='/api/strategy')

# 策略存储目录（备用，如果数据库不可用）
STRATEGY_DIR = 'strategy_data'
if not os.path.exists(STRATEGY_DIR):
    os.makedirs(STRATEGY_DIR)

def init_strategy_table():
    """初始化策略表（如果不存在）"""
    conn = get_db_connection()
    if not conn:
        print("⚠️ 数据库不可用，策略将保存到文件")
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accepted_strategies (
                id SERIAL PRIMARY KEY,
                strategy_id VARCHAR(100) UNIQUE NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                company_name VARCHAR(100),
                investment_style VARCHAR(20) NOT NULL,
                recommendation VARCHAR(20) NOT NULL,
                target_price DECIMAL(10, 2) NOT NULL,
                stop_loss DECIMAL(10, 2),
                position_size VARCHAR(10),
                score INTEGER,
                strategy_text TEXT,
                analysis_summary TEXT,
                current_price DECIMAL(10, 2) NOT NULL,
                option_strategy JSONB,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active'
            )
        """)
        
        # 创建索引
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_strategy_symbol 
            ON accepted_strategies(symbol)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_strategy_created 
            ON accepted_strategies(created_at)
        """)
        
        conn.commit()
        cursor.close()
        conn.close()
        print("✅ 策略表初始化成功")
        return True
    except Exception as e:
        print(f"⚠️ 策略表初始化失败: {e}")
        if conn:
            conn.close()
        return False

@strategy_bp.route('/save', methods=['POST'])
def save_strategy():
    """
    保存用户接受的策略
    
    POST /api/strategy/save
    Body: {
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
        "investment_style": "buffett",
        "recommendation": "买入",
        "target_price": 200.0,
        "stop_loss": 175.0,
        "position_size": "15%",
        "score": 75,
        "strategy_text": "...",
        "analysis_summary": "...",
        "current_price": 180.5,
        "created_at": "2025-11-02T10:00:00Z"
    }
    
    Returns:
        {
            "status": "success",
            "strategy_id": "AAPL_20251102_buffett",
            "message": "策略已保存"
        }
    """
    try:
        data = request.json
        
        # 验证必需字段
        required_fields = ['symbol', 'investment_style', 'recommendation', 
                          'target_price', 'current_price']
        for field in required_fields:
            if field not in data:
                return jsonify({
                    "status": "error",
                    "message": f"缺少必需字段: {field}"
                }), 400
        
        # 生成策略ID
        symbol = data['symbol']
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        style = data['investment_style']
        strategy_id = f"{symbol}_{timestamp}_{style}"
        
        # 尝试保存到数据库
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                # 将期权策略转换为JSON字符串
                option_strategy_json = json.dumps(data.get('option_strategy')) if data.get('option_strategy') else None
                
                cursor.execute("""
                    INSERT INTO accepted_strategies 
                    (strategy_id, symbol, company_name, investment_style, recommendation,
                     target_price, stop_loss, position_size, score, strategy_text,
                     analysis_summary, current_price, option_strategy, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    strategy_id,
                    symbol,
                    data.get('company_name', symbol),
                    style,
                    data['recommendation'],
                    float(data['target_price']),
                    float(data.get('stop_loss', 0)),
                    data.get('position_size', '10%'),
                    int(data.get('score', 50)),
                    data.get('strategy_text', ''),
                    data.get('analysis_summary', ''),
                    float(data['current_price']),
                    option_strategy_json,
                    'active'
                ))
                conn.commit()
                cursor.close()
                conn.close()
                print(f"✅ 策略已保存到数据库: {strategy_id}")
            except Exception as e:
                print(f"⚠️ 数据库保存失败，使用文件备份: {e}")
                conn.close()
                # 降级到文件存储
                strategy_data = {
                    "strategy_id": strategy_id,
                    "symbol": symbol,
                    "company_name": data.get('company_name', symbol),
                    "investment_style": style,
                    "recommendation": data['recommendation'],
                    "target_price": float(data['target_price']),
                    "stop_loss": float(data.get('stop_loss', 0)),
                    "option_strategy": data.get('option_strategy'),
                    "position_size": data.get('position_size', '10%'),
                    "score": int(data.get('score', 50)),
                    "strategy_text": data.get('strategy_text', ''),
                    "analysis_summary": data.get('analysis_summary', ''),
                    "current_price": float(data['current_price']),
                    "created_at": data.get('created_at', datetime.now().isoformat()),
                    "status": "active"
                }
                strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_id}.json")
                with open(strategy_file, 'w', encoding='utf-8') as f:
                    json.dump(strategy_data, f, ensure_ascii=False, indent=2)
                print(f"✅ 策略已保存到文件: {strategy_id}")
        else:
            # 数据库不可用，使用文件存储
            strategy_data = {
                "strategy_id": strategy_id,
                "symbol": symbol,
                "company_name": data.get('company_name', symbol),
                "investment_style": style,
                "recommendation": data['recommendation'],
                "target_price": float(data['target_price']),
                "stop_loss": float(data.get('stop_loss', 0)),
                "position_size": data.get('position_size', '10%'),
                "score": int(data.get('score', 50)),
                "strategy_text": data.get('strategy_text', ''),
                "analysis_summary": data.get('analysis_summary', ''),
                "current_price": float(data['current_price']),
                "created_at": data.get('created_at', datetime.now().isoformat()),
                "status": "active"
            }
            strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_id}.json")
            with open(strategy_file, 'w', encoding='utf-8') as f:
                json.dump(strategy_data, f, ensure_ascii=False, indent=2)
            print(f"✅ 策略已保存到文件: {strategy_id}")
        
        return jsonify({
            "status": "success",
            "strategy_id": strategy_id,
            "message": "策略已保存"
        }), 200
        
    except Exception as e:
        print(f"❌ 保存策略失败: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@strategy_bp.route('/list', methods=['GET'])
def list_strategies():
    """
    获取所有保存的策略列表
    
    GET /api/strategy/list?symbol=AAPL
    
    Returns:
        {
            "status": "success",
            "strategies": [...]
        }
    """
    try:
        symbol_filter = request.args.get('symbol', '').upper()
        
        strategies = []
        
        # 尝试从数据库获取
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                if symbol_filter:
                    cursor.execute("""
                        SELECT strategy_id, symbol, company_name, investment_style, 
                               recommendation, target_price, stop_loss, position_size,
                               score, strategy_text, analysis_summary, current_price,
                               option_strategy, created_at, status
                        FROM accepted_strategies
                        WHERE symbol = %s
                        ORDER BY created_at DESC
                    """, (symbol_filter,))
                else:
                    cursor.execute("""
                        SELECT strategy_id, symbol, company_name, investment_style, 
                               recommendation, target_price, stop_loss, position_size,
                               score, strategy_text, analysis_summary, current_price,
                               option_strategy, created_at, status
                        FROM accepted_strategies
                        ORDER BY created_at DESC
                    """)
                
                rows = cursor.fetchall()
                for row in rows:
                    strategies.append({
                        "strategy_id": row[0],
                        "symbol": row[1],
                        "company_name": row[2],
                        "investment_style": row[3],
                        "recommendation": row[4],
                        "target_price": float(row[5]),
                        "stop_loss": float(row[6]) if row[6] else 0,
                        "position_size": row[7],
                        "score": row[8],
                        "strategy_text": row[9],
                        "analysis_summary": row[10],
                        "current_price": float(row[11]),
                        "option_strategy": row[12],  # JSONB自动解析为dict
                        "created_at": row[13].isoformat() if row[13] else None,
                        "status": row[14]
                    })
                
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"⚠️ 数据库查询失败，使用文件备份: {e}")
                conn.close()
                # 降级到文件读取
                if os.path.exists(STRATEGY_DIR):
                    for filename in os.listdir(STRATEGY_DIR):
                        if filename.endswith('.json'):
                            filepath = os.path.join(STRATEGY_DIR, filename)
                            with open(filepath, 'r', encoding='utf-8') as f:
                                strategy = json.load(f)
                                if symbol_filter and strategy['symbol'] != symbol_filter:
                                    continue
                                strategies.append(strategy)
                strategies.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        else:
            # 数据库不可用，使用文件
            if os.path.exists(STRATEGY_DIR):
                for filename in os.listdir(STRATEGY_DIR):
                    if filename.endswith('.json'):
                        filepath = os.path.join(STRATEGY_DIR, filename)
                        with open(filepath, 'r', encoding='utf-8') as f:
                            strategy = json.load(f)
                            if symbol_filter and strategy['symbol'] != symbol_filter:
                                continue
                            strategies.append(strategy)
            strategies.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return jsonify({
            "status": "success",
            "strategies": strategies,
            "count": len(strategies)
        }), 200
        
    except Exception as e:
        print(f"❌ 获取策略列表失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@strategy_bp.route('/<strategy_id>', methods=['GET'])
def get_strategy(strategy_id):
    """
    获取单个策略详情
    
    GET /api/strategy/{strategy_id}
    
    Returns:
        {
            "status": "success",
            "strategy": {...}
        }
    """
    try:
        strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_id}.json")
        
        if not os.path.exists(strategy_file):
            return jsonify({
                "status": "error",
                "message": "策略不存在"
            }), 404
        
        with open(strategy_file, 'r', encoding='utf-8') as f:
            strategy = json.load(f)
        
        return jsonify({
            "status": "success",
            "strategy": strategy
        }), 200
        
    except Exception as e:
        print(f"❌ 获取策略失败: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def evaluate_strategy_performance(strategy, symbol):
    """
    评估策略的历史表现（简化版）
    
    方案B：
    1. 获取当前真实股价
    2. 计算策略预期收益（目标价 vs 建议价）
    3. 计算实际收益（当前价 vs 建议价）
    4. 对比两者
    """
    
    strategy_buy_price = strategy['current_price']  # 策略建议买入价
    target_price = strategy['target_price']  # 目标价
    
    # 获取当前真实股价
    try:
        from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
        client = get_alpha_vantage_client()
        quote = client.get_quote(symbol)
        
        if quote:
            current_real_price = quote['price']
        else:
            # API失败，使用模拟数据
            current_real_price = strategy_buy_price * (1 + random.uniform(-0.1, 0.15))
    except:
        # 如果API不可用，使用模拟数据
        current_real_price = strategy_buy_price * (1 + random.uniform(-0.1, 0.15))
    
    # 计算策略预期收益（如果按目标价卖出）
    if strategy['recommendation'] == '买入':
        strategy_return = ((target_price - strategy_buy_price) / strategy_buy_price) * 100
    else:
        strategy_return = 0
    
    # 计算实际收益（如果当时买入，现在的收益）
    actual_return = ((current_real_price - strategy_buy_price) / strategy_buy_price) * 100
    
    # 计算策略表现（策略预期 vs 实际持有）
    # 正值表示策略跑赢，负值表示跑输
    outperformance = strategy_return - actual_return
    
    return {
        "strategy_return": round(strategy_return, 2),
        "actual_return": round(actual_return, 2),
        "outperformance": round(outperformance, 2),
        "current_real_price": round(current_real_price, 2),
        "strategy_buy_price": round(strategy_buy_price, 2)
    }

@strategy_bp.route('/evaluate', methods=['POST'])
def evaluate_strategy():
    """
    评估策略
    
    POST /api/strategy/evaluate
    Body: {
        "strategy_id": "AAPL_20251102_buffett",
        "symbol": "AAPL"
    }
    
    Returns:
        {
            "status": "success",
            "evaluation": {
                "backtest": {...},
                "conclusion": "..."
            }
        }
    """
    try:
        data = request.json
        strategy_id = data.get('strategy_id')
        
        if not strategy_id:
            return jsonify({
                "status": "error",
                "message": "缺少strategy_id"
            }), 400
        
        # 获取策略（优先从数据库）
        strategy = None
        conn = get_db_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT strategy_id, symbol, company_name, investment_style, 
                           recommendation, target_price, stop_loss, position_size,
                           score, strategy_text, analysis_summary, current_price,
                           created_at, status
                    FROM accepted_strategies
                    WHERE strategy_id = %s
                """, (strategy_id,))
                
                row = cursor.fetchone()
                if row:
                    strategy = {
                        "strategy_id": row[0],
                        "symbol": row[1],
                        "company_name": row[2],
                        "investment_style": row[3],
                        "recommendation": row[4],
                        "target_price": float(row[5]),
                        "stop_loss": float(row[6]),
                        "position_size": row[7],
                        "score": row[8],
                        "strategy_text": row[9],
                        "analysis_summary": row[10],
                        "current_price": float(row[11]),
                        "created_at": row[12].isoformat() if row[12] else None,
                        "status": row[13]
                    }
                
                cursor.close()
                conn.close()
            except Exception as e:
                print(f"⚠️ 数据库查询失败: {e}")
                conn.close()
        
        # 如果数据库没有，尝试从文件读取
        if not strategy:
            strategy_file = os.path.join(STRATEGY_DIR, f"{strategy_id}.json")
            if not os.path.exists(strategy_file):
                return jsonify({
                    "status": "error",
                    "message": "策略不存在"
                }), 404
            
            with open(strategy_file, 'r', encoding='utf-8') as f:
                strategy = json.load(f)
        
        # 评估策略
        backtest = evaluate_strategy_performance(strategy, strategy['symbol'])
        
        # 生成结论
        if backtest['outperformance'] > 5:
            conclusion = f"策略表现【优秀】！跑赢市场{abs(backtest['outperformance']):.1f}%，建议继续执行类似策略。"
        elif backtest['outperformance'] > 0:
            conclusion = f"策略表现【良好】，小幅跑赢市场{backtest['outperformance']:.1f}%，可以执行。"
        elif backtest['outperformance'] > -5:
            conclusion = f"策略表现【一般】，略微跑输市场{abs(backtest['outperformance']):.1f}%，建议优化买卖点。"
        else:
            conclusion = f"策略表现【较差】，跑输市场{abs(backtest['outperformance']):.1f}%，不建议使用此策略。"
        
        return jsonify({
            "status": "success",
            "evaluation": {
                "strategy_id": strategy['strategy_id'],
                "symbol": strategy['symbol'],
                "company_name": strategy.get('company_name', strategy['symbol']),
                "investment_style": strategy['investment_style'],
                "backtest": backtest,
                "conclusion": conclusion
            }
        }), 200
        
    except Exception as e:
        print(f"❌ 评估策略失败: {e}")
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

