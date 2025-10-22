import React from 'react';
import './App.css';

function App() {
  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      height: '100vh',
      backgroundColor: '#f0f0f0'
    }}>
      <div style={{
        padding: '40px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h1>登录测试页面</h1>
        <p>版本: 2024-10-22-emergency-test</p>
        <input type="text" placeholder="用户名" style={{display: 'block', margin: '10px 0', padding: '10px', width: '250px'}} />
        <input type="password" placeholder="密码" style={{display: 'block', margin: '10px 0', padding: '10px', width: '250px'}} />
        <button style={{padding: '10px 20px', backgroundColor: '#007bff', color: 'white', border: 'none', borderRadius: '4px', width: '270px', marginTop: '10px'}}>
          登录
        </button>
        <p style={{marginTop: '20px', color: '#666', fontSize: '14px'}}>
          如果您能看到这个页面，说明React正常工作
        </p>
      </div>
    </div>
  );
}

export default App;
