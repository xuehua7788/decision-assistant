#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
自动创建数据库表（从环境变量读取连接信息）
"""

import os
import psycopg2

# 从环境变量读取（Render会自动设置）
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("❌ DATABASE_URL 环境变量未设置")
    print()
    print("解决方法:")
    print("1. 在Render Dashboard设置DATABASE_URL环境变量")
    print("2. 或者手动设置:")
    print("   set DATABASE_URL=postgresql://user:pass@host:port/db")
    print("   python auto_create_tables_env.py")
    exit(1)

print("=" * 70)
print("自动创建用户画像数据库表")
print("=" * 70)
print()
print("✅ 从环境变量读取DATABASE_URL")
print()

try:
    # 连接数据库
    print("正在连接数据库...")
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
            risk_tolerance VARCHAR(20),
            investment_style VARCHAR(20),
            time_horizon VARCHAR(20),
            chat_frequency INTEGER,
            decision_speed VARCHAR(20),
            information_depth VARCHAR(20),
            financial_knowledge VARCHAR(20),
            option_experience VARCHAR(20),
            sentiment_tendency VARCHAR(20),
            confidence_level FLOAT,
            ai_analysis JSONB,
            analysis_summary TEXT,
            last_analyzed_at TIMESTAMP,
            total_messages_analyzed INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        CREATE INDEX IF NOT EXISTS idx_user_profiles_username ON user_profiles(username);
    """)
    print("   ✅ 成功")
    
    # 创建策略推荐表
    print("\n2. 创建策略推荐表 (strategy_recommendations)...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS strategy_recommendations (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) NOT NULL,
            user_intent JSONB,
            user_profile_snapshot JSONB,
            strategy_type VARCHAR(50),
            strategy_parameters JSONB,
            adjustment_reason TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    print("   ✅ 成功")
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print()
    print("🎉 所有表创建成功！")
    print()
    
except Exception as e:
    print(f"\n❌ 失败: {e}")
    exit(1)


