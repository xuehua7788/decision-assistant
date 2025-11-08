-- 资金管理系统数据库迁移脚本
-- 创建日期: 2025-11-08

-- 1. 账户管理表
CREATE TABLE IF NOT EXISTS accounts (
    user_id INTEGER PRIMARY KEY REFERENCES users(id),
    total_cash DECIMAL(15, 2) NOT NULL DEFAULT 100000.00,  -- 初始10万
    margin_occupied DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 保证金占用
    available_cash DECIMAL(15, 2) NOT NULL DEFAULT 100000.00,  -- 可用现金
    position_value DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 持仓市值
    position_count INTEGER NOT NULL DEFAULT 0,  -- 持仓数量
    total_pnl DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 累计盈亏
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. 策略推荐表（双策略）
CREATE TABLE IF NOT EXISTS strategies (
    strategy_id VARCHAR(100) PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL,
    company_name VARCHAR(100),
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notional_value DECIMAL(15, 2) NOT NULL,  -- 名义本金（两策略相同）
    
    -- 期权策略字段
    option_type VARCHAR(10),  -- CALL/PUT
    strike_price DECIMAL(10, 2),  -- 执行价
    expiry_date DATE,  -- 到期日
    option_premium DECIMAL(10, 2),  -- 期权费
    option_delta DECIMAL(5, 4),  -- Delta值
    
    -- 股票策略字段
    stock_amount DECIMAL(15, 2),  -- 股票金额 = delta × 名义本金
    stock_margin DECIMAL(15, 2),  -- 保证金 = 股票金额 × 10%
    
    -- 市场状态（ML特征）
    current_price DECIMAL(10, 2),
    volatility DECIMAL(8, 4),  -- 波动率
    rsi DECIMAL(5, 2),  -- RSI指标
    volume_ratio DECIMAL(8, 4),  -- 成交量比
    
    -- 完整策略数据（JSON）
    option_strategy_detail JSONB,  -- 期权策略完整数据
    stock_strategy_detail JSONB,   -- 股票策略完整数据
    market_analysis JSONB  -- 市场分析
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_strategies_symbol ON strategies(symbol);
CREATE INDEX IF NOT EXISTS idx_strategies_create_time ON strategies(create_time);

-- 3. 持仓表（A/B对照组）
CREATE TABLE IF NOT EXISTS positions (
    position_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    strategy_id VARCHAR(100) NOT NULL REFERENCES strategies(strategy_id),
    decision_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    user_choice INTEGER NOT NULL,  -- 1=期权, 2=股票
    
    -- A组（实盘）
    actual_type VARCHAR(10) NOT NULL,  -- OPTION/STOCK
    actual_cost DECIMAL(15, 2) NOT NULL,  -- 实际成本
    actual_current_value DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 当前价值
    actual_pnl DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 浮动盈亏
    stop_loss DECIMAL(10, 2),  -- 止损价（股票用）
    take_profit DECIMAL(10, 2),  -- 止盈价（股票用）
    
    -- B组（虚拟）
    virtual_type VARCHAR(10) NOT NULL,  -- OPTION/STOCK
    virtual_cost DECIMAL(15, 2) NOT NULL,  -- 虚拟成本
    virtual_current_value DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 虚拟价值
    virtual_pnl DECIMAL(15, 2) NOT NULL DEFAULT 0.00,  -- 虚拟盈亏
    
    -- 状态
    status VARCHAR(10) NOT NULL DEFAULT 'OPEN',  -- OPEN/CLOSED
    close_time TIMESTAMP,  -- 平仓时间
    close_trigger VARCHAR(20),  -- MANUAL/STOP_LOSS/TAKE_PROFIT/EXPIRY
    
    -- ML特征（决策时记录）
    market_state JSONB,  -- 市场状态特征
    account_state JSONB,  -- 账户状态特征
    
    -- ML标签（平仓时记录）
    actual_return DECIMAL(8, 4),  -- 实际收益率
    virtual_return DECIMAL(8, 4),  -- 虚拟收益率
    regret_value DECIMAL(8, 4),  -- 后悔值
    optimal_choice INTEGER,  -- 是否最优选择 1/0
    holding_days INTEGER  -- 持有天数
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_positions_user_id ON positions(user_id);
CREATE INDEX IF NOT EXISTS idx_positions_strategy_id ON positions(strategy_id);
CREATE INDEX IF NOT EXISTS idx_positions_status ON positions(status);
CREATE INDEX IF NOT EXISTS idx_positions_decision_time ON positions(decision_time);

-- 4. 资金流水表
CREATE TABLE IF NOT EXISTS transactions (
    transaction_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    position_id INTEGER REFERENCES positions(position_id),
    type VARCHAR(20) NOT NULL,  -- OPEN/CLOSE/MARGIN_RETURN
    amount DECIMAL(15, 2) NOT NULL,  -- 正=入账，负=出账
    balance_after DECIMAL(15, 2) NOT NULL,  -- 交易后余额
    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_transactions_user_id ON transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_transactions_position_id ON transactions(position_id);
CREATE INDEX IF NOT EXISTS idx_transactions_create_time ON transactions(create_time);

-- 创建触发器：更新账户的last_update时间
CREATE OR REPLACE FUNCTION update_account_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.last_update = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_account_timestamp
BEFORE UPDATE ON accounts
FOR EACH ROW
EXECUTE FUNCTION update_account_timestamp();

-- 初始化现有用户的账户（给每个用户10万初始资金）
INSERT INTO accounts (user_id, total_cash, available_cash)
SELECT id, 100000.00, 100000.00
FROM users
ON CONFLICT (user_id) DO NOTHING;

COMMENT ON TABLE accounts IS '账户资金管理表';
COMMENT ON TABLE strategies IS '双策略推荐表（期权+股票）';
COMMENT ON TABLE positions IS '持仓表（A/B对照组）';
COMMENT ON TABLE transactions IS '资金流水表';

