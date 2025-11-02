#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试投资风格功能
"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from stock_analysis.investment_styles import get_available_styles, get_style_prompt

def test_get_styles():
    """测试获取投资风格列表"""
    print("=" * 60)
    print("测试：获取可用投资风格")
    print("=" * 60)
    
    styles = get_available_styles()
    
    print(f"\n✅ 找到 {len(styles)} 个投资风格：\n")
    
    for style in styles:
        print(f"{style['icon']} {style['name']} ({style['name_en']})")
        print(f"   描述：{style['description']}")
        print(f"   ID: {style['id']}")
        print()

def test_get_prompt():
    """测试获取提示词"""
    print("=" * 60)
    print("测试：获取巴菲特风格提示词")
    print("=" * 60)
    
    prompt = get_style_prompt('buffett', 'AAPL', 'Apple Inc.')
    
    print("\n提示词预览（前500字符）：\n")
    print(prompt[:500])
    print("\n...")
    print(f"\n✅ 提示词长度：{len(prompt)} 字符")

def test_all_styles():
    """测试所有风格的提示词"""
    print("\n" + "=" * 60)
    print("测试：所有投资风格的提示词")
    print("=" * 60)
    
    styles = ['buffett', 'lynch', 'soros']
    
    for style in styles:
        prompt = get_style_prompt(style, 'AAPL', 'Apple Inc.')
        print(f"\n{style.upper()}:")
        print(f"  ✅ 提示词长度：{len(prompt)} 字符")
        print(f"  ✅ 包含'分析框架'：{'分析框架' in prompt}")
        print(f"  ✅ 包含'JSON'：{'JSON' in prompt}")

if __name__ == "__main__":
    print("\n🧪 投资风格功能测试\n")
    
    try:
        test_get_styles()
        test_get_prompt()
        test_all_styles()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

