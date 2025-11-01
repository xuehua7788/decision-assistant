#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析API路由
提供股票数据获取和AI分析接口
"""

from flask import Blueprint, request, jsonify
import sys
import os

# 导入股票分析模块
try:
    from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
    from stock_analysis.stock_analyzer import get_stock_analyzer
    STOCK_ANALYSIS_AVAILABLE = True
    print("✅ 股票分析模块导入成功")
except ImportError as e:
    STOCK_ANALYSIS_AVAILABLE = False
    print(f"⚠️ 股票分析模块导入失败: {e}")

# 创建Blueprint
stock_bp = Blueprint('stock', __name__, url_prefix='/api/stock')

@stock_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify({
        "status": "healthy",
        "stock_analysis_available": STOCK_ANALYSIS_AVAILABLE
    }), 200

@stock_bp.route('/<symbol>/news', methods=['GET'])
def get_stock_news(symbol):
    """
    获取股票相关新闻
    
    GET /api/stock/{symbol}/news?limit=5
    
    Returns:
        {
            "status": "success",
            "news": [
                {
                    "title": "新闻标题",
                    "summary": "新闻摘要",
                    "url": "新闻链接",
                    "time_published": "2025-11-01 12:00",
                    "sentiment": "positive",
                    "sentiment_score": 0.35
                }
            ]
        }
    """
    if not STOCK_ANALYSIS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "股票分析功能暂不可用"
        }), 503
    
    try:
        symbol = symbol.upper()
        limit = request.args.get('limit', 5, type=int)
        
        print(f"📰 获取新闻: {symbol} (limit={limit})", flush=True)
        sys.stdout.flush()
        
        # 获取新闻
        client = get_alpha_vantage_client()
        news = client.get_news(symbol, limit=limit)
        
        print(f"✅ 新闻获取成功: {symbol} - {len(news)}条", flush=True)
        sys.stdout.flush()
        
        return jsonify({
            "status": "success",
            "news": news
        }), 200
        
    except Exception as e:
        print(f"❌ 获取新闻失败: {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@stock_bp.route('/<symbol>', methods=['GET'])
def get_stock_data(symbol):
    """
    获取股票数据和技术指标
    
    GET /api/stock/AAPL
    
    Returns:
        {
            "status": "success",
            "data": {
                "quote": {...},
                "history": [...],
                "indicators": {
                    "rsi": 65.5
                }
            }
        }
    """
    if not STOCK_ANALYSIS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "股票分析功能暂不可用"
        }), 503
    
    try:
        symbol = symbol.upper()
        print(f"📊 获取股票数据: {symbol}", flush=True)
        sys.stdout.flush()
        
        # 获取客户端
        client = get_alpha_vantage_client()
        
        # 获取实时报价
        quote = client.get_quote(symbol)
        if not quote:
            return jsonify({
                "status": "error",
                "message": f"未找到该股票: {symbol}"
            }), 404
        
        # 获取历史数据
        history = client.get_daily_history(symbol, days=30)
        if not history:
            return jsonify({
                "status": "error",
                "message": "无法获取历史数据"
            }), 500
        
        # 计算技术指标
        closes = [h['close'] for h in history]
        rsi = client.calculate_rsi(closes)
        volatility = client.calculate_volatility(closes)
        
        print(f"✅ 数据获取成功: {symbol} - ${quote['price']}", flush=True)
        sys.stdout.flush()
        
        return jsonify({
            "status": "success",
            "data": {
                "quote": quote,
                "history": history,
                "indicators": {
                    "rsi": rsi,
                    "volatility": volatility
                }
            }
        }), 200
        
    except Exception as e:
        print(f"❌ 获取股票数据失败: {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@stock_bp.route('/analyze', methods=['POST'])
def analyze_stock():
    """
    分析股票并给出AI建议
    
    POST /api/stock/analyze
    Body: {
        "symbol": "AAPL",
        "risk_preference": "balanced",  // conservative/balanced/aggressive
        "user_opinion": "我认为苹果新产品会大卖...",  // 可选
        "news_context": "苹果发布新款iPhone..."  // 可选
    }
    
    Returns:
        {
            "status": "success",
            "analysis": {
                "score": 75,
                "recommendation": "买入",
                "position_size": "20%",
                "target_price": 190.0,
                "stop_loss": 175.0,
                "key_points": [...],
                "analysis_summary": "...",
                "strategy": "具体投资策略..."
            }
        }
    """
    if not STOCK_ANALYSIS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "股票分析功能暂不可用"
        }), 503
    
    try:
        data = request.json
        symbol = data.get('symbol', '').upper()
        risk_preference = data.get('risk_preference', 'balanced')
        user_opinion = data.get('user_opinion', '').strip()
        news_context = data.get('news_context', '').strip()
        
        if not symbol:
            return jsonify({
                "status": "error",
                "message": "请提供股票代码"
            }), 400
        
        # 验证风险偏好
        valid_preferences = ['conservative', 'balanced', 'aggressive']
        if risk_preference not in valid_preferences:
            risk_preference = 'balanced'
        
        print(f"🤖 开始分析: {symbol} (风险偏好: {risk_preference})", flush=True)
        if user_opinion:
            print(f"   用户观点: {user_opinion[:50]}...", flush=True)
        if news_context:
            print(f"   新闻消息: {news_context[:50]}...", flush=True)
        sys.stdout.flush()
        
        # 获取股票数据
        client = get_alpha_vantage_client()
        
        quote = client.get_quote(symbol)
        if not quote:
            return jsonify({
                "status": "error",
                "message": f"未找到该股票: {symbol}"
            }), 404
        
        history = client.get_daily_history(symbol, days=30)
        if not history:
            return jsonify({
                "status": "error",
                "message": "无法获取历史数据"
            }), 500
        
        # 计算RSI
        closes = [h['close'] for h in history]
        rsi = client.calculate_rsi(closes)
        
        # AI分析
        analyzer = get_stock_analyzer()
        analysis = analyzer.analyze_stock(
            symbol=symbol,
            current_data=quote,
            history_data=history,
            rsi=rsi,
            risk_preference=risk_preference,
            user_opinion=user_opinion if user_opinion else None,
            news_context=news_context if news_context else None
        )
        
        if not analysis:
            return jsonify({
                "status": "error",
                "message": "AI分析失败"
            }), 500
        
        print(f"✅ 分析完成: {symbol} - 评分{analysis['score']}, 建议{analysis['recommendation']}", flush=True)
        sys.stdout.flush()
        
        return jsonify({
            "status": "success",
            "analysis": analysis
        }), 200
        
    except Exception as e:
        print(f"❌ 分析失败: {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@stock_bp.route('/trending', methods=['GET'])
def get_trending_stocks():
    """
    获取热门股票列表
    
    GET /api/stock/trending
    
    Returns:
        {
            "status": "success",
            "stocks": ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
        }
    """
    if not STOCK_ANALYSIS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "股票分析功能暂不可用"
        }), 503
    
    try:
        client = get_alpha_vantage_client()
        trending = client.get_trending_stocks()
        
        return jsonify({
            "status": "success",
            "stocks": trending
        }), 200
        
    except Exception as e:
        print(f"❌ 获取热门股票失败: {e}", flush=True)
        sys.stdout.flush()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

