#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
让Tom分析决策树模型结果
"""

import os
import openai
from ml_decision_tree import DecisionTreeModel
from ml_feature_extraction import get_training_data
import json

# 设置OpenAI API
openai.api_key = os.getenv('OPENAI_API_KEY')

def get_model_summary():
    """获取模型摘要数据"""
    model = DecisionTreeModel.load_model()
    if not model:
        return None
    
    df = get_training_data()
    if df is None or len(df) == 0:
        return None
    
    # 特征重要性
    top_features = sorted(
        model.feature_importance.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]
    
    # 选择分布
    choice_counts = df['user_choice'].value_counts()
    option_count = choice_counts.get(1, 0)
    stock_count = choice_counts.get(2, 0)
    
    # 平均收益
    option_return = df[df['user_choice'] == 1]['actual_return'].mean()
    stock_return = df[df['user_choice'] == 2]['actual_return'].mean()
    
    # 最优选择率
    optimal_rate = df['optimal_choice'].mean()
    
    summary = {
        'model_version': model.model_version,
        'train_samples': model.training_info.get('train_samples', 0),
        'test_samples': model.training_info.get('test_samples', 0),
        'total_samples': len(df),
        'accuracy': 0.8125,  # 从训练结果
        'f1_score': 0.7284,
        'top_features': [
            {'name': name, 'importance': float(importance), 'rank': i+1}
            for i, (name, importance) in enumerate(top_features)
        ],
        'choice_distribution': {
            'option': int(option_count),
            'stock': int(stock_count),
            'option_percentage': float(option_count / len(df) * 100),
            'stock_percentage': float(stock_count / len(df) * 100)
        },
        'average_returns': {
            'option': float(option_return),
            'stock': float(stock_return)
        },
        'optimal_choice_rate': float(optimal_rate),
        'market_stats': {
            'avg_volatility': float(df['volatility'].mean()),
            'avg_rsi': float(df['rsi'].mean()),
            'volatility_range': [float(df['volatility'].min()), float(df['volatility'].max())]
        }
    }
    
    return summary


def ask_tom_to_analyze(summary):
    """让Tom分析模型结果"""
    
    prompt = f"""你是一位专业的量化分析师Tom。请分析以下决策树模型的训练结果，并给出简短的分析和建议。

## 模型训练结果

**基本信息：**
- 总样本数：{summary['total_samples']} 个已平仓交易
- 训练集：{summary['train_samples']} 样本
- 测试集：{summary['test_samples']} 样本
- 模型准确率：{summary['accuracy']:.2%}
- F1分数：{summary['f1_score']:.2%}

**用户决策分布：**
- 选择期权：{summary['choice_distribution']['option']} 次 ({summary['choice_distribution']['option_percentage']:.1f}%)
- 选择股票：{summary['choice_distribution']['stock']} 次 ({summary['choice_distribution']['stock_percentage']:.1f}%)

**平均收益率：**
- 期权策略：{summary['average_returns']['option']:.2%}
- 股票策略：{summary['average_returns']['stock']:.2%}

**最优选择率：**
- {summary['optimal_choice_rate']:.2%} (用户选择确实是更好策略的比例)

**Top 5 特征重要性：**
{chr(10).join([f"{i}. {f['name']}: {f['importance']:.2%}" for i, f in enumerate(summary['top_features'], 1)])}

**市场环境：**
- 平均波动率：{summary['market_stats']['avg_volatility']:.4f}
- 平均RSI：{summary['market_stats']['avg_rsi']:.2f}
- 波动率范围：{summary['market_stats']['volatility_range'][0]:.4f} - {summary['market_stats']['volatility_range'][1]:.4f}

---

请从以下角度给出分析：
1. **模型表现评价**（准确率是否可接受？）
2. **用户行为洞察**（用户为什么更倾向期权？）
3. **特征重要性解读**（为什么这些特征最重要？）
4. **风险提示**（模型有什么局限性？）
5. **改进建议**（如何提升模型效果？）

要求：
- 语言简洁专业，每个角度2-3句话
- 突出关键发现
- 给出可操作的建议
- 总字数控制在400字以内
"""

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是Tom，一位专业的量化分析师和AI算法专家。你擅长解读机器学习模型结果，并给出实用的投资建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        analysis = response.choices[0].message.content
        return analysis
        
    except Exception as e:
        print(f"❌ Tom分析失败: {e}")
        return None


def main():
    print(f"\n{'='*80}")
    print(f"🤖 Tom的决策树模型分析")
    print(f"{'='*80}\n")
    
    # 1. 获取模型摘要
    print(f"📊 正在收集模型数据...")
    summary = get_model_summary()
    
    if not summary:
        print(f"❌ 无法获取模型数据")
        return
    
    print(f"✅ 数据收集完成")
    print(f"   - 总样本: {summary['total_samples']}")
    print(f"   - 准确率: {summary['accuracy']:.2%}")
    print(f"   - Top特征: {summary['top_features'][0]['name']}")
    
    # 2. 让Tom分析
    print(f"\n🔍 Tom正在分析...")
    analysis = ask_tom_to_analyze(summary)
    
    if not analysis:
        print(f"❌ Tom分析失败")
        return
    
    # 3. 显示分析结果
    print(f"\n{'='*80}")
    print(f"💡 Tom的分析报告")
    print(f"{'='*80}\n")
    print(analysis)
    print(f"\n{'='*80}\n")
    
    # 4. 保存到文件
    output = {
        'timestamp': summary['model_version'],
        'summary': summary,
        'tom_analysis': analysis
    }
    
    with open('tom_ml_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 分析结果已保存到: tom_ml_analysis.json\n")


if __name__ == "__main__":
    main()

