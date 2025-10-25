#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建用户画像相关数据库表
扩展现有数据库结构，支持AI #3用户画像分析
"""

import os
import psycopg2
from datetime import datetime

def create_profile_tables():
    """创建用户画像相关表"""
    
    # 从环境变量获取数据库连接
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("❌ DATABASE_URL 环境变量未设置")
        print("请在Render Dashboard设置环境变量或本地.env文件中配置")
        return False
    
    try:
        print("=== 创建用户画像数据库表 ===\n")
        
        # 连接数据库
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 1. 用户画像表
        print("1. 创建用户画像表 (user_profiles)...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id SERIAL PRIMARY KEY,
                user_id INTEGER UNIQUE,
                username VARCHAR(100) UNIQUE NOT NULL,
                
                -- 投资偏好
                risk_tolerance VARCHAR(20),              -- conservative/moderate/aggressive
                investment_style VARCHAR(20),            -- value/growth/momentum/contrarian
                time_horizon VARCHAR(20),                -- short/medium/long
                
                -- 行为特征
                chat_frequency INTEGER,                  -- 聊天频率（次/周）
                decision_speed VARCHAR(20),              -- fast/moderate/slow
                information_depth VARCHAR(20),           -- shallow/moderate/deep
                
                -- 知识水平
                financial_knowledge VARCHAR(20),         -- beginner/intermediate/advanced
                option_experience VARCHAR(20),           -- none/basic/experienced
                
                -- 情绪特征
                sentiment_tendency VARCHAR(20),          -- optimistic/pessimistic/balanced
                confidence_level FLOAT,                  -- 0.0-1.0
                
                -- AI #3 分析结果
                ai_analysis JSONB,                       -- 完整的AI分析JSON
                analysis_summary TEXT,                   -- 分析摘要
                
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
        
        # 2. 策略推荐历史表
        print("\n2. 创建策略推荐历史表 (strategy_recommendations)...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS strategy_recommendations (
                id SERIAL PRIMARY KEY,
                username VARCHAR(100) NOT NULL,
                
                -- 用户意图（AI #1）
                user_intent JSONB,                       -- 实时意图分析
                
                -- 用户画像（AI #3）
                user_profile_snapshot JSONB,             -- 当时的用户画像快照
                
                -- 推荐策略
                strategy_type VARCHAR(50),               -- 策略类型
                strategy_name VARCHAR(100),              -- 策略名称
                strategy_parameters JSONB,               -- 策略参数
                confidence_score FLOAT,                  -- 置信度
                
                -- 个性化调整
                adjustment_reason TEXT,                  -- 调整原因
                original_parameters JSONB,               -- 原始参数
                adjusted_parameters JSONB,               -- 调整后参数
                personalization_notes TEXT,              -- 个性化说明
                
                -- 结果追踪
                user_accepted BOOLEAN,                   -- 用户是否接受
                user_feedback TEXT,                      -- 用户反馈
                actual_outcome JSONB,                    -- 实际结果（如果有）
                
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            
            CREATE INDEX IF NOT EXISTS idx_strategy_recommendations_username ON strategy_recommendations(username);
            CREATE INDEX IF NOT EXISTS idx_strategy_recommendations_created_at ON strategy_recommendations(created_at);
            CREATE INDEX IF NOT EXISTS idx_strategy_recommendations_strategy_type ON strategy_recommendations(strategy_type);
        """)
        print("   ✅ 策略推荐历史表创建成功")
        
        # 3. 增强聊天消息表（添加分析字段）
        print("\n3. 增强聊天消息表 (chat_messages)...")
        cursor.execute("""
            -- 检查表是否存在
            CREATE TABLE IF NOT EXISTS chat_messages (
                id SERIAL PRIMARY KEY,
                session_id INTEGER,
                role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata JSONB DEFAULT '{}'
            );
            
            -- 添加新字段（如果不存在）
            DO $$ 
            BEGIN
                -- 情绪分析
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='chat_messages' AND column_name='sentiment') THEN
                    ALTER TABLE chat_messages ADD COLUMN sentiment VARCHAR(20);
                END IF;
                
                -- 意图分类
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='chat_messages' AND column_name='intent_category') THEN
                    ALTER TABLE chat_messages ADD COLUMN intent_category VARCHAR(50);
                END IF;
                
                -- 关键词
                IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                              WHERE table_name='chat_messages' AND column_name='keywords') THEN
                    ALTER TABLE chat_messages ADD COLUMN keywords JSONB;
                END IF;
                
                -- 是否已分析
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
        
        # 4. 创建聊天会话表（如果不存在）
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
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("\n🎉 所有表创建/更新成功！")
        print("\n📊 数据库准备完成，可以开始使用用户画像功能")
        return True
        
    except Exception as e:
        print(f"\n❌ 创建表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("用户画像数据库表创建脚本")
    print("=" * 60)
    print()
    
    success = create_profile_tables()
    
    if success:
        print("\n✅ 数据库表结构创建完成")
        print("\n下一步:")
        print("1. 确保环境变量 DATABASE_URL 已设置")
        print("2. 确保环境变量 DEEPSEEK_API_KEY 已设置")
        print("3. 运行: python ai_profile_analyzer.py 测试AI #3")
    else:
        print("\n❌ 数据库表创建失败，请检查:")
        print("1. DATABASE_URL 环境变量是否正确")
        print("2. 数据库连接是否正常")
        print("3. 数据库权限是否足够")

