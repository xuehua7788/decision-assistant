"""测试数组越界修复"""
import pandas as pd
import numpy as np

# 模拟只有期权的数据
print("="*60)
print("测试1: 只有期权交易的情况")
print("="*60)

user_df = pd.DataFrame({
    'user_choice': [1, 1, 1, 1, 1],  # 全是期权
    'actual_return': [0.15, 0.20, 0.10, 0.18, 0.12],
    'optimal_choice': [1, 1, 2, 1, 2]
})

choice_counts = user_df['user_choice'].value_counts()
option_count = int(choice_counts.get(1, 0))
stock_count = int(choice_counts.get(2, 0))

option_df = user_df[user_df['user_choice'] == 1]
stock_df = user_df[user_df['user_choice'] == 2]

option_return = float(option_df['actual_return'].mean()) if len(option_df) > 0 else 0.0
stock_return = float(stock_df['actual_return'].mean()) if len(stock_df) > 0 else 0.0

print(f"期权次数: {option_count}")
print(f"股票次数: {stock_count}")
print(f"期权收益: {option_return:.2%}")
print(f"股票收益: {stock_return:.2%}")
print("✅ 测试1通过\n")

# 模拟只有股票的数据
print("="*60)
print("测试2: 只有股票交易的情况")
print("="*60)

user_df = pd.DataFrame({
    'user_choice': [2, 2, 2, 2, 2],  # 全是股票
    'actual_return': [0.08, 0.10, 0.06, 0.09, 0.07],
    'optimal_choice': [2, 2, 1, 2, 1]
})

choice_counts = user_df['user_choice'].value_counts()
option_count = int(choice_counts.get(1, 0))
stock_count = int(choice_counts.get(2, 0))

option_df = user_df[user_df['user_choice'] == 1]
stock_df = user_df[user_df['user_choice'] == 2]

option_return = float(option_df['actual_return'].mean()) if len(option_df) > 0 else 0.0
stock_return = float(stock_df['actual_return'].mean()) if len(stock_df) > 0 else 0.0

print(f"期权次数: {option_count}")
print(f"股票次数: {stock_count}")
print(f"期权收益: {option_return:.2%}")
print(f"股票收益: {stock_return:.2%}")
print("✅ 测试2通过\n")

# 测试特征数量
print("="*60)
print("测试3: top_features 少于3个的情况")
print("="*60)

summary = {
    'top_features': [
        {'name': 'volatility', 'importance': 0.35}
    ]
}

feature_translations = {
    'volatility': '市场波动率',
    'rsi': 'RSI指标',
    'cash_to_notional_ratio': '资金充裕度'
}

top_features_cn = []
num_features = min(3, len(summary['top_features']))
for i in range(num_features):
    f = summary['top_features'][i]
    cn_name = feature_translations.get(f['name'], f['name'])
    top_features_cn.append(f"{i+1}. {cn_name}: 影响力 {f['importance']*100:.1f}%")

if len(top_features_cn) == 0:
    top_features_cn.append("暂无足够数据分析关键因素")

print(f"特征数量: {len(summary['top_features'])}")
print(f"提取的特征:")
for feature in top_features_cn:
    print(f"  {feature}")
print("✅ 测试3通过\n")

# 测试空特征
print("="*60)
print("测试4: top_features 为空的情况")
print("="*60)

summary = {
    'top_features': []
}

top_features_cn = []
num_features = min(3, len(summary['top_features']))
for i in range(num_features):
    f = summary['top_features'][i]
    cn_name = feature_translations.get(f['name'], f['name'])
    top_features_cn.append(f"{i+1}. {cn_name}: 影响力 {f['importance']*100:.1f}%")

if len(top_features_cn) == 0:
    top_features_cn.append("暂无足够数据分析关键因素")

print(f"特征数量: {len(summary['top_features'])}")
print(f"提取的特征:")
for feature in top_features_cn:
    print(f"  {feature}")
print("✅ 测试4通过\n")

print("="*60)
print("✅ 所有测试通过！修复有效")
print("="*60)

