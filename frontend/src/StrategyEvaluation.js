import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function StrategyEvaluation({ apiUrl }) {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(false);

  // 加载策略列表
  useEffect(() => {
    loadStrategies();
  }, []);

  const loadStrategies = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/strategy/list`);
      const result = await response.json();
      
      if (result.status === 'success') {
        setStrategies(result.strategies);
      }
    } catch (err) {
      console.error('加载策略失败:', err);
    }
  };

  const evaluateStrategy = async (strategy) => {
    setSelectedStrategy(strategy);
    setLoading(true);
    setEvaluation(null);

    try {
      const response = await fetch(`${apiUrl}/api/strategy/evaluate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          strategy_id: strategy.strategy_id,
          symbol: strategy.symbol
        })
      });

      const result = await response.json();

      if (result.status === 'success') {
        setEvaluation(result.evaluation);
      } else {
        alert('评估失败: ' + result.message);
      }
    } catch (err) {
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
                  <div style={{ fontSize: '1.2em', fontWeight: '600' }}>
                    {strategy.symbol} - {strategy.company_name}
                  </div>
                  <div style={{ fontSize: '1.5em' }}>
                    {getStyleIcon(strategy.investment_style)}
                  </div>
                </div>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '5px' }}>
                  {getStyleName(strategy.investment_style)}风格
                </div>
                <div style={{ fontSize: '0.9em', color: '#666', marginBottom: '10px' }}>
                  建议：{strategy.recommendation} | 目标价：${strategy.target_price}
                </div>
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

