#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
机器学习特征提取模块
从现有表中提取训练数据，无需额外存储
"""

import psycopg2
import pandas as pd
import numpy as np
import os

def get_db_connection():
    """获取数据库连接"""
    DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None

def get_training_data():
    """
    从ml_training_data视图获取训练数据
    返回: DataFrame
    """
    conn = get_db_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return None
    
    try:
        query = """
            SELECT * FROM ml_training_data
            WHERE user_choice IS NOT NULL
            ORDER BY decision_time DESC
        """
        
        df = pd.read_sql(query, conn)
        conn.close()
        
        print(f"✅ 成功加载 {len(df)} 条训练数据")
        return df
        
    except Exception as e:
        print(f"❌ 加载训练数据失败: {e}")
        if conn:
            conn.close()
        return None


def prepare_features_for_bayesian(df):
    """
    为朴素贝叶斯准备特征（离散化）
    """
    df_discrete = df.copy()
    
    # 1. 波动率离散化
    df_discrete['volatility_level'] = pd.cut(
        df['volatility'], 
        bins=[0, 0.3, 0.6, 1.0],
        labels=['low', 'medium', 'high']
    )
    
    # 2. RSI离散化
    df_discrete['rsi_level'] = pd.cut(
        df['rsi'],
        bins=[0, 30, 70, 100],
        labels=['oversold', 'neutral', 'overbought']
    )
    
    # 3. 现金水平离散化
    cash_median = df['available_cash'].median()
    df_discrete['cash_level'] = pd.cut(
        df['available_cash'],
        bins=[0, cash_median * 0.5, cash_median * 1.5, float('inf')],
        labels=['low', 'medium', 'high']
    )
    
    # 4. 盈亏状态离散化
    df_discrete['pnl_status'] = pd.cut(
        df['total_pnl'],
        bins=[-float('inf'), -100, 100, float('inf')],
        labels=['loss', 'breakeven', 'profit']
    )
    
    # 5. 期权费水平离散化
    premium_median = df['option_premium'].median()
    df_discrete['option_cost_level'] = pd.cut(
        df['option_premium'],
        bins=[0, premium_median * 0.7, premium_median * 1.3, float('inf')],
        labels=['low', 'medium', 'high']
    )
    
    # 6. Delta值离散化
    df_discrete['delta_level'] = pd.cut(
        df['option_delta'],
        bins=[0, 0.3, 0.7, 1.0],
        labels=['low', 'medium', 'high']
    )
    
    # 7. 保留分类特征（已经是离散的）
    categorical_features = [
        'risk_tolerance',
        'investment_style', 
        'option_experience',
        'financial_knowledge',
        'decision_speed'
    ]
    
    # 选择特征
    feature_columns = [
        'volatility_level', 'rsi_level', 'cash_level', 'pnl_status',
        'option_cost_level', 'delta_level'
    ] + categorical_features
    
    X = df_discrete[feature_columns]
    y = df['user_choice']  # 1=期权, 2=股票
    
    print(f"✅ 贝叶斯特征准备完成: {X.shape[1]} 个特征")
    return X, y, df_discrete


def prepare_features_for_decision_tree(df):
    """
    为决策树准备特征（数值+编码）
    """
    df_encoded = df.copy()
    
    # 1. 数值特征（直接使用）
    numerical_features = [
        'volatility', 'rsi', 'current_price', 'volume_ratio',
        'available_cash', 'total_pnl', 'position_count',
        'option_delta', 'option_premium', 'stock_margin',
        'confidence_level', 'notional_value'
    ]
    
    # 2. 分类特征（标签编码）
    categorical_mappings = {
        'risk_tolerance': {'conservative': 0, 'moderate': 1, 'aggressive': 2},
        'investment_style': {'value': 0, 'growth': 1, 'momentum': 2, 'balanced': 3},
        'option_experience': {'none': 0, 'basic': 1, 'experienced': 2},
        'financial_knowledge': {'beginner': 0, 'intermediate': 1, 'advanced': 2},
        'decision_speed': {'slow': 0, 'moderate': 1, 'fast': 2}
    }
    
    for col, mapping in categorical_mappings.items():
        if col in df_encoded.columns:
            df_encoded[f'{col}_encoded'] = df_encoded[col].map(mapping)
    
    # 3. 衍生特征
    df_encoded['cash_to_notional_ratio'] = df_encoded['available_cash'] / df_encoded['notional_value']
    df_encoded['premium_to_margin_ratio'] = df_encoded['option_premium'] / (df_encoded['stock_margin'] + 1)
    df_encoded['pnl_per_position'] = df_encoded['total_pnl'] / (df_encoded['position_count'] + 1)
    
    # 选择特征
    encoded_categorical = [f'{col}_encoded' for col in categorical_mappings.keys() if col in df_encoded.columns]
    derived_features = ['cash_to_notional_ratio', 'premium_to_margin_ratio', 'pnl_per_position']
    
    feature_columns = numerical_features + encoded_categorical + derived_features
    
    # 处理缺失值
    X = df_encoded[feature_columns].fillna(df_encoded[feature_columns].median())
    y = df['user_choice']  # 1=期权, 2=股票
    
    print(f"✅ 决策树特征准备完成: {X.shape[1]} 个特征")
    return X, y, df_encoded


def get_feature_summary(df):
    """
    获取特征统计摘要
    """
    summary = {
        'total_samples': len(df),
        'option_choices': (df['user_choice'] == 1).sum(),
        'stock_choices': (df['user_choice'] == 2).sum(),
        'class_balance': {
            'option_ratio': (df['user_choice'] == 1).sum() / len(df),
            'stock_ratio': (df['user_choice'] == 2).sum() / len(df)
        },
        'feature_stats': {
            'volatility': {
                'mean': df['volatility'].mean(),
                'std': df['volatility'].std(),
                'min': df['volatility'].min(),
                'max': df['volatility'].max()
            },
            'rsi': {
                'mean': df['rsi'].mean(),
                'std': df['rsi'].std()
            },
            'available_cash': {
                'mean': df['available_cash'].mean(),
                'median': df['available_cash'].median()
            }
        },
        'user_profiles': {
            'risk_tolerance': df['risk_tolerance'].value_counts().to_dict(),
            'investment_style': df['investment_style'].value_counts().to_dict(),
            'option_experience': df['option_experience'].value_counts().to_dict()
        }
    }
    
    return summary


if __name__ == "__main__":
    print("=" * 60)
    print("🔬 机器学习特征提取测试")
    print("=" * 60)
    
    # 1. 加载数据
    df = get_training_data()
    if df is None or len(df) == 0:
        print("⚠️ 没有可用的训练数据")
        exit(1)
    
    print(f"\n📊 数据概览:")
    print(df.head())
    
    # 2. 特征摘要
    print(f"\n📈 特征统计:")
    summary = get_feature_summary(df)
    print(f"   总样本数: {summary['total_samples']}")
    print(f"   期权选择: {summary['option_choices']} ({summary['class_balance']['option_ratio']:.1%})")
    print(f"   股票选择: {summary['stock_choices']} ({summary['class_balance']['stock_ratio']:.1%})")
    
    # 3. 贝叶斯特征
    print(f"\n🎲 贝叶斯特征准备:")
    X_bayes, y_bayes, df_bayes = prepare_features_for_bayesian(df)
    print(f"   特征形状: {X_bayes.shape}")
    print(f"   特征列表: {list(X_bayes.columns)}")
    
    # 4. 决策树特征
    print(f"\n🌳 决策树特征准备:")
    X_tree, y_tree, df_tree = prepare_features_for_decision_tree(df)
    print(f"   特征形状: {X_tree.shape}")
    print(f"   特征列表: {list(X_tree.columns)}")
    
    print(f"\n✅ 特征提取测试完成！")

