import React, { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getCurrentLanguage, setLanguage } from './i18n';

function StockAnalysis({ apiUrl }) {
  const [symbol, setSymbol] = useState('');
  const [stockData, setStockData] = useState(null);
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [investmentStyle, setInvestmentStyle] = useState('buffett');
  const [newsContext, setNewsContext] = useState('');
  const [userOpinion, setUserOpinion] = useState('');
  const [newsList, setNewsList] = useState([]);
  const [loadingNews, setLoadingNews] = useState(false);
  const [optionStrategy, setOptionStrategy] = useState(null);
  const [language, setLang] = useState(getCurrentLanguage());
  
  // 切换语言
  const toggleLanguage = () => {
    const newLang = language === 'zh' ? 'en' : 'zh';
    setLang(newLang);
    setLanguage(newLang);
  };
  
  // 热门股票列表（硬编码，不再从API获取）
  const trendingStocks = [
    { code: 'AAPL', name_zh: '苹果', name_en: 'Apple' },
    { code: 'GOOGL', name_zh: '谷歌', name_en: 'Google' },
    { code: 'MSFT', name_zh: '微软', name_en: 'Microsoft' },
    { code: 'TSLA', name_zh: '特斯拉', name_en: 'Tesla' },
    { code: 'NVDA', name_zh: '英伟达', name_en: 'NVIDIA' }
  ];

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
    setOptionStrategy(null);

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

  const analyzeStock = async () => {
    if (!stockData) {
      setError('请先搜索股票');
      return;
    }

    setLoading(true);
    setError('');
    setAnalysis(null);
    setOptionStrategy(null);

    try {
      // 获取AI分析
      const analysisResponse = await fetch(`${apiUrl}/api/stock/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockData.quote.symbol,
          investment_style: investmentStyle,
          news_context: newsContext,
          user_opinion: userOpinion,
          language: language
        })
      });

      const analysisResult = await analysisResponse.json();

      if (analysisResult.status === 'success') {
        setAnalysis(analysisResult.analysis);
        // 如果有期权策略，也保存
        if (analysisResult.option_strategy) {
          setOptionStrategy(analysisResult.option_strategy);
        }
      } else {
        setError('AI分析失败: ' + analysisResult.message);
      }

    } catch (err) {
      setError('网络连接失败: ' + err.message);
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

  const acceptStrategy = async () => {
    if (!stockData || !analysis) return;

    // 检查是否有期权策略
    if (!optionStrategy) {
      alert('⚠️ 当前没有期权策略推荐，无法保存');
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/strategy/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: stockData.quote.symbol,
          company_name: stockData.quote.name,
          investment_style: investmentStyle,
          recommendation: analysis.recommendation,
          target_price: analysis.target_price,
          stop_loss: analysis.stop_loss,
          position_size: analysis.position_size,
          score: analysis.score,
          strategy_text: analysis.strategy,
          analysis_summary: analysis.analysis_summary,
          current_price: stockData.quote.price,
          // 期权策略信息（核心）
          option_strategy: optionStrategy,
          created_at: new Date().toISOString()
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        alert(`✅ 期权策略已保存！\n策略类型: ${optionStrategy.strategy.name}\n您可以在"策略评估"模块查看历史表现`);
      } else {
        alert('❌ 保存失败: ' + result.message);
      }
    } catch (err) {
      alert('❌ 网络错误: ' + err.message);
    }
  };

  const rejectStrategy = () => {
    alert('❌ 已拒绝此策略，不会保存到数据库');
  };

  // 获取推荐颜色
  const getRecommendationColor = (recommendation) => {
    if (recommendation === '买入') return '#48bb78';
    if (recommendation === '卖出') return '#f56565';
    return '#ed8936';
  };

  // 获取评分颜色
  const getScoreColor = (score) => {
    if (score >= 70) return '#48bb78';
    if (score >= 50) return '#ed8936';
    return '#f56565';
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
        <div style={{ display: 'flex', gap: '10px', marginBottom: '15px' }}>
          <input
            type="text"
            value={symbol}
            onChange={(e) => setSymbol(e.target.value.toUpperCase())}
            onKeyPress={handleKeyPress}
            placeholder="输入美股代码（如 AAPL=苹果, TSLA=特斯拉）"
            style={{
              flex: 1,
              padding: '12px',
              border: '2px solid #e0e0e0',
              borderRadius: '8px',
              fontSize: '1em'
            }}
          />
          <button
            onClick={() => searchStock()}
            disabled={loading}
            style={{
              padding: '12px 30px',
              background: loading ? '#ccc' : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '600',
              fontSize: '1em'
            }}
          >
            {loading ? '🔍 搜索中...' : '🔍 搜索'}
          </button>
        </div>

        {/* 热门股票快捷按钮 */}
        <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignItems: 'center' }}>
          <span style={{ color: '#666', fontWeight: '600' }}>热门股票:</span>
          {trendingStocks.map(stock => (
            <button
              key={stock.code}
              onClick={() => {
                setSymbol(stock.code);
                searchStock(stock.code);
              }}
              style={{
                padding: '8px 16px',
                background: 'white',
                color: '#667eea',
                border: '2px solid #667eea',
                borderRadius: '20px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.9em'
              }}
              title={`${stock.name} (${stock.code})`}
            >
              {stock.code} {stock.name}
            </button>
          ))}
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
              { value: 'soros', label: '索罗斯', emoji: '🌊', desc: '趋势投机' }
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

        {/* 新闻/消息输入 */}
        <div style={{ marginTop: '15px', padding: '15px', background: '#fff3cd', borderRadius: '8px' }}>
          <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '600' }}>
            📝 选中的新闻/自定义消息（可选）：
          </label>
          <textarea
            value={newsContext}
            onChange={(e) => setNewsContext(e.target.value)}
            placeholder="点击上方新闻自动填充，或手动输入..."
            style={{
              width: '100%',
              minHeight: '80px',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
        </div>

        {/* 用户观点输入 */}
        <div style={{ marginTop: '15px', padding: '15px', background: '#d1ecf1', borderRadius: '8px' }}>
          <label style={{ display: 'block', marginBottom: '10px', color: '#333', fontWeight: '600' }}>
            💭 您的观点/研报（可选）：
          </label>
          <textarea
            value={userOpinion}
            onChange={(e) => setUserOpinion(e.target.value)}
            placeholder="例如：我认为该公司基本面良好，技术创新能力强，长期看好..."
            style={{
              width: '100%',
              minHeight: '80px',
              padding: '10px',
              border: '1px solid #ddd',
              borderRadius: '5px',
              fontSize: '14px',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
        </div>

        {/* AI分析按钮 */}
        {stockData && (
          <div style={{ marginTop: '20px', textAlign: 'center' }}>
            <button
              onClick={analyzeStock}
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
              {newsContext && '✅ 已选择新闻 '}
              {userOpinion && '✅ 已输入观点 '}
              {!newsContext && !userOpinion && '💡 提示：选择新闻或输入观点可获得更全面的分析'}
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

      {/* 数据展示区域 */}
      {stockData && (
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: window.innerWidth > 768 ? '1fr 1fr' : '1fr',
          gap: '20px',
          marginBottom: '20px'
        }}>
          {/* 左侧：股票数据 */}
          <div>
            {/* 价格卡片 */}
            <div style={{
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              padding: '20px',
              borderRadius: '10px',
              marginBottom: '20px'
            }}>
              <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>{stockData.quote.name}</div>
              <div style={{ fontSize: '2em', fontWeight: 'bold', marginBottom: '10px' }}>
                ${stockData.quote.price.toFixed(2)}
              </div>
              <div style={{ fontSize: '1.2em' }}>
                {stockData.quote.change >= 0 ? '📈' : '📉'} 
                {stockData.quote.change >= 0 ? '+' : ''}
                {stockData.quote.change.toFixed(2)} 
                ({stockData.quote.change_percent >= 0 ? '+' : ''}
                {stockData.quote.change_percent.toFixed(2)}%)
              </div>
              <div style={{ fontSize: '0.8em', marginTop: '10px', opacity: 0.8 }}>
                更新时间: {stockData.quote.updated_at}
              </div>
            </div>

            {/* 期权策略推荐 */}
            {optionStrategy && (
              <div style={{
                background: '#fff',
                border: '2px solid #667eea',
                padding: '20px',
                borderRadius: '10px',
                marginBottom: '20px'
              }}>
                <h3 style={{ color: '#667eea', marginBottom: '15px', display: 'flex', alignItems: 'center' }}>
                  📊 推荐期权策略: {optionStrategy.name}
                </h3>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '10px' }}>
                  {optionStrategy.description}
                </div>
                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '10px', marginBottom: '15px' }}>
                  <div style={{ padding: '10px', background: '#f8f9fa', borderRadius: '5px' }}>
                    <div style={{ fontSize: '0.8em', color: '#666' }}>风险等级</div>
                    <div style={{ fontWeight: '600', color: '#333' }}>{optionStrategy.risk_level}</div>
                  </div>
                  <div style={{ padding: '10px', background: '#f8f9fa', borderRadius: '5px' }}>
                    <div style={{ fontSize: '0.8em', color: '#666' }}>当前股价</div>
                    <div style={{ fontWeight: '600', color: '#333' }}>${optionStrategy.parameters.current_price.toFixed(2)}</div>
                  </div>
                </div>
                <div style={{ padding: '15px', background: '#e7f3ff', borderRadius: '8px' }}>
                  <div style={{ fontWeight: '600', marginBottom: '10px', color: '#333' }}>策略参数：</div>
                  {optionStrategy.parameters.buy_strike && (
                    <div style={{ marginBottom: '5px' }}>
                      • 买入执行价: ${optionStrategy.parameters.buy_strike.toFixed(2)}
                    </div>
                  )}
                  {optionStrategy.parameters.sell_strike && (
                    <div style={{ marginBottom: '5px' }}>
                      • 卖出执行价: ${optionStrategy.parameters.sell_strike.toFixed(2)}
                    </div>
                  )}
                  <div style={{ marginBottom: '5px' }}>
                    • 到期时间: {optionStrategy.parameters.expiry}
                  </div>
                  <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #ddd' }}>
                    <div style={{ fontWeight: '600', marginBottom: '5px' }}>风险指标：</div>
                    <div>最大收益: {optionStrategy.metrics.max_gain >= 999999 ? '无限' : `$${optionStrategy.metrics.max_gain.toFixed(2)}`}</div>
                    <div>最大损失: ${optionStrategy.metrics.max_loss.toFixed(2)}</div>
                    <div>盈亏平衡: ${optionStrategy.metrics.breakeven.toFixed(2)}</div>
                  </div>
                </div>
              </div>
            )}

            {/* K线图 */}
            <div style={{
              background: '#f8f9fa',
              padding: '20px',
              borderRadius: '10px',
              marginBottom: '20px'
            }}>
              <h3 style={{ color: '#333', marginBottom: '15px' }}>📊 30天价格走势</h3>
              <ResponsiveContainer width="100%" height={250}>
                <LineChart data={stockData.history}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date" 
                    tick={{ fontSize: 12 }}
                    tickFormatter={(value) => value.slice(5)}
                  />
                  <YAxis 
                    tick={{ fontSize: 12 }}
                    domain={['dataMin - 5', 'dataMax + 5']}
                  />
                  <Tooltip 
                    formatter={(value) => `$${value.toFixed(2)}`}
                    labelFormatter={(label) => `日期: ${label}`}
                  />
                  <Legend />
                  <Line 
                    type="monotone" 
                    dataKey="close" 
                    stroke="#667eea" 
                    strokeWidth={2}
                    name="收盘价"
                    dot={false}
                  />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* 关键指标 */}
            <div style={{
              background: '#f8f9fa',
              padding: '20px',
              borderRadius: '10px'
            }}>
              <h3 style={{ color: '#333', marginBottom: '15px' }}>📋 关键指标</h3>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))', gap: '15px' }}>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>今日最高</div>
                  <div style={{ fontSize: '1.2em', fontWeight: '600' }}>${stockData.quote.high.toFixed(2)}</div>
                </div>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>今日最低</div>
                  <div style={{ fontSize: '1.2em', fontWeight: '600' }}>${stockData.quote.low.toFixed(2)}</div>
                </div>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>成交量</div>
                  <div style={{ fontSize: '1.2em', fontWeight: '600' }}>
                    {(stockData.quote.volume / 1000000).toFixed(2)}M
                  </div>
                </div>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>RSI(14)</div>
                  <div style={{ 
                    fontSize: '1.2em', 
                    fontWeight: '600',
                    color: stockData.indicators.rsi > 70 ? '#f56565' : 
                           stockData.indicators.rsi < 30 ? '#48bb78' : '#333'
                  }}>
                    {stockData.indicators.rsi?.toFixed(2) || 'N/A'}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>30日波动率</div>
                  <div style={{ 
                    fontSize: '1.2em', 
                    fontWeight: '600',
                    color: stockData.indicators.volatility > 40 ? '#f56565' : 
                           stockData.indicators.volatility < 20 ? '#48bb78' : '#333'
                  }}>
                    {stockData.indicators.volatility?.toFixed(2)}%
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* 右侧：AI分析 */}
          {analysis && (
            <div>
              {/* 综合评分 */}
              <div style={{
                background: getScoreColor(analysis.score),
                color: 'white',
                padding: '20px',
                borderRadius: '10px',
                marginBottom: '20px',
                textAlign: 'center'
              }}>
                <div style={{ fontSize: '0.9em', marginBottom: '5px' }}>🎯 综合评分</div>
                <div style={{ fontSize: '3em', fontWeight: 'bold' }}>{analysis.score}</div>
                <div style={{ fontSize: '0.9em', opacity: 0.9 }}>满分100分</div>
              </div>

              {/* 操作建议 */}
              <div style={{
                background: '#f8f9fa',
                padding: '20px',
                borderRadius: '10px',
                marginBottom: '20px'
              }}>
                <h3 style={{ color: '#333', marginBottom: '15px' }}>💡 操作建议</h3>
                <div style={{
                  padding: '15px',
                  background: getRecommendationColor(analysis.recommendation),
                  color: 'white',
                  borderRadius: '8px',
                  fontSize: '1.5em',
                  fontWeight: 'bold',
                  textAlign: 'center',
                  marginBottom: '15px'
                }}>
                  {analysis.recommendation}
                </div>

                <div style={{ marginBottom: '10px' }}>
                  <strong>建议仓位:</strong> {analysis.position_size}
                </div>
                <div style={{ marginBottom: '10px' }}>
                  <strong>目标价:</strong> ${analysis.target_price.toFixed(2)}
                </div>
                <div>
                  <strong>止损价:</strong> ${analysis.stop_loss.toFixed(2)}
                </div>
              </div>

              {/* 分析要点 */}
              <div style={{
                background: '#f8f9fa',
                padding: '20px',
                borderRadius: '10px',
                marginBottom: '20px'
              }}>
                <h3 style={{ color: '#333', marginBottom: '15px' }}>📌 分析要点</h3>
                <ul style={{ margin: 0, paddingLeft: '20px', lineHeight: '1.8' }}>
                  {analysis.key_points.map((point, index) => (
                    <li key={index} style={{ marginBottom: '10px' }}>{point}</li>
                  ))}
                </ul>
                
                {analysis.analysis_summary && (
                  <div style={{
                    marginTop: '15px',
                    padding: '15px',
                    background: 'white',
                    borderRadius: '8px',
                    borderLeft: '4px solid #667eea'
                  }}>
                    <strong>综合分析:</strong>
                    <p style={{ margin: '10px 0 0 0', lineHeight: '1.6' }}>
                      {analysis.analysis_summary}
                    </p>
                  </div>
                )}
              </div>

              {/* 投资策略 */}
              {analysis.strategy && (
                <div style={{
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  padding: '20px',
                  borderRadius: '10px'
                }}>
                  <h3 style={{ marginBottom: '15px', display: 'flex', alignItems: 'center' }}>
                    🎯 综合投资策略
                  </h3>
                  <p style={{ margin: 0, lineHeight: '1.8', fontSize: '1.05em' }}>
                    {analysis.strategy}
                  </p>
                  <div style={{
                    marginTop: '15px',
                    padding: '10px',
                    background: 'rgba(255,255,255,0.2)',
                    borderRadius: '5px',
                    fontSize: '0.9em'
                  }}>
                    💡 此策略综合了技术指标、基本面消息和您的观点
                  </div>
                  
                  {/* 接受/拒绝策略按钮 */}
                  <div style={{
                    marginTop: '20px',
                    display: 'flex',
                    gap: '15px',
                    justifyContent: 'center'
                  }}>
                    <button
                      onClick={() => acceptStrategy()}
                      style={{
                        padding: '12px 30px',
                        background: '#48bb78',
                        color: 'white',
                        border: 'none',
                        borderRadius: '8px',
                        fontSize: '1em',
                        fontWeight: '600',
                        cursor: 'pointer',
                        boxShadow: '0 4px 15px rgba(72, 187, 120, 0.4)',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.transform = 'translateY(-2px)';
                        e.currentTarget.style.boxShadow = '0 6px 20px rgba(72, 187, 120, 0.6)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.transform = 'translateY(0)';
                        e.currentTarget.style.boxShadow = '0 4px 15px rgba(72, 187, 120, 0.4)';
                      }}
                    >
                      ✅ 接受此策略
                    </button>
                    <button
                      onClick={() => rejectStrategy()}
                      style={{
                        padding: '12px 30px',
                        background: 'rgba(255,255,255,0.2)',
                        color: 'white',
                        border: '2px solid white',
                        borderRadius: '8px',
                        fontSize: '1em',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.3)';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = 'rgba(255,255,255,0.2)';
                      }}
                    >
                      ❌ 不接受
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      )}

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
    </div>
  );
}

export default StockAnalysis;

