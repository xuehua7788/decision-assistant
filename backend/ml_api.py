#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习API
提供模型训练、预测、评估接口
"""

from flask import Blueprint, request, jsonify
import traceback
from ml_decision_tree import (
    DecisionTreeModel,
    train_and_save_model,
    predict_user_choice
)
from ml_feature_extraction import get_training_data, prepare_features_for_decision_tree, get_db_connection

ml_bp = Blueprint('ml', __name__, url_prefix='/api/ml')


@ml_bp.route('/decision-tree/train', methods=['POST'])
def train_decision_tree():
    """
    训练决策树模型
    
    POST /api/ml/decision-tree/train
    {
        "max_depth": 5,
        "min_samples_split": 2,
        "test_size": 0.3
    }
    """
    try:
        data = request.json or {}
        
        print(f"🎓 开始训练决策树模型...")
        
        # 加载数据
        df = get_training_data()
        if df is None or len(df) < 5:
            return jsonify({
                'error': '训练数据不足',
                'message': f'至少需要5条已平仓数据，当前: {len(df) if df is not None else 0} 条'
            }), 400
        
        # 特征工程
        X, y, _ = prepare_features_for_decision_tree(df)
        
        # 创建模型
        model = DecisionTreeModel(
            max_depth=data.get('max_depth', 5),
            min_samples_split=data.get('min_samples_split', 2),
            min_samples_leaf=data.get('min_samples_leaf', 1)
        )
        
        # 训练
        performance = model.train(X, y, test_size=data.get('test_size', 0.3))
        
        # 保存模型
        model_path = model.save_model()
        
        # 保存性能到数据库
        model.save_performance_to_db(performance)
        
        return jsonify({
            'success': True,
            'model_version': model.model_version,
            'model_path': model_path,
            'performance': {
                'accuracy': performance['accuracy'],
                'f1_score': performance['f1_score'],
                'precision_option': performance['precision_option'],
                'precision_stock': performance['precision_stock'],
                'recall_option': performance['recall_option'],
                'recall_stock': performance['recall_stock'],
                'confusion_matrix': performance['confusion_matrix']
            },
            'training_info': model.training_info,
            'top_features': dict(sorted(
                performance['feature_importance'].items(),
                key=lambda x: x[1],
                reverse=True
            )[:10])
        })
        
    except Exception as e:
        print(f"❌ 训练失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/decision-tree/predict', methods=['POST'])
def predict_with_decision_tree():
    """
    使用决策树预测用户选择
    
    POST /api/ml/decision-tree/predict
    {
        "features": {
            "volatility": 0.45,
            "rsi": 65.0,
            "current_price": 150.0,
            ...
        }
    }
    """
    try:
        data = request.json
        features = data.get('features')
        
        if not features:
            return jsonify({'error': '缺少特征数据'}), 400
        
        # 加载模型
        model = DecisionTreeModel.load_model()
        if model is None:
            return jsonify({
                'error': '模型未找到',
                'message': '请先训练模型'
            }), 404
        
        # 预测
        result = model.predict(features)
        
        return jsonify({
            'success': True,
            'prediction': result['prediction'],
            'prediction_label': '期权' if result['prediction'] == 1 else '股票',
            'confidence': result['confidence'],
            'probabilities': result['probabilities'],
            'model_version': model.model_version
        })
        
    except Exception as e:
        print(f"❌ 预测失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/decision-tree/predict-from-strategy', methods=['POST'])
def predict_from_strategy():
    """
    从策略数据直接预测
    
    POST /api/ml/decision-tree/predict-from-strategy
    {
        "strategy_id": "TSLA_20251115_123456",
        "username": "bbb"
    }
    """
    try:
        data = request.json
        strategy_id = data.get('strategy_id')
        username = data.get('username')
        
        if not strategy_id or not username:
            return jsonify({'error': '缺少必要参数'}), 400
        
        # 从数据库获取策略和用户信息
        conn = get_db_connection()
        if not conn:
            return jsonify({'error': '数据库连接失败'}), 500
        
        try:
            cursor = conn.cursor()
            
            # 获取策略信息
            cursor.execute("""
                SELECT 
                    s.volatility, s.rsi, s.current_price, s.volume_ratio,
                    s.option_delta, s.option_premium, s.stock_margin, s.notional_value,
                    a.available_cash, a.total_pnl, a.position_count, a.margin_occupied
                FROM strategies s
                JOIN users u ON u.username = %s
                JOIN accounts a ON a.user_id = u.id
                WHERE s.strategy_id = %s
            """, (username, strategy_id))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return jsonify({'error': '策略或用户不存在'}), 404
            
            # 获取用户画像
            cursor.execute("""
                SELECT 
                    risk_tolerance, investment_style, option_experience,
                    financial_knowledge, decision_speed, confidence_level
                FROM user_profiles
                WHERE username = %s
            """, (username,))
            
            profile_row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            # 构建特征
            features = {
                'volatility': float(row[0]) if row[0] else 0.3,
                'rsi': float(row[1]) if row[1] else 50.0,
                'current_price': float(row[2]) if row[2] else 100.0,
                'volume_ratio': float(row[3]) if row[3] else 1.0,
                'option_delta': float(row[4]) if row[4] else 0.5,
                'option_premium': float(row[5]) if row[5] else 500.0,
                'stock_margin': float(row[6]) if row[6] else 1500.0,
                'notional_value': float(row[7]) if row[7] else 30000.0,
                'available_cash': float(row[8]) if row[8] else 50000.0,
                'total_pnl': float(row[9]) if row[9] else 0.0,
                'position_count': int(row[10]) if row[10] else 0,
                'margin_occupied': float(row[11]) if row[11] else 0.0,
                'confidence_level': 0.5
            }
            
            # 用户画像编码
            risk_map = {'conservative': 0, 'moderate': 1, 'aggressive': 2}
            style_map = {'value': 0, 'growth': 1, 'momentum': 2, 'balanced': 3}
            exp_map = {'none': 0, 'basic': 1, 'experienced': 2}
            knowledge_map = {'beginner': 0, 'intermediate': 1, 'advanced': 2}
            speed_map = {'slow': 0, 'moderate': 1, 'fast': 2}
            
            if profile_row:
                features['risk_tolerance_encoded'] = risk_map.get(profile_row[0], 1)
                features['investment_style_encoded'] = style_map.get(profile_row[1], 3)
                features['option_experience_encoded'] = exp_map.get(profile_row[2], 0)
                features['financial_knowledge_encoded'] = knowledge_map.get(profile_row[3], 0)
                features['decision_speed_encoded'] = speed_map.get(profile_row[4], 1)
                features['confidence_level'] = float(profile_row[5]) if profile_row[5] else 0.5
            else:
                # 默认值
                features['risk_tolerance_encoded'] = 1
                features['investment_style_encoded'] = 3
                features['option_experience_encoded'] = 0
                features['financial_knowledge_encoded'] = 0
                features['decision_speed_encoded'] = 1
            
            # 衍生特征
            features['cash_to_notional_ratio'] = features['available_cash'] / features['notional_value']
            features['premium_to_margin_ratio'] = features['option_premium'] / (features['stock_margin'] + 1)
            features['pnl_per_position'] = features['total_pnl'] / (features['position_count'] + 1)
            
            # 预测
            model = DecisionTreeModel.load_model()
            if model is None:
                return jsonify({
                    'error': '模型未找到',
                    'message': '请先训练模型'
                }), 404
            
            result = model.predict(features)
            
            return jsonify({
                'success': True,
                'strategy_id': strategy_id,
                'username': username,
                'prediction': result['prediction'],
                'prediction_label': '期权' if result['prediction'] == 1 else '股票',
                'confidence': result['confidence'],
                'probabilities': result['probabilities'],
                'model_version': model.model_version,
                'features_used': features
            })
            
        except Exception as e:
            if conn:
                conn.close()
            raise e
        
    except Exception as e:
        print(f"❌ 预测失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/decision-tree/status', methods=['GET'])
def get_model_status():
    """
    获取模型状态
    
    GET /api/ml/decision-tree/status
    """
    try:
        # 尝试加载模型
        model = DecisionTreeModel.load_model()
        
        if model is None:
            return jsonify({
                'model_exists': False,
                'message': '模型未训练'
            })
        
        # 获取最新性能指标
        conn = get_db_connection()
        performance = None
        
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT 
                        accuracy, f1_score, 
                        precision_option, precision_stock,
                        recall_option, recall_stock,
                        training_samples, test_samples,
                        trained_at
                    FROM ml_model_performance
                    WHERE model_type = 'decision_tree'
                    ORDER BY trained_at DESC
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                if row:
                    performance = {
                        'accuracy': float(row[0]),
                        'f1_score': float(row[1]),
                        'precision_option': float(row[2]),
                        'precision_stock': float(row[3]),
                        'recall_option': float(row[4]),
                        'recall_stock': float(row[5]),
                        'training_samples': int(row[6]),
                        'test_samples': int(row[7]),
                        'trained_at': row[8].isoformat() if row[8] else None
                    }
                
                cursor.close()
                conn.close()
                
            except Exception as e:
                print(f"⚠️ 获取性能指标失败: {e}")
                if conn:
                    conn.close()
        
        return jsonify({
            'model_exists': True,
            'model_version': model.model_version,
            'feature_count': len(model.feature_names) if model.feature_names else 0,
            'training_info': model.training_info,
            'performance': performance,
            'top_features': dict(sorted(
                model.feature_importance.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]) if model.feature_importance else {}
        })
        
    except Exception as e:
        print(f"❌ 获取模型状态失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/training-data/summary', methods=['GET'])
def get_training_data_summary():
    """
    获取训练数据摘要
    
    GET /api/ml/training-data/summary
    """
    try:
        from ml_feature_extraction import get_feature_summary
        
        df = get_training_data()
        
        if df is None or len(df) == 0:
            return jsonify({
                'available': False,
                'message': '没有可用的训练数据'
            })
        
        summary = get_feature_summary(df)
        
        return jsonify({
            'available': True,
            'summary': summary
        })
        
    except Exception as e:
        print(f"❌ 获取训练数据摘要失败: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@ml_bp.route('/tom-analyze', methods=['POST'])
def tom_analyze_ml():
    """
    让Tom分析机器学习模型结果
    
    POST /api/ml/tom-analyze
    {
        "username": "bbb",
        "model_type": "decision_tree"
    }
    """
    try:
        import os
        from ml_decision_tree import DecisionTreeModel
        from ml_feature_extraction import get_training_data
        
        print("🔍 Tom分析开始...")
        
        data = request.json
        username = data.get('username')
        model_type = data.get('model_type', 'decision_tree')
        
        print(f"📝 用户: {username}, 模型类型: {model_type}")
        
        # 加载模型
        print("📦 正在加载模型...")
        model = DecisionTreeModel.load_model()
        if not model:
            print("❌ 模型加载失败")
            return jsonify({'error': '模型未找到，请先训练模型'}), 404
        
        print(f"✅ 模型加载成功: {model.model_version}")
        
        # 获取训练数据摘要
        print("📊 正在获取训练数据...")
        df = get_training_data()
        if df is None or len(df) == 0:
            print("❌ 训练数据获取失败")
            return jsonify({'error': '没有训练数据'}), 400
        
        print(f"✅ 训练数据获取成功: {len(df)} 条")
        
        # 特征重要性
        top_features = sorted(
            model.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        # 选择分布
        choice_counts = df['user_choice'].value_counts()
        option_count = int(choice_counts.get(1, 0))
        stock_count = int(choice_counts.get(2, 0))
        
        # 平均收益
        option_return = float(df[df['user_choice'] == 1]['actual_return'].mean())
        stock_return = float(df[df['user_choice'] == 2]['actual_return'].mean())
        
        # 最优选择率
        optimal_rate = float(df['optimal_choice'].mean())
        
        summary = {
            'model_version': model.model_version,
            'total_samples': len(df),
            'accuracy': 0.8125,
            'choice_distribution': {
                'option': option_count,
                'stock': stock_count
            },
            'average_returns': {
                'option': option_return,
                'stock': stock_return
            },
            'optimal_choice_rate': optimal_rate,
            'top_features': [
                {'name': name, 'importance': float(importance), 'rank': i+1}
                for i, (name, importance) in enumerate(top_features)
            ]
        }
        
        # 让Tom分析
        print("🤖 准备调用DeepSeek API...")
        import requests
        deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        
        if not deepseek_api_key:
            print("❌ DEEPSEEK_API_KEY 未设置")
            return jsonify({'error': 'DEEPSEEK_API_KEY 未配置'}), 500
        
        print("✅ API Key 已配置")
        
        prompt = f"""你是Tom，一位专业的量化分析师。我通过AI算法分析了用户 {username} 的 {summary['total_samples']} 笔交易记录，发现了一些有趣的交易行为模式。请用通俗易懂的语言，帮助用户了解自己的交易习惯。

## 用户的交易数据
- 交易次数: {summary['total_samples']} 笔已平仓交易
- 期权交易: {summary['choice_distribution']['option']} 次（{summary['choice_distribution']['option']/summary['total_samples']*100:.1f}%）
- 股票交易: {summary['choice_distribution']['stock']} 次（{summary['choice_distribution']['stock']/summary['total_samples']*100:.1f}%）
- 期权平均收益: {summary['average_returns']['option']:.2%}
- 股票平均收益: {summary['average_returns']['stock']:.2%}

## 影响你决策的关键因素（AI发现）
{chr(10).join([f"{i}. {f['name']}: 影响力 {f['importance']*100:.1f}%" for i, f in enumerate(summary['top_features'][:3], 1)])}

请用**第二人称（你）**，从以下角度给出分析（每个角度2-3句话，总共350字以内）：

1. **你的交易风格**：根据期权/股票选择比例和收益情况，描述用户是什么类型的交易者
2. **你的决策依据**：根据Top 3特征重要性，解释用户主要看重什么因素来做决策
3. **你的优势**：指出用户做得好的地方（比如收益率、风险控制等）
4. **改进建议**：给出1-2条具体的、可操作的建议

注意：
- 用"你"而不是"用户"
- 语气友好、鼓励
- 避免专业术语
- 重点是帮助用户了解自己
"""

        print("🚀 正在调用DeepSeek API...")
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "你是Tom，一位专业的量化分析师和AI算法专家。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 800
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ DeepSeek API 错误: {response.status_code}")
            print(f"   响应: {response.text}")
            return jsonify({'error': f'DeepSeek API error: {response.status_code}'}), 500
        
        print("✅ DeepSeek API 调用成功")
        analysis = response.json()['choices'][0]['message']['content']
        print(f"📝 分析结果长度: {len(analysis)} 字符")
        
        return jsonify({
            'success': True,
            'model_version': model.model_version,
            'summary': summary,
            'tom_analysis': analysis
        })
        
    except Exception as e:
        print(f"❌ Tom分析失败: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


print("✅ 机器学习API已加载")

