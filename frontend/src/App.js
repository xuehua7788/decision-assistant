import React, { useState } from 'react';
import './App.css';
import ChatViewer from './ChatViewer';

function App() {
  const API_URL = process.env.REACT_APP_API_URL || window.location.origin;
  const [currentMode, setCurrentMode] = useState('analysis');
  const [description, setDescription] = useState('');
  const [options, setOptions] = useState(['', '']);
  const [chatMessages, setChatMessages] = useState([
    { type: 'assistant', text: "Hello! I'm your decision assistant. Tell me what decision you're facing, and I'll help you think through it step by step. What's on your mind?" }
  ]);
  const [chatInput, setChatInput] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const switchMode = (mode) => {
    setCurrentMode(mode);
    setResult(null);
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

    setChatMessages([...chatMessages, { type: 'user', text: chatInput }]);
    const userMessage = chatInput;
    setChatInput('');

    try {
      const response = await fetch(`${API_URL}/api/decisions/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });
      
      const data = await response.json();
      setChatMessages(prev => [...prev, { type: 'assistant', text: data.response }]);
    } catch (error) {
      setChatMessages(prev => [...prev, { type: 'assistant', text: 'Error: Could not connect to server' }]);
    }
  };

  return (
    <div style={{ 
      fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '1000px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ textAlign: 'center', color: 'white', marginBottom: '20px' }}>
          <h1 style={{ fontSize: '2.5em', marginBottom: '10px', textShadow: '2px 2px 4px rgba(0,0,0,0.2)' }}>
            🤔 Decision Assistant
          </h1>
          <p>Powered by DeepSeek AI & Decision Algorithms</p>
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
    </div>
  );
}

export default App;

