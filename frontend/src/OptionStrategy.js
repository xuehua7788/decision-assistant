import React, { useRef, useEffect } from 'react';
import { Chart, registerables } from 'chart.js';

// Register Chart.js components
Chart.register(...registerables);

const OptionStrategy = ({ optionResult, onClose }) => {
  const chartRef = useRef(null);
  const chartInstance = useRef(null);

  useEffect(() => {
    // 创建图表
    if (chartRef.current && optionResult?.strategy?.payoff_data) {
      // 销毁之前的图表实例
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }

      const ctx = chartRef.current.getContext('2d');
      const payoffData = optionResult.strategy.payoff_data;

      chartInstance.current = new Chart(ctx, {
        type: 'line',
        data: {
          labels: payoffData.map(d => d.price.toFixed(2)),
          datasets: [{
            label: 'Profit/Loss ($)',
            data: payoffData.map(d => d.payoff),
            borderColor: payoffData.map(d => d.payoff >= 0 ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)'),
            backgroundColor: 'rgba(75, 192, 192, 0.1)',
            borderWidth: 2,
            pointRadius: 0,
            fill: true,
            segment: {
              borderColor: ctx => {
                const value = ctx.p1.parsed.y;
                return value >= 0 ? 'rgb(75, 192, 192)' : 'rgb(255, 99, 132)';
              }
            }
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: {
            legend: {
              display: true,
              position: 'top',
            },
            title: {
              display: true,
              text: 'Option Strategy Payoff Diagram',
              font: {
                size: 16
              }
            },
            tooltip: {
              mode: 'index',
              intersect: false,
              callbacks: {
                label: function(context) {
                  let label = context.dataset.label || '';
                  if (label) {
                    label += ': ';
                  }
                  if (context.parsed.y !== null) {
                    label += '$' + context.parsed.y.toFixed(2);
                  }
                  return label;
                }
              }
            }
          },
          scales: {
            x: {
              type: 'category',
              title: {
                display: true,
                text: 'Stock Price at Expiry ($)',
                font: {
                  size: 14
                }
              },
              ticks: {
                maxTicksLimit: 10,
                callback: function(value, index) {
                  // 只显示部分标签以避免拥挤
                  if (index % 10 === 0) {
                    return '$' + this.getLabelForValue(value);
                  }
                  return '';
                }
              }
            },
            y: {
              title: {
                display: true,
                text: 'Profit/Loss ($)',
                font: {
                  size: 14
                }
              },
              ticks: {
                callback: function(value) {
                  return '$' + value.toFixed(0);
                }
              },
              grid: {
                color: (context) => {
                  if (context.tick.value === 0) {
                    return 'rgba(0, 0, 0, 0.3)';
                  }
                  return 'rgba(0, 0, 0, 0.1)';
                },
                lineWidth: (context) => {
                  if (context.tick.value === 0) {
                    return 2;
                  }
                  return 1;
                }
              }
            }
          },
          interaction: {
            mode: 'nearest',
            axis: 'x',
            intersect: false
          }
        }
      });
    }

    // 清理函数
    return () => {
      if (chartInstance.current) {
        chartInstance.current.destroy();
      }
    };
  }, [optionResult]);

  if (!optionResult || !optionResult.strategy) {
    return (
      <div style={styles.overlay}>
        <div style={styles.modal}>
          <h2>错误</h2>
          <p>无法加载期权策略数据</p>
          <button onClick={onClose} style={styles.closeButton}>
            关闭
          </button>
        </div>
      </div>
    );
  }

  const { parsed_intent, strategy } = optionResult;
  const { parameters, metrics } = strategy;

  // 方向映射
  const directionMap = {
    'bullish': '看涨 📈',
    'bearish': '看跌 📉',
    'neutral': '震荡 ↔️'
  };

  return (
    <div style={styles.overlay} onClick={onClose}>
      <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
        {/* 标题栏 */}
        <div style={styles.header}>
          <h2 style={styles.title}>
            📊 期权策略推荐
          </h2>
          <button onClick={onClose} style={styles.closeButtonTop}>
            ✕
          </button>
        </div>

        <div style={styles.content}>
          {/* 意图识别部分 */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>🎯 识别的投资意图</h3>
            <div style={styles.intentGrid}>
              <div style={styles.intentItem}>
                <span style={styles.intentLabel}>标的:</span>
                <span style={styles.intentValue}>
                  {parsed_intent.ticker || '通用策略'}
                </span>
              </div>
              <div style={styles.intentItem}>
                <span style={styles.intentLabel}>方向:</span>
                <span style={styles.intentValue}>
                  {directionMap[parsed_intent.direction] || parsed_intent.direction}
                </span>
              </div>
              <div style={styles.intentItem}>
                <span style={styles.intentLabel}>强度:</span>
                <span style={styles.intentValue}>
                  {parsed_intent.strength || 'moderate'}
                </span>
              </div>
              <div style={styles.intentItem}>
                <span style={styles.intentLabel}>时间:</span>
                <span style={styles.intentValue}>
                  {parsed_intent.timeframe || 'short'}
                </span>
              </div>
              <div style={styles.intentItem}>
                <span style={styles.intentLabel}>风险偏好:</span>
                <span style={styles.intentValue}>
                  {parsed_intent.risk_profile || 'balanced'}
                </span>
              </div>
              <div style={styles.intentItem}>
                <span style={styles.intentLabel}>置信度:</span>
                <span style={{...styles.intentValue, color: parsed_intent.confidence > 0.7 ? '#4CAF50' : '#FF9800'}}>
                  {(parsed_intent.confidence * 100).toFixed(0)}%
                </span>
              </div>
            </div>
          </div>

          {/* 策略推荐部分 */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>💡 推荐策略</h3>
            <div style={styles.strategyInfo}>
              <h4 style={styles.strategyName}>{strategy.name}</h4>
              <p style={styles.strategyDesc}>{strategy.description}</p>
              <div style={styles.riskBadge}>
                风险等级: <strong>{strategy.risk_level}</strong>
              </div>
            </div>
          </div>

          {/* 策略参数 */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>📋 策略参数</h3>
            <div style={styles.paramsGrid}>
              <div style={styles.paramItem}>
                <span style={styles.paramLabel}>当前股价:</span>
                <span style={styles.paramValue}>${parameters.current_price.toFixed(2)}</span>
              </div>
              {parameters.buy_strike && (
                <div style={styles.paramItem}>
                  <span style={styles.paramLabel}>买入执行价:</span>
                  <span style={styles.paramValue}>${parameters.buy_strike.toFixed(2)}</span>
                </div>
              )}
              {parameters.sell_strike && (
                <div style={styles.paramItem}>
                  <span style={styles.paramLabel}>卖出执行价:</span>
                  <span style={styles.paramValue}>${parameters.sell_strike.toFixed(2)}</span>
                </div>
              )}
              {parameters.premium_paid && (
                <div style={styles.paramItem}>
                  <span style={styles.paramLabel}>支付权利金:</span>
                  <span style={styles.paramValue}>${parameters.premium_paid.toFixed(2)}</span>
                </div>
              )}
              {parameters.premium_received && (
                <div style={styles.paramItem}>
                  <span style={styles.paramLabel}>收到权利金:</span>
                  <span style={styles.paramValue}>${parameters.premium_received.toFixed(2)}</span>
                </div>
              )}
              <div style={styles.paramItem}>
                <span style={styles.paramLabel}>到期时间:</span>
                <span style={styles.paramValue}>{parameters.expiry}</span>
              </div>
            </div>
          </div>

          {/* 风险指标 */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>⚠️ 风险指标</h3>
            <div style={styles.metricsGrid}>
              <div style={{...styles.metricItem, ...styles.metricGain}}>
                <div style={styles.metricLabel}>最大收益</div>
                <div style={styles.metricValue}>
                  {metrics.max_gain >= 999999 ? '无限 ∞' : `$${metrics.max_gain.toFixed(2)}`}
                </div>
              </div>
              <div style={{...styles.metricItem, ...styles.metricLoss}}>
                <div style={styles.metricLabel}>最大损失</div>
                <div style={styles.metricValue}>${metrics.max_loss.toFixed(2)}</div>
              </div>
              <div style={styles.metricItem}>
                <div style={styles.metricLabel}>盈亏平衡点</div>
                <div style={styles.metricValue}>${metrics.breakeven.toFixed(2)}</div>
              </div>
              <div style={styles.metricItem}>
                <div style={styles.metricLabel}>成功概率</div>
                <div style={styles.metricValue}>{metrics.probability}</div>
              </div>
            </div>
          </div>

          {/* Payoff 图表 */}
          <div style={styles.section}>
            <h3 style={styles.sectionTitle}>📈 Payoff 曲线图</h3>
            <div style={styles.chartContainer}>
              <canvas ref={chartRef} />
            </div>
          </div>
        </div>

        {/* 底部按钮 */}
        <div style={styles.footer}>
          <button onClick={onClose} style={styles.closeButton}>
            关闭
          </button>
        </div>
      </div>
    </div>
  );
};

// 样式对象
const styles = {
  overlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000,
    padding: '20px',
    overflowY: 'auto'
  },
  modal: {
    backgroundColor: 'white',
    borderRadius: '12px',
    width: '95%',
    maxWidth: '1000px',
    maxHeight: '90vh',
    display: 'flex',
    flexDirection: 'column',
    boxShadow: '0 10px 40px rgba(0, 0, 0, 0.3)'
  },
  header: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '20px 24px',
    borderBottom: '1px solid #e0e0e0',
    backgroundColor: '#f8f9fa'
  },
  title: {
    margin: 0,
    fontSize: '24px',
    color: '#333'
  },
  closeButtonTop: {
    background: 'none',
    border: 'none',
    fontSize: '28px',
    cursor: 'pointer',
    color: '#666',
    padding: '0',
    width: '32px',
    height: '32px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: '50%',
    transition: 'background-color 0.2s',
  },
  content: {
    padding: '24px',
    overflowY: 'auto',
    flex: 1
  },
  section: {
    marginBottom: '24px',
    padding: '16px',
    backgroundColor: '#f8f9fa',
    borderRadius: '8px',
    border: '1px solid #e0e0e0'
  },
  sectionTitle: {
    margin: '0 0 16px 0',
    fontSize: '18px',
    color: '#333',
    fontWeight: '600'
  },
  intentGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '12px'
  },
  intentItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '8px 12px',
    backgroundColor: 'white',
    borderRadius: '6px',
    border: '1px solid #e0e0e0'
  },
  intentLabel: {
    color: '#666',
    fontWeight: '500'
  },
  intentValue: {
    color: '#333',
    fontWeight: '600'
  },
  strategyInfo: {
    backgroundColor: 'white',
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid #e0e0e0'
  },
  strategyName: {
    margin: '0 0 8px 0',
    fontSize: '20px',
    color: '#2196F3'
  },
  strategyDesc: {
    margin: '0 0 12px 0',
    color: '#666',
    lineHeight: '1.5'
  },
  riskBadge: {
    display: 'inline-block',
    padding: '6px 12px',
    backgroundColor: '#FFF3E0',
    border: '1px solid #FFB74D',
    borderRadius: '4px',
    color: '#F57C00',
    fontSize: '14px'
  },
  paramsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
    gap: '12px'
  },
  paramItem: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '10px 14px',
    backgroundColor: 'white',
    borderRadius: '6px',
    border: '1px solid #e0e0e0'
  },
  paramLabel: {
    color: '#666',
    fontSize: '14px'
  },
  paramValue: {
    color: '#333',
    fontWeight: '600',
    fontSize: '15px'
  },
  metricsGrid: {
    display: 'grid',
    gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
    gap: '16px'
  },
  metricItem: {
    padding: '16px',
    backgroundColor: 'white',
    borderRadius: '8px',
    border: '2px solid #e0e0e0',
    textAlign: 'center'
  },
  metricGain: {
    borderColor: '#4CAF50',
    backgroundColor: '#E8F5E9'
  },
  metricLoss: {
    borderColor: '#F44336',
    backgroundColor: '#FFEBEE'
  },
  metricLabel: {
    fontSize: '13px',
    color: '#666',
    marginBottom: '8px',
    fontWeight: '500'
  },
  metricValue: {
    fontSize: '20px',
    fontWeight: '700',
    color: '#333'
  },
  chartContainer: {
    height: '350px',
    backgroundColor: 'white',
    padding: '16px',
    borderRadius: '8px',
    border: '1px solid #e0e0e0'
  },
  footer: {
    padding: '16px 24px',
    borderTop: '1px solid #e0e0e0',
    display: 'flex',
    justifyContent: 'flex-end',
    backgroundColor: '#f8f9fa'
  },
  closeButton: {
    padding: '10px 24px',
    backgroundColor: '#2196F3',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    fontSize: '16px',
    cursor: 'pointer',
    fontWeight: '500',
    transition: 'background-color 0.2s'
  }
};

export default OptionStrategy;

