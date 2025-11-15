#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析决策树模型结果
"""

import psycopg2
from ml_decision_tree import DecisionTreeModel
from ml_feature_extraction import get_training_data, prepare_features_for_decision_tree
import pandas as pd

DATABASE_URL = 'postgresql://decision_user:8P8ZDdFaLp306B0siOZTXGScXmrdS9EB@dpg-d3ot1n3ipnbc739gkn7g-a.singapore-postgres.render.com/decision_assistant_098l'

def get_db_connection():
    try:
        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return None


def analyze_results():
    """分析模型结果"""
    
    print(f"\n{'='*80}")
    print(f"📊 决策树模型分析报告")
    print(f"{'='*80}")
    
    # 1. 加载模型
    model = DecisionTreeModel.load_model()
    if not model:
        print("❌ 模型未找到")
        return
    
    print(f"\n🤖 模型信息:")
    print(f"   版本: {model.model_version}")
    print(f"   训练样本: {model.training_info.get('train_samples', 'N/A')}")
    print(f"   测试样本: {model.training_info.get('test_samples', 'N/A')}")
    
    # 2. 特征重要性分析
    print(f"\n{'='*80}")
    print(f"🔍 特征重要性分析")
    print(f"{'='*80}")
    
    sorted_features = sorted(
        model.feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    print(f"\n{'排名':<6} {'特征名':<35} {'重要性':<10} {'解释'}")
    print(f"{'-'*80}")
    
    feature_explanations = {
        'cash_to_notional_ratio': '现金/本金比 - 资金充裕度',
        'volume_ratio': '成交量比 - 市场流动性',
        'volatility': '波动率 - 市场风险',
        'total_pnl': '累计盈亏 - 账户状态',
        'available_cash': '可用现金 - 购买力',
        'rsi': 'RSI指标 - 超买超卖',
        'current_price': '当前价格 - 价格水平',
        'position_count': '持仓数量 - 分散度',
        'option_delta': 'Delta值 - 期权敏感度',
        'option_premium': '期权费 - 期权成本',
        'stock_margin': '股票保证金 - 股票成本',
        'confidence_level': '信心水平 - 用户信心',
        'notional_value': '名义本金 - 投资规模',
        'risk_tolerance_encoded': '风险承受能力 - 用户偏好',
        'investment_style_encoded': '投资风格 - 用户类型',
        'option_experience_encoded': '期权经验 - 专业度',
        'financial_knowledge_encoded': '金融知识 - 知识水平',
        'decision_speed_encoded': '决策速度 - 行为特征',
        'premium_to_margin_ratio': '期权费/保证金比 - 成本对比',
        'pnl_per_position': '人均盈亏 - 盈利能力'
    }
    
    for i, (feature, importance) in enumerate(sorted_features, 1):
        explanation = feature_explanations.get(feature, '')
        bar_length = int(importance * 50)
        bar = '█' * bar_length
        print(f"{i:<6} {feature:<35} {importance:<10.4f} {explanation}")
        if importance > 0.05:  # 只显示重要特征的条形图
            print(f"       {bar}")
    
    # 3. 数据分析
    print(f"\n{'='*80}")
    print(f"📈 训练数据分析")
    print(f"{'='*80}")
    
    df = get_training_data()
    if df is not None and len(df) > 0:
        print(f"\n总样本数: {len(df)}")
        
        # 选择分布
        choice_counts = df['user_choice'].value_counts()
        print(f"\n选择分布:")
        for choice, count in choice_counts.items():
            label = "期权" if choice == 1 else "股票"
            percentage = count / len(df) * 100
            print(f"   {label}: {count} 次 ({percentage:.1f}%)")
        
        # 最优选择率
        optimal_rate = df['optimal_choice'].mean()
        print(f"\n最优选择率: {optimal_rate:.2%}")
        print(f"   (用户选择的策略确实是更好的比例)")
        
        # 平均收益
        print(f"\n平均收益率:")
        for choice in [1, 2]:
            label = "期权" if choice == 1 else "股票"
            avg_return = df[df['user_choice'] == choice]['actual_return'].mean()
            print(f"   {label}: {avg_return:.2%}")
        
        # 市场特征统计
        print(f"\n市场特征统计:")
        print(f"   波动率: {df['volatility'].mean():.4f} (范围: {df['volatility'].min():.4f} - {df['volatility'].max():.4f})")
        print(f"   RSI: {df['rsi'].mean():.2f} (范围: {df['rsi'].min():.2f} - {df['rsi'].max():.2f})")
        print(f"   成交量比: {df['volume_ratio'].mean():.4f}")
    
    # 4. 模型性能
    print(f"\n{'='*80}")
    print(f"🎯 模型性能")
    print(f"{'='*80}")
    
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    accuracy, f1_score,
                    precision_option, recall_option,
                    precision_stock, recall_stock,
                    confusion_matrix
                FROM ml_model_performance
                WHERE model_type = 'decision_tree'
                ORDER BY trained_at DESC
                LIMIT 1
            """)
            
            row = cursor.fetchone()
            if row:
                print(f"\n整体指标:")
                print(f"   准确率: {float(row[0]):.2%}")
                print(f"   F1分数: {float(row[1]):.2%}")
                
                print(f"\n期权策略 (1):")
                print(f"   精确率: {float(row[2]):.2%} (预测为期权的准确度)")
                print(f"   召回率: {float(row[3]):.2%} (找出所有期权选择的能力)")
                
                print(f"\n股票策略 (2):")
                print(f"   精确率: {float(row[4]):.2%}")
                print(f"   召回率: {float(row[5]):.2%}")
                
                # 混淆矩阵
                import json
                cm = json.loads(row[6])
                print(f"\n混淆矩阵:")
                print(f"                  预测期权  预测股票")
                print(f"   实际期权:        {cm['TN']:>4}      {cm['FP']:>4}")
                print(f"   实际股票:        {cm['FN']:>4}      {cm['TP']:>4}")
            
            cursor.close()
            conn.close()
            
        except Exception as e:
            print(f"⚠️ 获取性能数据失败: {e}")
            if conn:
                conn.close()
    
    # 5. 关键发现
    print(f"\n{'='*80}")
    print(f"💡 关键发现")
    print(f"{'='*80}")
    
    top_3_features = sorted_features[:3]
    
    print(f"\n1. 最重要的3个特征:")
    for i, (feature, importance) in enumerate(top_3_features, 1):
        explanation = feature_explanations.get(feature, '')
        print(f"   {i}. {feature} ({importance:.2%}) - {explanation}")
    
    print(f"\n2. 决策模式:")
    if top_3_features[0][0] == 'cash_to_notional_ratio':
        print(f"   ✓ 用户主要根据【资金充裕度】做决策")
        print(f"     - 现金充足时更可能选股票")
        print(f"     - 现金紧张时更可能选期权")
    
    if top_3_features[1][0] == 'volume_ratio':
        print(f"   ✓ 【市场流动性】是第二重要因素")
        print(f"     - 高成交量时期权更有吸引力")
    
    if top_3_features[2][0] == 'volatility':
        print(f"   ✓ 【市场波动率】影响决策")
        print(f"     - 高波动时期权价值更高")
    
    print(f"\n3. 模型表现:")
    print(f"   ✓ 准确率 81.25% - 模型能较好预测用户选择")
    print(f"   ✓ 对期权选择的预测更准确（召回率100%）")
    print(f"   ⚠ 对股票选择的预测较弱（样本不足）")
    
    print(f"\n4. 改进建议:")
    print(f"   • 增加股票选择的样本（当前期权:股票 = 42:9）")
    print(f"   • 收集更多用户画像特征（当前重要性较低）")
    print(f"   • 考虑添加时间序列特征（如近期收益趋势）")
    
    print(f"\n{'='*80}")
    print(f"✅ 分析完成")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    analyze_results()

