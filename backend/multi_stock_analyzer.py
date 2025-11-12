#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多股票分析模块
获取多只股票的完整数据并进行综合分析
"""

from typing import List, Dict, Optional
from stock_analysis.alpha_vantage_client import get_alpha_vantage_client


class MultiStockAnalyzer:
    """多股票分析器"""
    
    def __init__(self):
        self.client = get_alpha_vantage_client()
    
    def fetch_multiple_stocks_data(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        获取多只股票的数据
        
        Args:
            symbols: 股票代码列表，如 ['META', 'GOOGL', 'NVDA']
        
        Returns:
            {
                'META': {
                    'quote': {...},
                    'history': [...],
                    'rsi': 65.5,
                    'company_overview': {...},
                    'technical_indicators': {...}
                },
                'GOOGL': {...},
                ...
            }
        """
        all_stocks_data = {}
        
        for symbol in symbols:
            print(f"📊 获取股票数据: {symbol}")
            
            try:
                # 1. 获取实时报价
                quote = self.client.get_quote(symbol)
                if not quote:
                    print(f"❌ 无法获取 {symbol} 的报价")
                    continue
                
                # 2. 获取历史数据
                history = self.client.get_daily_history(symbol, days=30)
                if not history:
                    print(f"❌ 无法获取 {symbol} 的历史数据")
                    continue
                
                # 3. 计算RSI
                closes = [h['close'] for h in history]
                rsi = self.client.calculate_rsi(closes)
                
                # 4. 获取公司基本面
                company_overview = self.client.get_company_overview(symbol)
                
                # 5. 获取技术指标
                macd_data = self.client.get_technical_indicator(symbol, 'MACD', interval='daily')
                bbands_data = self.client.get_technical_indicator(symbol, 'BBANDS', interval='daily', time_period=20)
                atr_data = self.client.get_technical_indicator(symbol, 'ATR', interval='daily', time_period=14)
                
                technical_indicators = {
                    'rsi': rsi,
                    'macd': macd_data,
                    'bbands': bbands_data,
                    'atr': atr_data
                }
                
                # 6. 整合数据
                all_stocks_data[symbol] = {
                    'quote': quote,
                    'history': history,
                    'rsi': rsi,
                    'company_overview': company_overview,
                    'technical_indicators': technical_indicators
                }
                
                print(f"✅ {symbol} 数据获取完成")
                
            except Exception as e:
                print(f"❌ 获取 {symbol} 数据失败: {e}")
                continue
        
        return all_stocks_data
    
    def format_multi_stock_context(self, stocks_data: Dict[str, Dict]) -> str:
        """
        格式化多股票数据为AI可读的上下文
        
        Args:
            stocks_data: fetch_multiple_stocks_data() 返回的数据
        
        Returns:
            格式化的文本，包含所有股票的关键信息
        """
        context_parts = []
        
        context_parts.append("📊 **多股票对比分析**\n")
        
        for symbol, data in stocks_data.items():
            quote = data['quote']
            company = data['company_overview']
            
            stock_info = f"""
**{symbol}** - {quote.get('name', symbol)}
- 当前价格: ${quote['price']:.2f}
- 涨跌幅: {quote['change_percent']:.2f}%
- 市值: {company.get('MarketCapitalization', 'N/A') if company else 'N/A'}
- PE比率: {company.get('PERatio', 'N/A') if company else 'N/A'}
- EPS: {company.get('EPS', 'N/A') if company else 'N/A'}
- ROE: {company.get('ReturnOnEquityTTM', 'N/A') if company else 'N/A'}
- RSI(14): {data['rsi']:.2f}
"""
            context_parts.append(stock_info)
        
        return "\n".join(context_parts)


# 单例模式
_multi_stock_analyzer_instance = None

def get_multi_stock_analyzer():
    """获取MultiStockAnalyzer单例"""
    global _multi_stock_analyzer_instance
    if _multi_stock_analyzer_instance is None:
        _multi_stock_analyzer_instance = MultiStockAnalyzer()
    return _multi_stock_analyzer_instance

