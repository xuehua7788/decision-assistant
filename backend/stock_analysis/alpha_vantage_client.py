#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Alpha Vantage API客户端
获取股票实时数据和历史数据
"""

import os
import requests
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class AlphaVantageClient:
    """Alpha Vantage API客户端"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_KEY')
        if not self.api_key:
            raise ValueError("ALPHA_VANTAGE_KEY not configured")
        
        self.base_url = "https://www.alphavantage.co/query"
        self.cache = {}  # 简单的内存缓存
        self.cache_ttl = 300  # 5分钟缓存
        
        print(f"✅ AlphaVantageClient initialized with key: {self.api_key[:10]}...")
    
    def _get_cache_key(self, function: str, symbol: str) -> str:
        """生成缓存键"""
        return f"{function}:{symbol}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """检查缓存是否有效"""
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp', 0)
        return (time.time() - cached_time) < self.cache_ttl
    
    def _set_cache(self, cache_key: str, data: dict):
        """设置缓存"""
        self.cache[cache_key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    def _get_cache(self, cache_key: str) -> Optional[dict]:
        """获取缓存"""
        if self._is_cache_valid(cache_key):
            return self.cache[cache_key]['data']
        return None
    
    def get_quote(self, symbol: str) -> Optional[Dict]:
        """
        获取股票实时报价
        
        Args:
            symbol: 股票代码（如AAPL）
        
        Returns:
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "price": 180.50,
                "change": 2.30,
                "change_percent": 1.29,
                "volume": 50000000,
                "high": 182.00,
                "low": 179.00,
                "open": 180.00,
                "previous_close": 178.20,
                "updated_at": "2025-11-01 16:00:00"
            }
        """
        cache_key = self._get_cache_key("GLOBAL_QUOTE", symbol)
        
        # 检查缓存
        cached_data = self._get_cache(cache_key)
        if cached_data:
            print(f"📦 使用缓存数据: {symbol}")
            return cached_data
        
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': self.api_key
            }
            
            print(f"🔍 请求Alpha Vantage: {symbol}")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ API请求失败: {response.status_code}")
                return None
            
            data = response.json()
            
            # 检查错误
            if 'Error Message' in data:
                print(f"❌ 无效股票代码: {symbol}")
                return None
            
            if 'Note' in data:
                print(f"⚠️ API限制: {data['Note']}")
                return None
            
            # 解析数据
            quote = data.get('Global Quote', {})
            if not quote:
                print(f"❌ 无数据返回: {symbol}")
                return None
            
            result = {
                "symbol": quote.get('01. symbol', symbol),
                "name": self._get_company_name(symbol),
                "price": float(quote.get('05. price', 0)),
                "change": float(quote.get('09. change', 0)),
                "change_percent": float(quote.get('10. change percent', '0').replace('%', '')),
                "volume": int(quote.get('06. volume', 0)),
                "high": float(quote.get('03. high', 0)),
                "low": float(quote.get('04. low', 0)),
                "open": float(quote.get('02. open', 0)),
                "previous_close": float(quote.get('08. previous close', 0)),
                "updated_at": quote.get('07. latest trading day', datetime.now().strftime('%Y-%m-%d'))
            }
            
            # 缓存结果
            self._set_cache(cache_key, result)
            
            print(f"✅ 获取成功: {symbol} - ${result['price']}")
            return result
            
        except Exception as e:
            print(f"❌ 获取报价失败: {e}")
            return None
    
    def get_daily_history(self, symbol: str, days: int = 30) -> Optional[List[Dict]]:
        """
        获取日线历史数据
        
        Args:
            symbol: 股票代码
            days: 获取天数（默认30天）
        
        Returns:
            [
                {
                    "date": "2025-11-01",
                    "open": 180.00,
                    "high": 182.00,
                    "low": 179.00,
                    "close": 180.50,
                    "volume": 50000000
                },
                ...
            ]
        """
        cache_key = self._get_cache_key(f"TIME_SERIES_DAILY_{days}", symbol)
        
        # 检查缓存
        cached_data = self._get_cache(cache_key)
        if cached_data:
            print(f"📦 使用缓存历史数据: {symbol}")
            return cached_data
        
        try:
            params = {
                'function': 'TIME_SERIES_DAILY',
                'symbol': symbol,
                'apikey': self.api_key,
                'outputsize': 'compact'  # 最近100天
            }
            
            print(f"🔍 请求历史数据: {symbol} ({days}天)")
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ API请求失败: {response.status_code}")
                return None
            
            data = response.json()
            
            # 检查错误
            if 'Error Message' in data:
                print(f"❌ 无效股票代码: {symbol}")
                return None
            
            if 'Note' in data:
                print(f"⚠️ API限制: {data['Note']}")
                return None
            
            # 解析时间序列数据
            time_series = data.get('Time Series (Daily)', {})
            if not time_series:
                print(f"❌ 无历史数据: {symbol}")
                return None
            
            # 转换为列表格式
            history = []
            for date_str, values in sorted(time_series.items(), reverse=True)[:days]:
                history.append({
                    "date": date_str,
                    "open": float(values.get('1. open', 0)),
                    "high": float(values.get('2. high', 0)),
                    "low": float(values.get('3. low', 0)),
                    "close": float(values.get('4. close', 0)),
                    "volume": int(values.get('5. volume', 0))
                })
            
            # 按日期正序排列
            history.reverse()
            
            # 缓存结果
            self._set_cache(cache_key, history)
            
            print(f"✅ 获取历史数据成功: {symbol} ({len(history)}条)")
            return history
            
        except Exception as e:
            print(f"❌ 获取历史数据失败: {e}")
            return None
    
    def calculate_volatility(self, prices: List[float]) -> Optional[float]:
        """
        计算实现波动率（30天）
        
        Args:
            prices: 价格列表（从旧到新）
        
        Returns:
            年化波动率（百分比）
        """
        if len(prices) < 2:
            return None
        
        # 计算日收益率
        daily_returns = [(prices[i] - prices[i-1]) / prices[i-1] 
                        for i in range(1, len(prices))]
        
        # 计算标准差
        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = variance ** 0.5
        
        # 年化波动率（假设252个交易日）
        annualized_volatility = std_dev * (252 ** 0.5) * 100
        
        return round(annualized_volatility, 2)
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        计算RSI指标
        
        Args:
            prices: 价格列表（从旧到新）
            period: RSI周期（默认14）
        
        Returns:
            RSI值（0-100）
        """
        if len(prices) < period + 1:
            return None
        
        # 计算价格变化
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # 分离涨跌
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [-d if d < 0 else 0 for d in deltas]
        
        # 计算平均涨跌
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def _get_company_name(self, symbol: str) -> str:
        """获取公司名称（简单映射）"""
        names = {
            'AAPL': 'Apple Inc.',
            'GOOGL': 'Alphabet Inc.',
            'MSFT': 'Microsoft Corporation',
            'TSLA': 'Tesla Inc.',
            'NVDA': 'NVIDIA Corporation',
            'AMZN': 'Amazon.com Inc.',
            'META': 'Meta Platforms Inc.',
            'NFLX': 'Netflix Inc.',
            'AMD': 'Advanced Micro Devices Inc.',
            'INTC': 'Intel Corporation'
        }
        return names.get(symbol.upper(), symbol)
    
    def get_trending_stocks(self) -> List[str]:
        """获取热门股票列表"""
        return ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'NVDA']
    
    def get_news(self, symbol: str, limit: int = 5) -> List[Dict]:
        """
        获取股票相关新闻
        
        Args:
            symbol: 股票代码
            limit: 返回新闻数量，默认5条
        
        Returns:
            [
                {
                    "title": "新闻标题",
                    "summary": "新闻摘要",
                    "url": "新闻链接",
                    "time_published": "发布时间",
                    "sentiment": "positive/neutral/negative",
                    "sentiment_score": 0.35
                }
            ]
        """
        cache_key = self._get_cache_key('NEWS', symbol)
        
        # 检查缓存（新闻缓存1小时）
        if cache_key in self.cache:
            cached_time = self.cache[cache_key].get('timestamp', 0)
            if (time.time() - cached_time) < 3600:  # 1小时缓存
                print(f"📰 使用缓存的新闻: {symbol}")
                return self.cache[cache_key]['data']
        
        print(f"📰 获取新闻: {symbol}")
        
        try:
            params = {
                'function': 'NEWS_SENTIMENT',
                'tickers': symbol,
                'apikey': self.api_key,
                'limit': 50  # 获取更多，然后筛选
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            
            if response.status_code != 200:
                print(f"❌ API请求失败: {response.status_code}")
                return []
            
            data = response.json()
            
            # 检查错误
            if 'Error Message' in data:
                print(f"❌ API错误: {data['Error Message']}")
                return []
            
            if 'Note' in data:
                print(f"⚠️ API限制: {data['Note']}")
                return []
            
            # 解析新闻
            news_list = []
            feed = data.get('feed', [])
            
            for item in feed[:limit]:  # 只取前limit条
                # 查找该股票的情绪分数
                sentiment_score = 0.0
                sentiment_label = 'neutral'
                
                for ticker_sentiment in item.get('ticker_sentiment', []):
                    if ticker_sentiment.get('ticker') == symbol:
                        sentiment_score = float(ticker_sentiment.get('ticker_sentiment_score', 0))
                        # 根据分数判断情绪
                        if sentiment_score > 0.15:
                            sentiment_label = 'positive'
                        elif sentiment_score < -0.15:
                            sentiment_label = 'negative'
                        break
                
                # 格式化时间
                time_str = item.get('time_published', '')
                if len(time_str) >= 8:
                    formatted_time = f"{time_str[0:4]}-{time_str[4:6]}-{time_str[6:8]}"
                    if len(time_str) >= 15:
                        formatted_time += f" {time_str[9:11]}:{time_str[11:13]}"
                else:
                    formatted_time = time_str
                
                news_item = {
                    'title': item.get('title', ''),
                    'summary': item.get('summary', '')[:200] + '...' if len(item.get('summary', '')) > 200 else item.get('summary', ''),
                    'url': item.get('url', ''),
                    'time_published': formatted_time,
                    'sentiment': sentiment_label,
                    'sentiment_score': round(sentiment_score, 2)
                }
                
                news_list.append(news_item)
            
            # 缓存结果
            self.cache[cache_key] = {
                'data': news_list,
                'timestamp': time.time()
            }
            
            print(f"✅ 获取到 {len(news_list)} 条新闻")
            return news_list
            
        except Exception as e:
            print(f"❌ 获取新闻失败: {e}")
            import traceback
            traceback.print_exc()
            return []


# 全局单例
_alpha_vantage_client = None

def get_alpha_vantage_client() -> AlphaVantageClient:
    """获取Alpha Vantage客户端实例"""
    global _alpha_vantage_client
    if _alpha_vantage_client is None:
        _alpha_vantage_client = AlphaVantageClient()
    return _alpha_vantage_client


# 测试代码
if __name__ == "__main__":
    print("=" * 60)
    print("Alpha Vantage Client - 测试")
    print("=" * 60)
    print()
    
    try:
        client = get_alpha_vantage_client()
        
        # 测试获取报价
        print("📊 测试获取AAPL报价...")
        quote = client.get_quote('AAPL')
        if quote:
            print(f"✅ 价格: ${quote['price']}, 涨跌: {quote['change_percent']}%")
        
        print()
        
        # 测试获取历史数据
        print("📈 测试获取AAPL历史数据...")
        history = client.get_daily_history('AAPL', days=30)
        if history:
            print(f"✅ 获取到 {len(history)} 条历史数据")
            print(f"   最新: {history[-1]['date']} - ${history[-1]['close']}")
            
            # 计算RSI
            closes = [h['close'] for h in history]
            rsi = client.calculate_rsi(closes)
            print(f"   RSI(14): {rsi}")
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

