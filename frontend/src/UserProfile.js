import React, { useState, useEffect } from 'react';

function UserProfile({ username, apiUrl }) {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);

  // 加载用户画像
  const loadProfile = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}/api/profile/${username}`);
      
      if (response.ok) {
        const data = await response.json();
        setProfile(data.profile);
      } else if (response.status === 404) {
        setProfile(null);
      } else {
        setError('加载失败');
      }
    } catch (err) {
      setError('网络错误');
    } finally {
      setLoading(false);
    }
  };

  // 生成用户画像
  const generateProfile = async () => {
    if (!window.confirm(`确定要分析用户 ${username} 的聊天记录生成画像吗？\n\n注意：\n1. 需要至少5条聊天记录\n2. 分析可能需要1-2分钟\n3. 会消耗DeepSeek API额度`)) {
      return;
    }

    setAnalyzing(true);
    setError(null);

    try {
      const response = await fetch(`${apiUrl}/api/profile/${username}/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        alert('✅ 用户画像生成成功！');
        loadProfile();
      } else {
        setError(data.message || '生成失败');
      }
    } catch (err) {
      setError('网络错误');
    } finally {
      setAnalyzing(false);
    }
  };

  // 翻译函数
  const translateRiskTolerance = (value) => {
    const map = {
      'conservative': '保守型',
      'moderate': '中等',
      'aggressive': '激进型'
    };
    return map[value] || value;
  };

  const translateInvestmentStyle = (value) => {
    const map = {
      'value': '价值投资',
      'growth': '成长投资',
      'momentum': '动量投资',
      'contrarian': '逆向投资'
    };
    return map[value] || value;
  };

  const translateTimeHorizon = (value) => {
    const map = {
      'short': '短期',
      'medium': '中期',
      'long': '长期'
    };
    return map[value] || value;
  };

  const translateOptionExperience = (value) => {
    const map = {
      'none': '无经验',
      'basic': '基础',
      'experienced': '有经验'
    };
    return map[value] || value;
  };

  useEffect(() => {
    if (username) {
      loadProfile();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [username]);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ fontSize: '24px' }}>⏳ 加载中...</div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div style={{ padding: '40px', textAlign: 'center' }}>
        <div style={{ fontSize: '24px', marginBottom: '20px' }}>📊 用户画像</div>
        <div style={{ color: '#666', marginBottom: '30px' }}>
          暂无用户画像数据
        </div>
        <button
          onClick={generateProfile}
          disabled={analyzing}
          style={{
            background: analyzing ? '#ccc' : '#667eea',
            color: 'white',
            padding: '15px 40px',
            border: 'none',
            borderRadius: '10px',
            fontSize: '16px',
            cursor: analyzing ? 'not-allowed' : 'pointer'
          }}
        >
          {analyzing ? '⏳ 分析中...' : '🔄 生成用户画像'}
        </button>
        {error && (
          <div style={{ color: 'red', marginTop: '20px' }}>
            ❌ {error}
          </div>
        )}
      </div>
    );
  }

  const inv_pref = profile.investment_preferences || {};
  const knowledge = profile.knowledge_level || {};
  const emotion = profile.emotional_traits || {};
  // eslint-disable-next-line no-unused-vars
  const behav = profile.behavioral_traits || {};
  const insights = profile.key_insights || {};
  const recommendations = profile.recommendations || {};

  return (
    <div style={{ padding: '20px', maxWidth: '1200px', margin: '0 auto' }}>
      {/* 标题 */}
      <div style={{ textAlign: 'center', marginBottom: '30px' }}>
        <h2 style={{ color: '#667eea', marginBottom: '10px' }}>
          👤 {username} 的投资者画像
        </h2>
        <div style={{ color: '#666', fontSize: '14px' }}>
          最后分析: {profile.metadata?.analyzed_at ? new Date(profile.metadata.analyzed_at).toLocaleString('zh-CN') : 'N/A'} | 
          分析消息数: {profile.metadata?.total_messages_analyzed || 0} 条
        </div>
        <button
          onClick={generateProfile}
          disabled={analyzing}
          style={{
            marginTop: '15px',
            background: analyzing ? '#ccc' : '#764ba2',
            color: 'white',
            padding: '10px 25px',
            border: 'none',
            borderRadius: '8px',
            fontSize: '14px',
            cursor: analyzing ? 'not-allowed' : 'pointer'
          }}
        >
          {analyzing ? '⏳ 重新分析中...' : '🔄 重新生成画像'}
        </button>
      </div>

      {/* 投资特征卡片 */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        borderRadius: '15px',
        padding: '30px',
        color: 'white',
        marginBottom: '20px'
      }}>
        <h3 style={{ marginBottom: '20px', fontSize: '20px' }}>📊 投资特征</h3>
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '20px'
        }}>
          <div>
            <div style={{ opacity: 0.8, fontSize: '14px' }}>风险偏好</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '5px' }}>
              {translateRiskTolerance(inv_pref.risk_tolerance)}
            </div>
          </div>
          <div>
            <div style={{ opacity: 0.8, fontSize: '14px' }}>投资风格</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '5px' }}>
              {translateInvestmentStyle(inv_pref.investment_style)}
            </div>
          </div>
          <div>
            <div style={{ opacity: 0.8, fontSize: '14px' }}>时间范围</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '5px' }}>
              {translateTimeHorizon(inv_pref.time_horizon)}
            </div>
          </div>
          <div>
            <div style={{ opacity: 0.8, fontSize: '14px' }}>期权经验</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '5px' }}>
              {translateOptionExperience(knowledge.option_experience)}
            </div>
          </div>
          <div>
            <div style={{ opacity: 0.8, fontSize: '14px' }}>信心水平</div>
            <div style={{ fontSize: '20px', fontWeight: 'bold', marginTop: '5px' }}>
              {((emotion.confidence_level || 0) * 100).toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* 关键洞察 */}
      <div style={{
        background: 'white',
        borderRadius: '15px',
        padding: '25px',
        marginBottom: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ color: '#667eea', marginBottom: '15px' }}>🎯 关键洞察</h3>
        <div style={{ lineHeight: '1.8' }}>
          <p><strong>关注股票:</strong> {(insights.key_interests || []).join(', ') || 'N/A'}</p>
          <p><strong>决策模式:</strong> {insights.decision_patterns || 'N/A'}</p>
          <p><strong>风险关注:</strong> {(insights.risk_concerns || []).join(', ') || 'N/A'}</p>
        </div>
      </div>

      {/* AI推荐 */}
      <div style={{
        background: 'white',
        borderRadius: '15px',
        padding: '25px',
        marginBottom: '20px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ color: '#667eea', marginBottom: '15px' }}>💡 AI推荐</h3>
        <div style={{ lineHeight: '1.8' }}>
          <p><strong>推荐策略类型:</strong> {(recommendations.recommended_strategy_types || []).join(', ') || 'N/A'}</p>
          <p><strong>个性化建议:</strong> {recommendations.personalization_notes || 'N/A'}</p>
        </div>
      </div>

      {/* 分析摘要 */}
      <div style={{
        background: '#f8f9fa',
        borderRadius: '15px',
        padding: '25px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
      }}>
        <h3 style={{ color: '#667eea', marginBottom: '15px' }}>📝 分析摘要</h3>
        <p style={{ lineHeight: '1.8', color: '#333' }}>
          {profile.analysis_summary || 'N/A'}
        </p>
      </div>

      {error && (
        <div style={{
          marginTop: '20px',
          padding: '15px',
          background: '#fee',
          borderRadius: '10px',
          color: '#c33'
        }}>
          ❌ {error}
        </div>
      )}
    </div>
  );
}

export default UserProfile;

