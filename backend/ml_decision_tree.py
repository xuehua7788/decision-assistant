#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
决策树算法实现
用于预测用户交易行为（选择期权还是股票）
"""

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report
)
import joblib
import json
from datetime import datetime
import os

from ml_feature_extraction import (
    get_training_data,
    prepare_features_for_decision_tree,
    get_feature_summary,
    get_db_connection
)


class DecisionTreeModel:
    """决策树模型类"""
    
    def __init__(self, max_depth=5, min_samples_split=2, min_samples_leaf=1):
        """
        初始化决策树模型
        
        参数:
            max_depth: 最大深度（防止过拟合）
            min_samples_split: 分裂所需最小样本数
            min_samples_leaf: 叶节点最小样本数
        """
        self.model = DecisionTreeClassifier(
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            random_state=42,
            class_weight='balanced'  # 处理类别不平衡
        )
        self.feature_names = None
        self.feature_importance = None
        self.model_version = f"v1.0_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self.training_info = {}
        
    
    def train(self, X, y, test_size=0.3):
        """
        训练模型
        
        参数:
            X: 特征矩阵
            y: 标签向量
            test_size: 测试集比例
            
        返回:
            performance: 性能指标字典
        """
        print(f"\n{'='*60}")
        print(f"🌳 开始训练决策树模型")
        print(f"{'='*60}")
        
        # 1. 数据分割
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"📊 数据分割:")
        print(f"   训练集: {len(X_train)} 样本")
        print(f"   测试集: {len(X_test)} 样本")
        print(f"   特征数: {X_train.shape[1]}")
        
        # 2. 训练模型
        print(f"\n🔄 训练中...")
        self.model.fit(X_train, y_train)
        self.feature_names = list(X.columns)
        self.feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        print(f"✅ 训练完成！")
        
        # 3. 预测
        y_train_pred = self.model.predict(X_train)
        y_test_pred = self.model.predict(X_test)
        
        # 4. 评估
        performance = self._evaluate(
            y_train, y_train_pred,
            y_test, y_test_pred,
            X_train, X_test
        )
        
        # 5. 保存训练信息
        self.training_info = {
            'train_samples': len(X_train),
            'test_samples': len(X_test),
            'train_test_split': test_size,
            'hyperparameters': {
                'max_depth': self.model.max_depth,
                'min_samples_split': self.model.min_samples_split,
                'min_samples_leaf': self.model.min_samples_leaf
            },
            'trained_at': datetime.now().isoformat()
        }
        
        return performance
    
    
    def _evaluate(self, y_train, y_train_pred, y_test, y_test_pred, X_train, X_test):
        """
        评估模型性能
        """
        print(f"\n{'='*60}")
        print(f"📈 模型性能评估")
        print(f"{'='*60}")
        
        # 训练集性能
        train_accuracy = accuracy_score(y_train, y_train_pred)
        print(f"\n🎯 训练集:")
        print(f"   准确率: {train_accuracy:.2%}")
        
        # 测试集性能
        test_accuracy = accuracy_score(y_test, y_test_pred)
        test_precision_option = precision_score(y_test, y_test_pred, pos_label=1, zero_division=0)
        test_precision_stock = precision_score(y_test, y_test_pred, pos_label=2, zero_division=0)
        test_recall_option = recall_score(y_test, y_test_pred, pos_label=1, zero_division=0)
        test_recall_stock = recall_score(y_test, y_test_pred, pos_label=2, zero_division=0)
        test_f1 = f1_score(y_test, y_test_pred, average='weighted')
        
        print(f"\n🎯 测试集:")
        print(f"   准确率: {test_accuracy:.2%}")
        print(f"   F1分数: {test_f1:.2%}")
        print(f"\n   期权策略 (1):")
        print(f"      精确率: {test_precision_option:.2%}")
        print(f"      召回率: {test_recall_option:.2%}")
        print(f"\n   股票策略 (2):")
        print(f"      精确率: {test_precision_stock:.2%}")
        print(f"      召回率: {test_recall_stock:.2%}")
        
        # 混淆矩阵
        cm = confusion_matrix(y_test, y_test_pred)
        print(f"\n📊 混淆矩阵:")
        print(f"                预测期权  预测股票")
        print(f"   实际期权:      {cm[0][0]:>4}      {cm[0][1]:>4}")
        print(f"   实际股票:      {cm[1][0]:>4}      {cm[1][1]:>4}")
        
        # 特征重要性
        print(f"\n🔍 Top 10 特征重要性:")
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )
        for i, (feature, importance) in enumerate(sorted_features[:10], 1):
            print(f"   {i:2d}. {feature:30s} {importance:.4f}")
        
        # 交叉验证
        cv_scores = cross_val_score(
            self.model, X_train, y_train, cv=min(5, len(X_train)), scoring='accuracy'
        )
        print(f"\n🔄 5折交叉验证:")
        print(f"   平均准确率: {cv_scores.mean():.2%} (+/- {cv_scores.std() * 2:.2%})")
        
        # 返回性能指标
        performance = {
            'accuracy': float(test_accuracy),
            'precision_option': float(test_precision_option),
            'precision_stock': float(test_precision_stock),
            'recall_option': float(test_recall_option),
            'recall_stock': float(test_recall_stock),
            'f1_score': float(test_f1),
            'confusion_matrix': {
                'TN': int(cm[0][0]),  # 预测期权，实际期权
                'FP': int(cm[0][1]),  # 预测股票，实际期权
                'FN': int(cm[1][0]),  # 预测期权，实际股票
                'TP': int(cm[1][1])   # 预测股票，实际股票
            },
            'feature_importance': self.feature_importance,
            'cv_mean': float(cv_scores.mean()),
            'cv_std': float(cv_scores.std()),
            'train_accuracy': float(train_accuracy)
        }
        
        return performance
    
    
    def predict(self, X):
        """
        预测单个样本
        
        参数:
            X: 特征向量或DataFrame
            
        返回:
            prediction: 预测结果 (1=期权, 2=股票)
            confidence: 预测置信度
            probabilities: 各类别概率
        """
        if isinstance(X, pd.Series):
            X = X.to_frame().T
        elif isinstance(X, dict):
            X = pd.DataFrame([X])
        
        # 确保特征顺序一致
        if self.feature_names:
            X = X[self.feature_names]
        
        # 预测
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = max(probabilities)
        
        return {
            'prediction': int(prediction),
            'confidence': float(confidence),
            'probabilities': {
                'option': float(probabilities[0]),
                'stock': float(probabilities[1])
            }
        }
    
    
    def save_model(self, filepath='models/decision_tree_model.pkl'):
        """保存模型到文件"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model': self.model,
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'model_version': self.model_version,
            'training_info': self.training_info
        }
        
        joblib.dump(model_data, filepath)
        print(f"\n💾 模型已保存: {filepath}")
        return filepath
    
    
    @classmethod
    def load_model(cls, filepath='models/decision_tree_model.pkl'):
        """从文件加载模型"""
        if not os.path.exists(filepath):
            print(f"❌ 模型文件不存在: {filepath}")
            return None
        
        model_data = joblib.load(filepath)
        
        instance = cls()
        instance.model = model_data['model']
        instance.feature_names = model_data['feature_names']
        instance.feature_importance = model_data['feature_importance']
        instance.model_version = model_data['model_version']
        instance.training_info = model_data.get('training_info', {})
        
        print(f"✅ 模型已加载: {filepath}")
        print(f"   版本: {instance.model_version}")
        return instance
    
    
    def save_performance_to_db(self, performance):
        """保存性能指标到数据库"""
        conn = get_db_connection()
        if not conn:
            print("⚠️ 数据库连接失败，无法保存性能指标")
            return False
        
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO ml_model_performance (
                    model_type, model_version,
                    accuracy, precision_option, precision_stock,
                    recall_option, recall_stock, f1_score,
                    confusion_matrix, feature_importance,
                    training_samples, test_samples, train_test_split,
                    hyperparameters
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                'decision_tree',
                self.model_version,
                performance['accuracy'],
                performance['precision_option'],
                performance['precision_stock'],
                performance['recall_option'],
                performance['recall_stock'],
                performance['f1_score'],
                json.dumps(performance['confusion_matrix']),
                json.dumps(performance['feature_importance']),
                self.training_info['train_samples'],
                self.training_info['test_samples'],
                self.training_info['train_test_split'],
                json.dumps(self.training_info['hyperparameters'])
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            print(f"✅ 性能指标已保存到数据库")
            return True
            
        except Exception as e:
            print(f"❌ 保存性能指标失败: {e}")
            if conn:
                conn.close()
            return False


def train_and_save_model():
    """训练并保存模型的完整流程"""
    print(f"\n{'='*60}")
    print(f"🚀 决策树模型训练流程")
    print(f"{'='*60}")
    
    # 1. 加载数据
    print(f"\n📥 Step 1: 加载训练数据...")
    df = get_training_data()
    
    if df is None or len(df) < 5:
        print(f"❌ 训练数据不足（至少需要5条），当前: {len(df) if df is not None else 0} 条")
        return None
    
    print(f"✅ 成功加载 {len(df)} 条数据")
    
    # 2. 特征工程
    print(f"\n🔧 Step 2: 特征工程...")
    X, y, df_processed = prepare_features_for_decision_tree(df)
    
    # 3. 训练模型
    print(f"\n🎓 Step 3: 训练模型...")
    model = DecisionTreeModel(
        max_depth=5,
        min_samples_split=2,
        min_samples_leaf=1
    )
    
    performance = model.train(X, y, test_size=0.3)
    
    # 4. 保存模型
    print(f"\n💾 Step 4: 保存模型...")
    model_path = model.save_model()
    
    # 5. 保存性能到数据库
    print(f"\n📊 Step 5: 保存性能指标...")
    model.save_performance_to_db(performance)
    
    print(f"\n{'='*60}")
    print(f"✅ 训练流程完成！")
    print(f"{'='*60}")
    print(f"📁 模型文件: {model_path}")
    print(f"📈 测试准确率: {performance['accuracy']:.2%}")
    print(f"🎯 F1分数: {performance['f1_score']:.2%}")
    
    return model


def predict_user_choice(features):
    """
    预测用户选择
    
    参数:
        features: 特征字典
        
    返回:
        prediction_result: 预测结果字典
    """
    # 加载模型
    model = DecisionTreeModel.load_model()
    if model is None:
        return {'error': '模型未找到，请先训练模型'}
    
    # 预测
    result = model.predict(features)
    
    return result


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'train':
        # 训练模式
        train_and_save_model()
        
    elif len(sys.argv) > 1 and sys.argv[1] == 'test':
        # 测试模式
        print(f"\n{'='*60}")
        print(f"🧪 测试预测功能")
        print(f"{'='*60}")
        
        # 加载模型
        model = DecisionTreeModel.load_model()
        if model is None:
            print("❌ 请先训练模型: python ml_decision_tree.py train")
            sys.exit(1)
        
        # 测试样本
        test_features = {
            'volatility': 0.45,
            'rsi': 65.0,
            'current_price': 150.0,
            'volume_ratio': 1.2,
            'available_cash': 50000.0,
            'total_pnl': 1500.0,
            'position_count': 2,
            'option_delta': 0.6,
            'option_premium': 500.0,
            'stock_margin': 1500.0,
            'confidence_level': 0.8,
            'notional_value': 30000.0,
            'risk_tolerance_encoded': 2,  # aggressive
            'investment_style_encoded': 2,  # momentum
            'option_experience_encoded': 1,  # basic
            'financial_knowledge_encoded': 1,  # intermediate
            'decision_speed_encoded': 2,  # fast
            'cash_to_notional_ratio': 50000.0 / 30000.0,
            'premium_to_margin_ratio': 500.0 / 1500.0,
            'pnl_per_position': 1500.0 / 2
        }
        
        result = model.predict(test_features)
        
        print(f"\n📊 预测结果:")
        print(f"   选择: {'期权' if result['prediction'] == 1 else '股票'}")
        print(f"   置信度: {result['confidence']:.2%}")
        print(f"   期权概率: {result['probabilities']['option']:.2%}")
        print(f"   股票概率: {result['probabilities']['stock']:.2%}")
        
    else:
        # 默认：显示帮助
        print(f"""
使用方法:
    python ml_decision_tree.py train    # 训练模型
    python ml_decision_tree.py test     # 测试预测
        """)

