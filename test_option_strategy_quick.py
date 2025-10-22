"""
快速测试期权策略功能
"""

import sys
import os

# 添加backend到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_option_strategy():
    """测试期权策略处理器"""
    print("="*60)
    print("期权策略功能测试")
    print("="*60)
    print()
    
    try:
        from backend.option_strategy_handler import OptionStrategyHandler
        
        handler = OptionStrategyHandler()
        print("✅ 期权策略处理器加载成功")
        print()
        
        # 测试案例
        test_cases = [
            "我强烈看涨特斯拉股票，用什么策略？",
            "AAPL短期可能会下跌，保守一点",
            "英伟达震荡，激进策略",
        ]
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"\n{'='*60}")
            print(f"测试 {i}: {test_input}")
            print(f"{'='*60}")
            
            # 检测是否是期权请求
            is_option = handler.is_option_strategy_request(test_input)
            print(f"是期权请求: {is_option}")
            
            if is_option:
                # 处理请求
                result = handler.handle_option_strategy_request(test_input)
                
                if result['success']:
                    print("\n✅ 处理成功！")
                    print(f"\n置信度: {result['parsed_intent']['confidence']}")
                    print(f"策略名称: {result['strategy']['name']}")
                    print(f"策略类型: {result['strategy']['type']}")
                    print(f"风险等级: {result['strategy']['risk_level']}")
                    print(f"\nPayoff数据点数: {len(result['strategy']['payoff_data'])}")
                    
                    # 生成文字回复
                    text_response = handler.generate_text_response(result)
                    print(f"\n文字回复（前200字符）:")
                    print(text_response[:200] + "...")
                else:
                    print(f"\n❌ 处理失败: {result.get('error', 'Unknown error')}")
        
        print(f"\n{'='*60}")
        print("✅ 所有测试完成！")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    test_option_strategy()

