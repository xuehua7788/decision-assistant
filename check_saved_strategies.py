#!/usr/bin/env python3
"""检查已保存的策略"""
import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 80)
print("📊 检查已保存的策略")
print("=" * 80)
print()

try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        if data.get('status') == 'success':
            strategies = data.get('strategies', [])
            
            print(f"✅ 找到 {len(strategies)} 个已保存的策略")
            print()
            
            if strategies:
                for i, s in enumerate(strategies, 1):
                    print(f"策略 {i}:")
                    print(f"  ID: {s['strategy_id']}")
                    print(f"  股票: {s['symbol']} - {s.get('company_name', 'N/A')}")
                    print(f"  风格: {s['investment_style']}")
                    print(f"  建议: {s['recommendation']}")
                    print(f"  目标价: ${s['target_price']}")
                    print(f"  创建时间: {s['created_at']}")
                    
                    # 检查是否有期权策略
                    if s.get('option_strategy'):
                        opt = s['option_strategy']
                        print(f"  📊 期权策略: {opt.get('name', opt.get('strategy', {}).get('name', '已保存'))}")
                    
                    print()
            else:
                print("💡 还没有保存任何策略")
                print("   在 Stock Analysis 页面点击'✅ 接受期权策略并保存'来添加")
        else:
            print(f"❌ API错误: {data.get('message')}")
    else:
        print(f"❌ HTTP错误: {response.status_code}")
        
except Exception as e:
    print(f"❌ 错误: {e}")

print()
print("=" * 80)
print("💾 存储位置:")
print("  • 主存储: Render PostgreSQL 数据库")
print("  • 备份: backend/strategy_data/*.json")
print("=" * 80)

