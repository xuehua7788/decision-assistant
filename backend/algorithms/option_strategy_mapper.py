"""
期权策略映射器
根据解析的用户意图，推荐具体的期权策略并计算payoff
"""

import math
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from .option_nlp_parser import ParsedIntent


@dataclass
class StrategyParameters:
    """策略参数"""
    current_price: float  # 当前股价
    buy_strike: Optional[float] = None  # 买入执行价
    sell_strike: Optional[float] = None  # 卖出执行价
    premium_paid: Optional[float] = None  # 支付的权利金
    premium_received: Optional[float] = None  # 收到的权利金
    contracts: int = 1  # 合约数量
    expiry: str = "30天"  # 到期时间


@dataclass
class StrategyMetrics:
    """策略指标"""
    max_loss: float  # 最大损失
    max_gain: float  # 最大收益 (999999表示无限)
    breakeven: float  # 盈亏平衡点
    probability: str  # 成功概率估计


@dataclass
class OptionStrategy:
    """完整的期权策略"""
    name: str  # 策略名称
    type: str  # 策略类型
    description: str  # 策略描述
    parameters: Dict  # 策略参数
    metrics: Dict  # 策略指标
    payoff_data: List[Dict]  # Payoff曲线数据
    risk_level: str  # 风险等级


class StrategyMapper:
    """策略映射器"""
    
    def __init__(self):
        # 策略映射规则
        self.strategy_rules = {
            ('bullish', 'strong', 'aggressive'): {
                'name': '买入平值看涨期权',
                'type': 'long_call',
                'description': '适合强烈看涨且愿意承担高风险的投资者。潜在收益无限，最大损失为权利金。',
                'risk': '高'
            },
            ('bullish', 'strong', 'balanced'): {
                'name': '牛市价差',
                'type': 'bull_call_spread',
                'description': '买入较低执行价看涨期权，同时卖出较高执行价看涨期权。风险和收益都有限。',
                'risk': '中'
            },
            ('bullish', 'strong', 'conservative'): {
                'name': '卖出虚值看跌期权',
                'type': 'sell_otm_put',
                'description': '卖出低于当前价的看跌期权，收取权利金。适合愿意在较低价位买入的投资者。',
                'risk': '中低'
            },
            ('bullish', 'moderate', 'aggressive'): {
                'name': '比例价差',
                'type': 'ratio_spread',
                'description': '买入1个平值Call，卖出2个虚值Call。在温和上涨时获利最大。',
                'risk': '高'
            },
            ('bullish', 'moderate', 'balanced'): {
                'name': '牛市价差（宽价差）',
                'type': 'bull_call_spread_wide',
                'description': '较大的执行价差距，提供更多上涨空间。',
                'risk': '中'
            },
            ('bullish', 'moderate', 'conservative'): {
                'name': '卖出深度虚值看跌',
                'type': 'sell_deep_otm_put',
                'description': '卖出远低于当前价的看跌期权，风险较低但收益有限。',
                'risk': '低'
            },
            ('bearish', 'strong', 'aggressive'): {
                'name': '买入平值看跌期权',
                'type': 'long_put',
                'description': '适合强烈看跌的投资者。潜在收益高，最大损失为权利金。',
                'risk': '高'
            },
            ('bearish', 'strong', 'balanced'): {
                'name': '熊市价差',
                'type': 'bear_put_spread',
                'description': '买入较高执行价看跌期权，卖出较低执行价看跌期权。限制风险和收益。',
                'risk': '中'
            },
            ('bearish', 'strong', 'conservative'): {
                'name': '卖出虚值看涨期权',
                'type': 'sell_otm_call',
                'description': '卖出高于当前价的看涨期权，收取权利金。需要有股票作为担保。',
                'risk': '中'
            },
            ('neutral', 'moderate', 'aggressive'): {
                'name': '卖出跨式组合',
                'type': 'short_straddle',
                'description': '同时卖出同一执行价的Call和Put。适合预期波动率下降的震荡市。',
                'risk': '很高'
            },
            ('neutral', 'moderate', 'balanced'): {
                'name': '铁鹰式',
                'type': 'iron_condor',
                'description': '在震荡区间内收取权利金。风险和收益都有限，适合横盘市场。',
                'risk': '中'
            },
            ('neutral', 'moderate', 'conservative'): {
                'name': '铁蝶式',
                'type': 'iron_butterfly',
                'description': '类似铁鹰但执行价更接近，适合窄幅震荡。',
                'risk': '中低'
            },
        }
    
    def map_strategy(self, intent: ParsedIntent, current_price: float = 300.0) -> OptionStrategy:
        """
        根据意图映射策略
        
        Args:
            intent: 解析后的用户意图
            current_price: 当前股价（如果无法获取实时价格，使用默认值）
            
        Returns:
            OptionStrategy: 完整的期权策略
        """
        # 确保所有字段都有默认值
        direction = intent.direction or 'bullish'
        strength = intent.strength or 'moderate'
        risk_profile = intent.risk_profile or 'balanced'
        
        # 查找匹配的策略
        strategy_key = (direction, strength, risk_profile)
        strategy_template = self.strategy_rules.get(strategy_key)
        
        # 如果没有精确匹配，尝试找一个接近的
        if not strategy_template:
            strategy_template = self._find_closest_strategy(direction, strength, risk_profile)
        
        # 计算策略参数
        params = self._calculate_parameters(
            strategy_template['type'],
            current_price,
            intent.timeframe or 'short'
        )
        
        # 计算策略指标
        metrics = self._calculate_metrics(strategy_template['type'], params)
        
        # 生成payoff数据
        payoff_data = self._generate_payoff(strategy_template['type'], params)
        
        # 构建完整策略
        strategy = OptionStrategy(
            name=strategy_template['name'],
            type=strategy_template['type'],
            description=strategy_template['description'],
            parameters=asdict(params),
            metrics=asdict(metrics),
            payoff_data=payoff_data,
            risk_level=strategy_template['risk']
        )
        
        return strategy
    
    def _find_closest_strategy(self, direction: str, strength: str, risk_profile: str) -> Dict:
        """查找最接近的策略"""
        # 优先匹配方向，然后是风险偏好
        for key, template in self.strategy_rules.items():
            if key[0] == direction and key[2] == risk_profile:
                return template
        
        # 只匹配方向
        for key, template in self.strategy_rules.items():
            if key[0] == direction:
                return template
        
        # 返回默认策略
        return {
            'name': '牛市价差',
            'type': 'bull_call_spread',
            'description': '平衡的看涨策略',
            'risk': '中'
        }
    
    def _calculate_parameters(self, strategy_type: str, current_price: float, timeframe: str) -> StrategyParameters:
        """计算策略参数"""
        params = StrategyParameters(current_price=current_price)
        
        # 根据时间框架设置到期时间
        timeframe_map = {
            'short': '30天',
            'medium': '90天',
            'long': '180天'
        }
        params.expiry = timeframe_map.get(timeframe, '30天')
        
        # 根据策略类型设置执行价和权利金
        if strategy_type == 'long_call':
            params.buy_strike = current_price  # ATM
            params.premium_paid = current_price * 0.04  # 4%作为权利金
            
        elif strategy_type == 'bull_call_spread':
            params.buy_strike = current_price  # ATM
            params.sell_strike = current_price * 1.10  # OTM 10%
            params.premium_paid = current_price * 0.04
            params.premium_received = current_price * 0.02
            
        elif strategy_type == 'bull_call_spread_wide':
            params.buy_strike = current_price
            params.sell_strike = current_price * 1.15  # OTM 15%
            params.premium_paid = current_price * 0.04
            params.premium_received = current_price * 0.015
            
        elif strategy_type == 'sell_otm_put':
            params.sell_strike = current_price * 0.90  # OTM 10%
            params.premium_received = current_price * 0.03
            
        elif strategy_type == 'sell_deep_otm_put':
            params.sell_strike = current_price * 0.85  # OTM 15%
            params.premium_received = current_price * 0.02
            
        elif strategy_type == 'long_put':
            params.buy_strike = current_price  # ATM
            params.premium_paid = current_price * 0.04
            
        elif strategy_type == 'bear_put_spread':
            params.buy_strike = current_price  # ATM
            params.sell_strike = current_price * 0.90  # OTM 10%
            params.premium_paid = current_price * 0.04
            params.premium_received = current_price * 0.02
            
        elif strategy_type == 'sell_otm_call':
            params.sell_strike = current_price * 1.10  # OTM 10%
            params.premium_received = current_price * 0.03
            
        elif strategy_type == 'iron_condor':
            # 铁鹰：卖出OTM的Call和Put，买入更OTM的Call和Put
            params.buy_strike = current_price * 0.85  # 低Put
            params.sell_strike = current_price * 1.15  # 高Call
            params.premium_received = current_price * 0.06
            params.premium_paid = current_price * 0.03
            
        elif strategy_type == 'iron_butterfly':
            params.buy_strike = current_price * 0.90
            params.sell_strike = current_price * 1.10
            params.premium_received = current_price * 0.05
            params.premium_paid = current_price * 0.025
            
        elif strategy_type == 'short_straddle':
            params.sell_strike = current_price  # ATM
            params.premium_received = current_price * 0.08
        
        return params
    
    def _calculate_metrics(self, strategy_type: str, params: StrategyParameters) -> StrategyMetrics:
        """计算策略指标"""
        cp = params.current_price
        
        if strategy_type == 'long_call':
            max_loss = -params.premium_paid * 100  # 100股/合约
            max_gain = 999999  # 无限
            breakeven = params.buy_strike + params.premium_paid
            probability = "35%"
            
        elif strategy_type in ['bull_call_spread', 'bull_call_spread_wide']:
            net_premium = (params.premium_paid - params.premium_received) * 100
            max_loss = -net_premium
            max_gain = (params.sell_strike - params.buy_strike) * 100 - net_premium
            breakeven = params.buy_strike + (params.premium_paid - params.premium_received)
            probability = "45%"
            
        elif strategy_type in ['sell_otm_put', 'sell_deep_otm_put']:
            max_loss = -(params.sell_strike * 100 - params.premium_received * 100)
            max_gain = params.premium_received * 100
            breakeven = params.sell_strike - params.premium_received
            probability = "70%"
            
        elif strategy_type == 'long_put':
            max_loss = -params.premium_paid * 100
            max_gain = (params.buy_strike - 0) * 100 - params.premium_paid * 100  # 理论上股价可以跌到0
            breakeven = params.buy_strike - params.premium_paid
            probability = "35%"
            
        elif strategy_type == 'bear_put_spread':
            net_premium = (params.premium_paid - params.premium_received) * 100
            max_loss = -net_premium
            max_gain = (params.buy_strike - params.sell_strike) * 100 - net_premium
            breakeven = params.buy_strike - (params.premium_paid - params.premium_received)
            probability = "45%"
            
        elif strategy_type == 'sell_otm_call':
            max_loss = -999999  # 理论上无限（如果没有持有股票）
            max_gain = params.premium_received * 100
            breakeven = params.sell_strike + params.premium_received
            probability = "70%"
            
        elif strategy_type in ['iron_condor', 'iron_butterfly']:
            net_premium = (params.premium_received - params.premium_paid) * 100
            max_gain = net_premium
            max_loss = -((params.sell_strike - params.buy_strike) * 100 - net_premium) / 2
            breakeven = cp  # 简化，实际有两个盈亏平衡点
            probability = "60%"
            
        elif strategy_type == 'short_straddle':
            max_gain = params.premium_received * 100
            max_loss = -999999  # 理论上无限
            breakeven = cp  # 简化
            probability = "50%"
            
        else:
            # 默认值
            max_loss = -1000
            max_gain = 2000
            breakeven = cp
            probability = "50%"
        
        return StrategyMetrics(
            max_loss=round(max_loss, 2),
            max_gain=round(max_gain, 2) if max_gain < 999999 else 999999,
            breakeven=round(breakeven, 2),
            probability=probability
        )
    
    def _generate_payoff(self, strategy_type: str, params: StrategyParameters) -> List[Dict]:
        """生成payoff曲线数据"""
        cp = params.current_price
        
        # 生成股价范围：当前价格 ±30%
        price_range = []
        payoff_values = []
        
        min_price = cp * 0.7
        max_price = cp * 1.3
        step = (max_price - min_price) / 100
        
        for i in range(101):
            stock_price = min_price + i * step
            payoff = self._calculate_payoff_at_price(strategy_type, params, stock_price)
            price_range.append(round(stock_price, 2))
            payoff_values.append(round(payoff, 2))
        
        # 组合成数据点
        payoff_data = [
            {'price': price, 'payoff': payoff}
            for price, payoff in zip(price_range, payoff_values)
        ]
        
        return payoff_data
    
    def _calculate_payoff_at_price(self, strategy_type: str, params: StrategyParameters, stock_price: float) -> float:
        """计算特定股价下的payoff"""
        
        if strategy_type == 'long_call':
            # 买入Call的payoff
            intrinsic = max(0, stock_price - params.buy_strike)
            payoff = (intrinsic - params.premium_paid) * 100
            
        elif strategy_type in ['bull_call_spread', 'bull_call_spread_wide']:
            # 牛市价差
            long_call = max(0, stock_price - params.buy_strike)
            short_call = max(0, stock_price - params.sell_strike)
            net_premium = params.premium_paid - params.premium_received
            payoff = (long_call - short_call - net_premium) * 100
            
        elif strategy_type in ['sell_otm_put', 'sell_deep_otm_put']:
            # 卖出Put
            intrinsic = max(0, params.sell_strike - stock_price)
            payoff = (params.premium_received - intrinsic) * 100
            
        elif strategy_type == 'long_put':
            # 买入Put
            intrinsic = max(0, params.buy_strike - stock_price)
            payoff = (intrinsic - params.premium_paid) * 100
            
        elif strategy_type == 'bear_put_spread':
            # 熊市价差
            long_put = max(0, params.buy_strike - stock_price)
            short_put = max(0, params.sell_strike - stock_price)
            net_premium = params.premium_paid - params.premium_received
            payoff = (long_put - short_put - net_premium) * 100
            
        elif strategy_type == 'sell_otm_call':
            # 卖出Call
            intrinsic = max(0, stock_price - params.sell_strike)
            payoff = (params.premium_received - intrinsic) * 100
            
        elif strategy_type in ['iron_condor', 'iron_butterfly']:
            # 简化的铁鹰/铁蝶计算
            net_premium = params.premium_received - params.premium_paid
            if params.buy_strike < stock_price < params.sell_strike:
                payoff = net_premium * 100
            else:
                loss = min(
                    abs(stock_price - params.buy_strike),
                    abs(stock_price - params.sell_strike)
                )
                payoff = (net_premium - loss) * 100
            
        elif strategy_type == 'short_straddle':
            # 卖出跨式
            call_intrinsic = max(0, stock_price - params.sell_strike)
            put_intrinsic = max(0, params.sell_strike - stock_price)
            payoff = (params.premium_received - call_intrinsic - put_intrinsic) * 100
            
        else:
            payoff = 0
        
        return payoff


# 测试函数
def test_mapper():
    """测试策略映射器"""
    from .option_nlp_parser import OptionParser
    
    parser = OptionParser()
    mapper = StrategyMapper()
    
    test_input = "我强烈看涨特斯拉股票，激进一点"
    
    print("=== 期权策略映射器测试 ===\n")
    print(f"用户输入: {test_input}\n")
    
    # 解析
    intent = parser.parse(test_input)
    print(f"解析结果:")
    print(f"  Ticker: {intent.ticker}")
    print(f"  Direction: {intent.direction}")
    print(f"  Strength: {intent.strength}")
    print(f"  Risk: {intent.risk_profile}")
    print()
    
    # 映射策略
    strategy = mapper.map_strategy(intent, current_price=300.0)
    print(f"推荐策略:")
    print(f"  名称: {strategy.name}")
    print(f"  类型: {strategy.type}")
    print(f"  描述: {strategy.description}")
    print(f"  风险等级: {strategy.risk_level}")
    print()
    
    print(f"策略参数:")
    for key, value in strategy.parameters.items():
        print(f"  {key}: {value}")
    print()
    
    print(f"策略指标:")
    for key, value in strategy.metrics.items():
        print(f"  {key}: {value}")
    print()
    
    print(f"Payoff数据点数: {len(strategy.payoff_data)}")


if __name__ == '__main__':
    test_mapper()

