import React, { useState } from 'react';
import './App.css';
import Login from './Login';
import Register from './Register';

// Version: 2024-10-22-final-working
function App() {
  const [currentView, setCurrentView] = useState('login');
  const [user, setUser] = useState(null);

  const handleLogin = (userData) => {
    console.log('✅ Login successful:', userData);
    setUser(userData);
    setCurrentView('app');
  };

  const handleRegister = (userData) => {
    console.log('✅ Register successful:', userData);
    setUser(userData);
    setCurrentView('app');
  };

  const handleLogout = () => {
    localStorage.clear();
    setUser(null);
    setCurrentView('login');
  };

  // 显示登录界面
  if (currentView === 'login') {
    return <Login onLogin={handleLogin} onSwitchToRegister={() => setCurrentView('register')} />;
  }

  // 显示注册界面
  if (currentView === 'register') {
    return <Register onRegister={handleRegister} onSwitchToLogin={() => setCurrentView('login')} />;
  }

  // 登录成功后的简单界面
  if (currentView === 'app' && user) {
  return (
    <div style={{ 
        padding: '50px', 
        textAlign: 'center',
        minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        color: 'white'
      }}>
        <h1>✅ 登录成功！</h1>
        <p style={{ fontSize: '1.2em', marginTop: '20px' }}>欢迎 {user.username}</p>
        <p style={{ marginTop: '30px', color: '#ffd700' }}>
          完整应用功能将在此处加载
        </p>
            <button
              onClick={handleLogout}
              style={{
            marginTop: '30px',
            padding: '12px 30px',
              fontSize: '1.1em',
            background: 'white',
            color: '#667eea',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                  fontWeight: '600'
                }}
              >
          退出登录
            </button>
    </div>
  );
  }

  // 默认显示登录
  return <Login onLogin={handleLogin} onSwitchToRegister={() => setCurrentView('register')} />;
}

export default App;
