import React, { useState, useEffect } from 'react';
import './App.css';
import Login from './Login';
import Register from './Register';

// Version: 2024-10-22-force-login-debug
function App() {
  const API_URL = 'https://decision-assistant-backend.onrender.com';
  const [currentView, setCurrentView] = useState('login');
  const [user, setUser] = useState(null);

  // 强制清除所有缓存并显示登录界面
  useEffect(() => {
    console.log('🔍 App Version: 2024-10-22-force-login-debug');
    localStorage.clear();
    sessionStorage.clear();
    setCurrentView("login");
    setUser(null);
    console.log('✅ Forced login view - all storage cleared');
  }, []);

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

  // 🔴 临时调试：强制只显示登录界面
  console.log('🔍 Render Debug - currentView:', currentView, 'user:', user);
  
  if (currentView === 'register') {
    return <Register onRegister={handleRegister} onSwitchToLogin={() => setCurrentView('login')} />;
  }
  
  if (currentView === 'app' && user) {
    return (
      <div style={{ padding: '50px', textAlign: 'center' }}>
        <h1>✅ 登录成功！</h1>
        <p>欢迎 {user.username}</p>
        <button onClick={() => { setUser(null); setCurrentView('login'); localStorage.clear(); }}>
          退出登录
        </button>
      </div>
    );
  }
  
  // 默认显示登录界面
  return <Login onLogin={handleLogin} onSwitchToRegister={() => setCurrentView('register')} />;
}

export default App;

