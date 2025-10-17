#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算法分析API - 提供多种决策分析算法
"""

from flask import Blueprint, request, jsonify

# 导入算法管理器
try:
    from algorithms.algorithm_manager import get_algorithm_manager
    ALGORITHMS_AVAILABLE = True
except ImportError as e:
    ALGORITHMS_AVAILABLE = False
    get_algorithm_manager = None
    print(f"⚠️ 算法模块导入失败: {e}")

# 创建蓝图
algorithm_bp = Blueprint('algorithm', __name__, url_prefix='/api/algorithms')


@algorithm_bp.route('/list', methods=['GET'])
def list_algorithms():
    """列出所有可用的分析算法"""
    if not ALGORITHMS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "算法模块未加载"
        }), 500
    
    try:
        manager = get_algorithm_manager()
        algorithms = manager.list_algorithms()
        
        return jsonify({
            "status": "success",
            "total": len(algorithms),
            "algorithms": algorithms
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@algorithm_bp.route('/analyze', methods=['POST'])
def analyze_with_algorithm():
    """
    使用指定算法进行决策分析
    
    请求体:
    {
        "algorithm_id": "weighted_scoring",
        "question": "选择哪台电脑？",
        "options": [
            {"name": "选项A", "价格": 8, "性能": 9},
            {"name": "选项B", "价格": 9, "性能": 7}
        ],
        "criteria": ["价格", "性能"]  // 可选
    }
    """
    if not ALGORITHMS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "算法模块未加载"
        }), 500
    
    try:
        data = request.json
        
        algorithm_id = data.get('algorithm_id', 'weighted_scoring')
        question = data.get('question', '')
        options = data.get('options', [])
        criteria = data.get('criteria')
        
        if not options:
            return jsonify({
                "status": "error",
                "message": "请提供至少2个选项"
            }), 400
        
        # 使用算法分析
        manager = get_algorithm_manager()
        result = manager.analyze(algorithm_id, question, options, criteria)
        
        if 'error' in result:
            return jsonify({
                "status": "error",
                "message": result['error']
            }), 400
        
        return jsonify({
            "status": "success",
            "result": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@algorithm_bp.route('/compare', methods=['POST'])
def compare_algorithms():
    """
    使用多个算法进行对比分析
    
    请求体:
    {
        "question": "选择哪台电脑？",
        "options": [...],
        "algorithms": ["weighted_scoring", "pros_cons"]
    }
    """
    if not ALGORITHMS_AVAILABLE:
        return jsonify({
            "status": "error",
            "message": "算法模块未加载"
        }), 500
    
    try:
        data = request.json
        
        question = data.get('question', '')
        options = data.get('options', [])
        algorithm_ids = data.get('algorithms', ['weighted_scoring'])
        
        if not options:
            return jsonify({
                "status": "error",
                "message": "请提供至少2个选项"
            }), 400
        
        # 使用多个算法分析
        manager = get_algorithm_manager()
        results = {}
        
        for algo_id in algorithm_ids:
            try:
                result = manager.analyze(algo_id, question, options)
                results[algo_id] = result
            except Exception as e:
                results[algo_id] = {"error": str(e)}
        
        return jsonify({
            "status": "success",
            "question": question,
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

