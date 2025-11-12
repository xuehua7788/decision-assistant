import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { getCurrentLanguage, setLanguage } from './i18n';

function StockAnalysis({ apiUrl }) {
  const [symbol, setSymbol] = useState('');
  const [selectedSymbols, setSelectedSymbols] = useState([]); // 🆕 多股票选择
  const [stockData, setStockData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [investmentStyle, setInvestmentStyle] = useState('buffett');
  const [customStyleName, setCustomStyleName] = useState(''); // 🆕 自定义风格名称
  const [customStyleDesc, setCustomStyleDesc] = useState(''); // 🆕 自定义风格描述
  const [newsContext, setNewsContext] = useState('');
  const [newsList, setNewsList] = useState([]); // 改为数组存储多条新闻
  const [loadingNews, setLoadingNews] = useState(false);
  // eslint-disable-next-line no-unused-vars
  const [stockStrategy, setStockStrategy] = useState(null); // 保留：可能在策略接受时使用
  const [dualStrategyData, setDualStrategyData] = useState(null);
  const [language, setLang] = useState(getCurrentLanguage());
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);
  
  // 自定义指标选择（从localStorage加载或使用默认值）
  const [customIndicators, setCustomIndicators] = useState(() => {
    const saved = localStorage.getItem('customIndicators');
    return saved ? JSON.parse(saved) : {
      fundamental: ['market_cap', 'pe_ratio', 'eps', 'roe', 'profit_margin', 'dividend_yield'],
      technical: ['rsi', 'macd', 'atr', 'bbands'],
      macro: ['cpi', 'unemployment', 'fed_rate']
    };
  });
  const [showIndicatorSelector, setShowIndicatorSelector] = useState(false);
  const [selectorCategory, setSelectorCategory] = useState('fundamental'); // 当前编辑的类别
  
  // 新增：Tom对话相关状态
  const [conversationHistory, setConversationHistory] = useState([]);
  const [userMessage, setUserMessage] = useState('');
  const [sendingMessage, setSendingMessage] = useState(false);
  const [showChatWindow, setShowChatWindow] = useState(false);
  
  // 可用指标定义
  const availableIndicators = {
    fundamental: [
      { id: 'market_cap', label: '市值', icon: '💰' },
      { id: 'pe_ratio', label: '市盈率 P/E', icon: '📊' },
      { id: 'eps', label: '每股收益 EPS', icon: '💵' },
      { id: 'roe', label: 'ROE', icon: '📈' },
      { id: 'profit_margin', label: '利润率', icon: '💹' },
      { id: 'dividend_yield', label: '股息率', icon: '💎' },
      { id: 'peg_ratio', label: 'PEG比率', icon: '🎯' },
      { id: 'debt_to_equity', label: '负债率', icon: '⚖️' },
      { id: 'current_ratio', label: '流动比率', icon: '💧' },
      { id: 'book_value', label: '账面价值', icon: '📚' }
    ],
    technical: [
      { id: 'rsi', label: 'RSI(14)', icon: '📉' },
      { id: 'macd', label: 'MACD', icon: '📊' },
      { id: 'atr', label: 'ATR(14)', icon: '📏' },
      { id: 'bbands', label: '布林带位置', icon: '📐' },
      { id: 'sma_50', label: 'SMA(50)', icon: '📈' },
      { id: 'sma_200', label: 'SMA(200)', icon: '📊' },
      { id: 'volume', label: '成交量', icon: '📦' },
      { id: 'volatility', label: '波动率', icon: '🌊' }
    ],
    macro: [
      { id: 'cpi', label: 'CPI通胀率', icon: '💰' },
      { id: 'unemployment', label: '失业率', icon: '👥' },
      { id: 'fed_rate', label: '联邦利率', icon: '🏦' },
      { id: 'gdp_growth', label: 'GDP增长', icon: '📈' },
      { id: 'treasury_yield', label: '国债收益率', icon: '📜' }
    ]
  };
  
  // 打开指标选择器
  // eslint-disable-next-line no-unused-vars
  const openIndicatorSelector = (category) => {
    setSelectorCategory(category);
    setShowIndicatorSelector(true);
  };
  
  // 切换指标选择（临时，不保存）
  const toggleIndicator = (category, indicatorId) => {
    setCustomIndicators(prev => {
      const current = prev[category];
      const newSelection = current.includes(indicatorId)
        ? current.filter(id => id !== indicatorId)
        : [...current, indicatorId];
      return { ...prev, [category]: newSelection };
    });
  };
  
  // 保存自定义配置
  const saveCustomIndicators = () => {
    localStorage.setItem('customIndicators', JSON.stringify(customIndicators));
    setShowIndicatorSelector(false);
    alert('✅ 自定义配置已保存！以后的分析都会使用这个配置。');
  };
  
  // 重置为默认配置
  const resetToDefault = (category) => {
    const defaults = {
      fundamental: ['market_cap', 'pe_ratio', 'eps', 'roe', 'profit_margin', 'dividend_yield'],
      technical: ['rsi', 'macd', 'atr', 'bbands'],
      macro: ['cpi', 'unemployment', 'fed_rate']
    };
    setCustomIndicators(prev => ({ ...prev, [category]: defaults[category] }));
  };
  
  // 获取指标数据的辅助函数
  // eslint-disable-next-line no-unused-vars
  const getIndicatorData = (indicatorId) => {
    if (!stockData) return null;
    
    const overview = stockData.premium_data?.company_overview;
    const technical = stockData.premium_data?.technical;
    const economic = stockData.premium_data?.economic;
    
    const indicatorMap = {
      // 基本面
      market_cap: {
        label: '市值',
        value: overview?.MarketCapitalization ? `$${(parseFloat(overview.MarketCapitalization) / 1e12).toFixed(2)}T` : 'N/A',
        status: '🟢',
        desc: '巨型'
      },
      pe_ratio: {
        label: '市盈率 P/E',
        value: overview?.PERatio || 'N/A',
        status: overview?.PERatio && parseFloat(overview.PERatio) > 30 ? '🟡' : '🟢',
        desc: overview?.PERatio && parseFloat(overview.PERatio) > 30 ? '略高' : '合理'
      },
      eps: {
        label: '每股收益 EPS',
        value: overview?.EPS ? `$${overview.EPS}` : 'N/A',
        status: '🟢',
        desc: '优秀'
      },
      roe: {
        label: 'ROE',
        value: overview?.ReturnOnEquityTTM ? `${(parseFloat(overview.ReturnOnEquityTTM) * 100).toFixed(1)}%` : 'N/A',
        status: overview?.ReturnOnEquityTTM && parseFloat(overview.ReturnOnEquityTTM) > 0.15 ? '🟢' : '🟡',
        desc: overview?.ReturnOnEquityTTM && parseFloat(overview.ReturnOnEquityTTM) > 0.15 ? '卓越' : '良好'
      },
      profit_margin: {
        label: '利润率',
        value: overview?.ProfitMargin ? `${(parseFloat(overview.ProfitMargin) * 100).toFixed(1)}%` : 'N/A',
        status: overview?.ProfitMargin && parseFloat(overview.ProfitMargin) > 0.2 ? '🟢' : '🟡',
        desc: overview?.ProfitMargin && parseFloat(overview.ProfitMargin) > 0.2 ? '优秀' : '良好'
      },
      dividend_yield: {
        label: '股息率',
        value: overview?.DividendYield ? `${(parseFloat(overview.DividendYield) * 100).toFixed(2)}%` : 'N/A',
        status: overview?.DividendYield && parseFloat(overview.DividendYield) > 0.02 ? '🟢' : '🟡',
        desc: overview?.DividendYield && parseFloat(overview.DividendYield) > 0.02 ? '稳定' : '较低'
      },
      peg_ratio: {
        label: 'PEG比率',
        value: overview?.PEGRatio || 'N/A',
        status: overview?.PEGRatio && parseFloat(overview.PEGRatio) < 1 ? '🟢' : '🟡',
        desc: overview?.PEGRatio && parseFloat(overview.PEGRatio) < 1 ? '优秀' : '一般'
      },
      debt_to_equity: {
        label: '负债率',
        value: overview?.DebtToEquity ? `${overview.DebtToEquity}%` : 'N/A',
        status: overview?.DebtToEquity && parseFloat(overview.DebtToEquity) < 50 ? '🟢' : '🟡',
        desc: overview?.DebtToEquity && parseFloat(overview.DebtToEquity) < 50 ? '健康' : '偏高'
      },
      current_ratio: {
        label: '流动比率',
        value: overview?.CurrentRatio || 'N/A',
        status: overview?.CurrentRatio && parseFloat(overview.CurrentRatio) > 1.5 ? '🟢' : '🟡',
        desc: overview?.CurrentRatio && parseFloat(overview.CurrentRatio) > 1.5 ? '良好' : '一般'
      },
      book_value: {
        label: '账面价值',
        value: overview?.BookValue ? `$${overview.BookValue}` : 'N/A',
        status: '🟢',
        desc: '参考'
      },
      
      // 技术面
      rsi: {
        label: 'RSI(14)',
        value: stockData.indicators?.rsi?.toFixed(2) || 'N/A',
        status: stockData.indicators?.rsi > 70 ? '🔴 超买' : stockData.indicators?.rsi < 30 ? '🟢 超卖' : '🟡 中性',
        desc: stockData.indicators?.rsi > 70 ? '注意回调' : stockData.indicators?.rsi < 30 ? '可能反弹' : '震荡'
      },
      macd: {
        label: 'MACD',
        value: technical?.macd_value || 'N/A',
        status: technical?.macd_signal === 'bullish' ? '🟢 金叉' : technical?.macd_signal === 'bearish' ? '🔴 死叉' : '🟡',
        desc: technical?.macd_signal === 'bullish' ? '上涨动能' : technical?.macd_signal === 'bearish' ? '下跌动能' : '观察'
      },
      atr: {
        label: 'ATR(14)',
        value: technical?.atr ? `$${technical.atr.toFixed(2)}` : 'N/A',
        status: '🟡',
        desc: '波动适中'
      },
      bbands: {
        label: '布林带位置',
        value: technical?.bbands_position || '中轨附近',
        status: technical?.bbands_position === '上轨附近' ? '🔴' : technical?.bbands_position === '下轨附近' ? '🟢' : '🟡',
        desc: technical?.bbands_position || '震荡中'
      },
      sma_50: {
        label: 'SMA(50)',
        value: technical?.sma_50 ? `$${technical.sma_50.toFixed(2)}` : 'N/A',
        status: '🟡',
        desc: '中期均线'
      },
      sma_200: {
        label: 'SMA(200)',
        value: technical?.sma_200 ? `$${technical.sma_200.toFixed(2)}` : 'N/A',
        status: '🟡',
        desc: '长期均线'
      },
      volume: {
        label: '成交量',
        value: stockData.volume ? `${(stockData.volume / 1e6).toFixed(2)}M` : 'N/A',
        status: '🟡',
        desc: '交易活跃'
      },
      volatility: {
        label: '波动率',
        value: technical?.volatility ? `${(technical.volatility * 100).toFixed(2)}%` : 'N/A',
        status: '🟡',
        desc: '风险指标'
      },
      
      // 宏观面
      cpi: {
        label: 'CPI通胀率',
        value: economic?.cpi ? `${economic.cpi}%` : 'N/A',
        trend: '↑',
        status: '🟢 温和通胀'
      },
      unemployment: {
        label: '失业率',
        value: economic?.unemployment ? `${economic.unemployment}%` : 'N/A',
        trend: '→',
        status: '🟢 稳定'
      },
      fed_rate: {
        label: '联邦利率',
        value: economic?.fed_rate ? `${economic.fed_rate}%` : 'N/A',
        trend: '→',
        status: '🟡 高位'
      },
      gdp_growth: {
        label: 'GDP增长',
        value: economic?.gdp_growth ? `${economic.gdp_growth}%` : 'N/A',
        trend: '↑',
        status: '🟢 增长'
      },
      treasury_yield: {
        label: '国债收益率',
        value: economic?.treasury_yield ? `${economic.treasury_yield}%` : 'N/A',
        trend: '→',
        status: '🟡 参考'
      }
    };
    
    return indicatorMap[indicatorId] || null;
  };
  
  // 切换语言
  const toggleLanguage = () => {
    const newLang = language === 'zh' ? 'en' : 'zh';
    setLang(newLang);
    setLanguage(newLang);
  };
  
  // 热门股票列表（扩展版）
  const trendingStocks = [
    // 科技股
    { code: 'AAPL', name_zh: '苹果', name_en: 'Apple', category: '科技' },
    { code: 'MSFT', name_zh: '微软', name_en: 'Microsoft', category: '科技' },
    { code: 'GOOGL', name_zh: '谷歌', name_en: 'Google', category: '科技' },
    { code: 'META', name_zh: 'Meta', name_en: 'Meta', category: '科技' },
    { code: 'AMZN', name_zh: '亚马逊', name_en: 'Amazon', category: '科技' },
    { code: 'NVDA', name_zh: '英伟达', name_en: 'NVIDIA', category: '科技' },
    { code: 'TSLA', name_zh: '特斯拉', name_en: 'Tesla', category: '科技' },
    // 金融股
    { code: 'JPM', name_zh: '摩根大通', name_en: 'JPMorgan', category: '金融' },
    { code: 'V', name_zh: 'Visa', name_en: 'Visa', category: '金融' },
    { code: 'MA', name_zh: 'Mastercard', name_en: 'Mastercard', category: '金融' },
    // 中概股
    { code: 'BABA', name_zh: '阿里巴巴', name_en: 'Alibaba', category: '中概' },
    { code: 'JD', name_zh: '京东', name_en: 'JD.com', category: '中概' },
    { code: 'PDD', name_zh: '拼多多', name_en: 'Pinduoduo', category: '中概' }
  ];
  
  // 股票搜索
  const searchStocks = async (keywords) => {
    if (!keywords || keywords.length < 1) {
      setSearchResults([]);
      setShowSearchResults(false);
      return;
    }

    setSearching(true);
    
    try {
      const response = await fetch(`${apiUrl}/api/stock/search?keywords=${encodeURIComponent(keywords)}`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setSearchResults(result.results || []);
        setShowSearchResults(true);
      } else {
        setSearchResults([]);
      }
    } catch (err) {
      console.error('搜索失败:', err);
      setSearchResults([]);
    } finally {
      setSearching(false);
    }
  };
  
  // 选择搜索结果
  const selectSearchResult = (result) => {
    setSymbol(result.symbol);
    setShowSearchResults(false);
    setSearchResults([]);
    searchStock(result.symbol);
  };

  // 🆕 添加股票到选中列表
  const addSymbolToList = (symbolToAdd) => {
    const upperSymbol = symbolToAdd.toUpperCase();
    if (upperSymbol && !selectedSymbols.includes(upperSymbol)) {
      setSelectedSymbols([...selectedSymbols, upperSymbol]);
    }
  };

  // 🆕 从选中列表删除股票
  const removeSymbolFromList = (symbolToRemove) => {
    setSelectedSymbols(selectedSymbols.filter(s => s !== symbolToRemove));
  };

  // 🆕 添加新闻到列表
  const addNewsToList = () => {
    if (newsContext.trim()) {
      setNewsList([...newsList, { id: Date.now(), content: newsContext.trim() }]);
      setNewsContext('');
    }
  };

  // 🆕 从列表删除新闻
  const removeNewsFromList = (newsId) => {
    setNewsList(newsList.filter(n => n.id !== newsId));
  };

  const searchStock = async (searchSymbol) => {
    const targetSymbol = searchSymbol || symbol;
    if (!targetSymbol.trim()) {
      setError('请输入股票代码');
      return;
    }

    setLoading(true);
    setError('');
    setStockData(null);
    setAnalysis(null);

    try {
      // 1. 获取股票数据
      const dataResponse = await fetch(`${apiUrl}/api/stock/${targetSymbol.toUpperCase()}`);
      const dataResult = await dataResponse.json();

      if (dataResult.status !== 'success') {
        setError(dataResult.message || '未找到该股票');
        setLoading(false);
        return;
      }

      setStockData(dataResult.data);

      // 1.5 获取新闻（并行）
      loadNews(targetSymbol.toUpperCase());

    } catch (err) {
      setError('网络连接失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // 🆕 新逻辑：Tom初步分析（不自动生成策略）
  const tomInitialAnalysis = async () => {
    if (!stockData) {
      setError('请先搜索股票');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);
    setDualStrategyData(null); // 清空旧策略
    setConversationHistory([]); // 清空对话历史

    try {
      // 🆕 构建投资风格参数
      let styleParam = investmentStyle;
      if (investmentStyle === 'custom' && customStyleName && customStyleDesc) {
        styleParam = `${customStyleName}: ${customStyleDesc}`;
      }

      // 🆕 合并所有新闻内容
      const allNews = newsList.map(n => n.content).join('\n\n---\n\n');

      // 调用Tom初步分析API
      const analysisResponse = await fetch(`${apiUrl}/api/chat/tom/initial-analysis`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockData.quote.symbol,
          selected_symbols: selectedSymbols, // 🆕 多股票列表
          username: localStorage.getItem('username') || 'guest',
          investment_style: styleParam, // 🆕 支持自定义风格
          news_context: allNews // 🆕 所有新闻内容
        })
      });

      const analysisResult = await analysisResponse.json();

      if (analysisResult.success) {
        setAnalysis(analysisResult.analysis);
        setShowChatWindow(true); // 显示对话窗口
        
        // 🆕 将Tom的完整初步分析作为第一条消息添加到对话历史
        const analysis = analysisResult.analysis;
        
        // 构建完整的分析内容（类似第一张图的格式）
        let analysisContent = `📊 **综合分析：**\n\n`;
        
        // 添加关键点
        if (analysis.key_points && analysis.key_points.length > 0) {
          analysisContent += `💡 **${analysis.key_points.join(' | ')}**\n\n`;
        }
        
        // 添加详细分析摘要
        if (analysis.analysis_summary) {
          analysisContent += `${analysis.analysis_summary}\n\n`;
        }
        
        // 添加投资建议
        if (analysis.recommendation) {
          analysisContent += `🎯 **投资建议：** ${analysis.recommendation}\n`;
          if (analysis.position_size) {
            analysisContent += `📊 **建议仓位：** ${analysis.position_size}\n`;
          }
          if (analysis.target_price) {
            analysisContent += `🎯 **目标价：** $${analysis.target_price}\n`;
          }
          if (analysis.stop_loss) {
            analysisContent += `🛡️ **止损价：** $${analysis.stop_loss}\n`;
          }
        }
        
        const tomInitialMessage = {
          role: 'assistant',
          content: analysisContent,
          initial_analysis: true,
          full_analysis: analysis // 保存完整分析数据
        };
        setConversationHistory([tomInitialMessage]);
        
        console.log('✅ Tom初步分析完成:', analysisResult.analysis);
      } else {
        setError('Tom分析失败: ' + analysisResult.error);
      }

    } catch (err) {
      setError('网络连接失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  // 🆕 与Tom对话
  const sendMessageToTom = async () => {
    if (!userMessage.trim() || !analysis) {
      return;
    }

    setSendingMessage(true);
    const currentMessage = userMessage;
    setUserMessage(''); // 清空输入框

    try {
      // 添加用户消息到对话历史
      const newHistory = [
        ...conversationHistory,
        { role: 'user', content: currentMessage }
      ];
      setConversationHistory(newHistory);

      // 构建股票上下文
      const stockContext = {
        symbol: stockData.quote.symbol,
        current_price: stockData.quote.price,
        investment_style: investmentStyle,
        initial_analysis: analysis,
        news_context: newsContext,
        history_data: stockData.history || [], // 🆕 添加历史数据，用于绘制价格图表
        company_overview: stockData.premium_data?.company_overview,
        technical_indicators: stockData.premium_data?.technical_indicators,
        economic_data: stockData.premium_data?.economic_data
      };

      // 调用Tom对话API
      const response = await fetch(`${apiUrl}/api/chat/tom/message`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockData.quote.symbol,
          user_message: currentMessage,
          conversation_history: conversationHistory, // 传递之前的对话
          stock_context: stockContext
        })
      });

      const result = await response.json();

      if (result.success) {
        // 添加Tom的回复到对话历史（包含结构化数据）
        setConversationHistory([
          ...newHistory,
          { 
            role: 'assistant', 
            content: result.tom_reply,
            intent: result.intent,  // 用户意图
            price_chart_data: result.price_chart_data,  // 价格图表数据
            indicators_data: result.indicators_data  // 指标数据
          }
        ]);
      } else {
        setError('Tom回复失败: ' + result.error);
      }

    } catch (err) {
      setError('发送消息失败: ' + err.message);
    } finally {
      setSendingMessage(false);
    }
  };

  // 🆕 生成策略（Jany基于对话历史）- 每次都是全新的
  const generateStrategy = async () => {
    if (!analysis) {
      setError('请先进行Tom分析');
      return;
    }

    setLoading(true);
    setError('');
    
    // 🔑 清空旧策略数据，确保每次都是全新生成
    setDualStrategyData(null);
    setStockStrategy(null);

    try {
      const currentUser = localStorage.getItem('username');
      if (!currentUser) {
        setError('请先登录');
        setLoading(false);
        return;
      }

      console.log('🔄 Jany开始生成策略，基于对话历史:', conversationHistory);

      const response = await fetch(`${apiUrl}/api/dual-strategy/generate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockData.quote.symbol,
          username: currentUser,
          notional_value: 30000,
          investment_style: investmentStyle,
          ai_analysis: analysis,
          conversation_history: conversationHistory, // 🔑 关键：传递最新的对话历史
          timestamp: Date.now() // 🆕 添加时间戳，防止缓存
        })
      });

      if (response.ok) {
        const dualData = await response.json();
        setDualStrategyData(dualData);
        setStockStrategy(dualData.stock_strategy);
        console.log('✅ Jany策略生成成功（全新）:', dualData);
        
        // 🆕 将Jany的策略推荐添加到对话历史
        const janyMessage = {
          role: 'jany',
          content: `基于我对您与Tom的${conversationHistory.length}条对话的分析，以及当前市场数据，我为您生成了两个策略供选择：`,
          strategy_data: dualData, // 包含完整的策略数据
          timestamp: Date.now()
        };
        setConversationHistory(prev => [...prev, janyMessage]);
        
        alert('✅ 策略生成成功！请在对话框中查看并选择策略。');
      } else {
        const errorData = await response.json();
        setError('策略生成失败: ' + errorData.error);
        alert('❌ 策略生成失败: ' + errorData.error);
      }

    } catch (err) {
      setError('网络连接失败: ' + err.message);
      alert('❌ 网络连接失败: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const loadNews = async (targetSymbol) => {
    setLoadingNews(true);
    try {
      const newsResponse = await fetch(`${apiUrl}/api/stock/${targetSymbol}/news?limit=5`);
      const newsResult = await newsResponse.json();
      
      if (newsResult.status === 'success') {
        setNewsList(newsResult.news);
      } else {
        console.error('获取新闻失败:', newsResult.message);
        setNewsList([]);
      }
    } catch (err) {
      console.error('获取新闻失败:', err);
      setNewsList([]);
    } finally {
      setLoadingNews(false);
    }
  };

  const selectNews = (news) => {
    // 点击新闻，自动填充到输入框
    const newsText = `${news.title}\n\n${news.summary}`;
    setNewsContext(newsText);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      searchStock();
    }
  };

  const acceptStrategy = async (choice) => {
    if (!stockData || !analysis) return;

    // choice: 1=期权, 2=股票
    if (!choice) {
      alert('⚠️ 请选择策略类型');
      return;
    }

    // 检查是否已生成双策略
    if (!dualStrategyData) {
      alert('⚠️ 策略数据未准备好，请稍后再试');
      return;
    }

    // 获取当前登录用户
    const currentUser = localStorage.getItem('username');
    if (!currentUser) {
      alert('❌ 请先登录！');
      return;
    }

    try {
      // 使用已生成的策略ID
      const strategyId = dualStrategyData.strategy_id;

      // 接受策略（创建A/B对照组）
      const acceptResponse = await fetch(`${apiUrl}/api/dual-strategy/accept`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username: currentUser,
          strategy_id: strategyId,
          choice: choice
        })
      });

      const result = await acceptResponse.json();

      if (result.success) {
        const choiceText = choice === 1 ? '期权' : '股票';
        alert(`✅ ${choiceText}策略已接受！\n` +
              `实盘类型: ${result.actual_type}\n` +
              `成本: $${result.actual_cost.toFixed(2)}\n` +
              `账户余额: $${result.balance_after.toFixed(2)}\n\n` +
              `请前往 "Positions (A/B)" 查看持仓对照`);
        
        // 清空当前分析，鼓励用户查看持仓
        setStockData(null);
        setAnalysis(null);
        setStockStrategy(null);
        setDualStrategyData(null);
      } else {
        alert('❌ 接受策略失败: ' + (result.error || '未知错误'));
      }
    } catch (err) {
      alert('❌ 网络错误: ' + err.message);
    }
  };

  // 渲染双策略对比卡片
  const renderDualStrategyComparison = () => {
    if (!dualStrategyData) return null;

    const optionData = dualStrategyData.option_strategy;
    const stockData = dualStrategyData.stock_strategy;

    return (
      <div style={{
        marginTop: '30px',
        padding: '25px',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '15px',
        color: 'white'
      }}>
        <h3 style={{ marginBottom: '20px', fontSize: '1.3em' }}>
          🎯 双策略推荐（请选择一个）
        </h3>
        
        {/* 智能匹配推荐理由 */}
        {dualStrategyData.explanation && (
          <div style={{
            padding: '15px',
            background: 'rgba(255,255,255,0.2)',
            borderRadius: '10px',
            marginBottom: '20px',
            fontSize: '0.95em',
            lineHeight: '1.6'
          }}>
            <strong>🤖 AI智能推荐：</strong>
            <br/>{dualStrategyData.explanation}
          </div>
        )}
        
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
          {/* 期权策略 */}
          <div style={{
            background: 'rgba(255,255,255,0.15)',
            padding: '20px',
            borderRadius: '12px',
            border: '2px solid rgba(255,255,255,0.3)'
          }}>
            <h4 style={{ marginBottom: '15px', fontSize: '1.1em' }}>
              📊 期权策略
            </h4>
            <div style={{ fontSize: '0.95em', lineHeight: '1.8' }}>
              <div><strong>类型:</strong> {optionData.type}</div>
              <div><strong>等价股数:</strong> {optionData.equivalent_shares}股</div>
              <div><strong>执行价:</strong> ${optionData.strike_price}</div>
              <div><strong>到期日:</strong> {optionData.expiry_date} ({optionData.days_to_expiry}天)</div>
              <div><strong>期权费:</strong> ${(optionData.total_premium || 0).toFixed(2)}</div>
              <div><strong>Delta:</strong> {(optionData.delta || 0).toFixed(4)}</div>
              {optionData.data_source && (
                <div style={{ marginTop: '10px', fontSize: '0.85em', opacity: 0.9 }}>
                  📡 {optionData.data_source}
                </div>
              )}
            </div>
            <button
              onClick={() => acceptStrategy(1)}
              style={{
                marginTop: '15px',
                width: '100%',
                padding: '12px',
                background: '#48bb78',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1em',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              ✅ 选择期权策略
            </button>
          </div>

          {/* 股票策略 */}
          <div style={{
            background: 'rgba(255,255,255,0.15)',
            padding: '20px',
            borderRadius: '12px',
            border: '2px solid rgba(255,255,255,0.3)'
          }}>
            <h4 style={{ marginBottom: '15px', fontSize: '1.1em' }}>
              📈 Delta One股票策略
            </h4>
            <div style={{ fontSize: '0.95em', lineHeight: '1.8' }}>
              <div><strong>类型:</strong> {stockData.type}</div>
              <div><strong>股数:</strong> {stockData.shares}股</div>
              <div><strong>入场价:</strong> ${stockData.entry_price.toFixed(2)}</div>
              <div><strong>名义本金:</strong> ${stockData.notional.toFixed(2)}</div>
              <div><strong>保证金:</strong> ${stockData.margin.toFixed(2)}</div>
              <div><strong>止损价:</strong> ${stockData.stop_loss.toFixed(2)}</div>
              <div><strong>止盈价:</strong> ${stockData.take_profit.toFixed(2)}</div>
              <div><strong>对应Delta:</strong> {stockData.delta.toFixed(4)}</div>
            </div>
            <button
              onClick={() => acceptStrategy(2)}
              style={{
                marginTop: '15px',
                width: '100%',
                padding: '12px',
                background: '#4299e1',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1em',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              ✅ 选择股票策略
            </button>
          </div>
        </div>

        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: 'rgba(255,255,255,0.1)',
          borderRadius: '8px',
          fontSize: '0.9em'
        }}>
          <strong>💡 提示:</strong> 选择一个策略后，系统将创建A/B对照组：
          <br/>• A组：您选择的策略（实盘交易）
          <br/>• B组：未选择的策略（虚拟跟踪）
          <br/>• 这样您可以对比两种策略的实际表现！
          <br/><br/>
          <strong>📌 关于Delta One策略：</strong>
          <br/>• 期权Delta = {dualStrategyData?.option_strategy?.delta.toFixed(4)}
          <br/>• 股票名义本金 = 期权名义本金 × Delta = ${dualStrategyData?.stock_strategy?.notional.toFixed(2)}
          <br/>• 两个策略的风险敞口相当，便于公平对比
        </div>
      </div>
    );
  };


  return (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '30px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      {/* 搜索区域 */}
      <div style={{ marginBottom: '30px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ color: '#333', margin: 0 }}>
            {language === 'zh' ? '📈 智能股票分析' : '📈 Intelligent Stock Analysis'}
          </h2>
          <button
            onClick={toggleLanguage}
            style={{
              padding: '8px 16px',
              background: '#667eea',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: '600',
              fontSize: '0.9em'
            }}
          >
            {language === 'zh' ? '🌐 English' : '🌐 中文'}
          </button>
        </div>
        
        {/* 搜索框 */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px', position: 'relative' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <input
              type="text"
              value={symbol}
              onChange={(e) => {
                const val = e.target.value.toUpperCase();
                setSymbol(val);
                // 实时搜索（当输入2个字符以上时）
                if (val.length >= 2) {
                  searchStocks(val);
                } else {
                  setShowSearchResults(false);
                }
              }}
              onKeyPress={handleKeyPress}
              onFocus={() => {
                if (searchResults.length > 0) {
                  setShowSearchResults(true);
                }
              }}
              placeholder={language === 'zh' ? '输入股票代码或公司名（如：AAPL 或 Apple）' : 'Enter symbol or company name (e.g., AAPL or Apple)'}
              style={{
                width: '100%',
                padding: '12px',
                border: '2px solid #e0e0e0',
                borderRadius: '8px',
                fontSize: '1em',
                boxSizing: 'border-box'
              }}
            />
            {searching && (
              <div style={{
                position: 'absolute',
                right: '10px',
                top: '50%',
                transform: 'translateY(-50%)',
                color: '#667eea',
                fontSize: '1.2em'
              }}>
                🔍
              </div>
            )}
            
            {/* 搜索结果下拉列表 */}
            {showSearchResults && searchResults.length > 0 && (
              <div style={{
                position: 'absolute',
                top: '100%',
                left: 0,
                right: 0,
                marginTop: '5px',
                background: 'white',
                border: '2px solid #667eea',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
                maxHeight: '400px',
                overflowY: 'auto',
                zIndex: 1000
              }}>
                {searchResults.map((result, idx) => (
                  <div
                    key={idx}
                    onClick={() => selectSearchResult(result)}
                    style={{
                      padding: '12px 15px',
                      cursor: 'pointer',
                      borderBottom: idx < searchResults.length - 1 ? '1px solid #eee' : 'none',
                      transition: 'background 0.2s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = '#f0f4ff'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'white'}
                  >
                    <div style={{ fontWeight: '600', color: '#667eea', marginBottom: '3px' }}>
                      {result.symbol}
                    </div>
                    <div style={{ fontSize: '0.9em', color: '#666' }}>
                      {result.name}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#999', marginTop: '2px' }}>
                      {result.type} • {result.region}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
          
          <button
            onClick={() => {
              addSymbolToList(symbol);
              searchStock();
            }}
            disabled={loading || !symbol.trim()}
            style={{
              padding: '12px 24px',
              background: loading || !symbol.trim() ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading || !symbol.trim() ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              fontSize: '1em',
              whiteSpace: 'nowrap'
            }}
          >
            {loading ? '🔄' : '➕ 添加并搜索'}
          </button>
        </div>

        {/* 🆕 已选中的股票列表 */}
        {selectedSymbols.length > 0 && (
          <div style={{ 
            marginBottom: '15px', 
            padding: '12px 15px', 
            background: '#F0F4FF', 
            borderRadius: '8px',
            border: '1px solid #667eea'
          }}>
            <div style={{ fontWeight: '600', color: '#333', marginBottom: '8px', fontSize: '0.9em' }}>
              📊 已选择的股票：
            </div>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {selectedSymbols.map((sym) => (
                <div
                  key={sym}
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    padding: '6px 12px',
                    background: 'white',
                    border: '2px solid #667eea',
                    borderRadius: '20px',
                    fontSize: '0.9em',
                    fontWeight: '600',
                    color: '#667eea'
                  }}
                >
                  {sym}
                  <span
                    onClick={() => removeSymbolFromList(sym)}
                    style={{
                      cursor: 'pointer',
                      color: '#dc3545',
                      fontSize: '1.1em',
                      lineHeight: '1'
                    }}
                    title="删除"
                  >
                    ×
                  </span>
                </div>
              ))}
            </div>
            <div style={{ marginTop: '8px', fontSize: '0.85em', color: '#666' }}>
              💡 分析时将综合考虑所有选中的股票
            </div>
          </div>
        )}

        {/* 热门股票快捷按钮（按分类显示） */}
        <div style={{ marginTop: '15px' }}>
          {['科技', '金融', '中概'].map(category => {
            const categoryStocks = trendingStocks.filter(s => s.category === category);
            return (
              <div key={category} style={{ marginBottom: '12px' }}>
                <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
                  <span style={{ 
                    color: '#666', 
                    fontWeight: '600',
                    minWidth: '60px',
                    fontSize: '0.9em'
                  }}>
                    {category === '科技' && '💻'} 
                    {category === '金融' && '💰'} 
                    {category === '中概' && '🇨🇳'} 
                    {category}:
                  </span>
                  {categoryStocks.map(stock => (
                    <button
                      key={stock.code}
                      onClick={() => {
                        setSymbol(stock.code);
                        addSymbolToList(stock.code);
                      }}
                      style={{
                        padding: '6px 12px',
                        background: selectedSymbols.includes(stock.code) ? '#667eea' : 'white',
                        color: selectedSymbols.includes(stock.code) ? 'white' : '#667eea',
                        border: '2px solid #667eea',
                        borderRadius: '20px',
                        cursor: 'pointer',
                        fontWeight: '600',
                        fontSize: '0.85em',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => {
                        if (!selectedSymbols.includes(stock.code)) {
                          e.currentTarget.style.background = '#667eea';
                          e.currentTarget.style.color = 'white';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (!selectedSymbols.includes(stock.code)) {
                          e.currentTarget.style.background = 'white';
                          e.currentTarget.style.color = '#667eea';
                        }
                      }}
                      title={`${language === 'zh' ? stock.name_zh : stock.name_en} (${stock.code})`}
                    >
                      {selectedSymbols.includes(stock.code) ? '✓ ' : ''}{stock.code}
                    </button>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* 投资风格设置 */}
        <div style={{ marginTop: '15px', padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
          <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '600' }}>
            🎯 选择投资大师风格：
          </label>
          <div style={{ display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
            {[
              { value: 'buffett', label: '巴菲特', emoji: '🏛️', desc: '价值投资' },
              { value: 'lynch', label: '彼得·林奇', emoji: '🎯', desc: '成长股猎手' },
              { value: 'soros', label: '索罗斯', emoji: '🌊', desc: '趋势投机' },
              { value: 'custom', label: '自定义', emoji: '⚙️', desc: '个性化策略' }
            ].map(option => (
              <label 
                key={option.value} 
                style={{ 
                  display: 'flex', 
                  flexDirection: 'column',
                  alignItems: 'center', 
                  cursor: 'pointer',
                  padding: '12px 20px',
                  border: `2px solid ${investmentStyle === option.value ? '#667eea' : '#ddd'}`,
                  borderRadius: '10px',
                  background: investmentStyle === option.value ? '#e7f3ff' : 'white',
                  transition: 'all 0.2s',
                  flex: '1',
                  minWidth: '140px'
                }}
              >
                <input
                  type="radio"
                  value={option.value}
                  checked={investmentStyle === option.value}
                  onChange={(e) => setInvestmentStyle(e.target.value)}
                  style={{ display: 'none' }}
                />
                <div style={{ fontSize: '2em', marginBottom: '5px' }}>{option.emoji}</div>
                <div style={{ fontWeight: '600', color: '#333', marginBottom: '3px' }}>{option.label}</div>
                <div style={{ fontSize: '0.85em', color: '#666' }}>{option.desc}</div>
              </label>
            ))}
          </div>

          {/* 🆕 自定义投资风格输入框 */}
          {investmentStyle === 'custom' && (
            <div style={{ marginTop: '15px', padding: '12px', background: '#fff', borderRadius: '8px', border: '2px solid #667eea' }}>
              <div style={{ marginBottom: '10px' }}>
                <label style={{ display: 'block', marginBottom: '5px', color: '#333', fontWeight: '600', fontSize: '0.9em' }}>
                  风格名称：
                </label>
                <input
                  type="text"
                  value={customStyleName}
                  onChange={(e) => setCustomStyleName(e.target.value)}
                  placeholder="例如：科技成长型、保守稳健型、激进短线型"
                  style={{
                    width: '100%',
                    padding: '8px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '0.95em'
                  }}
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', color: '#333', fontWeight: '600', fontSize: '0.9em' }}>
                  策略描述：
                </label>
                <textarea
                  value={customStyleDesc}
                  onChange={(e) => setCustomStyleDesc(e.target.value)}
                  placeholder="详细描述您的投资策略...&#10;&#10;示范：&#10;• 关注高ROE（>20%）和低PE（<25）的科技股&#10;• 重视现金流和盈利能力&#10;• 看重创新能力和市场份额&#10;• 偏好中期持有（3-12个月）&#10;• 风险承受能力：中等"
                  style={{
                    width: '100%',
                    minHeight: '120px',
                    padding: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '6px',
                    fontSize: '0.95em',
                    fontFamily: 'inherit',
                    resize: 'vertical'
                  }}
                />
              </div>
              <div style={{ marginTop: '8px', fontSize: '0.85em', color: '#666', lineHeight: '1.5' }}>
                💡 提示：详细描述您的投资偏好，包括关注的财务指标、风险偏好、持有期限等，AI将据此为您定制分析
              </div>
            </div>
          )}
        </div>

        {/* 最新新闻列表 */}
        {newsList.length > 0 && (
          <div style={{ marginTop: '15px', padding: '15px', background: '#e7f3ff', borderRadius: '8px' }}>
            <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '600' }}>
              📰 最新相关新闻（点击选择）：
            </label>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {newsList.map((news, index) => (
                <div
                  key={index}
                  onClick={() => selectNews(news)}
                  style={{
                    padding: '12px',
                    background: 'white',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    border: '2px solid transparent',
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = '#667eea';
                    e.currentTarget.style.transform = 'translateX(5px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'transparent';
                    e.currentTarget.style.transform = 'translateX(0)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '5px' }}>
                    <div style={{ fontWeight: '600', fontSize: '0.95em', flex: 1 }}>
                      {news.sentiment === 'positive' && '🟢 '}
                      {news.sentiment === 'negative' && '🔴 '}
                      {news.sentiment === 'neutral' && '⚪ '}
                      {news.title}
                    </div>
                    <div style={{ fontSize: '0.8em', color: '#999', marginLeft: '10px', whiteSpace: 'nowrap' }}>
                      {news.time_published}
                    </div>
                  </div>
                  <div style={{ fontSize: '0.85em', color: '#666', lineHeight: '1.4' }}>
                    {news.summary}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {loadingNews && (
          <div style={{ marginTop: '15px', padding: '15px', background: '#e7f3ff', borderRadius: '8px', textAlign: 'center' }}>
            <div style={{ color: '#667eea' }}>🔄 正在加载新闻...</div>
          </div>
        )}

        {/* 🆕 新闻管理 - 添加和删除多条新闻 */}
        <div style={{ marginTop: '15px', padding: '15px', background: '#fff3cd', borderRadius: '8px' }}>
          <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '600' }}>
            📝 添加新闻/消息（分析时将综合考虑）：
          </label>
          
          {/* 已添加的新闻列表 */}
          {newsList.length > 0 && (
            <div style={{ marginBottom: '12px', display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {newsList.map((newsItem) => (
                <div
                  key={newsItem.id}
                  style={{
                    padding: '10px 12px',
                    background: 'white',
                    borderRadius: '6px',
                    border: '1px solid #ffc107',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'start',
                    gap: '10px'
                  }}
                >
                  <div style={{ flex: 1, fontSize: '0.9em', color: '#333', lineHeight: '1.4' }}>
                    {newsItem.content}
                  </div>
                  <button
                    onClick={() => removeNewsFromList(newsItem.id)}
                    style={{
                      padding: '4px 8px',
                      background: '#dc3545',
                      color: 'white',
                      border: 'none',
                      borderRadius: '4px',
                      cursor: 'pointer',
                      fontSize: '0.85em',
                      flexShrink: 0
                    }}
                  >
                    删除
                  </button>
                </div>
              ))}
            </div>
          )}
          
          {/* 新闻输入框 */}
          <div style={{ display: 'flex', gap: '8px' }}>
            <textarea
              value={newsContext}
              onChange={(e) => setNewsContext(e.target.value)}
              placeholder="点击上方新闻自动填充，或手动输入新闻/消息..."
              style={{
                flex: 1,
                minHeight: '80px',
                padding: '10px',
                border: '1px solid #ddd',
                borderRadius: '5px',
                fontSize: '14px',
                fontFamily: 'inherit',
                resize: 'vertical'
              }}
            />
            <button
              onClick={addNewsToList}
              disabled={!newsContext.trim()}
              style={{
                padding: '10px 20px',
                background: newsContext.trim() ? '#28a745' : '#ccc',
                color: 'white',
                border: 'none',
                borderRadius: '6px',
                cursor: newsContext.trim() ? 'pointer' : 'not-allowed',
                fontWeight: '600',
                fontSize: '0.9em',
                alignSelf: 'flex-start',
                whiteSpace: 'nowrap'
              }}
            >
              ➕ 添加
            </button>
          </div>
          
          <div style={{ marginTop: '8px', fontSize: '0.85em', color: '#666' }}>
            {newsList.length > 0 
              ? `✅ 已添加 ${newsList.length} 条新闻/消息` 
              : '💡 可添加多条新闻，分析时会综合考虑所有内容'
            }
          </div>
        </div>

        {/* 🆕 AI综合分析按钮 */}
        {stockData && !analysis && (
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              onClick={tomInitialAnalysis}
              disabled={loading}
              style={{
                padding: '15px 40px',
                background: loading ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                border: 'none',
                borderRadius: '10px',
                fontSize: '1.1em',
                fontWeight: 'bold',
                cursor: loading ? 'not-allowed' : 'pointer',
                boxShadow: '0 4px 15px rgba(102, 126, 234, 0.4)',
                transition: 'all 0.3s'
              }}
              onMouseEnter={(e) => {
                if (!loading) {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 6px 20px rgba(102, 126, 234, 0.6)';
                }
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = '0 4px 15px rgba(102, 126, 234, 0.4)';
              }}
            >
              {loading ? '🔄 分析中...' : '🤖 开始AI综合分析'}
            </button>
            <div style={{ marginTop: '10px', fontSize: '0.9em', color: '#666' }}>
              {newsList.length > 0 && `✅ 已添加 ${newsList.length} 条新闻 `}
              {selectedSymbols.length > 0 && `📊 已选择 ${selectedSymbols.length} 只股票 `}
              {newsList.length === 0 && selectedSymbols.length === 0 && '💡 提示：添加更多新闻或选择多只股票可获得更全面的分析'}
            </div>
          </div>
        )}
      </div>

      {/* 错误提示 */}
      {error && (
        <div style={{
          padding: '15px',
          background: '#fed7d7',
          color: '#c53030',
          borderRadius: '8px',
          marginBottom: '20px'
        }}>
          ❌ {error}
        </div>
      )}

      {/* 🆕 Tom对话窗口 - 现代化简洁设计 */}
      {analysis && showChatWindow && (
        <div style={{
          background: '#FFFFFF',
          borderRadius: '16px',
          padding: '0',
          maxWidth: '1200px', // 最大宽度1200px
          width: '70%', // 屏幕的70%
          margin: '34px auto', // 水平居中
          boxShadow: '0 2px 8px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.06)',
          border: '1px solid #E5E7EB'
        }}>
              {/* 头部 */}
              <div style={{
                padding: '24px 32px',
                borderBottom: '1px solid #F3F4F6',
                background: '#FAFBFC'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{
                    width: '40px',
                    height: '40px',
                    borderRadius: '50%',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    fontSize: '20px'
                  }}>
                    🤖
                  </div>
                  <div>
                    <h2 style={{ 
                      margin: 0, 
                      fontSize: '20px', 
                      fontWeight: '600',
                      color: '#111827',
                      lineHeight: '1.4'
                    }}>
                      与Tom讨论
                    </h2>
                    <p style={{ 
                      margin: 0, 
                      fontSize: '14px', 
                      color: '#6B7280',
                      lineHeight: '1.4'
                    }}>
                      AI分析师 · 在线
                    </p>
                  </div>
                </div>
              </div>
              
              {/* 对话历史 */}
              <div 
                className="chat-history"
                style={{
                  padding: '32px',
                  maxHeight: '600px',
                  overflowY: 'auto',
                  background: '#FFFFFF'
                }}
              >
                <style>{`
                  .chat-history::-webkit-scrollbar {
                    width: 6px;
                  }
                  .chat-history::-webkit-scrollbar-track {
                    background: #F3F4F6;
                    border-radius: 3px;
                  }
                  .chat-history::-webkit-scrollbar-thumb {
                    background: #D1D5DB;
                    border-radius: 3px;
                  }
                  .chat-history::-webkit-scrollbar-thumb:hover {
                    background: #9CA3AF;
                  }
                `}</style>
                {conversationHistory.length === 0 ? (
                  <div style={{ 
                    textAlign: 'center', 
                    padding: '64px 32px',
                    color: '#9CA3AF'
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>💬</div>
                    <div style={{ fontSize: '16px', fontWeight: '500', color: '#6B7280', marginBottom: '8px' }}>
                      开始对话
                    </div>
                    <div style={{ fontSize: '14px', color: '#9CA3AF' }}>
                      询问Tom关于ROE、新闻影响、技术指标等问题
                    </div>
                  </div>
                ) : (
                  conversationHistory.map((msg, idx) => (
                    <div key={idx} style={{
                      marginBottom: idx === conversationHistory.length - 1 ? 0 : '24px',
                      display: 'flex',
                      gap: '16px',
                      alignItems: 'flex-start'
                    }}>
                      {/* 头像 */}
                      <div style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '50%',
                        background: msg.role === 'user' 
                          ? 'linear-gradient(135deg, #3B82F6 0%, #2563EB 100%)'
                          : msg.role === 'jany'
                          ? 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)'
                          : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '18px',
                        flexShrink: 0
                      }}>
                        {msg.role === 'user' ? '👤' : msg.role === 'jany' ? '🎯' : '🤖'}
                      </div>
                      
                      {/* 消息内容 */}
                      <div style={{ flex: 1, minWidth: 0 }}>
                        {/* 名称和时间 */}
                        <div style={{ 
                          display: 'flex', 
                          alignItems: 'center', 
                          gap: '8px',
                          marginBottom: '8px'
                        }}>
                          <span style={{ 
                            fontSize: '15px', 
                            fontWeight: '600',
                            color: '#111827'
                          }}>
                            {msg.role === 'user' ? '您' : msg.role === 'jany' ? 'Jany（策略师）' : 'Tom（分析师）'}
                          </span>
                          <span style={{ 
                            fontSize: '13px', 
                            color: '#9CA3AF'
                          }}>
                            {new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })}
                          </span>
                        </div>
                        
                        {/* 消息气泡 */}
                        <div style={{
                          background: msg.role === 'user' ? '#F3F4F6' : '#FFFFFF',
                          padding: '16px 20px',
                          borderRadius: '12px',
                          border: msg.role === 'user' ? 'none' : '1px solid #E5E7EB',
                          lineHeight: '1.6',
                          fontSize: '15px',
                          color: '#374151',
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word'
                        }}>
                          {msg.content}
                        </div>
                      
                        {/* 🆕 动态渲染价格图表 */}
                        {msg.price_chart_data && msg.price_chart_data.length > 0 && (
                          <div style={{ 
                            marginTop: '16px', 
                            background: '#F9FAFB', 
                            padding: '16px', 
                            borderRadius: '8px',
                            border: '1px solid #E5E7EB'
                          }}>
                            <div style={{ 
                              color: '#374151', 
                              fontWeight: '600', 
                              marginBottom: '12px', 
                              fontSize: '14px' 
                            }}>
                              📈 价格走势图（最近30天）
                            </div>
                            <ResponsiveContainer width="100%" height={160}>
                              <LineChart data={msg.price_chart_data}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#E5E7EB" />
                                <XAxis dataKey="date" tick={{ fontSize: 11, fill: '#6B7280' }} />
                                <YAxis tick={{ fontSize: 11, fill: '#6B7280' }} />
                                <Tooltip />
                                <Line type="monotone" dataKey="close" stroke="#667eea" strokeWidth={2} dot={false} />
                              </LineChart>
                            </ResponsiveContainer>
                          </div>
                        )}
                        
                        {/* 🆕 动态渲染指标卡片 */}
                        {msg.indicators_data && Object.keys(msg.indicators_data).length > 0 && (
                          <div style={{ 
                            marginTop: '16px', 
                            display: 'grid', 
                            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', 
                            gap: '12px' 
                          }}>
                            {Object.entries(msg.indicators_data).map(([key, value]) => (
                              <div key={key} style={{
                                background: '#F9FAFB',
                                padding: '16px',
                                borderRadius: '8px',
                                border: '1px solid #E5E7EB',
                                textAlign: 'center'
                              }}>
                                <div style={{ 
                                  color: '#6B7280', 
                                  fontSize: '13px', 
                                  marginBottom: '8px',
                                  fontWeight: '500'
                                }}>
                                  {key.toUpperCase()}
                                </div>
                                <div style={{ 
                                  color: '#111827', 
                                  fontSize: '20px', 
                                  fontWeight: '700' 
                                }}>
                                  {value || 'N/A'}
                                </div>
                              </div>
                            ))}
                          </div>
                        )}
                      
                        {/* 🆕 Jany策略通知 */}
                        {msg.role === 'jany' && msg.strategy_data && (
                          <div style={{ 
                            marginTop: '16px',
                            padding: '16px',
                            background: '#FEF3C7',
                            borderRadius: '8px',
                            border: '1px solid #FCD34D'
                          }}>
                            <div style={{ 
                              fontSize: '14px', 
                              marginBottom: '8px',
                              color: '#92400E',
                              fontWeight: '600'
                            }}>
                              ✅ 策略已生成！
                            </div>
                            <div style={{ fontSize: '14px', color: '#78350F', lineHeight: '1.5' }}>
                              我已经为您生成了<strong>期权策略</strong>和<strong>股票策略</strong>，请在下方查看详情并选择。
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
              
              {/* 输入区域 - 现代化设计 */}
              <div style={{
                padding: '24px 32px',
                borderTop: '1px solid #F3F4F6',
                background: '#FFFFFF'
              }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                  <input
                    type="text"
                    value={userMessage}
                    onChange={(e) => setUserMessage(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && !sendingMessage && sendMessageToTom()}
                    placeholder="输入您的问题..."
                    disabled={sendingMessage}
                    style={{
                      flex: 1,
                      padding: '14px 16px',
                      borderRadius: '10px',
                      border: '1.5px solid #E5E7EB',
                      fontSize: '15px',
                      background: '#FFFFFF',
                      outline: 'none',
                      transition: 'all 0.2s',
                      color: '#111827'
                    }}
                    onFocus={(e) => e.target.style.borderColor = '#667eea'}
                    onBlur={(e) => e.target.style.borderColor = '#E5E7EB'}
                  />
                  <button
                    onClick={sendMessageToTom}
                    disabled={sendingMessage || !userMessage.trim()}
                    style={{
                      padding: '14px 24px',
                      background: sendingMessage || !userMessage.trim() ? '#E5E7EB' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      color: sendingMessage || !userMessage.trim() ? '#9CA3AF' : '#FFFFFF',
                      border: 'none',
                      borderRadius: '10px',
                      cursor: sendingMessage || !userMessage.trim() ? 'not-allowed' : 'pointer',
                      fontWeight: '600',
                      fontSize: '15px',
                      transition: 'all 0.2s',
                      boxShadow: sendingMessage || !userMessage.trim() ? 'none' : '0 2px 4px rgba(102, 126, 234, 0.2)'
                    }}
                    onMouseEnter={(e) => {
                      if (!sendingMessage && userMessage.trim()) {
                        e.target.style.transform = 'translateY(-1px)';
                        e.target.style.boxShadow = '0 4px 8px rgba(102, 126, 234, 0.3)';
                      }
                    }}
                    onMouseLeave={(e) => {
                      e.target.style.transform = 'translateY(0)';
                      e.target.style.boxShadow = '0 2px 4px rgba(102, 126, 234, 0.2)';
                    }}
                  >
                    {sendingMessage ? '发送中...' : '发送'}
                  </button>
                </div>
              </div>
              
              {/* 策略生成区域 - 现代化设计 */}
              <div style={{
                padding: '24px 32px',
                borderTop: '1px solid #F3F4F6',
                background: '#FAFBFC',
                textAlign: 'center'
              }}>
                <button
                  onClick={generateStrategy}
                  disabled={loading}
                  style={{
                    padding: '16px 32px',
                    background: loading ? '#E5E7EB' : 'linear-gradient(135deg, #F59E0B 0%, #D97706 100%)',
                    color: loading ? '#9CA3AF' : '#FFFFFF',
                    border: 'none',
                    borderRadius: '10px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    boxShadow: loading ? 'none' : '0 2px 4px rgba(245, 158, 11, 0.3)',
                    transition: 'all 0.2s',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '8px'
                  }}
                  onMouseEnter={(e) => {
                    if (!loading) {
                      e.target.style.transform = 'translateY(-2px)';
                      e.target.style.boxShadow = '0 4px 8px rgba(245, 158, 11, 0.4)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    e.target.style.transform = 'translateY(0)';
                    e.target.style.boxShadow = '0 2px 4px rgba(245, 158, 11, 0.3)';
                  }}
                >
                  <span>{loading ? '⏳' : '🎯'}</span>
                  <span>{loading ? '生成中...' : '生成交易策略（Jany）'}</span>
                </button>
                <div style={{ 
                  marginTop: '12px', 
                  fontSize: '13px', 
                  color: '#6B7280',
                  lineHeight: '1.5'
                }}>
                  {conversationHistory.length > 0 ? (
                    `Jany将基于您与Tom的 ${conversationHistory.length} 条对话生成策略`
                  ) : (
                    '满意Tom的分析后，点击此按钮让Jany生成具体交易策略'
                  )}
                </div>
              </div>
            </div>
          )}
      )}

      {/* 双策略对比显示 */}
      {renderDualStrategyComparison()}

      {/* 提示信息 */}
      {!stockData && !loading && !error && (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#999'
        }}>
          <div style={{ fontSize: '3em', marginBottom: '20px' }}>📊</div>
          <div style={{ fontSize: '1.2em' }}>输入股票代码开始分析</div>
          <div style={{ fontSize: '0.9em', marginTop: '10px' }}>
            支持美股代码，如 AAPL、GOOGL、MSFT 等
          </div>
        </div>
      )}
      
      {/* 指标选择器弹窗 */}
      {showIndicatorSelector && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(0,0,0,0.6)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999
        }}>
          <div style={{
            background: 'white',
            borderRadius: '16px',
            padding: '30px',
            maxWidth: '600px',
            width: '90%',
            maxHeight: '80vh',
            overflow: 'auto',
            boxShadow: '0 10px 40px rgba(0,0,0,0.3)'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <h3 style={{ margin: 0, color: '#667eea' }}>
                ⚙️ 自定义
                {selectorCategory === 'fundamental' && '基本面'}
                {selectorCategory === 'technical' && '技术面'}
                {selectorCategory === 'macro' && '宏观面'}
                指标
              </h3>
              <button
                onClick={() => setShowIndicatorSelector(false)}
                style={{
                  background: 'transparent',
                  border: 'none',
                  fontSize: '1.5em',
                  cursor: 'pointer',
                  color: '#999'
                }}
              >
                ✕
              </button>
            </div>
            
            <div style={{ marginBottom: '20px', padding: '15px', background: '#f8f9fa', borderRadius: '8px' }}>
              <p style={{ margin: 0, fontSize: '0.9em', color: '#666' }}>
                💡 选择您想在分析中看到的指标，点击"保存配置"后，以后的所有分析都会使用这个配置。
              </p>
            </div>
            
            {/* 指标列表 */}
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px', marginBottom: '25px' }}>
              {availableIndicators[selectorCategory].map(indicator => (
                <div
                  key={indicator.id}
                  onClick={() => toggleIndicator(selectorCategory, indicator.id)}
                  style={{
                    padding: '15px',
                    background: customIndicators[selectorCategory].includes(indicator.id) 
                      ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' 
                      : '#f8f9fa',
                    color: customIndicators[selectorCategory].includes(indicator.id) ? 'white' : '#333',
                    borderRadius: '10px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '10px',
                    fontWeight: '500',
                    transition: 'all 0.3s',
                    border: customIndicators[selectorCategory].includes(indicator.id) 
                      ? '2px solid #667eea' 
                      : '2px solid #e0e0e0'
                  }}
                >
                  <span style={{ fontSize: '1.3em' }}>{indicator.icon}</span>
                  <span>{indicator.label}</span>
                  {customIndicators[selectorCategory].includes(indicator.id) && (
                    <span style={{ marginLeft: 'auto', fontSize: '1.2em' }}>✓</span>
                  )}
                </div>
              ))}
            </div>
            
            {/* 底部按钮 */}
            <div style={{ display: 'flex', gap: '10px', justifyContent: 'space-between' }}>
              <button
                onClick={() => resetToDefault(selectorCategory)}
                style={{
                  padding: '12px 20px',
                  background: '#f8f9fa',
                  color: '#666',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600',
                  transition: 'all 0.3s'
                }}
              >
                🔄 恢复默认
              </button>
              <div style={{ display: 'flex', gap: '10px' }}>
                <button
                  onClick={() => setShowIndicatorSelector(false)}
                  style={{
                    padding: '12px 20px',
                    background: 'white',
                    color: '#666',
                    border: '2px solid #e0e0e0',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600'
                  }}
                >
                  取消
                </button>
                <button
                  onClick={saveCustomIndicators}
                  style={{
                    padding: '12px 30px',
                    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    fontWeight: '600',
                    boxShadow: '0 4px 12px rgba(102, 126, 234, 0.4)',
                    transition: 'all 0.3s'
                  }}
                >
                  💾 保存配置
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default StockAnalysis;

