#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略推荐记录保存辅助函数
"""

import json
from typing import Dict
from profile_integration_helpers import get_db_connection


def save_strategy_recommendation(username: str, 
                                 user_intent: Dict,
                                 user_profile_snapshot: Dict,
                                 optimized_strategy: Dict) -> bool:
    """
    保存策略推荐记录到数据库
    
    Args:
        username: 用户名
        user_intent: 用户意图
        user_profile_snapshot: 用户画像快照
        optimized_strategy: 优化后的策略
    
    Returns:
        是否保存成功
    """
    conn = get_db_connection()
    if not conn:
        print("⚠️ 数据库连接失败，无法保存推荐记录")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 提取策略信息
        strategy_type = optimized_strategy.get('strategy_type', 'unknown')
        strategy_parameters = json.dumps(optimized_strategy.get('parameters', {}))
        adjustment_reason = optimized_strategy.get('adjustment_reason', '')
        
        # 插入推荐记录
        cursor.execute("""
            INSERT INTO strategy_recommendations 
            (username, user_intent, user_profile_snapshot, strategy_type, 
             strategy_parameters, adjustment_reason, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            username,
            json.dumps(user_intent),
            json.dumps(user_profile_snapshot),
            strategy_type,
            strategy_parameters,
            adjustment_reason
        ))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"✅ 策略推荐已保存 (用户: {username}, 策略: {strategy_type})")
        return True
        
    except Exception as e:
        print(f"❌ 保存策略推荐失败: {e}")
        if conn:
            conn.rollback()
            conn.close()
        return False

