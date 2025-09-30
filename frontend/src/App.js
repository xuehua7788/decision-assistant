import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Decision Assistant</h1>
        <p>Welcome to your Decision Making Tool</p>
        <div style={{marginTop: '30px'}}>
          <button style={{
            padding: '10px 20px',
            fontSize: '16px',
            backgroundColor: '#4CAF50',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}>
            Get Started
          </button>
        </div>
      </header>
    </div>
  );
}

export default App;
