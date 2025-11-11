#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
与Tom对话API
用户可以与AI分析师Tom进行多轮对话，讨论股票分析
"""

from flask import Blueprint, request, jsonify
import os
import requests
from typing import List, Dict

chat_tom_bp = Blueprint('chat_tom', __name__)

class TomChatAgent:
    """Tom对话Agent"""
    
    def __init__(self):
        self.api_key = os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        print("✅ Tom对话Agent已初始化")
    
    def chat(self, 
             conversation_history: List[Dict],
             stock_context: Dict,
             user_message: str) -> str:
        """
        与Tom对话
        
        Args:
            conversation_history: 历史对话记录
            stock_context: 股票上下文（包含所有分析数据）
            user_message: 用户当前消息
        
        Returns:
            Tom的回复
        """
        
        # 构建系统Prompt
        system_prompt = self._build_system_prompt(stock_context)
        
        # 构建消息列表
        messages = [{"role": "system", "content": system_prompt}]
        
        # 添加历史对话
        messages.extend(conversation_history)
        
        # 添加当前用户消息
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1500
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ Tom对话API错误: {response.status_code}")
                return "抱歉，我现在无法回答。请稍后再试。"
            
            result = response.json()
            tom_reply = result["choices"][0]["message"]["content"]
            
            return tom_reply
            
        except Exception as e:
            print(f"❌ Tom对话失败: {e}")
            return "抱歉，我遇到了一些技术问题。"
    
    def _detect_user_intent(self, user_message: str) -> Dict:
        """检测用户意图"""
        intent = {
            "show_price_chart": False,
            "show_indicators": [],
            "show_indicator_selector": False,
            "list_available_indicators": False  # 新增：是否询问可用指标
        }
        
        message_lower = user_message.lower()
        
        # 检测"有哪些指标"类问题
        list_keywords = ['有哪些指标', '哪些指标', '可以看什么', '能看哪些', '有什么数据', '都有什么指标', 'what indicators']
        if any(keyword in message_lower for keyword in list_keywords):
            intent["list_available_indicators"] = True
            intent["show_indicator_selector"] = True  # 同时提示可以选择
        
        # 检测价格走势请求
        price_keywords = ['走势', '价格', '图表', '历史', 'chart', 'price', 'trend', '涨跌']
        if any(keyword in message_lower for keyword in price_keywords):
            intent["show_price_chart"] = True
        
        # 检测指标请求（扩展更多指标）
        indicator_map = {
            'rsi': ['rsi', '相对强弱'],
            'macd': ['macd'],
            'roe': ['roe', '净资产收益率'],
            'pe': ['pe', '市盈率', 'p/e', 'pe比率'],
            'eps': ['eps', '每股收益'],
            'atr': ['atr', '波动率', '真实波幅'],
            'bbands': ['布林带', 'bollinger'],
            'market_cap': ['市值', 'market cap'],
            'profit_margin': ['利润率', 'profit margin'],
            'dividend_yield': ['股息率', 'dividend'],
            'peg': ['peg', 'peg比率'],
            'debt': ['负债', 'debt'],
            'sma': ['sma', '移动平均', 'moving average'],
            'volume': ['成交量', 'volume'],
            'cpi': ['cpi', '通胀'],
            'unemployment': ['失业率', 'unemployment'],
            'fed_rate': ['利率', 'fed rate', '联邦利率']
        }
        
        for indicator_id, keywords in indicator_map.items():
            if any(keyword in message_lower for keyword in keywords):
                intent["show_indicators"].append(indicator_id)
        
        # 检测是否需要指标选择器
        selector_keywords = ['选择指标', '自定义', '看看其他', '更多指标']
        if any(keyword in message_lower for keyword in selector_keywords):
            intent["show_indicator_selector"] = True
        
        return intent
    
    def _build_system_prompt(self, stock_context: Dict) -> str:
        """构建系统Prompt"""
        
        symbol = stock_context.get('symbol', 'N/A')
        current_price = stock_context.get('current_price', 'N/A')
        investment_style = stock_context.get('investment_style', 'balanced')
        
        # 提取数据
        company_overview = stock_context.get('company_overview', {})
        technical_indicators = stock_context.get('technical_indicators', {})
        economic_data = stock_context.get('economic_data', {})
        news_context = stock_context.get('news_context', '')
        initial_analysis = stock_context.get('initial_analysis', {})
        
        prompt = f"""你是一位资深股票分析师Tom，正在与投资者讨论 {symbol} 股票的投资机会。

**当前股票信息**：
- 股票代码: {symbol}
- 当前价格: ${current_price}
- 投资风格: {investment_style}

**你已经掌握的数据**：

1. **基本面数据**：
"""
        
        if company_overview:
            prompt += f"""
   - 市值: {company_overview.get('MarketCapitalization', 'N/A')}
   - PE比率: {company_overview.get('PERatio', 'N/A')}
   - EPS: {company_overview.get('EPS', 'N/A')}
   - ROE: {company_overview.get('ReturnOnEquityTTM', 'N/A')}
   - 利润率: {company_overview.get('ProfitMargin', 'N/A')}
   - 股息率: {company_overview.get('DividendYield', 'N/A')}
"""
        
        if technical_indicators:
            prompt += f"""
2. **技术面数据**：
   - RSI: {technical_indicators.get('rsi', 'N/A')}
   - MACD: {technical_indicators.get('macd', 'N/A')}
   - 布林带: {technical_indicators.get('bbands', 'N/A')}
   - ATR: {technical_indicators.get('atr', 'N/A')}
"""
        
        if economic_data:
            prompt += f"""
3. **宏观经济数据**：
   - CPI: {economic_data.get('cpi', 'N/A')}
   - 失业率: {economic_data.get('unemployment', 'N/A')}
   - 联邦利率: {economic_data.get('fed_rate', 'N/A')}
"""
        
        if news_context:
            prompt += f"""
4. **最新新闻**：
{news_context[:500]}...
"""
        
        if initial_analysis:
            prompt += f"""
5. **你的初步分析结论**：
   - 综合评分: {initial_analysis.get('score', 'N/A')}/100
   - 操作建议: {initial_analysis.get('recommendation', 'N/A')}
   - 市场方向: {initial_analysis.get('market_direction', 'N/A')}
   - 关键要点: {', '.join(initial_analysis.get('key_points', [])[:3])}
"""
        
        prompt += """

**你掌握的指标数据（来自Alpha Vantage）**：

📊 **基本面指标**（来自Company Overview）：
- 市值 (MarketCapitalization)
- 市盈率 P/E (PERatio)
- 每股收益 EPS (EPS)
- 净资产收益率 ROE (ReturnOnEquityTTM)
- 利润率 (ProfitMargin)
- 股息率 (DividendYield)
- PEG比率 (PEGRatio)
- 负债率 (DebtToEquity)
- 流动比率 (CurrentRatio)
- 账面价值 (BookValue)

📈 **技术面指标**（来自Technical Indicators）：
- RSI(14) - 相对强弱指标
- MACD - 移动平均收敛/发散
- ATR(14) - 平均真实波幅
- 布林带位置 (Bollinger Bands)
- SMA(50) - 50日简单移动平均
- SMA(200) - 200日简单移动平均
- 成交量 (Volume)
- 波动率 (Volatility)

🌍 **宏观经济指标**（来自Economic Indicators）：
- CPI通胀率
- 失业率
- 联邦利率
- GDP增长率
- 国债收益率

**你的角色和任务**：
1. 你是一位专业、友好的分析师，善于用通俗易懂的语言解释复杂的金融概念
2. 用户可能会问你关于具体指标、新闻、或投资建议的问题
3. 你需要基于上述数据，结合你的专业知识，给出详细、有见地的回答
4. **如果用户问"有哪些指标"，你必须只列出上面列出的指标，不要编造其他指标**
5. 如果用户问到某个具体指标（如"ROE为什么这么高？"），你要深入分析该指标的含义、影响因素、以及对投资的意义
6. 如果用户问到新闻影响，你要分析新闻的正面/负面影响，以及对股价的潜在影响
7. 保持对话的连贯性，记住之前讨论的内容
8. 如果用户问到的指标不在上述列表中，诚实地说"这个指标我暂时没有数据"
9. **当用户问"能看看XX指标吗"，你要告诉用户这个指标的当前值（从上述数据中获取）**

**对话风格**：
- 专业但不失亲和力
- 用数据说话，但避免堆砌数字
- 适当使用比喻和例子帮助理解
- 中文回答，简洁明了

**重要提醒**：
- 你只负责分析和讨论，不直接给出具体的交易指令（如"买入100股"）
- 如果用户问"应该买多少"，引导他们点击"策略生成"按钮，让交易员Jany来处理
- 保持客观中立，既要指出机会，也要提示风险

现在，请回答用户的问题。"""
        
        return prompt

# 全局单例
_tom_chat_agent = None

def get_tom_chat_agent():
    """获取Tom对话Agent单例"""
    global _tom_chat_agent
    if _tom_chat_agent is None:
        _tom_chat_agent = TomChatAgent()
    return _tom_chat_agent


@chat_tom_bp.route('/api/chat/tom/initial-analysis', methods=['POST'])
def initial_analysis():
    """
    Tom的初步综合分析（自主选择指标）
    
    请求体：
    {
        "symbol": "AAPL",
        "username": "bbb",
        "investment_style": "buffett",
        "news_context": "...",
        "user_opinion": "..."
    }
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        username = data.get('username')
        investment_style = data.get('investment_style', 'balanced')
        news_context = data.get('news_context', '')
        user_opinion = data.get('user_opinion', '')
        
        if not symbol:
            return jsonify({'error': '缺少股票代码'}), 400
        
        print(f"🎯 Tom开始初步分析: {symbol}")
        
        # 🆕 Tom智能选择指标
        from tom_indicator_selector import get_tom_indicator_selector
        
        selector = get_tom_indicator_selector()
        selected_indicators = selector.select_indicators(
            symbol=symbol,
            investment_style=investment_style
        )
        selection_reason = selector.get_selection_reason(
            symbol=symbol,
            investment_style=investment_style,
            selected_indicators=selected_indicators
        )
        
        print(f"🎯 Tom智能选择指标:")
        print(f"   基本面: {selected_indicators['fundamental']}")
        print(f"   技术面: {selected_indicators['technical']}")
        print(f"   宏观面: {selected_indicators['macro']}")
        print(f"   理由: {selection_reason}")
        
        # 使用alpha_vantage_client获取数据
        from stock_analysis.alpha_vantage_client import get_alpha_vantage_client
        from stock_analysis.stock_analyzer import get_stock_analyzer
        
        client = get_alpha_vantage_client()
        analyzer = get_stock_analyzer()
        
        # 获取股票数据
        quote = client.get_quote(symbol)
        if not quote:
            return jsonify({'error': f'未找到该股票: {symbol}'}), 404
        
        # 获取历史数据
        history = client.get_daily_history(symbol, days=30)
        if not history:
            return jsonify({'error': '无法获取历史数据'}), 500
        
        # 计算RSI
        closes = [h['close'] for h in history]
        rsi = client.calculate_rsi(closes)
        
        # 获取高级数据
        company_overview = client.get_company_overview(symbol)
        macd_data = client.get_technical_indicator(symbol, 'MACD', interval='daily')
        bbands_data = client.get_technical_indicator(symbol, 'BBANDS', interval='daily', time_period=20)
        atr_data = client.get_technical_indicator(symbol, 'ATR', interval='daily', time_period=14)
        cpi_data = client.get_economic_indicator('CPI')
        unemployment_data = client.get_economic_indicator('UNEMPLOYMENT')
        fed_rate_data = client.get_economic_indicator('FEDERAL_FUNDS_RATE')
        
        # 构建技术指标字典
        technical_indicators = {
            'rsi': rsi,
            'macd': macd_data,
            'bbands': bbands_data,
            'atr': atr_data
        }
        
        # 构建宏观经济数据字典
        economic_data = {
            'cpi': cpi_data,
            'unemployment': unemployment_data,
            'fed_rate': fed_rate_data
        }
        
        # 调用分析
        analysis = analyzer.analyze_stock(
            symbol=symbol,
            current_data=quote,
            history_data=history,
            rsi=rsi,
            investment_style=investment_style,
            news_context=news_context,
            user_opinion=user_opinion,
            language='zh',
            company_overview=company_overview,
            technical_indicators=technical_indicators,
            economic_data=economic_data,
            custom_indicators=selected_indicators
        )
        
        # 在分析结果中添加指标选择信息
        if analysis:
            analysis['selected_indicators'] = selected_indicators
            analysis['indicator_selection_reason'] = selection_reason
        
        if not analysis:
            return jsonify({'error': 'Tom分析失败'}), 500
        
        print(f"✅ Tom初步分析完成: 评分 {analysis.get('score')}/100")
        
        return jsonify({
            'success': True,
            'analysis': analysis,
            'message': 'Tom已完成初步分析，你可以继续与他讨论'
        }), 200
        
    except Exception as e:
        print(f"❌ 初步分析失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@chat_tom_bp.route('/api/chat/tom/message', methods=['POST'])
def chat_message():
    """
    与Tom对话
    
    请求体：
    {
        "symbol": "AAPL",
        "user_message": "ROE为什么这么高？",
        "conversation_history": [...],
        "stock_context": {...}
    }
    """
    try:
        data = request.json
        symbol = data.get('symbol')
        user_message = data.get('user_message')
        conversation_history = data.get('conversation_history', [])
        stock_context = data.get('stock_context', {})
        
        if not symbol or not user_message:
            return jsonify({'error': '缺少必要参数'}), 400
        
        print(f"💬 用户问Tom: {user_message[:50]}...")
        
        # 获取Tom对话Agent
        tom = get_tom_chat_agent()
        
        # 检测用户意图
        intent = tom._detect_user_intent(user_message)
        
        # Tom回复
        tom_reply = tom.chat(
            conversation_history=conversation_history,
            stock_context=stock_context,
            user_message=user_message
        )
        
        print(f"✅ Tom回复: {tom_reply[:50]}...")
        print(f"   意图: {intent}")
        
        # 构建结构化响应
        response_data = {
            'success': True,
            'tom_reply': tom_reply,
            'intent': intent
        }
        
        # 如果需要显示价格图表，添加历史数据
        if intent['show_price_chart']:
            history_data = stock_context.get('history_data', [])
            if history_data:
                response_data['price_chart_data'] = history_data[-30:]  # 最近30天
        
        # 如果需要显示指标，添加指标数据
        if intent['show_indicators']:
            indicators_data = {}
            company_overview = stock_context.get('company_overview', {})
            technical_indicators = stock_context.get('technical_indicators', {})
            
            for indicator_id in intent['show_indicators']:
                if indicator_id == 'rsi':
                    indicators_data['rsi'] = technical_indicators.get('rsi')
                elif indicator_id == 'macd':
                    indicators_data['macd'] = technical_indicators.get('macd')
                elif indicator_id == 'roe':
                    indicators_data['roe'] = company_overview.get('ReturnOnEquityTTM')
                elif indicator_id == 'pe':
                    indicators_data['pe'] = company_overview.get('PERatio')
                elif indicator_id == 'eps':
                    indicators_data['eps'] = company_overview.get('EPS')
                elif indicator_id == 'atr':
                    indicators_data['atr'] = technical_indicators.get('atr')
                elif indicator_id == 'bbands':
                    indicators_data['bbands'] = technical_indicators.get('bbands')
            
            response_data['indicators_data'] = indicators_data
        
        return jsonify(response_data), 200
        
    except Exception as e:
        print(f"❌ 对话失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

