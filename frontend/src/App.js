import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './Login';
import Register from './Register';

// Version: 2024-10-22-fix-option-strategy-v2
function App() {
  // 硬编码 Render 后端地址，确保生产环境正确
  const API_URL = 'https://decision-assistant-backend.onrender.com';
  const [currentView, setCurrentView] = useState('login'); // 'login', 'register', 'app'
  const [user, setUser] = useState(null);
  const [currentMode, setCurrentMode] = useState('analysis');
  const [description, setDescription] = useState('');
  const [options, setOptions] = useState(['', '']);
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
  const [result, setResult] = useState(null);
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

  // 初始化用户聊天记录的函数
  const initializeChatForUser = React.useCallback((username) => {
    // 从localStorage获取该用户的聊天记录
    const userChatKey = `chat_${username}`;
    const savedChat = localStorage.getItem(userChatKey);
    
    if (savedChat) {
      try {
        setChatMessages(JSON.parse(savedChat));
      } catch (e) {
        // 如果解析失败，使用默认欢迎消息
        const welcomeMessage = [
          { type: 'assistant', text: `Hello ${username}! I'm your decision assistant. Tell me what decision you're facing, and I'll help you think through it step by step. What's on your mind?` }
        ];
        setChatMessages(welcomeMessage);
        localStorage.setItem(userChatKey, JSON.stringify(welcomeMessage));
      }
    } else {
      // 新用户，创建欢迎消息
      const welcomeMessage = [
        { type: 'assistant', text: `Hello ${username}! I'm your decision assistant. Tell me what decision you're facing, and I'll help you think through it step by step. What's on your mind?` }
      ];
      setChatMessages(welcomeMessage);
      localStorage.setItem(userChatKey, JSON.stringify(welcomeMessage));
    }
  }, []);

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

  // 检查本地存储的登录状态
  useEffect(() => {
    console.log('App Version: 2024-10-22-fix-option-strategy-v2');
    // 开发环境不清除，生产环境清除缓存
    if (window.location.hostname === 'decision-assistant-frontend-prod.vercel.app') {
      localStorage.clear();
      sessionStorage.clear();
      console.log('✅ Production: Cleared all cache');
    }
    setCurrentView("login");
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
    setCurrentView('app');
    // 为当前用户加载或初始化聊天记录
    initializeChatForUser(userData.username);
  };

  const handleRegister = (userData) => {
    setUser(userData);
    setCurrentView('app');
    // 新用户，初始化欢迎消息
    initializeChatForUser(userData.username);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('username');
    // 清空聊天记录
    setChatMessages([]);
    setUser(null);
    setCurrentView('login');
  };

  const switchMode = (mode) => {
    setCurrentMode(mode);
    setResult(null);
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

  const addOption = () => {
    setOptions([...options, '']);
  };

  const removeOption = (index) => {
    if (options.length > 1) {
      setOptions(options.filter((_, i) => i !== index));
    }
  };

  const updateOption = (index, value) => {
    const newOptions = [...options];
    newOptions[index] = value;
    setOptions(newOptions);
  };

  const analyzeDecision = async () => {
    const validOptions = options.filter(o => o.trim() !== '');
    
    if (!description || validOptions.length === 0) {
      alert('Please provide a description and at least one option');
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/decisions/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          description: description,
          options: validOptions
        })
      });
      
      const data = await response.json();
      setResult(data);
      setLoading(false);
    } catch (error) {
      setResult({
        recommendation: 'Error',
        readable_summary: 'Could not connect to server: ' + error.message
      });
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!chatInput.trim()) return;

    const newMessages = [...chatMessages, { type: 'user', text: chatInput }];
    setChatMessages(newMessages);
    const userMessage = chatInput;
    setChatInput('');

    try {
      const response = await fetch(`${API_URL}/api/decisions/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          message: userMessage,
          session_id: user?.username // 使用用户名作为session_id
        })
      });
      
      const data = await response.json();
      const updatedMessages = [...newMessages, { type: 'assistant', text: data.response }];
      setChatMessages(updatedMessages);
      
      // 检查是否是期权策略响应
      if (data.option_strategy_used && data.option_strategy_result) {
        console.log('=== Option Strategy Detected ===');
        console.log('Setting option strategy result:', data.option_strategy_result);
        setOptionStrategyResult(data.option_strategy_result);
        setShowOptionStrategy(true);
        // 添加强制刷新
        setTimeout(() => {
          console.log('Option strategy should be visible now');
          setShowOptionStrategy(true);
        }, 100);
      }
      
      // 保存到localStorage
      if (user?.username) {
        localStorage.setItem(`chat_${user.username}`, JSON.stringify(updatedMessages));
      }
    } catch (error) {
      const errorMessages = [...newMessages, { type: 'assistant', text: 'Error: Could not connect to server' }];
      setChatMessages(errorMessages);
      
      // 保存到localStorage
      if (user?.username) {
        localStorage.setItem(`chat_${user.username}`, JSON.stringify(errorMessages));
      }
    }
  };

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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
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

        {/* Mode Selector */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '30px' }}>
          <button
            onClick={() => switchMode('analysis')}
            style={{
              background: currentMode === 'analysis' ? '#ffd700' : 'white',
              color: currentMode === 'analysis' ? '#333' : '#667eea',
              padding: '10px 30px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1.1em',
              fontWeight: '600',
              transform: currentMode === 'analysis' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            📊 Decision Analysis
          </button>
          <button
            onClick={() => switchMode('algorithm')}
            style={{
              background: currentMode === 'algorithm' ? '#ffd700' : 'white',
              color: currentMode === 'algorithm' ? '#333' : '#667eea',
              padding: '10px 30px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1.1em',
              fontWeight: '600',
              transform: currentMode === 'algorithm' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            🧮 Algorithm Mode
          </button>
          <button
            onClick={() => switchMode('chat')}
            style={{
              background: currentMode === 'chat' ? '#ffd700' : 'white',
              color: currentMode === 'chat' ? '#333' : '#667eea',
              padding: '10px 30px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1.1em',
              fontWeight: '600',
              transform: currentMode === 'chat' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            💬 Chat Mode
          </button>
        </div>

        {/* Analysis Mode */}
        {currentMode === 'analysis' && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '30px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600', fontSize: '1.1em' }}>
                📝 Describe your decision:
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows="3"
                placeholder="e.g., I'm considering buying a new laptop for work..."
                style={{
                  width: '100%',
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1em'
                }}
              />
            </div>

            <div style={{ marginBottom: '25px' }}>
              <label style={{ display: 'block', marginBottom: '8px', color: '#333', fontWeight: '600', fontSize: '1.1em' }}>
                🎯 Options to consider:
              </label>
              {options.map((option, index) => (
                <div key={index} style={{ display: 'flex', gap: '10px', marginBottom: '10px' }}>
                  <input
                    type="text"
                    value={option}
                    onChange={(e) => updateOption(index, e.target.value)}
                    placeholder={`Option ${index + 1}`}
                    style={{
                      flex: 1,
                      padding: '12px',
                      border: '2px solid #e0e0e0',
                      borderRadius: '8px',
                      fontSize: '1em'
                    }}
                  />
                  <button
                    onClick={() => removeOption(index)}
                    style={{
                      background: '#f56565',
                      color: 'white',
                      padding: '8px 16px',
                      border: 'none',
                      borderRadius: '8px',
                      cursor: 'pointer'
                    }}
                  >
                    Remove
                  </button>
                </div>
              ))}
              <button
                onClick={addOption}
                style={{
                  background: '#48bb78',
                  color: 'white',
                  padding: '8px 16px',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  marginTop: '10px'
                }}
              >
                + Add Option
              </button>
            </div>

            <button
              onClick={analyzeDecision}
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
              {loading ? '⚙️ Analyzing...' : '🔍 Analyze My Decision'}
            </button>
          </div>
        )}

        {/* Algorithm Mode */}
        {currentMode === 'algorithm' && (
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

        {/* Chat Mode */}
        {currentMode === 'chat' && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '30px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
            marginBottom: '20px'
          }}>
            <div style={{
              minHeight: '400px',
              maxHeight: '400px',
              overflowY: 'auto',
              border: '2px solid #e0e0e0',
              borderRadius: '10px',
              padding: '20px',
              marginBottom: '20px',
              background: '#fafafa'
            }}>
              {chatMessages.map((msg, idx) => (
                <div
                  key={idx}
                  style={{
                    marginBottom: '15px',
                    padding: '12px 16px',
                    borderRadius: '10px',
                    maxWidth: '80%',
                    marginLeft: msg.type === 'user' ? 'auto' : '0',
                    background: msg.type === 'user' 
                      ? 'linear-gradient(135deg, #667eea, #764ba2)'
                      : 'white',
                    color: msg.type === 'user' ? 'white' : '#333',
                    border: msg.type === 'assistant' ? '1px solid #e0e0e0' : 'none',
                    textAlign: msg.type === 'user' ? 'right' : 'left'
                  }}
                >
                  {msg.text}
                </div>
              ))}
            </div>

            <div style={{ display: 'flex', gap: '10px' }}>
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your message..."
                style={{
                  flex: 1,
                  padding: '12px',
                  border: '2px solid #e0e0e0',
                  borderRadius: '8px',
                  fontSize: '1em'
                }}
              />
              <button
                onClick={sendMessage}
                style={{
                  padding: '12px 24px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
                Send
              </button>
            </div>
          </div>
        )}

        {/* Results */}
        {result && (
          <div style={{
            background: 'white',
            borderRadius: '15px',
            padding: '30px',
            boxShadow: '0 20px 40px rgba(0,0,0,0.1)'
          }}>
            <h2>📊 Decision Analysis Results</h2>
            
            <div style={{
              background: 'linear-gradient(135deg, #48bb78 0%, #38a169 100%)',
              color: 'white',
              padding: '20px',
              borderRadius: '10px',
              marginTop: '20px',
              marginBottom: '20px'
            }}>
              <h3>⭐ Recommendation</h3>
              <p style={{ fontSize: '1.3em', fontWeight: 'bold' }}>{result.recommendation}</p>
            </div>

            <div style={{
              background: '#f8f9fa',
              borderRadius: '10px',
              padding: '20px',
              marginBottom: '20px'
            }}>
              <h3>📋 Summary</h3>
              <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                {result.readable_summary}
              </div>
            </div>

            {result.algorithm_analysis?.algorithms_used?.weighted_score?.results && (
              <div style={{
                background: '#f8f9fa',
                borderRadius: '10px',
                padding: '20px'
              }}>
                <h3>📊 Score Analysis</h3>
                {Object.entries(result.algorithm_analysis.algorithms_used.weighted_score.results).map(([option, scores]) => (
                  <div key={option} style={{
                    background: 'white',
                    padding: '10px 15px',
                    borderRadius: '8px',
                    marginBottom: '10px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center'
                  }}>
                    <span><strong>{option}</strong></span>
                    <span>{scores.total_score}/10</span>
                  </div>
                ))}
              </div>
            )}

            <button
              onClick={() => window.location.reload()}
              style={{
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                color: 'white',
                width: '100%',
                padding: '15px',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.1em',
                cursor: 'pointer',
                fontWeight: '600',
                marginTop: '20px'
              }}
            >
              🔄 New Analysis
            </button>
          </div>
        )}
      </div>

      {/* 期权策略可视化组件 */}
      {showOptionStrategy && optionStrategyResult && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          zIndex: 99999,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          backgroundColor: 'rgba(0, 0, 0, 0.5)'
        }}>
          <div style={{
            backgroundColor: 'white',
            borderRadius: '12px',
            padding: '30px',
            maxWidth: '90%',
            maxHeight: '90%',
            overflow: 'auto',
            boxShadow: '0 20px 60px rgba(0,0,0,0.3)'
          }}>
            <h2>期权策略分析</h2>
            <pre>{JSON.stringify(optionStrategyResult, null, 2)}</pre>
            <button
              onClick={() => {
                setShowOptionStrategy(false);
                setOptionStrategyResult(null);
              }}
              style={{
                marginTop: '20px',
                padding: '10px 20px',
                background: '#667eea',
                color: 'white',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer'
              }}
            >
              关闭
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

