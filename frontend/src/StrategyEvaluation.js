import React, { useState, useEffect, useCallback } from 'react';

function StrategyEvaluation({ apiUrl }) {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);

  // 加载策略列表
  const loadStrategies = useCallback(async () => {
    try {
      // 获取当前登录用户
      const currentUser = localStorage.getItem('username');
      if (!currentUser) {
        console.warn('未登录，无法加载策略');
        return;
      }

      // 新的API地址：从 users 表读取
      const response = await fetch(`${apiUrl}/api/user/${currentUser}/strategies`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setStrategies(result.strategies);
      }
    } catch (err) {
      console.error('加载策略失败:', err);
    }
  }, [apiUrl]);

  // 删除策略
  const deleteStrategy = async (strategyId, e) => {
    e.stopPropagation(); // 防止触发卡片点击
    
    if (!window.confirm('确定要删除这个策略吗？')) {
      return;
    }

    try {
      // 获取当前登录用户
      const currentUser = localStorage.getItem('username');
      if (!currentUser) {
        alert('❌ 请先登录！');
        return;
      }

      // 新的API地址：从 users 表删除
      const response = await fetch(`${apiUrl}/api/user/${currentUser}/strategies/${strategyId}`, {
        method: 'DELETE'
      });

      const result = await response.json();

      if (result.status === 'success') {
        alert('✅ 策略已删除');
        // 如果删除的是当前选中的策略，清空选择
        if (selectedStrategy?.strategy_id === strategyId) {
          setSelectedStrategy(null);
          setEvaluation(null);
        }
        // 重新加载策略列表
        loadStrategies();
      } else {
        alert('删除失败: ' + result.message);
      }
    } catch (err) {
      alert('网络错误: ' + err.message);
    }
  };

  useEffect(() => {
    loadStrategies();
  }, [loadStrategies]);

  const evaluateStrategy = async (strategy) => {
    setSelectedStrategy(strategy);
    setLoading(true);
    setEvaluation(null);

    try {
      // 获取当前用户
      const currentUser = localStorage.getItem('username');
      
      const response = await fetch(`${apiUrl}/api/strategy/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_id: strategy.strategy_id,
          symbol: strategy.symbol,
          username: currentUser
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        setEvaluation(result.evaluation);
      } else {
        alert('评估失败: ' + result.message);
      }
    } catch (err) {
      console.error('评估错误:', err);
      alert('网络错误: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  const getStyleIcon = (style) => {
    const icons = {
      'buffett': '🏛️',
      'lynch': '🎯',
      'soros': '🌊'
    };
    return icons[style] || '📊';
  };

  const getStyleName = (style) => {
    const names = {
      'buffett': '巴菲特',
      'lynch': '彼得·林奇',
      'soros': '索罗斯'
    };
    return names[style] || style;
  };

  return (
    <div style={{
      background: 'white',
      borderRadius: '15px',
      padding: '30px',
      boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
      marginBottom: '20px'
    }}>
      <h2 style={{ color: '#333', marginBottom: '20px' }}>
        📊 策略评估 - Strategy Evaluation
      </h2>

      {/* 策略列表 */}
      {strategies.length > 0 ? (
        <div style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#666', marginBottom: '15px' }}>
            您接受的策略 ({strategies.length})
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px' }}>
            {strategies.map((strategy) => (
              <div
                key={strategy.strategy_id}
                onClick={() => evaluateStrategy(strategy)}
                style={{
                  padding: '20px',
                  border: selectedStrategy?.strategy_id === strategy.strategy_id ? '3px solid #667eea' : '2px solid #e0e0e0',
                  borderRadius: '10px',
                  cursor: 'pointer',
                  transition: 'all 0.3s',
                  background: selectedStrategy?.strategy_id === strategy.strategy_id ? '#f0f4ff' : 'white'
                }}
                onMouseEnter={(e) => {
                  if (selectedStrategy?.strategy_id !== strategy.strategy_id) {
                    e.currentTarget.style.borderColor = '#667eea';
                    e.currentTarget.style.transform = 'translateY(-2px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedStrategy?.strategy_id !== strategy.strategy_id) {
                    e.currentTarget.style.borderColor = '#e0e0e0';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '10px' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ fontSize: '1.2em', fontWeight: '600' }}>
                      {strategy.symbol} - {strategy.company_name}
                    </div>
                  </div>
                  <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                    <div style={{ fontSize: '1.5em' }}>
                      {getStyleIcon(strategy.investment_style)}
                    </div>
                    <button
                      onClick={(e) => deleteStrategy(strategy.strategy_id, e)}
                      style={{
                        padding: '6px 12px',
                        background: '#f56565',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        fontSize: '0.85em',
                        fontWeight: '600',
                        cursor: 'pointer',
                        transition: 'all 0.3s'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#e53e3e';
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#f56565';
                      }}
                    >
                      🗑️ 删除
                    </button>
                  </div>
                </div>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>
                  {getStyleName(strategy.investment_style)}风格
                </div>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '10px' }}>
                  建议：{strategy.recommendation} | 目标价：${strategy.target_price}
                </div>
                {strategy.option_strategy && (
                  <div style={{ 
                    fontSize: '0.85em', 
                    color: '#667eea', 
                    marginBottom: '8px',
                    padding: '5px 10px',
                    background: '#f0f4ff',
                    borderRadius: '5px',
                    fontWeight: '500'
                  }}>
                    📊 期权策略: {strategy.option_strategy.name || strategy.option_strategy.strategy?.name || '已保存'}
                  </div>
                )}
                <div style={{ fontSize: '0.85em', color: '#999' }}>
                  创建时间：{new Date(strategy.created_at).toLocaleString('zh-CN')}
                </div>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '60px 20px',
          color: '#999'
        }}>
          <div style={{ fontSize: '3em', marginBottom: '20px' }}>📊</div>
          <div style={{ fontSize: '1.2em' }}>暂无已接受的策略</div>
          <div style={{ fontSize: '0.9em', marginTop: '10px' }}>
            在"股票分析"中接受策略后，可以在这里查看历史表现
          </div>
        </div>
      )}

      {/* 加载中 */}
      {loading && (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          color: '#667eea'
        }}>
          <div style={{ fontSize: '2em', marginBottom: '10px' }}>🔄</div>
          <div>正在评估策略...</div>
        </div>
      )}

      {/* 评估结果 */}
      {evaluation && selectedStrategy && (
        <div>
          <div style={{
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            color: 'white',
            padding: '20px',
            borderRadius: '10px',
            marginBottom: '20px'
          }}>
            <h3 style={{ marginBottom: '15px' }}>
              策略评估 - {selectedStrategy.symbol} ({selectedStrategy.company_name})
            </h3>
            <div style={{ fontSize: '0.9em', opacity: 0.9 }}>
              {getStyleIcon(selectedStrategy.investment_style)} {getStyleName(selectedStrategy.investment_style)}风格
            </div>
          </div>

          {/* 策略详情 */}
          <div style={{
            background: '#f8f9fa',
            padding: '20px',
            borderRadius: '10px',
            marginBottom: '20px'
          }}>
            <h4 style={{ marginBottom: '15px' }}>您接受的策略：</h4>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '15px' }}>
              <div>
                <div style={{ color: '#666', fontSize: '0.9em' }}>建议操作</div>
                <div style={{ fontSize: '1.2em', fontWeight: '600', color: '#333' }}>
                  {selectedStrategy.recommendation}
                </div>
              </div>
              <div>
                <div style={{ color: '#666', fontSize: '0.9em' }}>建议买入价</div>
                <div style={{ fontSize: '1.2em', fontWeight: '600', color: '#333' }}>
                  ${selectedStrategy.current_price.toFixed(2)}
                </div>
              </div>
              <div>
                <div style={{ color: '#666', fontSize: '0.9em' }}>目标价</div>
                <div style={{ fontSize: '1.2em', fontWeight: '600', color: '#48bb78' }}>
                  ${selectedStrategy.target_price.toFixed(2)}
                </div>
              </div>
              <div>
                <div style={{ color: '#666', fontSize: '0.9em' }}>止损价</div>
                <div style={{ fontSize: '1.2em', fontWeight: '600', color: '#f56565' }}>
                  ${selectedStrategy.stop_loss.toFixed(2)}
                </div>
              </div>
            </div>
            
            {/* 期权策略显示 */}
            {selectedStrategy.option_strategy && (
              <div style={{
                marginTop: '20px',
                padding: '15px',
                background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)',
                borderRadius: '8px',
                border: '2px solid #667eea'
              }}>
                <h4 style={{ color: '#667eea', marginBottom: '10px', display: 'flex', alignItems: 'center' }}>
                  📊 推荐期权策略：{selectedStrategy.option_strategy.name || '已保存'}
                </h4>
                {selectedStrategy.option_strategy.type && (
                  <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '8px' }}>
                    策略类型：{selectedStrategy.option_strategy.type}
                  </div>
                )}
                {selectedStrategy.option_strategy.description && (
                  <div style={{ fontSize: '0.9em', color: '#555', marginBottom: '12px' }}>
                    {selectedStrategy.option_strategy.description}
                  </div>
                )}
                {selectedStrategy.option_strategy.parameters && (
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '10px' }}>
                    {selectedStrategy.option_strategy.parameters.buy_strike && (
                      <div style={{ fontSize: '0.85em' }}>
                        <span style={{ color: '#666' }}>买入行权价：</span>
                        <strong>${selectedStrategy.option_strategy.parameters.buy_strike.toFixed(2)}</strong>
                      </div>
                    )}
                    {selectedStrategy.option_strategy.parameters.sell_strike && (
                      <div style={{ fontSize: '0.85em' }}>
                        <span style={{ color: '#666' }}>卖出行权价：</span>
                        <strong>${selectedStrategy.option_strategy.parameters.sell_strike.toFixed(2)}</strong>
                      </div>
                    )}
                    {selectedStrategy.option_strategy.parameters.expiry && (
                      <div style={{ fontSize: '0.85em' }}>
                        <span style={{ color: '#666' }}>到期时间：</span>
                        <strong>{selectedStrategy.option_strategy.parameters.expiry}</strong>
                      </div>
                    )}
                  </div>
                )}
                {selectedStrategy.option_strategy.metrics && (
                  <div style={{ 
                    marginTop: '10px', 
                    paddingTop: '10px', 
                    borderTop: '1px solid #e0e0e0',
                    display: 'grid',
                    gridTemplateColumns: 'repeat(auto-fit, minmax(120px, 1fr))',
                    gap: '10px'
                  }}>
                    {selectedStrategy.option_strategy.metrics.max_loss && (
                      <div style={{ fontSize: '0.85em' }}>
                        <span style={{ color: '#666' }}>最大损失：</span>
                        <strong style={{ color: '#f56565' }}>${selectedStrategy.option_strategy.metrics.max_loss.toFixed(2)}</strong>
                      </div>
                    )}
                    {selectedStrategy.option_strategy.metrics.max_gain && (
                      <div style={{ fontSize: '0.85em' }}>
                        <span style={{ color: '#666' }}>最大收益：</span>
                        <strong style={{ color: '#48bb78' }}>${selectedStrategy.option_strategy.metrics.max_gain.toFixed(2)}</strong>
                      </div>
                    )}
                    {selectedStrategy.option_strategy.metrics.breakeven && (
                      <div style={{ fontSize: '0.85em' }}>
                        <span style={{ color: '#666' }}>盈亏平衡：</span>
                        <strong>${selectedStrategy.option_strategy.metrics.breakeven.toFixed(2)}</strong>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>

          {/* 历史回测结果 */}
          {evaluation.backtest && (
            <div style={{
              background: '#fff',
              border: '2px solid #667eea',
              padding: '20px',
              borderRadius: '10px',
              marginBottom: '20px'
            }}>
              <h4 style={{ marginBottom: '15px', color: '#667eea' }}>
                📈 历史回测（如果在策略时间执行）
              </h4>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(150px, 1fr))', gap: '15px' }}>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>策略收益</div>
                  <div style={{ 
                    fontSize: '1.5em', 
                    fontWeight: '600',
                    color: evaluation.backtest.strategy_return >= 0 ? '#48bb78' : '#f56565'
                  }}>
                    {evaluation.backtest.strategy_return >= 0 ? '+' : ''}
                    {evaluation.backtest.strategy_return.toFixed(2)}%
                  </div>
                </div>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>同期股价涨幅</div>
                  <div style={{ 
                    fontSize: '1.5em', 
                    fontWeight: '600',
                    color: evaluation.backtest.actual_return >= 0 ? '#48bb78' : '#f56565'
                  }}>
                    {evaluation.backtest.actual_return >= 0 ? '+' : ''}
                    {evaluation.backtest.actual_return.toFixed(2)}%
                  </div>
                </div>
                <div>
                  <div style={{ color: '#666', fontSize: '0.9em' }}>策略表现</div>
                  <div style={{ 
                    fontSize: '1.5em', 
                    fontWeight: '600',
                    color: evaluation.backtest.outperformance >= 0 ? '#48bb78' : '#f56565'
                  }}>
                    {evaluation.backtest.outperformance >= 0 ? '跑赢 +' : '跑输 '}
                    {Math.abs(evaluation.backtest.outperformance).toFixed(2)}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* 评估结论 */}
          <div style={{
            background: '#f0f4ff',
            padding: '20px',
            borderRadius: '10px',
            border: '2px solid #667eea'
          }}>
            <h4 style={{ marginBottom: '15px', color: '#667eea' }}>
              💡 评估结论
            </h4>
            <p style={{ lineHeight: '1.8', fontSize: '1.05em', margin: 0 }}>
              {evaluation.conclusion || '策略评估完成，请查看上方数据'}
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default StrategyEvaluation;

