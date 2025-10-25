#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务：自动分析用户画像
可以使用cron或其他任务调度器定期运行此脚本
"""

import os
import sys
from datetime import datetime, timedelta
from profile_integration_helpers import get_db_connection, load_chat_history_from_db
from ai_profile_analyzer import get_profile_analyzer

def analyze_all_active_users(days_threshold=7, min_messages=5):
    """
    分析所有活跃用户的画像
    
    Args:
        days_threshold: 多少天内有活动算作活跃用户
        min_messages: 最少消息数量
    """
    print("=" * 70)
    print(f"定时用户画像分析任务 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    print()
    
    conn = get_db_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 获取所有活跃用户
        cutoff_date = datetime.now() - timedelta(days=days_threshold)
        cursor.execute("""
            SELECT DISTINCT cs.username, COUNT(cm.id) as message_count
            FROM chat_sessions cs
            JOIN chat_messages cm ON cm.session_id = cs.id
            WHERE cm.created_at > %s
            AND cs.username IS NOT NULL
            AND cs.username != ''
            GROUP BY cs.username
            HAVING COUNT(cm.id) >= %s
            ORDER BY message_count DESC
        """, (cutoff_date, min_messages))
        
        active_users = cursor.fetchall()
        print(f"📊 找到 {len(active_users)} 个活跃用户（最近{days_threshold}天内有{min_messages}+条消息）")
        print()
        
        if len(active_users) == 0:
            print("ℹ️ 没有需要分析的用户")
            cursor.close()
            conn.close()
            return True
        
        # 获取画像分析器
        analyzer = get_profile_analyzer()
        
        success_count = 0
        skip_count = 0
        error_count = 0
        
        for username, message_count in active_users:
            print(f"{'='*70}")
            print(f"分析用户: {username} ({message_count} 条消息)")
            print(f"{'='*70}")
            
            try:
                # 检查是否需要更新（如果最近7天内已分析过，跳过）
                cursor.execute("""
                    SELECT last_analyzed_at 
                    FROM user_profiles 
                    WHERE username = %s
                """, (username,))
                
                result = cursor.fetchone()
                if result and result[0]:
                    last_analyzed = result[0]
                    age = datetime.now() - last_analyzed
                    if age.days < 7:
                        print(f"   ⏭️ 跳过（{age.days}天前已分析）")
                        skip_count += 1
                        continue
                
                # 加载聊天历史
                chat_history = load_chat_history_from_db(username, days=30)
                
                if len(chat_history) < min_messages:
                    print(f"   ⚠️ 聊天记录不足（{len(chat_history)} 条）")
                    error_count += 1
                    continue
                
                # 分析画像
                profile = analyzer.analyze_user_profile(
                    username=username,
                    chat_history=chat_history,
                    days=30
                )
                
                # 保存到数据库
                if profile.get('status') not in ['error', 'insufficient_data']:
                    analyzer.update_user_profile_in_db(conn, username, profile)
                    print(f"   ✅ 分析完成")
                    success_count += 1
                else:
                    print(f"   ❌ 分析失败: {profile.get('message', 'Unknown error')}")
                    error_count += 1
                
            except Exception as e:
                print(f"   ❌ 处理失败: {e}")
                error_count += 1
                continue
        
        cursor.close()
        conn.close()
        
        # 输出统计
        print()
        print("=" * 70)
        print("分析完成统计:")
        print("=" * 70)
        print(f"✅ 成功: {success_count}")
        print(f"⏭️ 跳过: {skip_count}")
        print(f"❌ 失败: {error_count}")
        print(f"📊 总计: {len(active_users)}")
        print()
        
        return True
        
    except Exception as e:
        print(f"❌ 定时任务失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False


def analyze_single_user(username, force=False):
    """
    分析单个用户的画像
    
    Args:
        username: 用户名
        force: 是否强制重新分析
    """
    print("=" * 70)
    print(f"单用户画像分析 - {username}")
    print("=" * 70)
    print()
    
    conn = get_db_connection()
    if not conn:
        print("❌ 数据库连接失败")
        return False
    
    try:
        # 检查是否需要更新
        if not force:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT last_analyzed_at 
                FROM user_profiles 
                WHERE username = %s
            """, (username,))
            
            result = cursor.fetchone()
            cursor.close()
            
            if result and result[0]:
                last_analyzed = result[0]
                age = datetime.now() - last_analyzed
                if age.days < 1:
                    print(f"⏭️ 用户画像很新（{age.days}天前分析），使用 --force 强制重新分析")
                    conn.close()
                    return True
        
        # 加载聊天历史
        chat_history = load_chat_history_from_db(username, days=30)
        
        if len(chat_history) < 5:
            print(f"❌ 聊天记录不足（{len(chat_history)} 条），需要至少5条")
            conn.close()
            return False
        
        # 分析画像
        analyzer = get_profile_analyzer()
        profile = analyzer.analyze_user_profile(
            username=username,
            chat_history=chat_history,
            days=30
        )
        
        # 保存到数据库
        if profile.get('status') not in ['error', 'insufficient_data']:
            analyzer.update_user_profile_in_db(conn, username, profile)
            print()
            print("✅ 分析完成")
            print()
            print("画像摘要:")
            print(f"  - 风险偏好: {profile.get('investment_preferences', {}).get('risk_tolerance')}")
            print(f"  - 期权经验: {profile.get('knowledge_level', {}).get('option_experience')}")
            print(f"  - 投资风格: {profile.get('investment_preferences', {}).get('investment_style')}")
            print(f"  - 分析消息数: {profile.get('metadata', {}).get('total_messages_analyzed')}")
            conn.close()
            return True
        else:
            print(f"❌ 分析失败: {profile.get('message', 'Unknown error')}")
            conn.close()
            return False
        
    except Exception as e:
        print(f"❌ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='用户画像定时分析任务')
    parser.add_argument('--user', type=str, help='分析指定用户')
    parser.add_argument('--force', action='store_true', help='强制重新分析')
    parser.add_argument('--all', action='store_true', help='分析所有活跃用户')
    parser.add_argument('--days', type=int, default=7, help='活跃用户的天数阈值（默认7天）')
    parser.add_argument('--min-messages', type=int, default=5, help='最少消息数（默认5条）')
    
    args = parser.parse_args()
    
    if args.user:
        # 分析单个用户
        success = analyze_single_user(args.user, force=args.force)
        sys.exit(0 if success else 1)
    elif args.all:
        # 分析所有活跃用户
        success = analyze_all_active_users(
            days_threshold=args.days,
            min_messages=args.min_messages
        )
        sys.exit(0 if success else 1)
    else:
        # 默认：分析所有活跃用户
        print("提示: 使用 --user <username> 分析单个用户，或 --all 分析所有用户")
        print()
        success = analyze_all_active_users()
        sys.exit(0 if success else 1)

