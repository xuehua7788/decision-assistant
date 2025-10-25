#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户画像集成辅助函数
用于在app.py中集成用户画像功能
"""

import os
import json
import psycopg2
from datetime import datetime, timedelta
from typing import Dict, List, Optional

def get_db_connection():
    """获取数据库连接"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        return None
    
    try:
        conn = psycopg2.connect(database_url)
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def load_user_profile_from_db(username: str) -> Optional[Dict]:
    """
    从数据库加载用户画像
    
    Args:
        username: 用户名
    
    Returns:
        用户画像字典，如果不存在返回None
    """
    conn = get_db_connection()
    if not conn:
        return None
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ai_analysis, last_analyzed_at, total_messages_analyzed
            FROM user_profiles
            WHERE username = %s
        """, (username,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0]:
            profile = json.loads(result[0]) if isinstance(result[0], str) else result[0]
            profile['last_analyzed_at'] = result[1].isoformat() if result[1] else None
            profile['total_messages_analyzed'] = result[2]
            return profile
        
        return None
        
    except Exception as e:
        print(f"加载用户画像失败: {e}")
        if conn:
            conn.close()
        return None


def load_chat_history_from_db(username: str, days: int = 30) -> List[Dict]:
    """
    从数据库加载聊天历史
    
    Args:
        username: 用户名
        days: 加载最近N天的记录
    
    Returns:
        聊天历史列表
    """
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cursor = conn.cursor()
        
        # 查询聊天记录（使用session_id，因为username字段可能不存在）
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute("""
            SELECT cm.role, cm.content, cm.created_at
            FROM chat_messages cm
            JOIN chat_sessions cs ON cm.session_id = cs.id
            WHERE cs.session_id = %s
            AND cm.created_at > %s
            ORDER BY cm.created_at ASC
        """, (username, cutoff_date))
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                "role": row[0],
                "content": row[1],
                "timestamp": row[2].isoformat() if row[2] else None
            })
        
        cursor.close()
        conn.close()
        
        return messages
        
    except Exception as e:
        print(f"加载聊天历史失败: {e}")
        if conn:
            conn.close()
        return []


def check_profile_freshness(username: str, max_age_days: int = 7) -> bool:
    """
    检查用户画像是否需要更新
    
    Args:
        username: 用户名
        max_age_days: 画像最大有效期（天）
    
    Returns:
        True表示画像新鲜，False表示需要更新
    """
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT last_analyzed_at
            FROM user_profiles
            WHERE username = %s
        """, (username,))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not result or not result[0]:
            return False
        
        last_analyzed = result[0]
        age = datetime.now() - last_analyzed
        
        return age.days < max_age_days
        
    except Exception as e:
        print(f"检查画像新鲜度失败: {e}")
        if conn:
            conn.close()
        return False


def trigger_profile_analysis_async(username: str):
    """
    异步触发用户画像分析
    （实际项目中应该使用Celery等任务队列）
    
    Args:
        username: 用户名
    """
    import threading
    
    def analyze():
        try:
            from ai_profile_analyzer import get_profile_analyzer
            
            # 加载聊天历史
            chat_history = load_chat_history_from_db(username, days=30)
            
            if len(chat_history) < 5:
                print(f"用户 {username} 聊天记录不足，跳过分析")
                return
            
            # 分析画像
            analyzer = get_profile_analyzer()
            profile = analyzer.analyze_user_profile(
                username=username,
                chat_history=chat_history,
                days=30
            )
            
            # 保存到数据库
            if profile.get('status') != 'error':
                conn = get_db_connection()
                if conn:
                    analyzer.update_user_profile_in_db(conn, username, profile)
                    conn.close()
                    print(f"✅ 用户 {username} 画像分析完成")
            
        except Exception as e:
            print(f"❌ 异步画像分析失败: {e}")
    
    # 启动后台线程
    thread = threading.Thread(target=analyze, daemon=True)
    thread.start()


def get_profile_summary(profile: Dict) -> str:
    """
    生成用户画像摘要（用于日志）
    
    Args:
        profile: 用户画像字典
    
    Returns:
        摘要字符串
    """
    if not profile or profile.get('status') in ['insufficient_data', 'error']:
        return "无画像数据"
    
    inv_pref = profile.get('investment_preferences', {})
    knowledge = profile.get('knowledge_level', {})
    
    return f"风险偏好:{inv_pref.get('risk_tolerance', 'unknown')}, 期权经验:{knowledge.get('option_experience', 'unknown')}"


# 数据库初始化检查
def ensure_profile_tables_exist():
    """确保用户画像表存在，如果不存在则自动创建"""
    conn = get_db_connection()
    if not conn:
        print("⚠️ 数据库连接不可用，用户画像功能将被禁用")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 检查user_profiles表是否存在
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'user_profiles'
            );
        """)
        
        exists = cursor.fetchone()[0]
        
        if not exists:
            print("⚠️ user_profiles表不存在，正在自动创建...")
            
            # 创建用户画像表
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
            
            # 创建策略推荐表
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
            
            conn.commit()
            print("✅ 用户画像表创建成功")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"检查/创建数据库表失败: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

