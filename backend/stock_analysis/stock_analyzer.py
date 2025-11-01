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
                     news_context: str = None) -> Optional[Dict]:
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
            system_prompt = self._build_system_prompt(risk_preference)
            user_prompt = self._build_user_prompt(
                symbol, current_data, history_data, rsi, user_opinion, news_context
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
    
    def _build_system_prompt(self, risk_preference: str) -> str:
        """构建系统提示词"""
        
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
1. **技术面分析**：价格走势、RSI指标、成交量变化、波动率
2. **基本面分析**：相关新闻、市场消息对股价的影响
3. **用户观点整合**：结合用户提供的研报或个人观点
4. **短期趋势**：最近5天的价格变化
5. **风险评估**：波动率、支撑位、阻力位
6. **综合策略**：技术面+基本面的投资策略

**输出格式**（严格JSON）：
{{
  "score": 75,
  "recommendation": "买入",
  "position_size": "20%",
  "target_price": 190.0,
  "stop_loss": 175.0,
  "key_points": [
    "技术面分析要点",
    "基本面分析要点",
    "用户观点评估",
    "风险提示"
  ],
  "analysis_summary": "综合分析总结（150字以内）",
  "strategy": "具体投资策略建议（结合技术面和基本面，100字以内）"
}}

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

请用中文分析，JSON键名用英文。"""
    
    def _build_user_prompt(self, symbol: str, current_data: Dict, 
                          history_data: list, rsi: float,
                          user_opinion: str = None, news_context: str = None) -> str:
        """构建用户提示词"""
        
        # 计算最近5天涨跌
        if len(history_data) >= 5:
            recent_5_days = history_data[-5:]
            price_change_5d = ((recent_5_days[-1]['close'] - recent_5_days[0]['close']) 
                              / recent_5_days[0]['close'] * 100)
        else:
            price_change_5d = 0
        
        # 计算波动率（最近30天）
        if len(history_data) >= 2:
            closes = [h['close'] for h in history_data]
            daily_returns = [(closes[i] - closes[i-1]) / closes[i-1] 
                            for i in range(1, len(closes))]
            volatility = (sum([r**2 for r in daily_returns]) / len(daily_returns)) ** 0.5 * 100
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
        
        # 添加新闻/消息
        if news_context:
            prompt += f"\n\n**相关新闻/消息**:\n{news_context}"
            prompt += "\n\n请评估该消息对股价的影响（利好/利空/中性），并纳入分析。"
        
        # 添加用户观点
        if user_opinion:
            prompt += f"\n\n**用户观点/研报**:\n{user_opinion}"
            prompt += "\n\n请结合用户观点，评估其合理性，并给出综合建议。"
        
        prompt += "\n\n请按照系统提示的JSON格式返回分析结果。"
        
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

