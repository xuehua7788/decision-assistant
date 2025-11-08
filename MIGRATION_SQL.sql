-- ============================================
-- 数据库迁移SQL脚本
-- 目的：将 accepted_strategies 表合并到 users 表
-- ============================================

-- 步骤1: 在 users 表添加 accepted_strategies 字段
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS accepted_strategies JSONB DEFAULT '[]'::jsonb;

-- 步骤2: 将 bbb 用户的策略迁移到 users 表
UPDATE users 
SET accepted_strategies = (
    SELECT jsonb_agg(
        jsonb_build_object(
            'strategy_id', strategy_id,
            'symbol', symbol,
            'company_name', company_name,
            'investment_style', investment_style,
            'recommendation', recommendation,
            'target_price', target_price,
            'stop_loss', stop_loss,
            'position_size', position_size,
            'score', score,
            'strategy_text', strategy_text,
            'analysis_summary', analysis_summary,
            'current_price', current_price,
            'option_strategy', option_strategy,
            'created_at', created_at,
            'status', status
        )
    )
    FROM accepted_strategies
    WHERE accepted_strategies.username = users.username
)
WHERE username = 'bbb';

-- 步骤3: 验证迁移结果
SELECT 
    username,
    jsonb_array_length(accepted_strategies) as strategy_count
FROM users
WHERE username = 'bbb';

-- 步骤4: 删除旧表（确认迁移成功后再执行）
-- DROP TABLE accepted_strategies CASCADE;


