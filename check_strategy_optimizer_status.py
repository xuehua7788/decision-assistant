#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查策略优化器的集成状态
"""

import os
import sys

print("=" * 80)
print("🔍 策略优化器集成状态检查")
print("=" * 80)

# 1. 检查文件是否存在
print("\n1. 检查核心文件...")
files_to_check = [
    'backend/profile_based_strategy_optimizer.py',
    'backend/ai_profile_analyzer.py',
    'backend/profile_integration_helpers.py',
    'backend/profile_api_routes.py',
    'backend/app.py'
]

for file_path in files_to_check:
    exists = os.path.exists(file_path)
    status = "✅" if exists else "❌"
    print(f"   {status} {file_path}")

# 2. 检查app.py中的导入
print("\n2. 检查app.py中的集成...")
with open('backend/app.py', 'r', encoding='utf-8') as f:
    app_content = f.read()

checks = {
    'profile_api_routes导入': 'from profile_api_routes import profile_bp' in app_content,
    'profile_api注册': 'app.register_blueprint(profile_bp)' in app_content,
    'ProfileBasedStrategyOptimizer导入': 'ProfileBasedStrategyOptimizer' in app_content,
    'profile_integration_helpers导入': 'from profile_integration_helpers import' in app_content,
}

for check_name, result in checks.items():
    status = "✅" if result else "❌"
    print(f"   {status} {check_name}")

# 3. 检查策略优化器是否在聊天路由中使用
print("\n3. 检查策略优化器使用情况...")

if 'ProfileBasedStrategyOptimizer' not in app_content:
    print("   ⚠️  策略优化器未在app.py中导入")
    print("\n   💡 需要添加以下代码到app.py:")
    print("""
   # 在文件顶部导入区域添加:
   from profile_based_strategy_optimizer import ProfileBasedStrategyOptimizer
   from profile_integration_helpers import load_user_profile_from_db
   
   # 在聊天路由中使用:
   @app.route('/api/chat', methods=['POST'])
   def chat():
       ...
       # 1. 加载用户画像
       user_profile = load_user_profile_from_db(username)
       
       # 2. 如果触发策略生成
       if need_option_strategy:
           # 生成基础策略
           base_strategy = generate_strategy(...)
           
           # 3. 优化策略
           optimizer = ProfileBasedStrategyOptimizer()
           optimized_strategy = optimizer.optimize_strategy(
               base_strategy=base_strategy,
               user_profile=user_profile,
               parsed_intent=parsed_intent
           )
           
           return optimized_strategy
    """)
else:
    print("   ✅ 策略优化器已导入")

# 4. 查看用户画像API端点
print("\n4. 用户画像API端点:")
print("   GET  /api/profile/<username>           - 获取用户画像")
print("   POST /api/profile/<username>/analyze   - 触发画像分析")
print("   GET  /api/profile/<username>/recommendations - 获取推荐历史")

# 5. 数据库表
print("\n5. 数据库表结构:")
print("   📊 user_profiles - 存储用户画像")
print("      • username, risk_tolerance, investment_style")
print("      • option_experience, confidence_level")
print("      • ai_analysis (完整JSON)")
print("")
print("   📈 strategy_recommendations - 存储策略推荐")
print("      • username, strategy_type, strategy_parameters")
print("      • original_parameters, adjusted_parameters")
print("      • adjustment_reason, personalization_notes")

# 6. 查看工具
print("\n6. 查看数据的方法:")
print("   方法1: 使用API")
print("      curl https://decision-assistant-githubv3.onrender.com/api/profile/bbb")
print("")
print("   方法2: 使用查看脚本")
print("      python view_strategy_recommendations.py")
print("      python view_strategy_recommendations.py --user bbb")
print("      python view_strategy_recommendations.py --detail 1")
print("")
print("   方法3: 直接查询数据库")
print("      通过Render Dashboard -> PostgreSQL -> Connect")

# 7. 测试脚本
print("\n7. 测试脚本:")
print("   本地测试: python backend/test_profile_system.py")
print("   Render测试: python test_render_profile_api.py")

print("\n" + "=" * 80)
print("检查完成")
print("=" * 80)








