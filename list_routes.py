#!/usr/bin/env python3
import sys
sys.path.insert(0, 'backend')

from app import app

print("="*60)
print("所有注册的路由:")
print("="*60)

for rule in app.url_map.iter_rules():
    print(f"{rule.rule:50} {list(rule.methods)}")

print("\n" + "="*60)
print("策略相关路由:")
print("="*60)

strategy_routes = [rule for rule in app.url_map.iter_rules() if 'strategy' in rule.rule]
if strategy_routes:
    for rule in strategy_routes:
        print(f"✅ {rule.rule:50} {list(rule.methods)}")
else:
    print("❌ 没有找到任何策略路由！")


