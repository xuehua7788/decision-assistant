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

**你的角色和任务**：
1. 你是一位专业、友好的分析师，善于用通俗易懂的语言解释复杂的金融概念
2. 用户可能会问你关于具体指标、新闻、或投资建议的问题
3. 你需要基于上述数据，结合你的专业知识，给出详细、有见地的回答
4. 如果用户问到某个具体指标（如"ROE为什么这么高？"），你要深入分析该指标的含义、影响因素、以及对投资的意义
5. 如果用户问到新闻影响，你要分析新闻的正面/负面影响，以及对股价的潜在影响
6. 保持对话的连贯性，记住之前讨论的内容
7. 如果用户的问题超出你掌握的数据范围，诚实地说明，并基于常识和经验给出合理推测

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
        
        # 调用stock_analyzer进行初步分析（Tom自主选择指标）
        from stock_analysis.stock_analyzer import StockAnalyzer
        
        analyzer = StockAnalyzer()
        
        # Tom自主分析（不需要用户指定custom_indicators）
        analysis = analyzer.analyze_stock(
            symbol=symbol,
            investment_style=investment_style,
            news_context=news_context,
            user_opinion=user_opinion,
            language='zh',
            custom_indicators=None  # Tom自主选择
        )
        
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
        
        # Tom回复
        tom_reply = tom.chat(
            conversation_history=conversation_history,
            stock_context=stock_context,
            user_message=user_message
        )
        
        print(f"✅ Tom回复: {tom_reply[:50]}...")
        
        return jsonify({
            'success': True,
            'tom_reply': tom_reply
        }), 200
        
    except Exception as e:
        print(f"❌ 对话失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

