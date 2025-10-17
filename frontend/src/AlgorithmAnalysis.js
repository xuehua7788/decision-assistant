import React, { useState, useEffect } from 'react';

const API_URL = 'https://decision-assistant-backend.onrender.com';

function AlgorithmAnalysis() {
  const [algorithms, setAlgorithms] = useState([]);
  const [selectedAlgorithm, setSelectedAlgorithm] = useState('weighted_scoring');
  const [question, setQuestion] = useState('');
  const [options, setOptions] = useState([
    { name: '选项A', 价格: 8, 性能: 9, 外观: 7 },
    { name: '选项B', 价格: 9, 性能: 7, 外观: 8 }
  ]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  // 获取可用算法列表
  useEffect(() => {
    fetch(`${API_URL}/api/algorithms/list`)
      .then(res => res.json())
      .then(data => {
        if (data.status === 'success') {
          setAlgorithms(data.algorithms);
        }
      })
      .catch(err => console.error('获取算法列表失败:', err));
  }, []);

  // 执行分析
  const handleAnalyze = async () => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`${API_URL}/api/algorithms/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          algorithm_id: selectedAlgorithm,
          question: question,
          options: options
        })
      });

      const data = await response.json();
      
      if (data.status === 'success') {
        setResult(data.result);
      } else {
        alert('分析失败: ' + data.message);
      }
    } catch (error) {
      alert('请求失败: ' + error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1>🧮 决策分析工具</h1>

      {/* 选择算法 */}
      <div style={{ marginBottom: '20px' }}>
        <label>选择算法：</label>
        <select 
          value={selectedAlgorithm} 
          onChange={(e) => setSelectedAlgorithm(e.target.value)}
          style={{ marginLeft: '10px', padding: '5px' }}
        >
          {algorithms.map(algo => (
            <option key={algo.id} value={algo.id}>
              {algo.name} (v{algo.version})
            </option>
          ))}
        </select>
      </div>

      {/* 输入问题 */}
      <div style={{ marginBottom: '20px' }}>
        <label>决策问题：</label>
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="例如：选择哪款笔记本电脑？"
          style={{ width: '100%', padding: '8px', marginTop: '5px' }}
        />
      </div>

      {/* 选项列表 */}
      <div style={{ marginBottom: '20px' }}>
        <label>选项（JSON格式）：</label>
        <textarea
          value={JSON.stringify(options, null, 2)}
          onChange={(e) => {
            try {
              setOptions(JSON.parse(e.target.value));
            } catch (err) {
              // 忽略JSON解析错误
            }
          }}
          rows={10}
          style={{ width: '100%', padding: '8px', marginTop: '5px', fontFamily: 'monospace' }}
        />
      </div>

      {/* 分析按钮 */}
      <button 
        onClick={handleAnalyze}
        disabled={loading}
        style={{ 
          padding: '10px 20px', 
          fontSize: '16px', 
          cursor: loading ? 'not-allowed' : 'pointer',
          backgroundColor: '#007bff',
          color: 'white',
          border: 'none',
          borderRadius: '5px'
        }}
      >
        {loading ? '分析中...' : '开始分析'}
      </button>

      {/* 显示结果 */}
      {result && (
        <div style={{ marginTop: '30px', padding: '20px', backgroundColor: '#f8f9fa', borderRadius: '5px' }}>
          <h2>📊 分析结果</h2>
          
          <div style={{ marginBottom: '15px' }}>
            <strong>推荐：</strong>
            <span style={{ fontSize: '20px', color: '#28a745', marginLeft: '10px' }}>
              {result.recommendation}
            </span>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <strong>得分：</strong>
            <ul>
              {Object.entries(result.scores).map(([option, score]) => (
                <li key={option}>
                  {option}: <strong>{typeof score === 'number' ? score.toFixed(2) : score}</strong>
                </li>
              ))}
            </ul>
          </div>

          <div style={{ marginBottom: '15px' }}>
            <strong>总结：</strong>
            <p>{result.summary}</p>
          </div>

          {result.analysis && (
            <div>
              <strong>详细分析：</strong>
              <pre style={{ 
                whiteSpace: 'pre-wrap', 
                backgroundColor: 'white', 
                padding: '10px',
                borderRadius: '5px',
                marginTop: '10px'
              }}>
                {result.analysis}
              </pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default AlgorithmAnalysis;

