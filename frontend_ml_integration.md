# 前端ML集成说明

## 需要在 `frontend/src/StockAnalysis.js` 中添加的代码

### 1. 添加状态（在第22行后）
```javascript
const [mlAdvice, setMLAdvice] = useState(null);
const [loadingML, setLoadingML] = useState(false);
```

### 2. 添加获取ML建议的函数（在第165行 `analyzeStock` 函数后）
```javascript
// 获取ML交易建议
const getMLAdvice = async () => {
  if (!stockData || !analysis) {
    console.log('等待股票数据和分析完成');
    return;
  }
  
  const currentUser = localStorage.getItem('username');
  if (!currentUser) {
    console.log('用户未登录，跳过ML建议');
    return;
  }
  
  setLoadingML(true);
  
  try {
    const response = await fetch(`${apiUrl}/api/ml/trading/advice`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        user_id: currentUser,
        symbol: stockData.quote.symbol,
        stock_data: stockData,
        investment_style: investmentStyle,
        user_opinion: userOpinion,
        news_context: newsContext
      })
    });
    
    const result = await response.json();
    
    if (result.status === 'success') {
      setMLAdvice(result.advice);
      console.log('✅ ML建议获取成功');
    } else {
      console.error('ML建议失败:', result.message);
    }
  } catch (err) {
    console.error('ML建议错误:', err);
  } finally {
    setLoadingML(false);
  }
};
```

### 3. 在 `analyzeStock` 函数的末尾自动调用（约第160行）
```javascript
// 在 analyzeStock 函数的最后，成功获取AI分析后
if (analysisResult.status === 'success') {
  setAnalysis(analysisResult.analysis);
  if (analysisResult.option_strategy) {
    setOptionStrategy(analysisResult.option_strategy);
  }
  
  // 🆕 自动获取ML建议
  setTimeout(() => {
    getMLAdvice();
  }, 500);  // 延迟500ms确保状态更新
}
```

### 4. 在UI中显示ML建议（在分析结果后，约第900行）
```javascript
{/* 🆕 ML智能交易建议 */}
{mlAdvice && (
  <div style={{
    background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    padding: '25px',
    borderRadius: '15px',
    marginTop: '20px',
    color: 'white',
    boxShadow: '0 10px 30px rgba(102, 126, 234, 0.3)'
  }}>
    <h3 style={{ 
      margin: '0 0 20px 0', 
      fontSize: '1.3em',
      display: 'flex',
      alignItems: 'center',
      gap: '10px'
    }}>
      <span>🤖</span>
      {language === 'zh' ? 'ML智能交易建议' : 'ML Trading Advice'}
      {loadingML && <span style={{fontSize: '0.8em'}}>⏳</span>}
    </h3>
    
    {/* 核心建议 */}
    <div style={{
      background: 'rgba(255,255,255,0.15)',
      padding: '20px',
      borderRadius: '10px',
      marginBottom: '15px'
    }}>
      <div style={{ 
        display: 'grid', 
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '15px'
      }}>
        <div>
          <div style={{ fontSize: '0.9em', opacity: 0.9 }}>
            {language === 'zh' ? '⏰ 交易时机' : '⏰ Timing'}
          </div>
          <div style={{ fontSize: '1.3em', fontWeight: 'bold', marginTop: '5px' }}>
            {mlAdvice.timing_recommendation === 'BUY_NOW' && '🟢 立即买入'}
            {mlAdvice.timing_recommendation === 'WAIT' && '🟡 等待'}
            {mlAdvice.timing_recommendation === 'AVOID' && '🔴 避免'}
          </div>
        </div>
        
        <div>
          <div style={{ fontSize: '0.9em', opacity: 0.9 }}>
            {language === 'zh' ? '📊 信心度' : '📊 Confidence'}
          </div>
          <div style={{ fontSize: '1.3em', fontWeight: 'bold', marginTop: '5px' }}>
            {(mlAdvice.confidence * 100).toFixed(0)}%
          </div>
        </div>
        
        <div>
          <div style={{ fontSize: '0.9em', opacity: 0.9 }}>
            {language === 'zh' ? '💰 建议价格' : '💰 Target Price'}
          </div>
          <div style={{ fontSize: '1.3em', fontWeight: 'bold', marginTop: '5px' }}>
            ${mlAdvice.suggested_price.toFixed(2)}
          </div>
        </div>
        
        <div>
          <div style={{ fontSize: '0.9em', opacity: 0.9 }}>
            {language === 'zh' ? '📦 建议仓位' : '📦 Position'}
          </div>
          <div style={{ fontSize: '1.3em', fontWeight: 'bold', marginTop: '5px' }}>
            {(mlAdvice.suggested_position * 100).toFixed(0)}%
          </div>
        </div>
      </div>
    </div>
    
    {/* 个性化建议 */}
    {mlAdvice.personalized_insights && mlAdvice.personalized_insights.length > 0 && (
      <div style={{
        background: 'rgba(255,255,255,0.1)',
        padding: '15px',
        borderRadius: '10px',
        marginBottom: '15px'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '10px', fontSize: '1.1em' }}>
          💡 {language === 'zh' ? '个性化建议' : 'Personalized Insights'}
        </div>
        {mlAdvice.personalized_insights.map((insight, idx) => (
          <div key={idx} style={{ 
            padding: '8px 0', 
            borderBottom: idx < mlAdvice.personalized_insights.length - 1 ? '1px solid rgba(255,255,255,0.2)' : 'none'
          }}>
            • {insight}
          </div>
        ))}
      </div>
    )}
    
    {/* 风险提示 */}
    {mlAdvice.regret_prevention && mlAdvice.regret_prevention.length > 0 && (
      <div style={{
        background: 'rgba(255,255,255,0.1)',
        padding: '15px',
        borderRadius: '10px'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '10px', fontSize: '1.1em' }}>
          🛡️ {language === 'zh' ? '风险提示' : 'Risk Alerts'}
        </div>
        {mlAdvice.regret_prevention.map((tip, idx) => (
          <div key={idx} style={{ 
            padding: '8px 0', 
            borderBottom: idx < mlAdvice.regret_prevention.length - 1 ? '1px solid rgba(255,255,255,0.2)' : 'none'
          }}>
            • {tip}
          </div>
        ))}
      </div>
    )}
    
    {/* 执行计划按钮 */}
    <button
      onClick={() => alert(JSON.stringify(mlAdvice.execution_plan, null, 2))}
      style={{
        marginTop: '15px',
        padding: '12px 25px',
        background: 'rgba(255,255,255,0.2)',
        border: '2px solid rgba(255,255,255,0.5)',
        borderRadius: '8px',
        color: 'white',
        cursor: 'pointer',
        fontSize: '1em',
        fontWeight: 'bold',
        transition: 'all 0.3s'
      }}
      onMouseOver={(e) => e.target.style.background = 'rgba(255,255,255,0.3)'}
      onMouseOut={(e) => e.target.style.background = 'rgba(255,255,255,0.2)'}
    >
      📋 {language === 'zh' ? '查看完整执行计划' : 'View Execution Plan'}
    </button>
  </div>
)}
```

## 集成步骤

1. 打开 `frontend/src/StockAnalysis.js`
2. 按照上述标注的行号添加代码
3. 保存文件
4. 提交到GitHub：
   ```bash
   git add frontend/src/StockAnalysis.js
   git commit -m "✨ 前端集成ML智能交易建议"
   git push origin main
   ```

## 测试

1. 在前端搜索股票（如AAPL）
2. 点击"AI分析"
3. 分析完成后，自动显示ML建议卡片
4. 查看个性化建议和风险提示

## 注意事项

- ML建议需要用户登录
- 如果ML API不可用，会优雅降级（不显示）
- ML建议基于用户历史行为，新用户使用默认值


