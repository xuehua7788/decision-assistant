#!/usr/bin/env python3
"""获取用户的历史策略"""
import requests
import json
from datetime import datetime

# API配置
RENDER_URL = "https://decision-assistant-backend.onrender.com"
LOCAL_URL = "http://localhost:5000"

# 选择使用哪个URL
API_URL = RENDER_URL  # 或者 LOCAL_URL

def get_all_strategies():
    """获取所有策略"""
    print("=" * 60)
    print("📊 获取所有历史策略")
    print("=" * 60)
    
    try:
        response = requests.get(f"{API_URL}/api/strategy/list", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                strategies = data.get('strategies', [])
                print(f"\n✅ 找到 {len(strategies)} 个策略\n")
                
                return strategies
            else:
                print(f"❌ 错误: {data.get('message')}")
                return []
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            print(f"响应: {response.text[:200]}")
            return []
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return []

def filter_strategies_by_user(strategies, user_identifier=None):
    """
    按用户筛选策略
    
    注意：当前系统没有用户ID字段，但可以通过以下方式筛选：
    - 按股票代码 (symbol)
    - 按投资风格 (investment_style)
    - 按创建时间 (created_at)
    """
    if not user_identifier:
        return strategies
    
    # 这里展示如何按不同条件筛选
    # 实际使用时根据需求调整
    
    filtered = strategies
    
    # 示例：按投资风格筛选
    if user_identifier.get('investment_style'):
        filtered = [s for s in filtered 
                   if s.get('investment_style') == user_identifier['investment_style']]
    
    # 示例：按股票代码筛选
    if user_identifier.get('symbol'):
        filtered = [s for s in filtered 
                   if s.get('symbol') == user_identifier['symbol']]
    
    # 示例：按时间范围筛选
    if user_identifier.get('start_date'):
        start = datetime.fromisoformat(user_identifier['start_date'])
        filtered = [s for s in filtered 
                   if datetime.fromisoformat(s['created_at']) >= start]
    
    return filtered

def display_strategy(strategy, index=None):
    """显示策略详情"""
    prefix = f"[{index}] " if index is not None else ""
    
    print(f"{prefix}{'=' * 55}")
    print(f"📌 策略ID: {strategy.get('strategy_id', 'N/A')}")
    print(f"📈 股票: {strategy.get('symbol', 'N/A')} - {strategy.get('company_name', 'N/A')}")
    print(f"🎯 投资风格: {strategy.get('investment_style', 'N/A')}")
    print(f"💡 推荐: {strategy.get('recommendation', 'N/A')}")
    print(f"⭐ 评分: {strategy.get('score', 'N/A')}")
    print(f"💰 当前价: ${strategy.get('current_price', 0):.2f}")
    
    if strategy.get('target_price'):
        print(f"🎯 目标价: ${strategy.get('target_price'):.2f}")
    if strategy.get('stop_loss'):
        print(f"🛑 止损价: ${strategy.get('stop_loss'):.2f}")
    if strategy.get('position_size'):
        print(f"📊 仓位: {strategy.get('position_size')}%")
    
    print(f"📅 创建时间: {strategy.get('created_at', 'N/A')}")
    print(f"📊 状态: {strategy.get('status', 'N/A')}")
    
    # 期权策略
    if strategy.get('option_strategy'):
        opt = strategy['option_strategy']
        print(f"\n🎲 期权策略:")
        print(f"   名称: {opt.get('name', 'N/A')}")
        print(f"   类型: {opt.get('type', 'N/A')}")
        if opt.get('parameters'):
            params = opt['parameters']
            print(f"   当前价: ${params.get('current_price', 0):.2f}")
            if params.get('buy_strike'):
                print(f"   买入行权价: ${params.get('buy_strike'):.2f}")
            if params.get('sell_strike'):
                print(f"   卖出行权价: ${params.get('sell_strike'):.2f}")
            if params.get('expiry_days'):
                print(f"   到期天数: {params.get('expiry_days')}天")
    
    print()

def evaluate_strategy(strategy_id):
    """评估单个策略"""
    print(f"\n🔍 评估策略: {strategy_id}")
    print("-" * 60)
    
    try:
        response = requests.get(
            f"{API_URL}/api/strategy/{strategy_id}/evaluate",
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            
            if data.get('status') == 'success':
                eval_data = data.get('evaluation', {})
                
                print(f"✅ 评估成功")
                print(f"   当前价格: ${eval_data.get('current_price', 0):.2f}")
                print(f"   接受时价格: ${eval_data.get('accepted_price', 0):.2f}")
                print(f"   实际收益: {eval_data.get('actual_return', 0):.2f}%")
                print(f"   策略收益: {eval_data.get('strategy_return', 0):.2f}%")
                print(f"   超额表现: {eval_data.get('outperformance', 0):.2f}%")
                print(f"   持有天数: {eval_data.get('days_held', 0)}")
                
                return eval_data
            else:
                print(f"❌ 评估失败: {data.get('message')}")
                return None
        else:
            print(f"❌ HTTP错误: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ 错误: {e}")
        return None

def main():
    """主函数"""
    # 1. 获取所有策略
    strategies = get_all_strategies()
    
    if not strategies:
        print("\n⚠️  没有找到任何策略")
        return
    
    # 2. 显示所有策略
    print("📋 策略列表:")
    print("=" * 60)
    for i, strategy in enumerate(strategies, 1):
        display_strategy(strategy, i)
    
    # 3. 示例：筛选特定条件的策略
    print("\n" + "=" * 60)
    print("🔍 筛选示例")
    print("=" * 60)
    
    # 示例1：只看巴菲特风格的策略
    buffett_strategies = filter_strategies_by_user(
        strategies, 
        {'investment_style': 'buffett'}
    )
    print(f"\n💼 巴菲特风格策略: {len(buffett_strategies)} 个")
    
    # 示例2：只看某个股票的策略
    aapl_strategies = filter_strategies_by_user(
        strategies,
        {'symbol': 'AAPL'}
    )
    print(f"🍎 AAPL策略: {len(aapl_strategies)} 个")
    
    # 4. 评估第一个策略（如果有）
    if strategies:
        print("\n" + "=" * 60)
        print("📊 策略表现评估")
        print("=" * 60)
        
        first_strategy = strategies[0]
        strategy_id = first_strategy.get('strategy_id')
        
        if strategy_id:
            evaluate_strategy(strategy_id)
    
    # 5. 导出为JSON（可选）
    export_choice = input("\n是否导出为JSON文件？(y/n): ").strip().lower()
    if export_choice == 'y':
        filename = f"strategies_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(strategies, f, ensure_ascii=False, indent=2)
        print(f"✅ 已导出到: {filename}")

if __name__ == "__main__":
    main()


