#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户画像系统完整测试脚本
测试所有组件是否正常工作
"""

import os
import sys
from datetime import datetime

def test_environment():
    """测试环境变量"""
    print("=" * 70)
    print("1. 测试环境变量")
    print("=" * 70)
    
    required_vars = ['DATABASE_URL', 'DEEPSEEK_API_KEY']
    all_set = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            masked = value[:10] + "..." if len(value) > 10 else value
            print(f"   ✅ {var}: {masked}")
        else:
            print(f"   ❌ {var}: 未设置")
            all_set = False
    
    print()
    return all_set


def test_database_connection():
    """测试数据库连接"""
    print("=" * 70)
    print("2. 测试数据库连接")
    print("=" * 70)
    
    try:
        from profile_integration_helpers import get_db_connection
        
        conn = get_db_connection()
        if conn:
            print("   ✅ 数据库连接成功")
            conn.close()
            return True
        else:
            print("   ❌ 数据库连接失败")
            return False
    except Exception as e:
        print(f"   ❌ 数据库连接失败: {e}")
        return False
    finally:
        print()


def test_database_tables():
    """测试数据库表是否存在"""
    print("=" * 70)
    print("3. 测试数据库表")
    print("=" * 70)
    
    try:
        from profile_integration_helpers import get_db_connection
        
        conn = get_db_connection()
        if not conn:
            print("   ❌ 无法连接数据库")
            return False
        
        cursor = conn.cursor()
        
        required_tables = ['user_profiles', 'strategy_recommendations', 'chat_sessions', 'chat_messages']
        all_exist = True
        
        for table in required_tables:
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """, (table,))
            
            exists = cursor.fetchone()[0]
            if exists:
                print(f"   ✅ {table}")
            else:
                print(f"   ❌ {table} (不存在)")
                all_exist = False
        
        cursor.close()
        conn.close()
        print()
        return all_exist
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        print()
        return False


def test_ai_analyzer():
    """测试AI #3分析器"""
    print("=" * 70)
    print("4. 测试AI #3分析器")
    print("=" * 70)
    
    try:
        from ai_profile_analyzer import get_profile_analyzer
        
        analyzer = get_profile_analyzer()
        print("   ✅ AI #3分析器初始化成功")
        
        # 测试分析（使用模拟数据）
        test_chat = [
            {"role": "user", "content": "我想了解特斯拉", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "特斯拉是...", "timestamp": datetime.now().isoformat()},
            {"role": "user", "content": "我比较保守", "timestamp": datetime.now().isoformat()},
            {"role": "assistant", "content": "理解", "timestamp": datetime.now().isoformat()},
            {"role": "user", "content": "期权是什么", "timestamp": datetime.now().isoformat()},
        ]
        
        print("   🔄 执行测试分析（这可能需要10-30秒）...")
        profile = analyzer.analyze_user_profile("test_user", test_chat, days=30)
        
        if profile.get('status') == 'error':
            print(f"   ⚠️ AI分析返回错误: {profile.get('message')}")
            return False
        elif profile.get('investment_preferences'):
            print("   ✅ AI分析成功")
            print(f"      风险偏好: {profile.get('investment_preferences', {}).get('risk_tolerance')}")
            print(f"      期权经验: {profile.get('knowledge_level', {}).get('option_experience')}")
            return True
        else:
            print("   ⚠️ AI分析返回格式异常")
            return False
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        print()


def test_strategy_optimizer():
    """测试策略优化器"""
    print("=" * 70)
    print("5. 测试策略优化器")
    print("=" * 70)
    
    try:
        from profile_based_strategy_optimizer import ProfileBasedStrategyOptimizer
        
        optimizer = ProfileBasedStrategyOptimizer()
        print("   ✅ 策略优化器初始化成功")
        
        # 模拟数据
        base_strategy = {
            "name": "Bull Call Spread",
            "type": "bull_call_spread",
            "description": "测试策略",
            "parameters": {
                "ticker": "TSLA",
                "current_price": 250.0,
                "strike": 260.0,
                "quantity": 5
            }
        }
        
        user_profile = {
            "investment_preferences": {"risk_tolerance": "conservative"},
            "knowledge_level": {"option_experience": "basic"},
            "emotional_traits": {"confidence_level": 0.5},
            "behavioral_traits": {"decision_speed": "moderate"},
            "recommendations": {}
        }
        
        parsed_intent = {"direction": "bullish"}
        
        optimized = optimizer.optimize_strategy(base_strategy, user_profile, parsed_intent)
        
        if optimized and optimized.get('parameters'):
            print("   ✅ 策略优化成功")
            print(f"      原始仓位: {base_strategy['parameters']['quantity']}")
            print(f"      优化仓位: {optimized['parameters']['quantity']}")
            return True
        else:
            print("   ❌ 策略优化失败")
            return False
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    finally:
        print()


def test_integration_helpers():
    """测试集成辅助函数"""
    print("=" * 70)
    print("6. 测试集成辅助函数")
    print("=" * 70)
    
    try:
        from profile_integration_helpers import (
            load_user_profile_from_db,
            load_chat_history_from_db,
            check_profile_freshness
        )
        
        print("   ✅ 辅助函数导入成功")
        
        # 测试加载（可能返回None，但不应该报错）
        profile = load_user_profile_from_db("test_user")
        print(f"   ✅ load_user_profile_from_db: {'有数据' if profile else '无数据（正常）'}")
        
        history = load_chat_history_from_db("test_user", days=7)
        print(f"   ✅ load_chat_history_from_db: {len(history)} 条消息")
        
        fresh = check_profile_freshness("test_user")
        print(f"   ✅ check_profile_freshness: {'新鲜' if fresh else '需要更新'}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ 测试失败: {e}")
        return False
    finally:
        print()


def main():
    """主测试函数"""
    print("\n")
    print("=" * 70)
    print("用户画像系统完整测试")
    print("=" * 70)
    print()
    
    results = {}
    
    # 执行所有测试
    results['environment'] = test_environment()
    results['database_connection'] = test_database_connection()
    results['database_tables'] = test_database_tables()
    results['integration_helpers'] = test_integration_helpers()
    results['strategy_optimizer'] = test_strategy_optimizer()
    
    # AI分析测试（可选，因为需要API调用）
    if os.getenv('DEEPSEEK_API_KEY'):
        results['ai_analyzer'] = test_ai_analyzer()
    else:
        print("⚠️ 跳过AI分析测试（DEEPSEEK_API_KEY未设置）\n")
        results['ai_analyzer'] = None
    
    # 输出总结
    print("=" * 70)
    print("测试总结")
    print("=" * 70)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result is True else ("❌ 失败" if result is False else "⏭️ 跳过")
        print(f"   {status}: {test_name}")
    
    print()
    print(f"总计: {total} 项测试")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"⏭️ 跳过: {skipped}")
    print()
    
    if failed == 0:
        print("🎉 所有测试通过！系统已准备就绪。")
        print()
        print("下一步:")
        print("1. 运行: python scheduled_profile_analysis.py --user <username>")
        print("2. 或集成到app.py中使用")
        return 0
    else:
        print("⚠️ 部分测试失败，请检查上述错误信息。")
        print()
        print("常见问题:")
        print("1. 数据库连接失败 → 检查DATABASE_URL环境变量")
        print("2. 表不存在 → 运行: python create_user_profile_tables.py")
        print("3. AI分析失败 → 检查DEEPSEEK_API_KEY环境变量")
        return 1


if __name__ == "__main__":
    sys.exit(main())

