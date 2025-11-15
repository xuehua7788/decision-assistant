#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
设置机器学习数据库表和视图
"""

import psycopg2
import os

# 直接使用数据库URL
DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

def get_db_connection():
    """获取数据库连接"""
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def setup_ml_database():
    """创建ML相关的表和视图"""
    conn = get_db_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return False
    
    try:
        cursor = conn.cursor()
        
        print("🔧 创建机器学习视图和表...")
        
        # 1. 创建训练数据视图
        print("\n1️⃣ 创建 ml_training_data 视图...")
        cursor.execute("""
            CREATE OR REPLACE VIEW ml_training_data AS
            SELECT 
                -- 标签
                p.user_choice,
                p.optimal_choice,
                
                -- 市场特征
                COALESCE((p.market_state->>'current_price')::FLOAT, s.current_price) as current_price,
                COALESCE((p.market_state->>'volatility')::FLOAT, s.volatility) as volatility,
                COALESCE((p.market_state->>'rsi')::FLOAT, s.rsi) as rsi,
                COALESCE((p.market_state->>'volume_ratio')::FLOAT, s.volume_ratio) as volume_ratio,
                
                -- 账户特征
                (p.account_state->>'available_cash')::FLOAT as available_cash,
                (p.account_state->>'position_count')::INT as position_count,
                (p.account_state->>'total_pnl')::FLOAT as total_pnl,
                (p.account_state->>'margin_occupied')::FLOAT as margin_occupied,
                
                -- 策略特征
                s.option_delta,
                s.option_premium,
                s.stock_margin,
                s.stock_amount,
                s.notional_value,
                s.strike_price,
                
                -- 用户画像
                COALESCE(up.risk_tolerance, 'moderate') as risk_tolerance,
                COALESCE(up.investment_style, 'balanced') as investment_style,
                COALESCE(up.option_experience, 'none') as option_experience,
                COALESCE(up.financial_knowledge, 'beginner') as financial_knowledge,
                COALESCE(up.confidence_level, 0.5) as confidence_level,
                COALESCE(up.decision_speed, 'moderate') as decision_speed,
                
                -- 结果特征
                p.actual_return,
                p.virtual_return,
                p.regret_value,
                p.holding_days,
                
                -- 元数据
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
            WHERE p.status = 'CLOSED'
            ORDER BY p.decision_time DESC
        """)
        print("✅ ml_training_data 视图创建成功")
        
        # 2. 创建模型预测结果表
        print("\n2️⃣ 创建 ml_predictions 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_predictions (
                id SERIAL PRIMARY KEY,
                position_id INTEGER REFERENCES positions(position_id),
                model_type VARCHAR(20) NOT NULL,
                model_version VARCHAR(50),
                
                predicted_choice INTEGER NOT NULL,
                prediction_confidence FLOAT,
                prediction_probabilities JSONB,
                
                actual_choice INTEGER,
                is_correct BOOLEAN,
                
                features_used JSONB,
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ml_predictions_position 
            ON ml_predictions(position_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ml_predictions_model 
            ON ml_predictions(model_type)
        """)
        print("✅ ml_predictions 表创建成功")
        
        # 3. 创建模型性能评估表
        print("\n3️⃣ 创建 ml_model_performance 表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ml_model_performance (
                id SERIAL PRIMARY KEY,
                model_type VARCHAR(20) NOT NULL,
                model_version VARCHAR(50),
                
                accuracy FLOAT,
                f1_score FLOAT,
                
                precision_option FLOAT,
                recall_option FLOAT,
                
                precision_stock FLOAT,
                recall_stock FLOAT,
                
                confusion_matrix JSONB,
                feature_importance JSONB,
                conditional_probabilities JSONB,
                
                training_samples INTEGER,
                test_samples INTEGER,
                train_test_split FLOAT,
                
                hyperparameters JSONB,
                
                trained_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ml_performance_model 
            ON ml_model_performance(model_type)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_ml_performance_trained 
            ON ml_model_performance(trained_at)
        """)
        print("✅ ml_model_performance 表创建成功")
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "="*60)
        print("✅ 机器学习数据库设置完成！")
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ 设置失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    setup_ml_database()

