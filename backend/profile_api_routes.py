#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户画像API路由
提供用户画像的查询、分析、管理接口
"""

from flask import Blueprint, jsonify, request
from profile_integration_helpers import (
    load_user_profile_from_db,
    load_chat_history_from_db,
    check_profile_freshness,
    get_db_connection
)
from ai_profile_analyzer import get_profile_analyzer
import json

# 创建蓝图
profile_bp = Blueprint('profile', __name__, url_prefix='/api/profile')


@profile_bp.route('/<username>', methods=['GET'])
def get_user_profile(username):
    """
    获取用户画像
    
    GET /api/profile/alice
    """
    try:
        profile = load_user_profile_from_db(username)
        
        if profile:
            return jsonify({
                "status": "success",
                "profile": profile
            }), 200
        else:
            return jsonify({
                "status": "not_found",
                "message": f"用户 {username} 的画像不存在，可能需要先进行分析"
            }), 404
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@profile_bp.route('/<username>/analyze', methods=['POST'])
def analyze_user_profile(username):
    """
    触发用户画像分析
    
    POST /api/profile/alice/analyze
    Body: {
        "days": 30,  // 可选，默认30天
        "force": false  // 可选，是否强制重新分析
    }
    """
    try:
        data = request.json or {}
        days = data.get('days', 30)
        force = data.get('force', False)
        
        # 检查是否需要重新分析
        if not force and check_profile_freshness(username, max_age_days=7):
            profile = load_user_profile_from_db(username)
            return jsonify({
                "status": "success",
                "message": "用户画像已是最新，无需重新分析",
                "profile": profile
            }), 200
        
        # 加载聊天历史
        chat_history = load_chat_history_from_db(username, days=days)
        
        if len(chat_history) < 5:
            return jsonify({
                "status": "insufficient_data",
                "message": f"用户 {username} 的聊天记录不足（{len(chat_history)} 条），需要至少5条记录"
            }), 400
        
        # 执行分析
        analyzer = get_profile_analyzer()
        profile = analyzer.analyze_user_profile(
            username=username,
            chat_history=chat_history,
            days=days
        )
        
        if profile.get('status') == 'error':
            return jsonify({
                "status": "error",
                "message": profile.get('message', 'AI分析失败')
            }), 500
        
        # 保存到数据库
        conn = get_db_connection()
        if conn:
            analyzer.update_user_profile_in_db(conn, username, profile)
            conn.close()
        
        return jsonify({
            "status": "success",
            "message": "用户画像分析完成",
            "profile": profile
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@profile_bp.route('/<username>/summary', methods=['GET'])
def get_profile_summary(username):
    """
    获取用户画像摘要（简化版）
    
    GET /api/profile/alice/summary
    """
    try:
        profile = load_user_profile_from_db(username)
        
        if not profile:
            return jsonify({
                "status": "not_found",
                "message": "用户画像不存在"
            }), 404
        
        # 提取关键信息
        inv_pref = profile.get('investment_preferences', {})
        knowledge = profile.get('knowledge_level', {})
        emotion = profile.get('emotional_traits', {})
        
        summary = {
            "username": username,
            "risk_tolerance": inv_pref.get('risk_tolerance'),
            "investment_style": inv_pref.get('investment_style'),
            "option_experience": knowledge.get('option_experience'),
            "confidence_level": emotion.get('confidence_level'),
            "analysis_summary": profile.get('analysis_summary'),
            "last_analyzed_at": profile.get('last_analyzed_at'),
            "total_messages_analyzed": profile.get('total_messages_analyzed')
        }
        
        return jsonify({
            "status": "success",
            "summary": summary
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@profile_bp.route('/<username>/recommendations', methods=['GET'])
def get_recommendation_history(username):
    """
    获取用户的策略推荐历史
    
    GET /api/profile/alice/recommendations?limit=10
    """
    try:
        limit = request.args.get('limit', 10, type=int)
        
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "数据库连接失败"
            }), 500
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                id, strategy_type, strategy_parameters,
                adjustment_reason, created_at
            FROM strategy_recommendations
            WHERE username = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (username, limit))
        
        recommendations = []
        for row in cursor.fetchall():
            recommendations.append({
                "id": row[0],
                "strategy_type": row[1],
                "strategy_parameters": row[2],
                "adjustment_reason": row[3],
                "created_at": row[4].isoformat() if row[4] else None
            })
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "total": len(recommendations),
            "recommendations": recommendations
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@profile_bp.route('/stats', methods=['GET'])
def get_profile_stats():
    """
    获取用户画像统计信息（管理员功能）
    
    GET /api/profile/stats
    """
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({
                "status": "error",
                "message": "数据库连接失败"
            }), 500
        
        cursor = conn.cursor()
        
        # 统计总用户数
        cursor.execute("SELECT COUNT(*) FROM user_profiles")
        total_profiles = cursor.fetchone()[0]
        
        # 统计风险偏好分布
        cursor.execute("""
            SELECT risk_tolerance, COUNT(*) 
            FROM user_profiles 
            GROUP BY risk_tolerance
        """)
        risk_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 统计期权经验分布
        cursor.execute("""
            SELECT option_experience, COUNT(*) 
            FROM user_profiles 
            GROUP BY option_experience
        """)
        experience_distribution = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 统计最近分析的用户
        cursor.execute("""
            SELECT COUNT(*) 
            FROM user_profiles 
            WHERE last_analyzed_at > NOW() - INTERVAL '7 days'
        """)
        recently_analyzed = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_profiles": total_profiles,
                "recently_analyzed": recently_analyzed,
                "risk_distribution": risk_distribution,
                "experience_distribution": experience_distribution
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# 导出蓝图
__all__ = ['profile_bp']

