import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './Login';
import Register from './Register';
import OptionStrategy from './OptionStrategy';
import UserProfile from './UserProfile';
import StockAnalysis from './StockAnalysis';
import StrategyEvaluation from './StrategyEvaluation';

function App() {
  // 硬编码 Render 后端地址，确保生产环境正确
  const API_URL = 'https://decision-assistant-backend.onrender.com';
  const [currentView, setCurrentView] = useState('login'); // 'login', 'register', 'app'
  const [user, setUser] = useState(null);
  const [currentMode, setCurrentMode] = useState('analysis');
  const [chatMessages, setChatMessages] = useState([]);
  const [chatInput, setChatInput] = useState('');
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
  const initializeChatForUser = React.useCallback(async (username) => {
    console.log(`🔄 正在为用户 ${username} 加载聊天记录...`);
    
    // 优先从后端API获取该用户的聊天记录
    try {
      const response = await fetch(`${API_URL}/api/decisions/chat/${username}`);
      
      if (response.ok) {
        const data = await response.json();
        console.log(`✅ 从后端加载到 ${data.messages?.length || 0} 条消息`);
        
        if (data.messages) {
          // 将后端格式转换为前端格式
          const formattedMessages = [];
          data.messages.forEach(msg => {
            if (msg.user) {
              formattedMessages.push({ type: 'user', text: msg.user });
            }
            if (msg.assistant) {
              formattedMessages.push({ type: 'assistant', text: msg.assistant });
            }
          });
          
          // 即使是空数组也要设置，避免后续创建欢迎消息
          if (formattedMessages.length > 0) {
            console.log(`📝 显示 ${formattedMessages.length} 条历史消息`);
            setChatMessages(formattedMessages);
            localStorage.setItem(`chat_${username}`, JSON.stringify(formattedMessages));
            return;
          } else {
            // 后端返回空消息，但用户已存在，说明是新用户或聊天已清空
            console.log(`📝 新用户或空聊天记录`);
          }
        }
      }
    } catch (error) {
      console.log('⚠️ 无法从后端加载聊天记录，尝试使用本地缓存:', error);
    }
    
    // 如果后端没有消息，尝试从localStorage获取
    const userChatKey = `chat_${username}`;
    const savedChat = localStorage.getItem(userChatKey);
    
    if (savedChat) {
      try {
        const parsedChat = JSON.parse(savedChat);
        console.log(`📦 从localStorage加载到 ${parsedChat.length} 条消息`);
        setChatMessages(parsedChat);
        return;
      } catch (e) {
        console.log('❌ localStorage解析失败:', e);
      }
    }
    
    // 只有在后端和localStorage都没有数据时，才创建欢迎消息
    console.log(`🆕 创建欢迎消息`);
    const welcomeMessage = [
      { type: 'assistant', text: `Hello ${username}! I'm your decision assistant. Tell me what decision you're facing, and I'll help you think through it step by step. What's on your mind?` }
    ];
    setChatMessages(welcomeMessage);
    localStorage.setItem(userChatKey, JSON.stringify(welcomeMessage));
  }, [API_URL]);

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
    // 清理其他用户的localStorage缓存
    const currentUsername = userData.username;
    const keysToRemove = [];
    
    // 找出所有不属于当前用户的聊天记录键
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('chat_') && key !== `chat_${currentUsername}`) {
        keysToRemove.push(key);
      }
    }
    
    // 删除其他用户的聊天记录
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
    setUser(userData);
    setCurrentView('app');
    // 为当前用户加载或初始化聊天记录
    initializeChatForUser(userData.username);
  };

  const handleRegister = (userData) => {
    // 清理所有旧的localStorage缓存
    const currentUsername = userData.username;
    const keysToRemove = [];
    
    // 找出所有不属于当前用户的聊天记录键
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key && key.startsWith('chat_') && key !== `chat_${currentUsername}`) {
        keysToRemove.push(key);
      }
    }
    
    // 删除其他用户的聊天记录
    keysToRemove.forEach(key => localStorage.removeItem(key));
    
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
      
      // 检查是否返回了期权策略结果
      if (data.option_strategy_used && data.option_strategy_result) {
        console.log('🎯 检测到期权策略响应:', data.option_strategy_result);
        setOptionStrategyResult(data.option_strategy_result);
        setShowOptionStrategy(true);
      }
      
      const updatedMessages = [...newMessages, { type: 'assistant', text: data.response }];
      setChatMessages(updatedMessages);
      
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
            📈 Stock Analysis
          </button>
          <button
            onClick={() => switchMode('strategy')}
            style={{
              background: currentMode === 'strategy' ? '#ffd700' : 'white',
              color: currentMode === 'strategy' ? '#333' : '#667eea',
              padding: '10px 30px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1.1em',
              fontWeight: '600',
              transform: currentMode === 'strategy' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            📊 Strategy Evaluation
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
          <button
            onClick={() => switchMode('profile')}
            style={{
              background: currentMode === 'profile' ? '#ffd700' : 'white',
              color: currentMode === 'profile' ? '#333' : '#667eea',
              padding: '10px 30px',
              border: 'none',
              borderRadius: '25px',
              cursor: 'pointer',
              fontSize: '1.1em',
              fontWeight: '600',
              transform: currentMode === 'profile' ? 'scale(1.05)' : 'scale(1)'
            }}
          >
            👤 User Profile
          </button>
        </div>

        {/* Stock Analysis Mode */}
        {currentMode === 'analysis' && (
          <StockAnalysis apiUrl={API_URL} />
        )}

        {/* Strategy Evaluation Mode */}
        {currentMode === 'strategy' && (
          <StrategyEvaluation apiUrl={API_URL} />
        )}

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

      </div>

      {/* User Profile Mode */}
      {currentMode === 'profile' && (
        <UserProfile username={user?.username} apiUrl={API_URL} />
      )}

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

