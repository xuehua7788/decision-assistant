import React, { useState, useEffect } from 'react';
import './PositionComparison.css';

function PositionComparison() {
  const [positions, setPositions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [closingPosition, setClosingPosition] = useState(null);

  const apiUrl = process.env.REACT_APP_API_URL || 'https://decision-assistant-githubv3.onrender.com';

  useEffect(() => {
    loadPositions();
    // 每10秒刷新一次持仓
    const interval = setInterval(loadPositions, 10000);
    return () => clearInterval(interval);
  }, []);

  const loadPositions = async () => {
    const username = localStorage.getItem('username');
    if (!username) {
      setError('请先登录');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/fund/positions/${username}`);
      if (response.ok) {
        const data = await response.json();
        setPositions(data.positions);
        setError(null);
      } else {
        setError('获取持仓失败');
      }
    } catch (err) {
      console.error('加载持仓失败:', err);
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  };

  const closePosition = async (positionId) => {
    if (!window.confirm('确定要平仓吗？平仓后将结算盈亏。')) {
      return;
    }

    setClosingPosition(positionId);
    const username = localStorage.getItem('username');

    try {
      const response = await fetch(`${apiUrl}/api/position/close`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          username,
          position_id: positionId,
          trigger: 'MANUAL'
        })
      });

      if (response.ok) {
        const result = await response.json();
        alert(`✅ 平仓成功！\n实际收益: ${result.actual_pnl.toFixed(2)} (${result.actual_return})\n虚拟收益: ${result.virtual_pnl.toFixed(2)} (${result.virtual_return})\n${result.message}`);
        loadPositions(); // 刷新列表
      } else {
        const error = await response.json();
        alert(`❌ 平仓失败: ${error.error}`);
      }
    } catch (err) {
      console.error('平仓失败:', err);
      alert('❌ 平仓失败，请重试');
    } finally {
      setClosingPosition(null);
    }
  };

  if (loading) {
    return <div className="position-comparison loading">加载中...</div>;
  }

  if (error) {
    return <div className="position-comparison error">{error}</div>;
  }

  const openPositions = positions.filter(p => p.status === 'OPEN');
  const closedPositions = positions.filter(p => p.status === 'CLOSED');

  return (
    <div className="position-comparison">
      <h2>📊 持仓对照（A/B组）</h2>
      
      {openPositions.length === 0 && closedPositions.length === 0 && (
        <div className="empty-state">
          <p>暂无持仓记录</p>
          <small>接受策略后，将在这里显示A/B对照组</small>
        </div>
      )}

      {openPositions.length > 0 && (
        <div className="positions-section">
          <h3>🟢 持仓中 ({openPositions.length})</h3>
          {openPositions.map(position => (
            <PositionCard 
              key={position.position_id} 
              position={position} 
              onClose={closePosition}
              closing={closingPosition === position.position_id}
            />
          ))}
        </div>
      )}

      {closedPositions.length > 0 && (
        <div className="positions-section">
          <h3>⚪ 已平仓 ({closedPositions.length})</h3>
          {closedPositions.map(position => (
            <PositionCard 
              key={position.position_id} 
              position={position} 
              onClose={null}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function PositionCard({ position, onClose, closing }) {
  const choiceLabel = position.user_choice === 1 ? '期权' : '股票';
  const actualPnlClass = position.actual.pnl >= 0 ? 'positive' : 'negative';
  const virtualPnlClass = position.virtual.pnl >= 0 ? 'positive' : 'negative';

  return (
    <div className={`position-card ${position.status.toLowerCase()}`}>
      <div className="position-header">
        <div className="position-title">
          <h4>{position.symbol} - {position.company_name}</h4>
          <span className="choice-badge">{choiceLabel}</span>
        </div>
        <div className="position-actions">
          {position.status === 'OPEN' && onClose && (
            <button 
              className="close-btn" 
              onClick={() => onClose(position.position_id)}
              disabled={closing}
            >
              {closing ? '平仓中...' : '⚠️ 平仓'}
            </button>
          )}
          {position.status === 'CLOSED' && (
            <span className="closed-badge">
              {position.close_trigger === 'MANUAL' ? '手动平仓' : 
               position.close_trigger === 'STOP_LOSS' ? '止损' :
               position.close_trigger === 'TAKE_PROFIT' ? '止盈' : '到期'}
            </span>
          )}
        </div>
      </div>

      <div className="ab-comparison">
        {/* A组：实盘 */}
        <div className="group-card actual-group">
          <div className="group-header">
            <h5>A组 - 实盘</h5>
            <span className="type-badge">{position.actual.type}</span>
          </div>
          <div className="group-stats">
            <div className="stat-row">
              <span>成本</span>
              <span>${position.actual.cost.toFixed(2)}</span>
            </div>
            <div className="stat-row">
              <span>当前价值</span>
              <span>${position.actual.current_value.toFixed(2)}</span>
            </div>
            <div className="stat-row highlight">
              <span>盈亏</span>
              <span className={actualPnlClass}>
                {position.actual.pnl >= 0 ? '+' : ''}${position.actual.pnl.toFixed(2)}
                ({position.actual.return_rate >= 0 ? '+' : ''}{position.actual.return_rate.toFixed(2)}%)
              </span>
            </div>
            {position.actual.stop_loss && (
              <div className="stat-row">
                <span>止损价</span>
                <span>${position.actual.stop_loss.toFixed(2)}</span>
              </div>
            )}
            {position.actual.take_profit && (
              <div className="stat-row">
                <span>止盈价</span>
                <span>${position.actual.take_profit.toFixed(2)}</span>
              </div>
            )}
          </div>
        </div>

        {/* B组：虚拟 */}
        <div className="group-card virtual-group">
          <div className="group-header">
            <h5>B组 - 虚拟</h5>
            <span className="type-badge">{position.virtual.type}</span>
          </div>
          <div className="group-stats">
            <div className="stat-row">
              <span>成本</span>
              <span>${position.virtual.cost.toFixed(2)}</span>
            </div>
            <div className="stat-row">
              <span>当前价值</span>
              <span>${position.virtual.current_value.toFixed(2)}</span>
            </div>
            <div className="stat-row highlight">
              <span>盈亏</span>
              <span className={virtualPnlClass}>
                {position.virtual.pnl >= 0 ? '+' : ''}${position.virtual.pnl.toFixed(2)}
                ({position.virtual.return_rate >= 0 ? '+' : ''}{position.virtual.return_rate.toFixed(2)}%)
              </span>
            </div>
          </div>
          <div className="virtual-note">
            <small>如果选了这个策略会怎样</small>
          </div>
        </div>
      </div>

      <div className="position-footer">
        <small>
          决策时间: {new Date(position.decision_time).toLocaleString('zh-CN')}
          {position.close_time && ` | 平仓时间: ${new Date(position.close_time).toLocaleString('zh-CN')}`}
        </small>
      </div>
    </div>
  );
}

export default PositionComparison;

