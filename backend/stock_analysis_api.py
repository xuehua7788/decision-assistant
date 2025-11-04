#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票分析API路由 - 修复路由顺序
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

# ============================================================
# 路由顺序很重要！具体的路由必须在通用的 /<symbol> 之前
# ============================================================

@stock_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查 - 股票分析API"""
    import os
    alpha_key = os.getenv('ALPHA_VANTAGE_KEY', 'NOT_SET')
    return jsonify({
        "status": "healthy",
        "stock_analysis_available": STOCK_ANALYSIS_AVAILABLE,
        "version": "1.2.0",  # 版本号更新，表示路由已修复
        "alpha_vantage_key_set": alpha_key != 'NOT_SET',
        "alpha_vantage_key_prefix": alpha_key[:10] if alpha_key != 'NOT_SET' else 'NOT_SET'
    }), 200

@stock_bp.route('/styles', methods=['GET'])
def get_investment_styles():
    """
    获取可用的投资风格列表
    
    GET /api/stock/styles
    
    Returns:
        {
            "status": "success",
            "styles": [
                {
                    "id": "buffett",
                    "name": "巴菲特",
                    "name_en": "Warren Buffett",
                    "description": "价值投资大师",
                    "icon": "🏛️"
                },
                ...
            ]
        }
    """
    try:
        from stock_analysis.investment_styles import get_available_styles
        styles = get_available_styles()
        
        return jsonify({
            "status": "success",
            "styles": styles
        }), 200
        
    except Exception as e:
        print(f"❌ 获取投资风格失败: {e}", flush=True)
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
        investment_style = data.get('investment_style', None)  # buffett/lynch/soros
        user_opinion = data.get('user_opinion', '').strip()
        news_context = data.get('news_context', '').strip()
        language = data.get('language', 'zh')  # 默认中文
        
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
        print(f"   📝 用户观点长度: {len(user_opinion)} 字符", flush=True)
        print(f"   📰 新闻消息长度: {len(news_context)} 字符", flush=True)
        if user_opinion:
            print(f"   用户观点内容: {user_opinion[:50]}...", flush=True)
        else:
            print(f"   ⚠️ 用户观点为空", flush=True)
        if news_context:
            print(f"   新闻消息内容: {news_context[:50]}...", flush=True)
        else:
            print(f"   ⚠️ 新闻消息为空", flush=True)
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
        
        # 🆕 获取Premium功能数据
        print(f"📊 获取Premium数据...", flush=True)
        
        # 1. 公司基本面
        company_overview = client.get_company_overview(symbol)
        
        # 2. 技术指标 (MACD, 布林带, ATR)
        macd_data = client.get_technical_indicator(symbol, 'MACD', interval='daily')
        bbands_data = client.get_technical_indicator(symbol, 'BBANDS', interval='daily', time_period=20)
        atr_data = client.get_technical_indicator(symbol, 'ATR', interval='daily', time_period=14)
        
        # 3. 宏观经济数据
        cpi_data = client.get_economic_indicator('CPI')
        unemployment_data = client.get_economic_indicator('UNEMPLOYMENT')
        fed_rate_data = client.get_economic_indicator('FEDERAL_FUNDS_RATE')
        
        print(f"✅ Premium数据获取完成", flush=True)
        print(f"   公司数据: {'✅' if company_overview else '❌'}", flush=True)
        print(f"   MACD: {'✅' if macd_data else '❌'}", flush=True)
        print(f"   布林带: {'✅' if bbands_data else '❌'}", flush=True)
        print(f"   ATR: {'✅' if atr_data else '❌'}", flush=True)
        print(f"   CPI: {'✅' if cpi_data else '❌'}", flush=True)
        print(f"   失业率: {'✅' if unemployment_data else '❌'}", flush=True)
        print(f"   联邦利率: {'✅' if fed_rate_data else '❌'}", flush=True)
        sys.stdout.flush()
        
        # AI分析
        analyzer = get_stock_analyzer()
        analysis = analyzer.analyze_stock(
            symbol=symbol,
            current_data=quote,
            history_data=history,
            rsi=rsi,
            risk_preference=risk_preference,
            user_opinion=user_opinion if user_opinion else None,
            news_context=news_context if news_context else None,
            language=language,
            investment_style=investment_style,
            # 🆕 传递Premium数据
            company_overview=company_overview,
            technical_indicators={
                'macd': macd_data,
                'bbands': bbands_data,
                'atr': atr_data
            },
            economic_data={
                'cpi': cpi_data,
                'unemployment': unemployment_data,
                'fed_rate': fed_rate_data
            }
        )
        
        if not analysis:
            return jsonify({
                "status": "error",
                "message": "AI分析失败"
            }), 500
        
        print(f"✅ 分析完成: {symbol} - 评分{analysis['score']}, 建议{analysis['recommendation']}", flush=True)
        
        # 根据AI分析结果生成期权策略
        option_strategy = None
        if 'market_direction' in analysis and 'direction_strength' in analysis:
            try:
                from option_strategy_handler import OptionStrategyHandler
                
                # 构建期权策略请求文本
                direction_map = {
                    'bullish': '看涨',
                    'bearish': '看跌',
                    'neutral': '震荡'
                }
                strength_map = {
                    'strong': '强烈',
                    'moderate': '一般',
                    'weak': '略微'
                }
                
                direction_cn = direction_map.get(analysis['market_direction'], '震荡')
                strength_cn = strength_map.get(analysis['direction_strength'], '一般')
                
                option_text = f"我{strength_cn}{direction_cn}{symbol}股票，{risk_preference}风险偏好"
                
                print(f"🎯 生成期权策略: {option_text}", flush=True)
                
                handler = OptionStrategyHandler()
                option_result = handler.handle_option_strategy_request(
                    option_text,
                    current_price=quote['price']
                )
                
                if option_result['success']:
                    option_strategy = option_result['strategy']
                    print(f"✅ 期权策略: {option_strategy['name']}", flush=True)
                
            except Exception as e:
                print(f"⚠️ 期权策略生成失败: {e}", flush=True)
        
        sys.stdout.flush()
        
        # 返回结果（包含期权策略）
        response_data = {
            "status": "success",
            "analysis": analysis
        }
        
        if option_strategy:
            response_data["option_strategy"] = option_strategy
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ 分析失败: {e}", flush=True)
        sys.stdout.flush()
        import traceback
        traceback.print_exc()
        
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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

# 注意：/<symbol> 路由必须放在最后！
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


