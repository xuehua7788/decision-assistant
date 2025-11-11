#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tom智能指标选择器
根据股票特点、投资风格、市场环境智能选择最相关的指标
"""

from typing import Dict, List

class TomIndicatorSelector:
    """Tom的智能指标选择器"""
    
    def __init__(self):
        # 定义所有可用指标
        self.all_indicators = {
            'fundamental': ['market_cap', 'pe_ratio', 'eps', 'roe', 'profit_margin', 
                          'dividend_yield', 'peg_ratio', 'debt_to_equity', 'current_ratio', 'book_value'],
            'technical': ['rsi', 'macd', 'atr', 'bbands', 'sma_50', 'sma_200', 'volume', 'volatility'],
            'macro': ['cpi', 'unemployment', 'fed_rate', 'gdp_growth', 'treasury_yield']
        }
        
        # 投资风格偏好
        self.style_preferences = {
            'buffett': {
                'fundamental': ['roe', 'pe_ratio', 'eps', 'profit_margin', 'debt_to_equity', 'book_value'],
                'technical': ['sma_200', 'volume'],
                'macro': ['fed_rate', 'gdp_growth']
            },
            'lynch': {
                'fundamental': ['peg_ratio', 'eps', 'roe', 'market_cap'],
                'technical': ['rsi', 'macd', 'volume'],
                'macro': ['gdp_growth', 'cpi']
            },
            'soros': {
                'fundamental': ['pe_ratio', 'market_cap'],
                'technical': ['rsi', 'macd', 'atr', 'bbands', 'volatility'],
                'macro': ['fed_rate', 'cpi', 'unemployment']
            },
            'balanced': {
                'fundamental': ['pe_ratio', 'eps', 'roe', 'profit_margin'],
                'technical': ['rsi', 'macd', 'bbands'],
                'macro': ['cpi', 'fed_rate']
            }
        }
    
    def select_indicators(self, 
                         symbol: str,
                         investment_style: str = 'balanced',
                         sector: str = None) -> Dict[str, List[str]]:
        """
        智能选择指标
        
        Args:
            symbol: 股票代码
            investment_style: 投资风格
            sector: 行业（可选）
        
        Returns:
            选中的指标字典
        """
        
        # 基于投资风格选择
        style = investment_style.lower() if investment_style else 'balanced'
        selected = self.style_preferences.get(style, self.style_preferences['balanced']).copy()
        
        # 基于股票特点调整
        symbol_upper = symbol.upper()
        
        # 科技股：更关注成长性指标
        tech_stocks = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX']
        if symbol_upper in tech_stocks:
            if 'peg_ratio' not in selected['fundamental']:
                selected['fundamental'].append('peg_ratio')
            if 'roe' not in selected['fundamental']:
                selected['fundamental'].append('roe')
            # 科技股波动大，关注技术指标
            if 'volatility' not in selected['technical']:
                selected['technical'].append('volatility')
        
        # 传统价值股：更关注分红和负债
        value_stocks = ['IBM', 'JPM', 'JNJ', 'PG', 'KO', 'WMT', 'XOM']
        if symbol_upper in value_stocks:
            if 'dividend_yield' not in selected['fundamental']:
                selected['fundamental'].append('dividend_yield')
            if 'debt_to_equity' not in selected['fundamental']:
                selected['fundamental'].append('debt_to_equity')
            if 'current_ratio' not in selected['fundamental']:
                selected['fundamental'].append('current_ratio')
        
        # 金融股：特别关注负债和流动性
        financial_stocks = ['JPM', 'BAC', 'GS', 'MS', 'C', 'WFC']
        if symbol_upper in financial_stocks:
            if 'debt_to_equity' not in selected['fundamental']:
                selected['fundamental'].append('debt_to_equity')
            if 'current_ratio' not in selected['fundamental']:
                selected['fundamental'].append('current_ratio')
            # 金融股对利率敏感
            if 'fed_rate' not in selected['macro']:
                selected['macro'].append('fed_rate')
        
        # 确保每个类别至少有3个指标，最多6个
        for category in ['fundamental', 'technical', 'macro']:
            if len(selected[category]) < 3:
                # 补充到3个
                available = [ind for ind in self.all_indicators[category] 
                           if ind not in selected[category]]
                needed = 3 - len(selected[category])
                selected[category].extend(available[:needed])
            elif len(selected[category]) > 6:
                # 限制到6个
                selected[category] = selected[category][:6]
        
        return selected
    
    def get_selection_reason(self, 
                            symbol: str,
                            investment_style: str,
                            selected_indicators: Dict[str, List[str]]) -> str:
        """
        生成指标选择理由
        
        Args:
            symbol: 股票代码
            investment_style: 投资风格
            selected_indicators: 选中的指标
        
        Returns:
            选择理由文本
        """
        
        reasons = []
        
        # 投资风格理由
        style_reasons = {
            'buffett': '巴菲特价值投资风格，重点关注基本面指标（ROE、PE、负债率等）',
            'lynch': '彼得·林奇成长投资风格，关注成长性指标（PEG、EPS增长等）',
            'soros': '索罗斯趋势投机风格，重点关注技术面和宏观指标',
            'balanced': '平衡投资风格，综合考虑基本面、技术面和宏观面'
        }
        
        style = investment_style.lower() if investment_style else 'balanced'
        reasons.append(style_reasons.get(style, style_reasons['balanced']))
        
        # 股票特点理由
        symbol_upper = symbol.upper()
        
        if symbol_upper in ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'META', 'NVDA', 'TSLA', 'NFLX']:
            reasons.append(f'{symbol}是科技股，额外关注成长性指标（PEG、ROE）和波动率')
        elif symbol_upper in ['IBM', 'JPM', 'JNJ', 'PG', 'KO', 'WMT', 'XOM']:
            reasons.append(f'{symbol}是传统价值股，额外关注分红率和财务稳健性')
        elif symbol_upper in ['JPM', 'BAC', 'GS', 'MS', 'C', 'WFC']:
            reasons.append(f'{symbol}是金融股，特别关注负债率、流动性和利率环境')
        
        # 指标数量
        total_indicators = sum(len(v) for v in selected_indicators.values())
        reasons.append(f'共选择{total_indicators}个指标进行深度分析')
        
        return '；'.join(reasons) + '。'


# 全局单例
_tom_indicator_selector = None

def get_tom_indicator_selector():
    """获取Tom指标选择器单例"""
    global _tom_indicator_selector
    if _tom_indicator_selector is None:
        _tom_indicator_selector = TomIndicatorSelector()
    return _tom_indicator_selector

