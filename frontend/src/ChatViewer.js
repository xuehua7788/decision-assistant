import React, { useState, useEffect } from 'react';

function ChatViewer() {
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
  
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSessions();
  }, []);

  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/api/decisions/sessions`);
      if (!response.ok) {
        throw new Error('获取会话列表失败');
      }
      const data = await response.json();
      setSessions(data.sessions || []);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      setError('无法连接到后端服务器，请确保后端服务正在运行');
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionDetail = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/api/decisions/sessions/${sessionId}`);
      if (!response.ok) {
        throw new Error('获取会话详情失败');
      }
      const data = await response.json();
      setSelectedSession(data);
    } catch (error) {
      console.error('Failed to fetch session:', error);
      alert('加载会话失败：' + error.message);
    }
  };

  const formatDateTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleString('zh-CN');
  };

  if (loading) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>聊天记录查看器</h1>
        <p>加载中...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>聊天记录查看器</h1>
        <div style={{ color: 'red', marginTop: '20px' }}>
          <h3>错误：{error}</h3>
          <button onClick={fetchSessions}>重试</button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1 style={{ textAlign: 'center' }}>聊天记录查看器</h1>
      
      <div style={{ display: 'flex', gap: '20px', marginTop: '20px' }}>
        
        <div style={{ flex: '0 0 300px', borderRight: '1px solid #ddd', paddingRight: '20px' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '15px' }}>
            <h2 style={{ margin: 0, color: '#333' }}>会话列表</h2>
            <button onClick={fetchSessions} style={{ padding: '5px 10px', cursor: 'pointer' }}>
              刷新
            </button>
          </div>
          
          {sessions.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '40px 20px', color: '#666' }}>
              <p>暂无聊天记录</p>
            </div>
          ) : (
            <div style={{ maxHeight: '600px', overflowY: 'auto' }}>
              {sessions.map((session) => (
                <div
                  key={session.session_id}
                  onClick={() => fetchSessionDetail(session.session_id)}
                  style={{
                    padding: '10px',
                    marginBottom: '10px',
                    border: '1px solid #ddd',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    backgroundColor: selectedSession?.session_id === session.session_id ? '#e3f2fd' : '#f9f9f9',
                  }}
                >
                  <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
                    {session.session_id.substring(0, 8)}...
                  </div>
                  <div style={{ fontSize: '12px', color: '#666' }}>
                    消息数：<strong>{session.message_count}</strong>
                  </div>
                  <div style={{ fontSize: '11px', color: '#999', marginTop: '5px' }}>
                    {session.first_message || '(空会话)'}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        <div style={{ flex: 1 }}>
          {selectedSession ? (
            <div>
              <h2 style={{ marginTop: 0, color: '#333' }}>消息详情</h2>
              
              <div style={{ marginBottom: '20px', padding: '15px', backgroundColor: '#f5f5f5', borderRadius: '5px' }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
                  <div>
                    <strong>创建时间:</strong> {formatDateTime(selectedSession.created_at)}
                  </div>
                  <div>
                    <strong>最后活动:</strong> {formatDateTime(selectedSession.last_activity)}
                  </div>
                  <div>
                    <strong>消息总数:</strong> {selectedSession.messages.length}
                  </div>
                </div>
              </div>

              <div style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {selectedSession.messages.map((msg, index) => (
                  <div
                    key={index}
                    style={{
                      marginBottom: '15px',
                      padding: '15px',
                      backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f1f8e9',
                      borderLeft: `4px solid ${msg.role === 'user' ? '#2196F3' : '#8BC34A'}`,
                      borderRadius: '5px',
                    }}
                  >
                    <div style={{ fontWeight: 'bold', marginBottom: '8px', color: '#333' }}>
                      {msg.role === 'user' ? '用户' : '助手'}
                    </div>
                    <div style={{ whiteSpace: 'pre-wrap', lineHeight: '1.6' }}>
                      {msg.content}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '100px 20px', color: '#999' }}>
              <p style={{ fontSize: '18px' }}>请从左侧选择一个会话查看详情</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatViewer;