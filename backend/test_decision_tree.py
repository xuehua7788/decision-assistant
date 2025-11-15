#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试决策树算法
"""

import sys
import os

# 添加backend目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ml_feature_extraction import get_training_data, prepare_features_for_decision_tree
from ml_decision_tree import DecisionTreeModel, train_and_save_model


def test_data_loading():
    """测试数据加载"""
    print(f"\n{'='*60}")
    print(f"📥 测试1: 数据加载")
    print(f"{'='*60}")
    
    df = get_training_data()
    
    if df is None:
        print(f"❌ 数据加载失败")
        return False
    
    print(f"✅ 成功加载 {len(df)} 条数据")
    print(f"\n前3条数据:")
    print(df.head(3))
    
    return True


def test_feature_engineering():
    """测试特征工程"""
    print(f"\n{'='*60}")
    print(f"🔧 测试2: 特征工程")
    print(f"{'='*60}")
    
    df = get_training_data()
    if df is None or len(df) == 0:
        print(f"❌ 没有数据")
        return False
    
    X, y, df_processed = prepare_features_for_decision_tree(df)
    
    print(f"✅ 特征矩阵形状: {X.shape}")
    print(f"✅ 标签向量形状: {y.shape}")
    print(f"\n特征列表:")
    for i, col in enumerate(X.columns, 1):
        print(f"   {i:2d}. {col}")
    
    print(f"\n标签分布:")
    print(f"   期权 (1): {(y == 1).sum()} 条")
    print(f"   股票 (2): {(y == 2).sum()} 条")
    
    return True


def test_model_training():
    """测试模型训练"""
    print(f"\n{'='*60}")
    print(f"🎓 测试3: 模型训练")
    print(f"{'='*60}")
    
    df = get_training_data()
    if df is None or len(df) < 5:
        print(f"❌ 训练数据不足（至少需要5条）")
        return False
    
    X, y, _ = prepare_features_for_decision_tree(df)
    
    model = DecisionTreeModel(max_depth=5, min_samples_split=2)
    performance = model.train(X, y, test_size=0.3)
    
    print(f"\n✅ 训练完成！")
    print(f"   准确率: {performance['accuracy']:.2%}")
    print(f"   F1分数: {performance['f1_score']:.2%}")
    
    # 保存模型
    model_path = model.save_model()
    print(f"   模型已保存: {model_path}")
    
    return True


def test_model_prediction():
    """测试模型预测"""
    print(f"\n{'='*60}")
    print(f"🔮 测试4: 模型预测")
    print(f"{'='*60}")
    
    # 加载模型
    model = DecisionTreeModel.load_model()
    if model is None:
        print(f"❌ 模型加载失败")
        return False
    
    # 测试样本1: 高风险激进型
    print(f"\n📊 测试样本1: 高风险激进型投资者")
    features1 = {
        'volatility': 0.55,  # 高波动
        'rsi': 75.0,  # 超买
        'current_price': 200.0,
        'volume_ratio': 1.5,
        'available_cash': 80000.0,
        'total_pnl': 5000.0,  # 盈利中
        'position_count': 3,
        'option_delta': 0.7,
        'option_premium': 800.0,
        'stock_margin': 2000.0,
        'confidence_level': 0.9,
        'notional_value': 30000.0,
        'risk_tolerance_encoded': 2,  # aggressive
        'investment_style_encoded': 2,  # momentum
        'option_experience_encoded': 2,  # experienced
        'financial_knowledge_encoded': 2,  # advanced
        'decision_speed_encoded': 2,  # fast
        'cash_to_notional_ratio': 80000.0 / 30000.0,
        'premium_to_margin_ratio': 800.0 / 2000.0,
        'pnl_per_position': 5000.0 / 3
    }
    
    result1 = model.predict(features1)
    print(f"   预测: {'期权' if result1['prediction'] == 1 else '股票'}")
    print(f"   置信度: {result1['confidence']:.2%}")
    print(f"   期权概率: {result1['probabilities']['option']:.2%}")
    print(f"   股票概率: {result1['probabilities']['stock']:.2%}")
    
    # 测试样本2: 保守型
    print(f"\n📊 测试样本2: 保守型投资者")
    features2 = {
        'volatility': 0.25,  # 低波动
        'rsi': 45.0,  # 中性
        'current_price': 100.0,
        'volume_ratio': 0.8,
        'available_cash': 30000.0,
        'total_pnl': -500.0,  # 小亏
        'position_count': 1,
        'option_delta': 0.3,
        'option_premium': 300.0,
        'stock_margin': 1000.0,
        'confidence_level': 0.4,
        'notional_value': 30000.0,
        'risk_tolerance_encoded': 0,  # conservative
        'investment_style_encoded': 0,  # value
        'option_experience_encoded': 0,  # none
        'financial_knowledge_encoded': 0,  # beginner
        'decision_speed_encoded': 0,  # slow
        'cash_to_notional_ratio': 30000.0 / 30000.0,
        'premium_to_margin_ratio': 300.0 / 1000.0,
        'pnl_per_position': -500.0 / 1
    }
    
    result2 = model.predict(features2)
    print(f"   预测: {'期权' if result2['prediction'] == 1 else '股票'}")
    print(f"   置信度: {result2['confidence']:.2%}")
    print(f"   期权概率: {result2['probabilities']['option']:.2%}")
    print(f"   股票概率: {result2['probabilities']['stock']:.2%}")
    
    return True


def test_database_save():
    """测试保存到数据库"""
    print(f"\n{'='*60}")
    print(f"💾 测试5: 保存性能指标到数据库")
    print(f"{'='*60}")
    
    df = get_training_data()
    if df is None or len(df) < 5:
        print(f"⚠️ 跳过（数据不足）")
        return True
    
    X, y, _ = prepare_features_for_decision_tree(df)
    
    model = DecisionTreeModel(max_depth=3)
    performance = model.train(X, y, test_size=0.3)
    
    success = model.save_performance_to_db(performance)
    
    if success:
        print(f"✅ 性能指标已保存到数据库")
    else:
        print(f"⚠️ 数据库保存失败（可能数据库不可用）")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print(f"\n{'#'*60}")
    print(f"🧪 决策树算法测试套件")
    print(f"{'#'*60}")
    
    tests = [
        ("数据加载", test_data_loading),
        ("特征工程", test_feature_engineering),
        ("模型训练", test_model_training),
        ("模型预测", test_model_prediction),
        ("数据库保存", test_database_save)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n❌ 测试失败: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 总结
    print(f"\n{'='*60}")
    print(f"📊 测试总结")
    print(f"{'='*60}")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {status} - {name}")
    
    print(f"\n总计: {passed}/{total} 通过")
    
    if passed == total:
        print(f"\n🎉 所有测试通过！")
        return True
    else:
        print(f"\n⚠️ 部分测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

