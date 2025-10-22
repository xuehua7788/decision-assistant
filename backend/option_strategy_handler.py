"""
期权策略处理器
整合NLP解析和策略映射，处理期权策略请求
"""

import sys
import os

# 确保可以导入algorithms模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from algorithms.option_nlp_parser import OptionParser, ParsedIntent
from algorithms.option_strategy_mapper import StrategyMapper, OptionStrategy
from typing import Dict, Optional


class OptionStrategyHandler:
    """期权策略请求处理器"""
    
    def __init__(self):
        self.parser = OptionParser()
        self.mapper = StrategyMapper()
        
        # 期权策略相关关键词（用于快速检测）
        self.option_keywords = [
            '期权', 'option', 'call', 'put', '看涨', '看跌',
            '策略', 'strategy', '执行价', 'strike',
            '权利金', 'premium', '价差', 'spread',
            '跨式', 'straddle', '蝶式', 'butterfly',
            '铁鹰', 'condor', '什么策略', '推荐策略'
        ]
    
    def is_option_strategy_request(self, user_input: str) -> bool:
        """
        判断用户输入是否是期权策略请求
        
        Args:
            user_input: 用户输入文本
            
        Returns:
            bool: 是否是期权策略请求
        """
        text_lower = user_input.lower()
        
        # 检查是否包含期权相关关键词
        for keyword in self.option_keywords:
            if keyword in text_lower:
                return True
        
        # 检查是否包含股票代码 + 方向词
        has_ticker = any(ticker in user_input.upper() for ticker in ['TSLA', 'AAPL', 'NVDA', 'MSFT'])
        has_ticker = has_ticker or any(name in user_input for name in ['特斯拉', '苹果', '英伟达', '微软'])
        
        direction_words = ['看涨', '看跌', '上涨', '下跌', '震荡']
        has_direction = any(word in user_input for word in direction_words)
        
        if has_ticker and has_direction:
            return True
        
        return False
    
    def handle_option_strategy_request(self, user_input: str, current_price: Optional[float] = None) -> Dict:
        """
        处理期权策略请求
        
        Args:
            user_input: 用户输入
            current_price: 当前股价（可选，如果没有则使用默认值300）
            
        Returns:
            Dict: 包含解析结果和推荐策略的字典
        """
        # 解析用户意图
        intent = self.parser.parse(user_input)
        
        # 如果解析置信度太低，返回错误
        if intent.confidence < 0.3:
            return {
                'success': False,
                'error': '抱歉，我无法从您的输入中识别出足够的信息来推荐期权策略。请提供更多细节，例如：\n'
                        '- 股票名称或代码（如"特斯拉"或"TSLA"）\n'
                        '- 您的看法（看涨/看跌/震荡）\n'
                        '- 强度（强烈/一般/略微）\n'
                        '- 风险偏好（激进/平衡/保守）',
                'confidence': intent.confidence
            }
        
        # 确定当前股价
        if current_price is None:
            # 使用默认价格（实际应用中应该从API获取实时价格）
            current_price = 300.0
            if intent.ticker:
                # 可以根据不同ticker设置不同的默认价格
                price_map = {
                    'TSLA': 250.0,
                    'AAPL': 180.0,
                    'NVDA': 450.0,
                    'MSFT': 380.0,
                    'GOOGL': 140.0,
                    'AMZN': 150.0,
                    'META': 320.0
                }
                current_price = price_map.get(intent.ticker, 300.0)
        
        # 映射到具体策略
        strategy = self.mapper.map_strategy(intent, current_price)
        
        # 构建返回结果
        result = {
            'success': True,
            'parsed_intent': {
                'ticker': intent.ticker,
                'direction': intent.direction,
                'strength': intent.strength,
                'timeframe': intent.timeframe,
                'risk_profile': intent.risk_profile,
                'confidence': round(intent.confidence, 2)
            },
            'strategy': {
                'name': strategy.name,
                'type': strategy.type,
                'description': strategy.description,
                'risk_level': strategy.risk_level,
                'parameters': strategy.parameters,
                'metrics': strategy.metrics,
                'payoff_data': strategy.payoff_data
            }
        }
        
        return result
    
    def generate_text_response(self, result: Dict) -> str:
        """
        生成文字形式的策略推荐回复
        
        Args:
            result: handle_option_strategy_request的返回结果
            
        Returns:
            str: 文字形式的回复
        """
        if not result['success']:
            return result['error']
        
        intent = result['parsed_intent']
        strategy = result['strategy']
        params = strategy['parameters']
        metrics = strategy['metrics']
        
        # 构建回复文本
        response_parts = []
        
        # 1. 意图识别
        ticker_text = intent['ticker'] if intent['ticker'] else '目标股票'
        direction_map = {'bullish': '看涨', 'bearish': '看跌', 'neutral': '震荡'}
        direction_text = direction_map.get(intent['direction'], intent['direction'])
        
        response_parts.append(f"📊 **分析结果**")
        response_parts.append(f"标的: {ticker_text}")
        response_parts.append(f"方向: {direction_text}")
        response_parts.append(f"强度: {intent['strength']}")
        response_parts.append(f"风险偏好: {intent['risk_profile']}")
        response_parts.append(f"置信度: {intent['confidence']*100:.0f}%")
        response_parts.append("")
        
        # 2. 策略推荐
        response_parts.append(f"💡 **推荐策略: {strategy['name']}**")
        response_parts.append(f"{strategy['description']}")
        response_parts.append(f"风险等级: {strategy['risk_level']}")
        response_parts.append("")
        
        # 3. 策略参数
        response_parts.append(f"📋 **策略参数**")
        response_parts.append(f"当前股价: ${params['current_price']:.2f}")
        if params.get('buy_strike'):
            response_parts.append(f"买入执行价: ${params['buy_strike']:.2f}")
        if params.get('sell_strike'):
            response_parts.append(f"卖出执行价: ${params['sell_strike']:.2f}")
        if params.get('premium_paid'):
            response_parts.append(f"支付权利金: ${params['premium_paid']:.2f}")
        if params.get('premium_received'):
            response_parts.append(f"收到权利金: ${params['premium_received']:.2f}")
        response_parts.append(f"到期时间: {params['expiry']}")
        response_parts.append("")
        
        # 4. 风险指标
        response_parts.append(f"⚠️ **风险指标**")
        max_gain = metrics['max_gain']
        max_gain_text = "无限" if max_gain >= 999999 else f"${max_gain:.2f}"
        response_parts.append(f"最大收益: {max_gain_text}")
        response_parts.append(f"最大损失: ${metrics['max_loss']:.2f}")
        response_parts.append(f"盈亏平衡点: ${metrics['breakeven']:.2f}")
        response_parts.append(f"成功概率: {metrics['probability']}")
        response_parts.append("")
        
        # 5. 提示
        response_parts.append("📈 **Payoff曲线已生成，请查看图表了解详细的盈亏情况。**")
        
        return "\n".join(response_parts)


# 测试函数
def test_handler():
    """测试处理器"""
    handler = OptionStrategyHandler()
    
    test_cases = [
        "我强烈看涨特斯拉股票，用什么策略？",
        "AAPL可能会下跌，保守一点",
        "英伟达震荡，激进策略",
        "买什么",  # 信息不足
    ]
    
    print("=== 期权策略处理器测试 ===\n")
    
    for i, text in enumerate(test_cases, 1):
        print(f"{'='*60}")
        print(f"测试 {i}: {text}")
        print(f"{'='*60}")
        
        # 检测是否是期权策略请求
        is_option = handler.is_option_strategy_request(text)
        print(f"是否是期权策略请求: {is_option}\n")
        
        if is_option:
            # 处理请求
            result = handler.handle_option_strategy_request(text)
            
            # 生成文字回复
            response = handler.generate_text_response(result)
            print(response)
        
        print("\n")


if __name__ == '__main__':
    test_handler()

