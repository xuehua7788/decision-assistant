#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动连接Render PostgreSQL并创建用户画像表
"""

import psycopg2
from datetime import datetime

# Render PostgreSQL连接信息（从你的截图）
DATABASE_URL = "postgresql://decision_user:YOUR_PASSWORD@dpg-d3otin3ipnbc739gk7g-a.singapore-postgres.render.com:5432/decision_assistant_0981"

print("=" * 70)
print("自动创建用户画像数据库表")
print("=" * 70)
print()

# 提示用户输入密码
print("请输入Render PostgreSQL密码（从Dashboard复制）:")
password = input("密码: ").strip()

if not password:
    print("❌ 密码不能为空")
    exit(1)

# 替换密码
DATABASE_URL = DATABASE_URL.replace("YOUR_PASSWORD", password)

print()
print("正在连接数据库...")

try:
    # 连接数据库
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("✅ 数据库连接成功")
    print()
    
    # 创建用户画像表
    print("1. 创建用户画像表 (user_profiles)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            
            -- 投资偏好
            risk_tolerance VARCHAR(20),
            investment_style VARCHAR(20),
            time_horizon VARCHAR(20),
            
            -- 行为特征
            chat_frequency INTEGER,
            decision_speed VARCHAR(20),
            information_depth VARCHAR(20),
            
            -- 知识水平
            financial_knowledge VARCHAR(20),
            option_experience VARCHAR(20),
            
            -- 情绪特征
            sentiment_tendency VARCHAR(20),
            confidence_level FLOAT,
            
            -- AI分析结果
            ai_analysis JSONB,
            analysis_summary TEXT,
            
            -- 元数据
            last_analyzed_at TIMESTAMP,
            analysis_period_start TIMESTAMP,
            analysis_period_end TIMESTAMP,
            total_messages_analyzed INTEGER DEFAULT 0,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_risk_tolerance ON user_profiles(risk_tolerance);
        CREATE INDEX IF NOT EXISTS idx_user_profiles_last_analyzed ON user_profiles(last_analyzed_at);
    """)
    print("   ✅ 用户画像表创建成功")
    
    # 创建策略推荐历史表
    print("\n2. 创建策略推荐历史表 (strategy_recommendations)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_recommendations (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            
            -- 用户意图
            user_intent JSONB,
            
            -- 用户画像
            user_profile_snapshot JSONB,
            
            -- 推荐策略
            strategy_type VARCHAR(50),
            strategy_name VARCHAR(100),
            strategy_parameters JSONB,
            confidence_score FLOAT,
            
            -- 个性化调整
            adjustment_reason TEXT,
            original_parameters JSONB,
            adjusted_parameters JSONB,
            personalization_notes TEXT,
            
            -- 结果追踪
            user_accepted BOOLEAN,
            user_feedback TEXT,
            actual_outcome JSONB,
            
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        
        CREATE INDEX IF NOT EXISTS idx_strategy_recommendations_username ON strategy_recommendations(username);
        CREATE INDEX IF NOT EXISTS idx_strategy_recommendations_created_at ON strategy_recommendations(created_at);
        CREATE INDEX IF NOT EXISTS idx_strategy_recommendations_strategy_type ON strategy_recommendations(strategy_type);
    """)
    print("   ✅ 策略推荐历史表创建成功")
    
    # 增强聊天消息表
    print("\n3. 增强聊天消息表 (chat_messages)...")
    cursor.execute("""
        -- 创建表（如果不存在）
        CREATE TABLE IF NOT EXISTS chat_messages (
            id SERIAL PRIMARY KEY,
            session_id INTEGER,
            role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata JSONB DEFAULT '{}'
        );
        
        -- 添加新字段
        DO $$ 
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='chat_messages' AND column_name='sentiment') THEN
                ALTER TABLE chat_messages ADD COLUMN sentiment VARCHAR(20);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='chat_messages' AND column_name='intent_category') THEN
                ALTER TABLE chat_messages ADD COLUMN intent_category VARCHAR(50);
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='chat_messages' AND column_name='keywords') THEN
                ALTER TABLE chat_messages ADD COLUMN keywords JSONB;
            END IF;
            
            IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                          WHERE table_name='chat_messages' AND column_name='analyzed') THEN
                ALTER TABLE chat_messages ADD COLUMN analyzed BOOLEAN DEFAULT FALSE;
            END IF;
        END $$;
        
        CREATE INDEX IF NOT EXISTS idx_chat_messages_sentiment ON chat_messages(sentiment);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_intent_category ON chat_messages(intent_category);
        CREATE INDEX IF NOT EXISTS idx_chat_messages_analyzed ON chat_messages(analyzed);
    """)
    print("   ✅ 聊天消息表增强成功")
    
    # 确保聊天会话表存在
    print("\n4. 确保聊天会话表存在 (chat_sessions)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chat_sessions (
            id SERIAL PRIMARY KEY,
            session_id VARCHAR(100) UNIQUE NOT NULL,
            username VARCHAR(100),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE,
            metadata JSONB DEFAULT '{}'
        );
        
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
        CREATE INDEX IF NOT EXISTS idx_chat_sessions_username ON chat_sessions(username);
    """)
    print("   ✅ 聊天会话表确认")
    
    # 提交更改
    conn.commit()
    
    # 验证表创建
    print("\n5. 验证表结构...")
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        AND table_name IN ('user_profiles', 'strategy_recommendations', 'chat_messages', 'chat_sessions')
        ORDER BY table_name;
    """)
    tables = cursor.fetchall()
    print(f"   已创建/确认的表: {len(tables)}个")
    for table in tables:
        print(f"   - {table[0]}")
    
    cursor.close()
    conn.close()
    
    print()
    print("🎉 所有表创建/更新成功！")
    print()
    print("下一步:")
    print("1. 运行: python auto_test_render.py")
    print("2. 运行: python check_user_profile.py")
    print()
    
except Exception as e:
    print(f"\n❌ 创建表失败: {str(e)}")
    import traceback
    traceback.print_exc()
    exit(1)


