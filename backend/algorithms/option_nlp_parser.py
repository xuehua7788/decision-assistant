"""
期权策略自然语言解析器
解析用户输入，提取投资意图关键信息
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class ParsedIntent:
    """解析后的用户意图"""
    ticker: Optional[str] = None  # 股票代码
    direction: Optional[str] = None  # 方向: bullish, bearish, neutral
    strength: Optional[str] = None  # 强度: strong, moderate, slight
    timeframe: Optional[str] = None  # 时间: short, medium, long
    risk_profile: Optional[str] = None  # 风险偏好: aggressive, balanced, conservative
    confidence: float = 0.0  # 解析置信度
    raw_text: str = ""  # 原始输入


class OptionParser:
    """期权策略NLP解析器"""
    
    def __init__(self):
        # 方向关键词
        self.direction_keywords = {
            'bullish': ['看涨', '看多', '上涨', '涨', '突破', '新高', '买入', 'long', 'call', '做多', '上升', '牛市'],
            'bearish': ['看跌', '看空', '下跌', '跌', '回调', '做空', 'short', 'put', '下降', '熊市', '跌破'],
            'neutral': ['震荡', '横盘', '区间', '盘整', '不确定', '中性', 'neutral', '波动', '震荡市']
        }
        
        # 强度关键词
        self.strength_keywords = {
            'strong': ['强烈', '非常', '极度', '大幅', '暴涨', '暴跌', '必定', '肯定', '确信', '很', '十分'],
            'moderate': ['可能', '应该', '预计', '温和', '适度', '一般', '或许', '大概', '估计'],
            'slight': ['略微', '小幅', '稍微', '轻微', '也许', '微微', '稍稍']
        }
        
        # 时间关键词
        self.timeframe_keywords = {
            'short': ['短期', '近期', '本周', '本月', '1个月', '快速', '短线', '一周', '几天'],
            'medium': ['中期', '季度', '2-3个月', '几个月', '中线', '两个月', '三个月'],
            'long': ['长期', '年度', '长线', '半年', '一年', '长远', '长久']
        }
        
        # 风险偏好关键词
        self.risk_keywords = {
            'aggressive': ['激进', '赌', 'all in', '梭哈', '重仓', '高风险', '冒险', '大胆'],
            'balanced': ['平衡', '稳健', '适中', '中等', '均衡'],
            'conservative': ['保守', '稳妥', '安全', '低风险', '谨慎', '稳定']
        }
        
        # 股票代码和名称映射
        self.ticker_map = {
            '特斯拉': 'TSLA',
            '苹果': 'AAPL',
            '英伟达': 'NVDA',
            '微软': 'MSFT',
            '谷歌': 'GOOGL',
            '亚马逊': 'AMZN',
            '脸书': 'META',
            'meta': 'META',
            '奈飞': 'NFLX',
            '阿里巴巴': 'BABA',
            '腾讯': 'TCEHY',
            '比亚迪': 'BYDDY',
            '拼多多': 'PDD',
            '京东': 'JD',
            '百度': 'BIDU',
            '小鹏': 'XPEV',
            '蔚来': 'NIO',
            '理想': 'LI'
        }
    
    def parse(self, user_input: str) -> ParsedIntent:
        """
        解析用户输入
        
        Args:
            user_input: 用户的自然语言输入
            
        Returns:
            ParsedIntent: 解析后的意图对象
        """
        intent = ParsedIntent(raw_text=user_input)
        text_lower = user_input.lower()
        
        # 1. 提取股票代码
        intent.ticker = self._extract_ticker(user_input)
        
        # 2. 识别方向
        intent.direction = self._extract_direction(text_lower)
        
        # 3. 识别强度
        intent.strength = self._extract_strength(text_lower)
        
        # 4. 识别时间框架
        intent.timeframe = self._extract_timeframe(text_lower)
        
        # 5. 识别风险偏好
        intent.risk_profile = self._extract_risk_profile(text_lower)
        
        # 6. 计算置信度
        intent.confidence = self._calculate_confidence(intent)
        
        return intent
    
    def _extract_ticker(self, text: str) -> Optional[str]:
        """提取股票代码"""
        # 先检查中文名称
        for name, ticker in self.ticker_map.items():
            if name in text:
                return ticker
        
        # 检查英文ticker (大写字母，2-5个字符)
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        matches = re.findall(ticker_pattern, text)
        if matches:
            return matches[0]
        
        # 检查小写的ticker
        ticker_pattern_lower = r'\b([a-z]{2,5})\b'
        matches = re.findall(ticker_pattern_lower, text.lower())
        if matches:
            ticker_upper = matches[0].upper()
            # 只返回常见的ticker
            if ticker_upper in ['TSLA', 'AAPL', 'NVDA', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NFLX']:
                return ticker_upper
        
        return None
    
    def _extract_direction(self, text: str) -> Optional[str]:
        """识别方向倾向"""
        scores = {'bullish': 0, 'bearish': 0, 'neutral': 0}
        
        for direction, keywords in self.direction_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    scores[direction] += 1
        
        # 返回得分最高的方向
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        
        return None
    
    def _extract_strength(self, text: str) -> Optional[str]:
        """识别强度级别"""
        for strength, keywords in self.strength_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return strength
        
        # 默认返回moderate
        return 'moderate'
    
    def _extract_timeframe(self, text: str) -> Optional[str]:
        """识别时间框架"""
        for timeframe, keywords in self.timeframe_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return timeframe
        
        # 默认返回short
        return 'short'
    
    def _extract_risk_profile(self, text: str) -> Optional[str]:
        """识别风险偏好"""
        for risk, keywords in self.risk_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return risk
        
        # 默认返回balanced
        return 'balanced'
    
    def _calculate_confidence(self, intent: ParsedIntent) -> float:
        """
        计算解析置信度
        
        基于提取到的字段数量和质量
        """
        confidence = 0.0
        
        # 必要字段
        if intent.ticker:
            confidence += 0.3
        if intent.direction:
            confidence += 0.3
        
        # 可选字段
        if intent.strength:
            confidence += 0.15
        if intent.timeframe:
            confidence += 0.15
        if intent.risk_profile:
            confidence += 0.1
        
        return min(confidence, 1.0)


# 测试函数
def test_parser():
    """测试解析器"""
    parser = OptionParser()
    
    test_cases = [
        "我强烈看涨特斯拉股票，用什么策略？",
        "AAPL短期可能会下跌",
        "英伟达长期看多，但要保守一点",
        "MSFT震荡，想激进一点",
        "看跌TSLA，短期内会跌"
    ]
    
    print("=== 期权策略NLP解析器测试 ===\n")
    for i, text in enumerate(test_cases, 1):
        print(f"测试 {i}: {text}")
        intent = parser.parse(text)
        print(f"  Ticker: {intent.ticker}")
        print(f"  Direction: {intent.direction}")
        print(f"  Strength: {intent.strength}")
        print(f"  Timeframe: {intent.timeframe}")
        print(f"  Risk: {intent.risk_profile}")
        print(f"  Confidence: {intent.confidence:.2%}")
        print()


if __name__ == '__main__':
    test_parser()

