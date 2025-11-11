#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
股票AI分析器
使用DeepSeek AI分析股票数据并给出投资建议
"""

import os
import requests
import json
from typing import Dict, Optional

class StockAnalyzer:
    """股票AI分析器"""
    
    def __init__(self, deepseek_api_key: str = None):
        self.api_key = deepseek_api_key or os.getenv('DEEPSEEK_API_KEY')
        if not self.api_key:
            raise ValueError("DEEPSEEK_API_KEY not configured")
        
        self.api_url = "https://api.deepseek.com/v1/chat/completions"
        print(f"✅ StockAnalyzer initialized")
    
    def analyze_stock(self, 
                     symbol: str,
                     current_data: Dict,
                     history_data: list,
                     rsi: float,
                     risk_preference: str = "balanced",
                     user_opinion: str = None,
                     news_context: str = None,
                     language: str = "zh",
                     investment_style: str = None,
                     company_overview: Dict = None,
                     technical_indicators: Dict = None,
                     economic_data: Dict = None) -> Optional[Dict]:
        """
        分析股票并给出投资建议
        
        Args:
            symbol: 股票代码
            current_data: 当前数据（价格、涨跌幅等）
            history_data: 历史数据（30天）
            rsi: RSI指标
            risk_preference: 风险偏好（conservative/balanced/aggressive）
            user_opinion: 用户观点或研报内容
            news_context: 相关新闻或消息
        
        Returns:
            {
                "score": 75,  # 综合评分 0-100
                "recommendation": "买入",  # 买入/观望/卖出
                "position_size": "20%",  # 建议仓位
                "target_price": 190.0,  # 目标价
                "stop_loss": 175.0,  # 止损价
                "key_points": [
                    "技术面强势，价格突破关键阻力位",
                    "RSI处于健康区间，未超买",
                    "成交量放大，市场关注度提升"
                ],
                "analysis_summary": "综合分析..."
            }
        """
        print(f"🤖 开始AI分析: {symbol}")
        
        try:
            # 构建分析提示词
            system_prompt = self._build_system_prompt(risk_preference, language, investment_style, current_data.get('name', symbol))
            user_prompt = self._build_user_prompt(
                symbol, current_data, history_data, rsi, user_opinion, news_context, language,
                company_overview, technical_indicators, economic_data
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
                    "temperature": 0.5,  # 中等温度，平衡创造性和稳定性
                    "max_tokens": 1500
                },
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"❌ DeepSeek API错误: {response.status_code}")
                return None
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            print(f"✅ AI分析完成")
            print(f"   响应长度: {len(ai_response)} 字符")
            
            # 解析JSON
            try:
                analysis = json.loads(ai_response.strip())
                
                # 验证必需字段
                required_fields = ["score", "recommendation", "position_size", 
                                 "target_price", "stop_loss", "key_points"]
                for field in required_fields:
                    if field not in analysis:
                        print(f"⚠️ 缺少字段: {field}")
                        analysis[field] = self._get_default_value(field)
                
                return analysis
                
            except json.JSONDecodeError as e:
                print(f"⚠️ JSON解析失败，尝试提取JSON部分...")
                # 尝试提取JSON部分
                import re
                json_match = re.search(r'\{.*\}', ai_response, re.DOTALL)
                if json_match:
                    analysis = json.loads(json_match.group())
                    return analysis
                else:
                    print(f"❌ 无法解析AI响应")
                    return None
                    
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _build_system_prompt(self, risk_preference: str, language: str = "zh", investment_style: str = None, company_name: str = "") -> str:
        """构建系统提示词"""
        
        # 如果指定了投资风格，使用大师风格的提示词
        if investment_style:
            try:
                from stock_analysis.investment_styles import get_style_prompt
                return get_style_prompt(investment_style, "", company_name)
            except Exception as e:
                print(f"⚠️ 加载投资风格失败: {e}，使用默认风格")
        
        # 默认风格
        if language == "en":
            risk_profiles = {
                "conservative": "Conservative investor, focusing on capital protection and preferring low-risk investments",
                "balanced": "Balanced investor, seeking balance between risk and return",
                "aggressive": "Aggressive investor, willing to take higher risks for higher returns"
            }
        else:
            risk_profiles = {
                "conservative": "保守型投资者，注重资本保护，偏好低风险投资",
                "balanced": "平衡型投资者，追求风险与收益的平衡",
                "aggressive": "激进型投资者，愿意承担较高风险以追求更高收益"
            }
        
        risk_desc = risk_profiles.get(risk_preference, risk_profiles["balanced"])
        
        return f"""你是一个专业的股票分析师，擅长技术分析和基本面分析。

**用户画像**: {risk_desc}

**你的任务**：
综合分析股票数据、市场消息和用户观点，给出全面的投资建议。

**分析维度**：
1. **技术面分析**：价格走势、RSI、MACD、布林带、ATR、成交量变化、波动率
2. **基本面分析**：市盈率、ROE、利润率、股息率、市值等公司财务数据
3. **宏观经济**：CPI通胀率、失业率、联邦利率等宏观环境
4. **市场消息**：相关新闻、市场消息对股价的影响
5. **用户观点整合**：结合用户提供的研报或个人观点
6. **短期趋势**：最近5天的价格变化
7. **风险评估**：波动率、ATR、支撑位、阻力位
8. **综合策略**：技术面+基本面+宏观面的全方位投资策略

**输出格式**（严格JSON）：
{{
  "score": 75,
  "recommendation": "买入",
  "market_direction": "bullish",
  "direction_strength": "strong",
  "position_size": "20%",
  "target_price": 190.0,
  "stop_loss": 175.0,
  "key_points": [
    "技术面分析要点",
    "基本面分析要点（如果有新闻）",
    "用户观点评估（如果有）",
    "风险提示"
  ],
  "analysis_summary": "综合分析总结（150字以内）",
  "strategy": "具体投资策略建议（结合技术面和基本面，100字以内）"
}}

**market_direction说明**（必须返回，必须与strategy文字一致）：
- "bullish": 看涨（技术面强势 + 新闻利好 + 明确建议买入）
- "bearish": 看跌（技术面走弱 + 新闻利空 + 明确建议卖出）
- "neutral": 震荡/观望（信号不明确、谨慎、不是买入时候、小仓位试探）

**⚠️ 重要**：如果strategy中提到"不是买入时候"、"观望"、"谨慎"、"小仓位"，必须设置market_direction为"neutral"！

**direction_strength说明**：
- "strong": 强烈（评分>80或<20，明确看涨或看跌）
- "moderate": 一般（评分50-80或20-50）
- "weak": 略微（评分接近50，或文字谨慎）

**评分标准**（0-100分）：
- 90-100: 强烈买入信号
- 70-89: 买入信号
- 50-69: 观望
- 30-49: 卖出信号
- 0-29: 强烈卖出信号

**操作建议**：
- 买入：技术面强势，趋势向上
- 观望：信号不明确，等待更好时机
- 卖出：技术面走弱，趋势向下

**仓位建议**（根据风险偏好）：
- 保守型：5-15%
- 平衡型：15-25%
- 激进型：25-40%

**重要原则**：
1. 基于实际数据分析，不要臆测
2. 考虑用户的风险偏好
3. 提供具体的价格目标和止损位
4. key_points要简洁明了，每条不超过30字

请用{'中文' if language == 'zh' else '英文'}分析，JSON键名用英文。"""
    
    def _build_user_prompt(self, symbol: str, current_data: Dict, 
                          history_data: list, rsi: float,
                          user_opinion: str = None, news_context: str = None,
                          language: str = "zh",
                          company_overview: Dict = None,
                          technical_indicators: Dict = None,
                          economic_data: Dict = None) -> str:
        """构建用户提示词"""
        
        # 计算最近5天涨跌
        if len(history_data) >= 5:
            recent_5_days = history_data[-5:]
            price_change_5d = ((recent_5_days[-1]['close'] - recent_5_days[0]['close']) 
                              / recent_5_days[0]['close'] * 100)
        else:
            price_change_5d = 0
        
        # 计算波动率（最近30天，年化）
        if len(history_data) >= 2:
            closes = [h['close'] for h in history_data]
            daily_returns = [(closes[i] - closes[i-1]) / closes[i-1] 
                            for i in range(1, len(closes))]
            mean_return = sum(daily_returns) / len(daily_returns)
            variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
            std_dev = variance ** 0.5
            # 年化波动率（假设252个交易日）
            volatility = std_dev * (252 ** 0.5) * 100
        else:
            volatility = 0
        
        # 找出最高最低价（30天）
        if history_data:
            high_30d = max([h['high'] for h in history_data])
            low_30d = min([h['low'] for h in history_data])
        else:
            high_30d = current_data['high']
            low_30d = current_data['low']
        
        prompt = f"""请分析以下股票数据：

**股票代码**: {symbol} ({current_data.get('name', symbol)})

**当前数据**:
- 当前价格: ${current_data['price']:.2f}
- 今日涨跌: {current_data['change_percent']:.2f}%
- 今日最高: ${current_data['high']:.2f}
- 今日最低: ${current_data['low']:.2f}
- 成交量: {current_data['volume']:,}

**技术指标**:
- RSI(14): {rsi:.2f}
- 最近5日涨跌: {price_change_5d:.2f}%
- 30日波动率: {volatility:.2f}%
- 30日最高: ${high_30d:.2f}
- 30日最低: ${low_30d:.2f}

**价格走势**（最近10天）:
"""
        
        # 添加最近10天价格
        recent_10_days = history_data[-10:] if len(history_data) >= 10 else history_data
        for day in recent_10_days:
            prompt += f"\n{day['date']}: ${day['close']:.2f} (成交量: {day['volume']:,})"
        
        # 🆕 添加公司基本面数据
        if company_overview:
            prompt += "\n\n**📊 公司基本面** (Premium数据):\n"
            try:
                pe_ratio = company_overview.get('PERatio', 'N/A')
                eps = company_overview.get('EPS', 'N/A')
                roe = company_overview.get('ReturnOnEquityTTM', 'N/A')
                profit_margin = company_overview.get('ProfitMargin', 'N/A')
                dividend_yield = company_overview.get('DividendYield', 'N/A')
                market_cap = company_overview.get('MarketCapitalization', 'N/A')
                
                prompt += f"- 市值: {market_cap}\n"
                prompt += f"- 市盈率(P/E): {pe_ratio}\n"
                prompt += f"- 每股收益(EPS): {eps}\n"
                if roe != 'N/A':
                    prompt += f"- 净资产收益率(ROE): {float(roe)*100:.2f}%\n"
                if profit_margin != 'N/A':
                    prompt += f"- 利润率: {float(profit_margin)*100:.2f}%\n"
                if dividend_yield != 'N/A':
                    prompt += f"- 股息率: {float(dividend_yield)*100:.2f}%\n"
            except Exception as e:
                print(f"⚠️ 解析基本面数据失败: {e}")
        
        # 🆕 添加高级技术指标
        if technical_indicators:
            prompt += "\n\n**📈 高级技术指标** (Premium数据):\n"
            
            # MACD
            if technical_indicators.get('macd'):
                try:
                    macd_data = technical_indicators['macd']
                    if 'Technical Analysis: MACD' in macd_data:
                        latest_macd = list(macd_data['Technical Analysis: MACD'].values())[0]
                        prompt += f"- MACD: {latest_macd.get('MACD', 'N/A')}\n"
                        prompt += f"- MACD信号线: {latest_macd.get('MACD_Signal', 'N/A')}\n"
                        prompt += f"- MACD柱状图: {latest_macd.get('MACD_Hist', 'N/A')}\n"
                except:
                    pass
            
            # 布林带
            if technical_indicators.get('bbands'):
                try:
                    bbands_data = technical_indicators['bbands']
                    if 'Technical Analysis: BBANDS' in bbands_data:
                        latest_bb = list(bbands_data['Technical Analysis: BBANDS'].values())[0]
                        prompt += f"- 布林带上轨: ${float(latest_bb.get('Real Upper Band', 0)):.2f}\n"
                        prompt += f"- 布林带中轨: ${float(latest_bb.get('Real Middle Band', 0)):.2f}\n"
                        prompt += f"- 布林带下轨: ${float(latest_bb.get('Real Lower Band', 0)):.2f}\n"
                except:
                    pass
            
            # ATR (平均真实波幅)
            if technical_indicators.get('atr'):
                try:
                    atr_data = technical_indicators['atr']
                    if 'Technical Analysis: ATR' in atr_data:
                        latest_atr = list(atr_data['Technical Analysis: ATR'].values())[0]
                        prompt += f"- ATR(14): ${float(latest_atr.get('ATR', 0)):.2f}\n"
                except:
                    pass
        
        # 🆕 添加宏观经济数据
        if economic_data:
            prompt += "\n\n**🌍 宏观经济环境** (Premium数据):\n"
            
            # CPI
            if economic_data.get('cpi'):
                try:
                    cpi_data = economic_data['cpi']
                    if 'data' in cpi_data and len(cpi_data['data']) > 0:
                        latest_cpi = cpi_data['data'][0]
                        prompt += f"- 最新CPI(通胀率): {latest_cpi.get('value', 'N/A')}%\n"
                except:
                    pass
            
            # 失业率
            if economic_data.get('unemployment'):
                try:
                    unemployment_data = economic_data['unemployment']
                    if 'data' in unemployment_data and len(unemployment_data['data']) > 0:
                        latest_unemployment = unemployment_data['data'][0]
                        prompt += f"- 失业率: {latest_unemployment.get('value', 'N/A')}%\n"
                except:
                    pass
            
            # 联邦基金利率
            if economic_data.get('fed_rate'):
                try:
                    fed_rate_data = economic_data['fed_rate']
                    if 'data' in fed_rate_data and len(fed_rate_data['data']) > 0:
                        latest_fed_rate = fed_rate_data['data'][0]
                        prompt += f"- 联邦基金利率: {latest_fed_rate.get('value', 'N/A')}%\n"
                except:
                    pass
        
        # 添加新闻/消息
        if news_context:
            prompt += f"\n\n**相关新闻/消息**:\n{news_context}"
            prompt += "\n\n⚠️ 重要：请务必在key_points中包含一条「基本面分析要点」，评估该新闻对股价的影响（利好/利空/中性），并在analysis_summary中总结新闻影响。"
        
        # 添加用户观点
        if user_opinion:
            prompt += f"\n\n**用户观点/研报**:\n{user_opinion}"
            prompt += "\n\n⚠️ 重要：请务必在key_points中包含一条「用户观点评估」，评估观点的合理性，并在analysis_summary中总结您对用户观点的看法。"
        
        prompt += "\n\n请按照系统提示的JSON格式返回分析结果。"
        
        # 如果有新闻或用户观点，强调综合分析
        if news_context or user_opinion:
            prompt += "\n\n⚠️ 特别提醒：您的分析必须综合考虑："
            prompt += "\n1. 技术指标（RSI、价格走势、波动率）"
            if news_context:
                prompt += "\n2. 新闻消息的影响（必须在key_points和analysis_summary中体现）"
            if user_opinion:
                prompt += f"\n{3 if news_context else 2}. 用户观点的合理性（必须在key_points和analysis_summary中体现）"
            prompt += "\n\n请确保analysis_summary是一个完整的综合分析，而不仅仅是技术面分析。"
        
        return prompt
    
    def _get_default_value(self, field: str):
        """获取字段的默认值"""
        defaults = {
            "score": 50,
            "recommendation": "观望",
            "position_size": "10%",
            "target_price": 0.0,
            "stop_loss": 0.0,
            "key_points": ["数据不足，建议谨慎操作"],
            "analysis_summary": "分析数据不足"
        }
        return defaults.get(field, None)


# 全局单例
_stock_analyzer = None

def get_stock_analyzer() -> StockAnalyzer:
    """获取股票分析器实例"""
    global _stock_analyzer
    if _stock_analyzer is None:
        _stock_analyzer = StockAnalyzer()
    return _stock_analyzer


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("Stock Analyzer - 测试")
    print("=" * 60)
    print()
    
    # 模拟数据
    current_data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "price": 180.50,
        "change": 2.30,
        "change_percent": 1.29,
        "volume": 50000000,
        "high": 182.00,
        "low": 179.00
    }
    
    history_data = [
        {"date": f"2025-10-{i:02d}", "close": 175 + i * 0.5, "high": 176 + i * 0.5, 
         "low": 174 + i * 0.5, "volume": 45000000 + i * 100000}
        for i in range(1, 31)
    ]
    
    rsi = 65.5
    
    try:
        analyzer = get_stock_analyzer()
        result = analyzer.analyze_stock(
            symbol="AAPL",
            current_data=current_data,
            history_data=history_data,
            rsi=rsi,
            risk_preference="balanced"
        )
        
        if result:
            print("\n" + "=" * 60)
            print("分析结果:")
            print("=" * 60)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

