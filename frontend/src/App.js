import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './Login';
import Register from './Register';
import OptionStrategy from './OptionStrategy';
import StockAnalysis from './StockAnalysis';
import AccountBalance from './AccountBalance';
import PositionComparison from './PositionComparison';

function App() {
  // 根据环境自动切换API地址：本地开发使用localhost，生产环境使用Render
  const API_URL = process.env.REACT_APP_API_URL || 
                  (window.location.hostname === 'localhost' 
                    ? 'http://localhost:10000' 
                    : 'https://decision-assistant-backend.onrender.com');
  const [currentView, setCurrentView] = useState('login'); // 'login', 'register', 'app'
  const [user, setUser] = useState(null);
  const [currentMode, setCurrentMode] = useState('analysis');
  const [loading, setLoading] = useState(false);
  
  // 算法分析相关状态
  const [algorithms, setAlgorithms] = useState([]);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('weighted_scoring');
  const [algoQuestion, setAlgoQuestion] = useState('');
  const [algoOptions, setAlgoOptions] = useState('[\n  {"name": "选项A", "价格": 8, "性能": 9, "外观": 7},\n  {"name": "选项B", "价格": 9, "性能": 7, "外观": 8}\n]');
  const [algoResult, setAlgoResult] = useState(null);

  // 期权策略相关状态
  const [optionStrategyResult, setOptionStrategyResult] = useState(null);
  const [showOptionStrategy, setShowOptionStrategy] = useState(false);

  // 删除了聊天相关功能

  // 加载算法列表
  useEffect(() => {
    fetch(`${API_URL}/api/algorithms/list`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setAlgorithms(data.algorithms);
        }
      })
      .catch(err => console.error('获取算法列表失败:', err));
  }, [API_URL]);

  // 注意：已移除自动登录逻辑，始终显示登录界面
  // 用户必须手动登录才能进入应用

  const handleLogin = (userData) => {
    setUser(userData);
    setCurrentView('app');
  };

  const handleRegister = (userData) => {
    setUser(userData);
    setCurrentView('app');
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    setUser(null);
    setCurrentView('login');
  };

  const switchMode = (mode) => {
    setCurrentMode(mode);
    setAlgoResult(null);
  };
  
  // 算法分析函数
  const analyzeWithAlgorithm = async () => {
    if (!algoQuestion.trim()) {
      alert('请输入决策问题');
      return;
    }
    
    let parsedOptions;
    try {
      parsedOptions = JSON.parse(algoOptions);
    } catch (e) {
      alert('选项格式错误，请输入有效的JSON');
      return;
    }
    
    setLoading(true);
    setAlgoResult(null);
    
    try {
      const response = await fetch(`${API_URL}/api/algorithms/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          algorithm_id: selectedAlgorithm,
          question: algoQuestion,
          options: parsedOptions
        })
      });
      
      const data = await response.json();
      
      if (data.status === 'success') {
        setAlgoResult(data.result);
      } else {
        alert('分析失败: ' + data.message);
      }
    } catch (error) {
      alert('请求失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };


  // 删除了聊天功能

  // 如果未登录，显示登录或注册页面
  if (currentView === 'login') {
    return <Login onLogin={handleLogin} onSwitchToRegister={() => setCurrentView('register')} />;
  }

  if (currentView === 'register') {
    return <Register onRegister={handleRegister} onSwitchToLogin={() => setCurrentView('login')} />;
  }

  // 已登录，显示主应用
  return (
    <div style={{ 
      fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', // 蓝紫色渐变背景
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        {/* Header with User Info */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div style={{ textAlign: 'center', color: 'white', flex: 1 }}>
            <h1 style={{ fontSize: '2.5em', marginBottom: '10px', textShadow: '2px 2px 4px rgba(0,0,0,0.2)' }}>
              🤔 Decision Assistant
            </h1>
            <p>Powered by DeepSeek AI & Decision Algorithms</p>
          </div>
          <div style={{ 
            background: 'rgba(255,255,255,0.2)', 
            padding: '15px 20px', 
            borderRadius: '10px',
            color: 'white',
            textAlign: 'right'
          }}>
            <div style={{ fontWeight: '600', marginBottom: '5px' }}>👤 {user?.username}</div>
            <button
              onClick={handleLogout}
              style={{
                background: 'rgba(255,255,255,0.3)',
                color: 'white',
                border: '1px solid white',
                padding: '8px 16px',
                borderRadius: '5px',
                cursor: 'pointer',
                fontWeight: '600',
                fontSize: '0.9em'
              }}
            >
              🚪 退出登录
            </button>
          </div>
        </div>

        {/* 账户资金显示 */}
        <AccountBalance />

        {/* Mode Selector */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '15px', marginBottom: '30px', flexWrap: 'wrap' }}>
          <button
            onClick={() => switchMode('analysis')}
            style={{
              background: currentMode === 'analysis' ? '#ffd700' : 'white',
              color: currentMode === 'analysis' ? '#333' : '#667eea',
              padding: '10px 25px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1em',
              fontWeight: '600',
              transform: currentMode === 'analysis' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            📈 Stock Analysis
          </button>
          <button
            onClick={() => switchMode('positions')}
            style={{
              background: currentMode === 'positions' ? '#ffd700' : 'white',
              color: currentMode === 'positions' ? '#333' : '#667eea',
              padding: '10px 25px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1em',
              fontWeight: '600',
              transform: currentMode === 'positions' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            📊 Positions (A/B)
          </button>
        </div>

        {/* Stock Analysis Mode */}
        {currentMode === 'analysis' && (
          <StockAnalysis apiUrl={API_URL} username={user?.username} />
        )}

        {/* Positions A/B Comparison Mode */}
        {currentMode === 'positions' && (
          <PositionComparison />
        )}

        {/* Old Strategy Evaluation Mode */}

        {/* Old Algorithm Mode - Hidden */}
        {currentMode === 'algorithm_old' && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '30px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <h2 style={{ marginBottom: '20px', color: '#333' }}>🧮 算法分析模式</h2>
            
            {/* 选择算法 */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600' }}>
                选择算法：
              </label>
              <select 
                value={selectedAlgorithm} 
                onChange={(e) => setSelectedAlgorithm(e.target.value)}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1em'
                }}
              >
                {algorithms.map(algo => (
                  <option key={algo.id} value={algo.id}>
                    {algo.name} (v{algo.version})
                  </option>
                ))}
              </select>
            </div>

            {/* 决策问题 */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600' }}>
                决策问题：
              </label>
              <input
                type="text"
                value={algoQuestion}
                onChange={(e) => setAlgoQuestion(e.target.value)}
                placeholder="例如：选择哪款笔记本电脑？"
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1em'
                }}
              />
            </div>

            {/* 选项JSON */}
            <div style={{ marginBottom: '20px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600' }}>
                选项（JSON格式）：
              </label>
              <textarea
                value={algoOptions}
                onChange={(e) => setAlgoOptions(e.target.value)}
                rows={10}
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '0.9em',
                  fontFamily: 'monospace'
                }}
              />
            </div>

            {/* 分析按钮 */}
            <button 
              onClick={analyzeWithAlgorithm}
              disabled={loading}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                width: '100%',
                padding: '15px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.1em',
                cursor: loading ? 'not-allowed' : 'pointer',
                fontWeight: '600'
              }}
            >
              {loading ? '⚙️ 分析中...' : '🔍 开始分析'}
            </button>

            {/* 显示结果 */}
            {algoResult && (
              <div style={{
                marginTop: '30px',
                padding: '20px',
                backgroundColor: '#f8f9fa',
                borderRadius: '10px'
              }}>
                <h3 style={{ color: '#333', marginBottom: '15px' }}>📊 分析结果</h3>
                
                <div style={{
                  background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
                  color: 'white',
                  padding: '15px',
                  borderRadius: '8px',
                  marginBottom: '15px'
                }}>
                  <strong>推荐：</strong>
                  <span style={{ fontSize: '1.5em', marginLeft: '10px' }}>
                    {algoResult.recommendation}
                  </span>
                </div>

                <div style={{ marginBottom: '15px' }}>
                  <strong>得分：</strong>
                  <div style={{ marginTop: '10px' }}>
                    {Object.entries(algoResult.scores).map(([option, score]) => (
                      <div key={option} style={{
                        background: 'white',
                        padding: '10px',
                        marginBottom: '5px',
                        borderRadius: '5px',
                        display: 'flex',
                        justifyContent: 'space-between'
                      }}>
                        <span>{option}</span>
                        <strong>{typeof score === 'number' ? score.toFixed(2) : score}</strong>
                      </div>
                    ))}
                  </div>
                </div>

                {algoResult.summary && (
                  <div style={{ marginBottom: '15px' }}>
                    <strong>总结：</strong>
                    <p style={{ marginTop: '8px', lineHeight: '1.6' }}>{algoResult.summary}</p>
                  </div>
                )}

                {algoResult.analysis && (
                  <details style={{ marginTop: '15px' }}>
                    <summary style={{ cursor: 'pointer', fontWeight: '600' }}>详细分析</summary>
                    <pre style={{
                      whiteSpace: 'pre-wrap',
                      background: 'white',
                      padding: '15px',
                      borderRadius: '5px',
                      marginTop: '10px',
                      fontSize: '0.9em',
                      lineHeight: '1.6'
                    }}>
                      {algoResult.analysis}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </div>
        )}


      </div>

      {/* 期权策略模态框 */}
      {showOptionStrategy && optionStrategyResult && (
        <OptionStrategy
          optionResult={optionStrategyResult}
          onClose={() => {
            setShowOptionStrategy(false);
            setOptionStrategyResult(null);
          }}
        />
      )}
    </div>
  );
}

export default App;

