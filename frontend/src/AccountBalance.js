import React, { useState, useEffect } from 'react';
import './AccountBalance.css';

function AccountBalance() {
  const [account, setAccount] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const apiUrl = process.env.REACT_APP_API_URL || 'https://decision-assistant-backend.onrender.com';

  const loadAccount = React.useCallback(async () => {
    const username = localStorage.getItem('username');
    if (!username) {
      setError('请先登录');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${apiUrl}/api/fund/account/${username}`);
      if (response.ok) {
        const data = await response.json();
        setAccount(data);
        setError(null);
      } else {
        setError('获取账户信息失败');
      }
    } catch (err) {
      console.error('加载账户信息失败:', err);
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  }, [apiUrl]);

  useEffect(() => {
    loadAccount();
    // 每30秒刷新一次
    const interval = setInterval(loadAccount, 30000);
    return () => clearInterval(interval);
  }, [loadAccount]);

  if (loading) {
    return <div className="account-balance loading">加载中...</div>;
  }

  if (error) {
    return <div className="account-balance error">{error}</div>;
  }

  if (!account) {
    return null;
  }

  const pnlClass = account.total_pnl >= 0 ? 'positive' : 'negative';
  const pnlSign = account.total_pnl >= 0 ? '+' : '';

  return (
    <div className="account-balance">
      <h3>💰 账户资金</h3>
      <div className="balance-grid">
        <div className="balance-item">
          <span className="label">总资产</span>
          <span className="value highlight">${account.total_assets.toFixed(2)}</span>
        </div>
        <div className="balance-item">
          <span className="label">现金</span>
          <span className="value">${account.total_cash.toFixed(2)}</span>
        </div>
        <div className="balance-item">
          <span className="label">可用资金</span>
          <span className="value">${account.available_cash.toFixed(2)}</span>
        </div>
        <div className="balance-item">
          <span className="label">保证金占用</span>
          <span className="value">${account.margin_occupied.toFixed(2)}</span>
        </div>
        <div className="balance-item">
          <span className="label">持仓市值</span>
          <span className="value">${account.position_value.toFixed(2)}</span>
        </div>
        <div className="balance-item">
          <span className="label">持仓数量</span>
          <span className="value">{account.position_count}</span>
        </div>
        <div className="balance-item">
          <span className="label">累计盈亏</span>
          <span className={`value ${pnlClass}`}>
            {pnlSign}${Math.abs(account.total_pnl).toFixed(2)}
          </span>
        </div>
      </div>
      <div className="balance-formula">
        <small>总资产 = 现金 + 持仓市值 | 可用资金 = 现金 - 保证金占用</small>
      </div>
    </div>
  );
}

export default AccountBalance;

