-- 创建机器学习训练数据视图
-- 用途：从现有表中提取特征，无需额外存储

CREATE OR REPLACE VIEW ml_training_data AS
SELECT 
    -- ========== 标签 ==========
    p.user_choice,                    -- 1=期权, 2=股票
    p.optimal_choice,                 -- 是否最优选择
    
    -- ========== 市场特征 ==========
    COALESCE((p.market_state->>'current_price')::FLOAT, s.current_price) as current_price,
    COALESCE((p.market_state->>'volatility')::FLOAT, s.volatility) as volatility,
    COALESCE((p.market_state->>'rsi')::FLOAT, s.rsi) as rsi,
    COALESCE((p.market_state->>'volume_ratio')::FLOAT, s.volume_ratio) as volume_ratio,
    
    -- ========== 账户特征 ==========
    (p.account_state->>'available_cash')::FLOAT as available_cash,
    (p.account_state->>'position_count')::INT as position_count,
    (p.account_state->>'total_pnl')::FLOAT as total_pnl,
    (p.account_state->>'margin_occupied')::FLOAT as margin_occupied,
    
    -- ========== 策略特征 ==========
    s.option_delta,
    s.option_premium,
    s.stock_margin,
    s.stock_amount,
    s.notional_value,
    s.strike_price,
    
    -- ========== 用户画像 ==========
    COALESCE(up.risk_tolerance, 'moderate') as risk_tolerance,
    COALESCE(up.investment_style, 'balanced') as investment_style,
    COALESCE(up.option_experience, 'none') as option_experience,
    COALESCE(up.financial_knowledge, 'beginner') as financial_knowledge,
    COALESCE(up.confidence_level, 0.5) as confidence_level,
    COALESCE(up.decision_speed, 'moderate') as decision_speed,
    
    -- ========== 结果特征（用于后验分析）==========
    p.actual_return,
    p.virtual_return,
    p.regret_value,
    p.holding_days,
    
    -- ========== 元数据 ==========
    p.position_id,
    p.user_id,
    u.username,
    s.symbol,
    p.decision_time,
    p.close_time,
    p.status
    
FROM positions p
JOIN strategies s ON p.strategy_id = s.strategy_id
JOIN users u ON p.user_id = u.id
LEFT JOIN user_profiles up ON u.username = up.username
WHERE p.status = 'CLOSED'  -- 只用已平仓的数据
ORDER BY p.decision_time DESC;

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_user_id_status ON positions(user_id, status);

COMMENT ON VIEW ml_training_data IS '机器学习训练数据视图：整合市场、账户、策略、用户画像特征';

