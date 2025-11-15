-- 机器学习算法相关表
-- 用途：保存模型预测结果和性能评估

-- 1. 模型预测结果表
CREATE TABLE IF NOT EXISTS ml_predictions (
    id SERIAL PRIMARY KEY,
    position_id INTEGER REFERENCES positions(position_id),
    model_type VARCHAR(20) NOT NULL,  -- 'bayesian' / 'decision_tree'
    model_version VARCHAR(50),
    
    -- 预测结果
    predicted_choice INTEGER NOT NULL,  -- 1=期权, 2=股票
    prediction_confidence FLOAT,  -- 预测置信度 [0-1]
    prediction_probabilities JSONB,  -- {'option': 0.3, 'stock': 0.7}
    
    -- 实际结果
    actual_choice INTEGER,  -- 用户实际选择
    is_correct BOOLEAN,  -- 预测是否正确
    
    -- 特征快照（用于分析）
    features_used JSONB,  -- 使用的特征值
    
    -- 元数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ml_predictions_position ON ml_predictions(position_id);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_model ON ml_predictions(model_type);
CREATE INDEX IF NOT EXISTS idx_ml_predictions_correct ON ml_predictions(is_correct);

COMMENT ON TABLE ml_predictions IS '模型预测结果表：保存每次预测的详细信息';


-- 2. 模型性能评估表
CREATE TABLE IF NOT EXISTS ml_model_performance (
    id SERIAL PRIMARY KEY,
    model_type VARCHAR(20) NOT NULL,  -- 'bayesian' / 'decision_tree'
    model_version VARCHAR(50),
    
    -- 整体性能指标
    accuracy FLOAT,  -- 准确率
    f1_score FLOAT,  -- F1分数
    
    -- 期权类别指标
    precision_option FLOAT,  -- 精确率
    recall_option FLOAT,  -- 召回率
    
    -- 股票类别指标
    precision_stock FLOAT,
    recall_stock FLOAT,
    
    -- 混淆矩阵
    confusion_matrix JSONB,  -- {'TP': 10, 'FP': 2, 'TN': 8, 'FN': 3}
    
    -- 特征重要性（决策树）
    feature_importance JSONB,  -- {'volatility': 0.3, 'rsi': 0.25, ...}
    
    -- 条件概率（贝叶斯）
    conditional_probabilities JSONB,  -- P(feature|class)
    
    -- 训练信息
    training_samples INTEGER,  -- 训练样本数
    test_samples INTEGER,  -- 测试样本数
    train_test_split FLOAT,  -- 训练/测试比例
    
    -- 超参数
    hyperparameters JSONB,  -- 模型超参数
    
    -- 元数据
    trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX IF NOT EXISTS idx_ml_performance_model ON ml_model_performance(model_type);
CREATE INDEX IF NOT EXISTS idx_ml_performance_trained ON ml_model_performance(trained_at);

COMMENT ON TABLE ml_model_performance IS '模型性能评估表：保存模型训练和评估指标';


-- 3. 特征工程配置表（可选）
CREATE TABLE IF NOT EXISTS ml_feature_config (
    id SERIAL PRIMARY KEY,
    feature_name VARCHAR(100) UNIQUE NOT NULL,
    feature_type VARCHAR(20) NOT NULL,  -- 'numerical' / 'categorical'
    source_table VARCHAR(50),  -- 来源表
    source_column VARCHAR(50),  -- 来源字段
    
    -- 离散化配置（贝叶斯用）
    discretization_method VARCHAR(20),  -- 'equal_width' / 'equal_frequency' / 'custom'
    discretization_bins JSONB,  -- [0, 0.3, 0.6, 1.0] 或 {'low': [0, 0.3], ...}
    
    -- 编码配置（决策树用）
    encoding_method VARCHAR(20),  -- 'label' / 'onehot'
    encoding_mapping JSONB,  -- {'conservative': 0, 'moderate': 1, 'aggressive': 2}
    
    -- 缺失值处理
    missing_value_strategy VARCHAR(20),  -- 'mean' / 'median' / 'mode' / 'constant'
    missing_value_fill VARCHAR(50),
    
    -- 元数据
    is_active BOOLEAN DEFAULT TRUE,
    importance_score FLOAT,  -- 特征重要性
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ml_feature_active ON ml_feature_config(is_active);

COMMENT ON TABLE ml_feature_config IS '特征工程配置表：定义特征提取和预处理规则';

