// 多语言配置文件
export const translations = {
  zh: {
    // 导航栏
    stockAnalysis: '📈 股票分析',
    algorithmMode: '🧮 算法模式',
    chatMode: '💬 聊天模式',
    userProfile: '👤 用户画像',
    
    // 股票搜索
    searchTitle: '智能股票分析',
    searchPlaceholder: '输入美股代码（如 AAPL=苹果, TSLA=特斯拉）',
    searchButton: '搜索',
    hotStocks: '热门股票:',
    
    // 股票信息
    currentPrice: '当前价格',
    change: '涨跌',
    volume: '成交量',
    high: '最高',
    low: '最低',
    rsi: 'RSI指标',
    volatility: '30日波动率',
    updatedAt: '更新时间',
    
    // K线图
    priceChart: '价格走势（30天）',
    keyMetrics: '关键指标',
    
    // 风险偏好
    riskPreference: '风险偏好：',
    conservative: '保守',
    balanced: '平衡',
    aggressive: '激进',
    
    // 新闻
    latestNews: '最新相关新闻（点击选择）：',
    loadingNews: '正在加载新闻...',
    selectedNews: '选中的新闻/自定义消息（可选）：',
    newsPlaceholder: '点击上方新闻自动填充，或手动输入...',
    
    // 用户观点
    userOpinion: '您的观点/研报（可选）：',
    opinionPlaceholder: '例如：我认为该公司基本面良好，技术创新能力强，长期看好...',
    
    // AI分析按钮
    startAnalysis: '开始AI综合分析',
    analyzing: '分析中...',
    newsSelected: '已选择新闻',
    opinionEntered: '已输入观点',
    analysisHint: '提示：选择新闻或输入观点可获得更全面的分析',
    
    // AI分析结果
    aiAnalysis: 'AI 综合分析',
    score: '综合评分',
    recommendation: '操作建议',
    positionSize: '建议仓位',
    targetPrice: '目标价',
    stopLoss: '止损价',
    keyPoints: '分析要点',
    summary: '综合分析',
    strategy: '投资策略',
    
    // 操作建议
    buy: '买入',
    hold: '观望',
    sell: '卖出',
    
    // 期权策略
    optionStrategy: '推荐期权策略',
    riskLevel: '风险等级',
    strategyParams: '策略参数：',
    buyStrike: '买入执行价',
    sellStrike: '卖出执行价',
    expiry: '到期时间',
    riskMetrics: '风险指标：',
    maxGain: '最大收益',
    maxLoss: '最大损失',
    breakeven: '盈亏平衡',
    unlimited: '无限',
    
    // 错误信息
    errorStockNotFound: '未找到该股票',
    errorApiLimit: '请求过快，请稍后再试',
    errorNetwork: '网络连接失败',
    errorAnalysisFailed: 'AI分析失败',
    errorSearchFirst: '请先搜索股票',
    
    // 加载状态
    loading: '加载中...',
    
    // 情感标签
    positive: '利好',
    negative: '利空',
    neutral: '中性'
  },
  
  en: {
    // Navigation
    stockAnalysis: '📈 Stock Analysis',
    algorithmMode: '🧮 Algorithm Mode',
    chatMode: '💬 Chat Mode',
    userProfile: '👤 User Profile',
    
    // Stock Search
    searchTitle: 'Intelligent Stock Analysis',
    searchPlaceholder: 'Enter US stock symbol (e.g., AAPL, TSLA)',
    searchButton: 'Search',
    hotStocks: 'Hot Stocks:',
    
    // Stock Info
    currentPrice: 'Current Price',
    change: 'Change',
    volume: 'Volume',
    high: 'High',
    low: 'Low',
    rsi: 'RSI',
    volatility: '30-Day Volatility',
    updatedAt: 'Updated',
    
    // Price Chart
    priceChart: 'Price Trend (30 Days)',
    keyMetrics: 'Key Metrics',
    
    // Risk Preference
    riskPreference: 'Risk Preference:',
    conservative: 'Conservative',
    balanced: 'Balanced',
    aggressive: 'Aggressive',
    
    // News
    latestNews: 'Latest News (Click to Select):',
    loadingNews: 'Loading news...',
    selectedNews: 'Selected News/Custom Message (Optional):',
    newsPlaceholder: 'Click news above to auto-fill, or enter manually...',
    
    // User Opinion
    userOpinion: 'Your Opinion/Research (Optional):',
    opinionPlaceholder: 'e.g., I believe the company has strong fundamentals and innovation capabilities...',
    
    // AI Analysis Button
    startAnalysis: 'Start AI Analysis',
    analyzing: 'Analyzing...',
    newsSelected: 'News Selected',
    opinionEntered: 'Opinion Entered',
    analysisHint: 'Tip: Select news or enter opinion for more comprehensive analysis',
    
    // AI Analysis Results
    aiAnalysis: 'AI Comprehensive Analysis',
    score: 'Score',
    recommendation: 'Recommendation',
    positionSize: 'Position Size',
    targetPrice: 'Target Price',
    stopLoss: 'Stop Loss',
    keyPoints: 'Key Points',
    summary: 'Summary',
    strategy: 'Strategy',
    
    // Recommendations
    buy: 'Buy',
    hold: 'Hold',
    sell: 'Sell',
    
    // Option Strategy
    optionStrategy: 'Recommended Option Strategy',
    riskLevel: 'Risk Level',
    strategyParams: 'Strategy Parameters:',
    buyStrike: 'Buy Strike',
    sellStrike: 'Sell Strike',
    expiry: 'Expiry',
    riskMetrics: 'Risk Metrics:',
    maxGain: 'Max Gain',
    maxLoss: 'Max Loss',
    breakeven: 'Breakeven',
    unlimited: 'Unlimited',
    
    // Error Messages
    errorStockNotFound: 'Stock not found',
    errorApiLimit: 'Too many requests, please try again later',
    errorNetwork: 'Network connection failed',
    errorAnalysisFailed: 'AI analysis failed',
    errorSearchFirst: 'Please search for a stock first',
    
    // Loading State
    loading: 'Loading...',
    
    // Sentiment Labels
    positive: 'Positive',
    negative: 'Negative',
    neutral: 'Neutral'
  }
};

// 获取翻译文本
export const t = (key, lang = 'zh') => {
  return translations[lang]?.[key] || translations['zh'][key] || key;
};

// 获取当前语言
export const getCurrentLanguage = () => {
  return localStorage.getItem('language') || 'zh';
};

// 设置语言
export const setLanguage = (lang) => {
  localStorage.setItem('language', lang);
};

