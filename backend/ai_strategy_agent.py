#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI策略Agent - Jany
专门负责根据分析结果生成具体的期权和股票交易策略
"""

import os
import requests
import json
from typing import Dict, Optional, List

class AIStrategyAgent:
    """
    AI策略生成Agent - Jany
    基于Tom的分析结果和Alpha Vantage期权数据，生成具体交易策略
    """
    
    def __init__(self, deepseek_api_key: str = None):
        self.api_key = deepseek_api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        print(f"✅ AI策略Agent (Jany) 已初始化")
    
    def infer_target_symbol_from_conversation(self, conversation_history: List[Dict], available_symbols: List[str]) -> str:
        """
        从对话历史中推断用户最终选择的股票
        
        Args:
            conversation_history: 对话历史
            available_symbols: 可选的股票列表
        
        Returns:
            推断出的股票代码
        """
        if not conversation_history or not available_symbols:
            return available_symbols[0] if available_symbols else None
        
        # 从最近的消息开始查找
        for msg in reversed(conversation_history):
            content = msg.get('content', '').upper()
            
            # 检查是否提到某只股票
            for symbol in available_symbols:
                if symbol.upper() in content:
                    print(f"🎯 从对话中推断用户选择: {symbol}")
                    return symbol
        
        # 如果没有明确提到，返回第一只（主股票）
        print(f"💡 未明确提到股票，默认使用主股票: {available_symbols[0]}")
        return available_symbols[0]
    
    def generate_trading_strategy(self,
                                  symbol: str,
                                  current_price: float,
                                  tom_analysis: Dict,
                                  option_chain_data: Dict,
                                  investment_style: str,
                                  notional_value: float = 30000,
                                  conversation_history: List[Dict] = None,
                                  selected_symbols: List[str] = None) -> Optional[Dict]:
        """
        生成交易策略
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
            tom_analysis: Tom的分析结果
            option_chain_data: Alpha Vantage期权链数据
            investment_style: 投资风格
            notional_value: 名义本金
            conversation_history: 用户与Tom的对话历史（可选）
        
        Returns:
            {
                "option_strategy": {...},
                "stock_strategy": {...},
                "explanation": "..."
            }
        """
        
        print(f"🤖 AI策略Agent (Jany) 开始生成策略: {symbol}")
        
        try:
            # 构建System Prompt
            system_prompt = self._build_system_prompt(investment_style)
            
            # 构建User Prompt（包含对话历史）
            user_prompt = self._build_user_prompt(
                symbol, current_price, tom_analysis, 
                option_chain_data, notional_value, conversation_history
            )
            
            # 调用DeepSeek API
            response = requests.post(
                self.api_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.3,  # 较低温度，确保策略稳定
                    "max_tokens": 2000
                },
                timeout=60  # 增加超时时间，因为包含对话历史
            )
            
            if response.status_code != 200:
                print(f"❌ AI策略Agent API错误: {response.status_code}")
                return None
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            print(f"✅ AI策略生成完成")
            print(f"   响应长度: {len(ai_response)} 字符")
            
            # 解析JSON
            try:
                # 尝试直接解析
                strategy = json.loads(ai_response)
                return strategy
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败，尝试提取JSON部分...")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    strategy = json.loads(json_match.group())
                    return strategy
                else:
                    print(f"❌ 无法解析AI策略响应")
                    return None
                    
        except Exception as e:
            print(f"❌ 策略生成失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_system_prompt(self, investment_style: str) -> str:
        """构建System Prompt"""
        
        style_desc = {
            'buffett': '巴菲特价值投资风格：注重安全边际，偏好实值或平值期权，保守稳健',
            'lynch': '彼得·林奇成长投资风格：关注成长潜力，平衡风险收益，适度杠杆',
            'soros': '索罗斯趋势投机风格：追求高杠杆，虚值期权，快进快出',
            'aggressive': '激进风格：高杠杆，虚值期权，追求最大收益',
            'balanced': '平衡风格：平值期权，风险收益平衡',
            'conservative': '保守风格：实值期权，注重本金安全'
        }
        
        style_guidance = style_desc.get(investment_style, style_desc['balanced'])
        
        return f"""你是一位专业的期权交易员 Jany，擅长根据市场分析生成具体的交易策略。

**你的角色**：
- 你的同事Tom（分析师）已经完成了股票分析
- 你的任务是根据Tom的分析和实时期权数据，生成具体的交易策略
- 你需要给出两个策略：期权策略 + Delta One股票策略

**用户投资风格**：{style_guidance}

**期权策略要求**：
1. 必须从提供的Alpha Vantage真实期权数据中选择
2. 根据Tom的分析方向选择Call或Put
3. 根据投资风格选择执行价（实值/平值/虚值）
4. 计算等价股数 = 名义本金 / 当前股价
5. 计算期权费 = 等价股数 × 期权单价
6. 记录期权的Delta值

**Delta One股票策略要求**：
1. 股票名义本金 = 期权名义本金 × |期权Delta|
2. 保证金 = 股票名义本金 × 10%
3. 股数 = 股票名义本金 / 当前股价（取整）
4. 设置止损价和止盈价

**策略匹配逻辑**：
- Tom说"强烈看涨" + 激进风格 → 虚值Call（执行价高于当前价3-5%）
- Tom说"看涨" + 平衡风格 → 平值Call（执行价接近当前价）
- Tom说"看涨" + 保守风格 → 略实值Call（执行价低于当前价2-3%）
- Tom说"观望/谨慎" → 不推荐期权，或推荐观望
- Tom说"看跌" → 选择Put期权

**输出格式**（严格JSON）：
{{
  "option_strategy": {{
    "type": "Long Call",
    "symbol": "AAPL250116C00185000",
    "underlying": "AAPL",
    "option_type": "call",
    "strike_price": 185.0,
    "expiry_date": "2025-01-16",
    "days_to_expiry": 66,
    "equivalent_shares": 100.0,
    "premium_per_share": 8.50,
    "total_premium": 850.0,
    "delta": 0.5607,
    "data_source": "Alpha Vantage Real Data",
    "reasoning": "Tom强烈看涨（评分78），选择略虚值Call（执行价$185 vs 当前价$182.50），符合巴菲特稳健风格"
  }},
  "stock_strategy": {{
    "type": "Long Stock",
    "symbol": "AAPL",
    "shares": 92,
    "entry_price": 182.50,
    "notional": 16821.0,
    "margin": 1682.1,
    "stop_loss": 175.0,
    "take_profit": 195.0,
    "delta": 0.5607,
    "reasoning": "Delta One策略：股票名义本金 = $30,000 × 0.5607 = $16,821，保证金10% = $1,682"
  }},
  "explanation": "综合Tom的分析（看涨，评分78）和{investment_style}投资风格，推荐略虚值Call期权配合Delta One股票策略。期权提供杠杆收益，股票策略风险敞口相当，便于A/B对比。",
  "risk_warning": "期权有到期风险，最大损失为期权费$850。股票策略需保证金$1,682，止损价$175。"
}}

**重要原则**：
1. 必须从提供的期权数据中选择，不能编造
2. 如果Tom说"观望"，可以返回 {{"recommendation": "观望", "explanation": "..."}}
3. 所有数字必须基于真实计算，不能估算
4. Delta One策略的股票名义本金必须 = 期权名义本金 × |期权Delta|
5. 解释要清晰，说明为什么选择这个策略

请用中文分析，JSON键名用英文。"""
    
    def _build_user_prompt(self, 
                          symbol: str,
                          current_price: float,
                          tom_analysis: Dict,
                          option_chain_data: Dict,
                          notional_value: float,
                          conversation_history: List[Dict] = None) -> str:
        """构建User Prompt"""
        
        # 提取Tom的分析结果
        score = tom_analysis.get('score', 50)
        recommendation = tom_analysis.get('recommendation', '观望')
        market_direction = tom_analysis.get('market_direction', 'neutral')
        direction_strength = tom_analysis.get('direction_strength', 'moderate')
        strategy_text = tom_analysis.get('strategy', '')
        analysis_summary = tom_analysis.get('analysis_summary', '')
        
        # 格式化期权数据
        option_data_text = self._format_option_data(option_chain_data)
        
        prompt = f"""
**交易标的**: {symbol}
**当前价格**: ${current_price}
**名义本金**: ${notional_value}

**Tom的初步分析结果**：
- 综合评分: {score}/100
- 操作建议: {recommendation}
- 市场方向: {market_direction} ({direction_strength})
- 分析总结: {analysis_summary}
- 具体策略: {strategy_text}"""
        
        # 添加对话历史
        if conversation_history and len(conversation_history) > 0:
            prompt += "\n\n**用户与Tom的对话历史**："
            prompt += "\n（用户在与Tom讨论后，对投资有了更深入的理解，请仔细阅读对话内容）\n"
            
            for i, msg in enumerate(conversation_history[-10:], 1):  # 只显示最近10条
                role = "用户" if msg.get('role') == 'user' else "Tom"
                content = msg.get('content', '')[:200]  # 限制长度
                prompt += f"\n{i}. {role}: {content}"
            
            prompt += "\n\n⚠️ 重要：请综合Tom的初步分析和对话中的讨论，生成最合适的交易策略。"
        
        prompt += f"""

**Alpha Vantage实时期权数据**：
{option_data_text}

**你的任务**：
1. 仔细阅读Tom的分析，理解他的市场判断
2. 从上述期权数据中选择最合适的期权
3. 计算期权策略的具体参数
4. 生成配套的Delta One股票策略
5. 解释为什么选择这个策略

**计算示例**：
- 等价股数 = ${notional_value} / ${current_price} = {notional_value/current_price:.2f}股
- 如果选择执行价$185的Call，Delta=0.5607，期权费$8.50/股
  - 期权总费用 = {notional_value/current_price:.2f} × $8.50 = ${(notional_value/current_price)*8.50:.2f}
  - 股票名义本金 = ${notional_value} × 0.5607 = ${notional_value*0.5607:.2f}
  - 股票保证金 = ${notional_value*0.5607:.2f} × 10% = ${notional_value*0.5607*0.1:.2f}
  - 股票股数 = ${notional_value*0.5607:.2f} / ${current_price} = {int(notional_value*0.5607/current_price)}股

请按照JSON格式返回策略。
"""
        
        return prompt
    
    def _format_option_data(self, option_chain_data: Dict) -> str:
        """格式化期权链数据"""
        
        if not option_chain_data or 'data' not in option_chain_data:
            return "⚠️ 无可用期权数据"
        
        options = option_chain_data['data'][:10]  # 只显示前10个
        
        text = "可选期权列表：\n\n"
        
        for i, opt in enumerate(options, 1):
            text += f"{i}. {opt.get('contractID', 'N/A')}\n"
            text += f"   类型: {opt.get('type', 'N/A')}\n"
            text += f"   执行价: ${opt.get('strike', 'N/A')}\n"
            text += f"   到期日: {opt.get('expiration', 'N/A')}\n"
            text += f"   期权费: ${opt.get('last', 'N/A')}/股\n"
            text += f"   Delta: {opt.get('delta', 'N/A')}\n"
            text += f"   隐含波动率: {opt.get('impliedVolatility', 'N/A')}\n"
            text += f"   成交量: {opt.get('volume', 'N/A')}\n"
            text += "\n"
        
        return text


# 全局单例
_ai_strategy_agent = None

def get_ai_strategy_agent():
    """获取AI策略Agent单例"""
    global _ai_strategy_agent
    if _ai_strategy_agent is None:
        _ai_strategy_agent = AIStrategyAgent()
    return _ai_strategy_agent

