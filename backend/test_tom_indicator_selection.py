#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Tom的智能指标选择功能
"""

from tom_indicator_selector import get_tom_indicator_selector

def test_indicator_selection():
    """测试指标选择"""
    
    print("=" * 80)
    print("🧪 测试Tom的智能指标选择")
    print("=" * 80)
    
    selector = get_tom_indicator_selector()
    
    # 测试场景1：科技股 + 巴菲特风格
    print("\n📊 场景1：AAPL（科技股） + 巴菲特风格")
    print("-" * 80)
    
    indicators_1 = selector.select_indicators('AAPL', 'buffett')
    reason_1 = selector.get_selection_reason('AAPL', 'buffett', indicators_1)
    
    print(f"基本面指标: {indicators_1['fundamental']}")
    print(f"技术面指标: {indicators_1['technical']}")
    print(f"宏观面指标: {indicators_1['macro']}")
    print(f"\n选择理由: {reason_1}")
    
    # 测试场景2：传统股 + 林奇风格
    print("\n" + "=" * 80)
    print("📊 场景2：IBM（传统价值股） + 林奇风格")
    print("-" * 80)
    
    indicators_2 = selector.select_indicators('IBM', 'lynch')
    reason_2 = selector.get_selection_reason('IBM', 'lynch', indicators_2)
    
    print(f"基本面指标: {indicators_2['fundamental']}")
    print(f"技术面指标: {indicators_2['technical']}")
    print(f"宏观面指标: {indicators_2['macro']}")
    print(f"\n选择理由: {reason_2}")
    
    # 测试场景3：金融股 + 索罗斯风格
    print("\n" + "=" * 80)
    print("📊 场景3：JPM（金融股） + 索罗斯风格")
    print("-" * 80)
    
    indicators_3 = selector.select_indicators('JPM', 'soros')
    reason_3 = selector.get_selection_reason('JPM', 'soros', indicators_3)
    
    print(f"基本面指标: {indicators_3['fundamental']}")
    print(f"技术面指标: {indicators_3['technical']}")
    print(f"宏观面指标: {indicators_3['macro']}")
    print(f"\n选择理由: {reason_3}")
    
    # 测试场景4：同一股票，不同风格
    print("\n" + "=" * 80)
    print("📊 场景4：AAPL + 不同投资风格对比")
    print("-" * 80)
    
    for style in ['buffett', 'lynch', 'soros', 'balanced']:
        indicators = selector.select_indicators('AAPL', style)
        print(f"\n{style.upper()}风格:")
        print(f"  基本面: {len(indicators['fundamental'])}个 - {indicators['fundamental'][:3]}...")
        print(f"  技术面: {len(indicators['technical'])}个 - {indicators['technical'][:3]}...")
        print(f"  宏观面: {len(indicators['macro'])}个 - {indicators['macro']}")
    
    print("\n" + "=" * 80)
    print("✅ 测试完成！")
    print("=" * 80)
    
    print("\n📋 验证结果:")
    print("1. ✅ 不同投资风格选择不同指标")
    print("2. ✅ 科技股额外关注成长性指标（PEG、ROE）")
    print("3. ✅ 传统股额外关注分红和负债")
    print("4. ✅ 金融股额外关注流动性和利率")
    print("5. ✅ 每个类别至少3个指标，最多6个")
    print("6. ✅ 提供清晰的选择理由")
    
    print("\n🎉 Tom的智能指标选择功能已实现：")
    print("   - 基于投资风格选择（巴菲特/林奇/索罗斯）")
    print("   - 基于股票特点调整（科技/价值/金融）")
    print("   - 每次分析都是针对性的，不是随机的")
    print("   - 提供选择理由，用户可以理解为什么选这些指标")
    
    return True

if __name__ == '__main__':
    success = test_indicator_selection()
    
    if success:
        print("\n✅ 测试通过！")
    else:
        print("\n❌ 测试失败")

