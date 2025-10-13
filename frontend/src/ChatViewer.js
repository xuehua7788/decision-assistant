import React, { useState, useEffect } from 'react';

/**
 * 聊天记录查看器组件
 * 功能等同于 ViewChatUTF8.ps1，但在 Web 界面中实现
 */
function ChatViewer() {
  const [sessions, setSessions] = useState([]);
  const [selectedSession, setSelectedSession] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // API URL 配置（支持环境变量）
  const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

  // 组件加载时获取所有会话
  useEffect(() => {
    fetchSessions();
  }, []);

  // 获取所有会话列表
  const fetchSessions = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await fetch(`${API_URL}/api/decisions/sessions`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSessions(data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch sessions:', error);
      setError('无法连接到服务器，请确保后端服务正在运行');
      setLoading(false);
    }
  };

  // 查看特定会话的详细内容
  const viewSession = async (sessionId) => {
    try {
      const response = await fetch(`${API_URL}/api/decisions/session/${sessionId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      setSelectedSession(data);
    } catch (error) {
      console.error('Failed to fetch session:', error);
      alert('加载会话失败：' + error.message);
    }
  };

  // 格式化日期时间
  const formatDateTime = (isoString) => {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  return (
    <div style={{ 
      fontFamily: "'Segoe UI', system-ui, -apple-system, sans-serif",
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      minHeight: '100vh',
      padding: '20px'
    }}>
      <div style={{ maxWidth: '1400px', margin: '0 auto' }}>
        {/* 页头 */}
        <div style={{ textAlign: 'center', color: 'white', marginBottom: '20px' }}>
          <h1 style={{ fontSize: '2.5em', marginBottom: '10px', textShadow: '2px 2px 4px rgba(0,0,0,0.2)' }}>
            💬 聊天记录查看器
          </h1>
          <p>等同于 ViewChatUTF8.ps1 的 Web 版本</p>
          {error && (
            <div style={{
              background: '#f56565',
              color: 'white',
              padding: '10px',
              borderRadius: '8px',
              marginTop: '10px'
            }}>
              ⚠️ {error}
            </div>
          )}
        </div>

        {/* 主内容区域 */}
        <div style={{
          background: 'white',
          borderRadius: '15px',
          padding: '30px',
          boxShadow: '0 20px 40px rgba(0,0,0,0.1)',
          minHeight: '600px'
        }}>
          <div style={{ display: 'flex', gap: '30px', height: '100%' }}>
            
            {/* 左侧：会话列表 */}
            <div style={{ 
              flex: '0 0 350px', 
              borderRight: '2px solid #e0e0e0', 
              paddingRight: '20px',
              maxHeight: '700px',
              overflowY: 'auto'
            }}>
              <div style={{ 
                display: 'flex', 
                justifyContent: 'space-between', 
                alignItems: 'center',
                marginBottom: '15px'
              }}>
                <h2 style={{ margin: 0, color: '#333' }}>📋 会话列表</h2>
                <button
                  onClick={fetchSessions}
                  style={{
                    background: '#667eea',
                    color: 'white',
                    border: 'none',
                    padding: '8px 16px',
                    borderRadius: '5px',
                    cursor: 'pointer',
                    fontSize: '14px'
                  }}
                >
                  🔄 刷新
                </button>
              </div>

              {loading ? (
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                  <div style={{ fontSize: '40px', marginBottom: '10px' }}>⏳</div>
                  <p>加载中...</p>
                </div>
              ) : sessions.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 0', color: '#999' }}>
                  <div style={{ fontSize: '40px', marginBottom: '10px' }}>📭</div>
                  <p>暂无聊天记录</p>
                </div>
              ) : (
                <div>
                  {sessions.map((session, index) => (
                    <div 
                      key={session.session_id}
                      onClick={() => viewSession(session.session_id)}
                      style={{
                        padding: '15px',
                        margin: '10px 0',
                        border: '2px solid #e0e0e0',
                        borderRadius: '8px',
                        cursor: 'pointer',
                        backgroundColor: selectedSession?.session_id === session.session_id 
                          ? '#e3f2fd' 
                          : 'white',
                        transition: 'all 0.2s',
                        boxShadow: selectedSession?.session_id === session.session_id 
                          ? '0 4px 8px rgba(102, 126, 234, 0.2)' 
                          : 'none'
                      }}
                      onMouseEnter={(e) => {
                        if (selectedSession?.session_id !== session.session_id) {
                          e.currentTarget.style.backgroundColor = '#f5f5f5';
                        }
                      }}
                      onMouseLeave={(e) => {
                        if (selectedSession?.session_id !== session.session_id) {
                          e.currentTarget.style.backgroundColor = 'white';
                        }
                      }}
                    >
                      <div style={{ 
                        fontWeight: 'bold', 
                        marginBottom: '8px',
                        color: '#667eea',
                        fontSize: '16px'
                      }}>
                        #{index + 1}
                      </div>
                      <div style={{ fontSize: '13px', color: '#666', marginBottom: '5px' }}>
                        📅 {formatDateTime(session.created_at)}
                      </div>
                      <div style={{ fontSize: '13px', color: '#888', marginBottom: '8px' }}>
                        💬 消息数: <strong>{session.message_count}</strong>
                      </div>
                      <div style={{ 
                        fontSize: '12px', 
                        color: '#999', 
                        lineHeight: '1.4',
                        overflow: 'hidden',
                        textOverflow: 'ellipsis',
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical'
                      }}>
                        {session.first_message || '(空会话)'}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* 右侧：消息详情 */}
            <div style={{ flex: 1, maxHeight: '700px', overflowY: 'auto' }}>
              <h2 style={{ marginTop: 0, color: '#333' }}>💭 消息详情</h2>
              
              {selectedSession ? (
                <div>
                  {/* 会话信息卡片 */}
                  <div style={{ 
                    marginBottom: '25px', 
                    padding: '20px', 
                    background: 'linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%)',
                    borderRadius: '10px',
                    border: '1px solid #e0e0e0'
                  }}>
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🆔 Session ID:</strong>
                      <code style={{ 
                        marginLeft: '10px', 
                        background: 'white', 
                        padding: '4px 8px', 
                        borderRadius: '4px',
                        fontSize: '12px'
                      }}>
                        {selectedSession.session_id}
                      </code>
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🕐 创建时间:</strong> {formatDateTime(selectedSession.created_at)}
                    </div>
                    <div style={{ marginBottom: '10px' }}>
                      <strong>🕒 最后活动:</strong> {formatDateTime(selectedSession.last_activity)}
                    </div>
                    <div>
                      <strong>📊 消息总数:</strong> {selectedSession.messages.length}
                    </div>
                  </div>
                  
                  {/* 消息列表 */}
                  {selectedSession.messages.map((msg, index) => (
                    <div 
                      key={index}
                      style={{
                        padding: '18px',
                        margin: '15px 0',
                        borderRadius: '10px',
                        backgroundColor: msg.role === 'user' ? '#e3f2fd' : '#f5f5f5',
                        borderLeft: `5px solid ${msg.role === 'user' ? '#2196f3' : '#4caf50'}`,
                        boxShadow: '0 2px 4px rgba(0,0,0,0.05)',
                        transition: 'transform 0.2s',
                      }}
                      onMouseEnter={(e) => e.currentTarget.style.transform = 'translateX(5px)'}
                      onMouseLeave={(e) => e.currentTarget.style.transform = 'translateX(0)'}
                    >
                      <div style={{ 
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'center',
                        marginBottom: '10px'
                      }}>
                        <div style={{ 
                          fontWeight: 'bold', 
                          color: msg.role === 'user' ? '#1976d2' : '#388e3c',
                          fontSize: '14px'
                        }}>
                          {msg.role === 'user' ? '👤 用户' : '🤖 助手'}
                        </div>
                        <div style={{ fontSize: '11px', color: '#999' }}>
                          {formatDateTime(msg.timestamp)}
                        </div>
                      </div>
                      <div style={{ 
                        whiteSpace: 'pre-wrap', 
                        lineHeight: '1.6',
                        color: '#333',
                        fontSize: '14px'
                      }}>
                        {msg.content}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div style={{ 
                  textAlign: 'center', 
                  color: '#999', 
                  marginTop: '100px',
                  padding: '40px'
                }}>
                  <div style={{ fontSize: '80px', marginBottom: '20px', opacity: 0.3 }}>💬</div>
                  <p style={{ fontSize: '18px' }}>请从左侧选择一个会话查看详情</p>
                  <p style={{ fontSize: '14px', marginTop: '10px' }}>
                    功能等同于 <code>ViewChatUTF8.ps1</code>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* 底部说明 */}
        <div style={{ 
          textAlign: 'center', 
          color: 'white', 
          marginTop: '20px',
          fontSize: '14px',
          opacity: 0.8
        }}>
          <p>此页面功能等同于 ViewChatUTF8.ps1 PowerShell 脚本</p>
          <p>数据源：{API_URL}/api/decisions/sessions</p>
        </div>
      </div>
    </div>
  );
}

export default ChatViewer;

