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
        
        # 查询聊天记录
        cutoff_date = datetime.now() - timedelta(days=days)
        cursor.execute("""
            SELECT cm.role, cm.content, cm.created_at
            FROM chat_messages cm
            JOIN chat_sessions cs ON cm.session_id = cs.id
            WHERE cs.username = %s
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
    """确保用户画像表存在"""
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
        cursor.close()
        conn.close()
        
        if not exists:
            print("⚠️ user_profiles表不存在，请运行: python create_user_profile_tables.py")
            return False
        
        return True
        
    except Exception as e:
        print(f"检查数据库表失败: {e}")
        if conn:
            conn.close()
        return False

