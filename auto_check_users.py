#!/usr/bin/env python3
"""
自动化用户查询脚本
尝试多种方式自动获取用户信息，无需手动输入
"""
import os
import sys
import json

print("\n" + "=" * 80)
print("🤖 自动化用户查询")
print("=" * 80)

# ========================================
# 方法1：本地 JSON 文件
# ========================================
print("\n【方法1】本地文件查询")
print("-" * 80)

json_file = 'backend/users_data.json'
local_users = []

if os.path.exists(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            users_data = json.load(f)
        
        print(f"✅ 找到本地文件")
        print(f"📊 用户数: {len(users_data)}\n")
        
        for username in users_data.keys():
            local_users.append(username)
            print(f"   👤 {username}")
        
    except Exception as e:
        print(f"⚠️  读取失败: {e}")
else:
    print(f"❌ 文件不存在")

# ========================================
# 方法2：尝试从环境变量获取 DATABASE_URL
# ========================================
print("\n【方法2】环境变量 DATABASE_URL")
print("-" * 80)

database_url = os.getenv('DATABASE_URL')

if database_url:
    print("✅ 找到 DATABASE_URL")
    print(f"📍 主机: {database_url.split('@')[1].split('/')[0] if '@' in database_url else 'N/A'}")
    
    try:
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        print("\n🔌 连接数据库...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # 查询所有用户
        cursor.execute("""
            SELECT username, email, created_at
            FROM users
            ORDER BY created_at DESC
        """)
        
        db_users = cursor.fetchall()
        
        print(f"✅ 数据库查询成功")
        print(f"📊 用户数: {len(db_users)}\n")
        
        for user in db_users:
            print(f"   👤 {user['username']}")
            print(f"      邮箱: {user['email'] or '(无)'}")
            print(f"      注册: {user['created_at']}")
        
        # 检查 bbb 用户
        print(f"\n🔍 查找 bbb 用户...")
        cursor.execute("SELECT * FROM users WHERE username = 'bbb'")
        bbb = cursor.fetchone()
        
        if bbb:
            print(f"   ✅ 找到 bbb 用户！")
            print(f"      用户ID: {bbb['user_id']}")
            print(f"      注册时间: {bbb['created_at']}")
        else:
            print(f"   ❌ 数据库中没有 bbb 用户")
        
        # 查询策略表
        print(f"\n📊 策略表信息...")
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                COUNT(CASE WHEN username IS NOT NULL THEN 1 END) as with_user
            FROM accepted_strategies
        """)
        
        stats = cursor.fetchone()
        print(f"   总策略数: {stats['total']}")
        print(f"   关联用户: {stats['with_user']}")
        print(f"   未关联: {stats['total'] - stats['with_user']}")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        print("\n⚠️  psycopg2 未安装")
        print("   运行: pip install psycopg2-binary")
    except Exception as e:
        print(f"\n❌ 数据库连接失败: {e}")
else:
    print("⚠️  未设置 DATABASE_URL 环境变量")

# ========================================
# 方法3：通过 API 测试注册
# ========================================
print("\n【方法3】Render API 测试")
print("-" * 80)

try:
    import requests
    import time
    
    RENDER_URL = "https://decision-assistant-backend.onrender.com"
    
    # 测试健康检查
    print("🏥 检查后端状态...")
    response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=10)
    
    if response.status_code == 200:
        print("✅ 后端在线\n")
        
        # 尝试注册测试用户
        test_user = f"autotest_{int(time.time())}"
        
        print(f"📝 注册测试用户: {test_user}")
        reg_response = requests.post(
            f"{RENDER_URL}/api/auth/register",
            json={
                "username": test_user,
                "password": "test123456"
            },
            timeout=15
        )
        
        if reg_response.status_code == 200:
            data = reg_response.json()
            print(f"   ✅ 注册成功")
            print(f"   用户名: {data.get('username')}")
            print(f"   说明：用户数据已保存到数据库")
        elif reg_response.status_code == 400:
            print(f"   ⚠️  {reg_response.json().get('detail', '注册失败')}")
        else:
            print(f"   ❌ 状态码: {reg_response.status_code}")
        
    else:
        print(f"⚠️  后端状态: {response.status_code}")
        
except ImportError:
    print("⚠️  requests 未安装")
    print("   运行: pip install requests")
except requests.exceptions.Timeout:
    print("⏱️  请求超时（可能是网络问题）")
except Exception as e:
    print(f"⚠️  API请求失败: {e}")

# ========================================
# 总结
# ========================================
print("\n" + "=" * 80)
print("📋 总结")
print("=" * 80)

print("\n✅ 可以确认的信息：")
print(f"   1. 本地文件中有 {len(local_users)} 个用户: {', '.join(local_users)}")

if database_url:
    print(f"   2. 数据库连接可用")
    print(f"   3. 已查询数据库中的用户")
else:
    print(f"   2. 未设置 DATABASE_URL（无法查询数据库）")

print("\n❓ 关于 bbb 用户：")

if database_url:
    print("   已从数据库查询，结果见上方")
else:
    print("   ⚠️  需要 DATABASE_URL 才能查询数据库")
    print("   可能的情况：")
    print("      a) bbb 在数据库中（需要 DATABASE_URL 查询）")
    print("      b) bbb 注册失败（数据库不可用时）")
    print("      c) 用户名记错了（实际是 bx 不是 bbb）")

print("\n💡 下一步建议：")

if not database_url:
    print("   1. 设置 DATABASE_URL 环境变量")
    print("   2. 或在 Render Shell 运行此脚本")
    print("   3. 或手动在 Render Dashboard 查询数据库")
else:
    print("   1. 运行数据库迁移（如果策略未关联用户）")
    print("      python migrate_add_user_columns.py")
    print("   2. 测试新的用户策略查询API")
    print("      python test_user_fix.py")

print("\n" + "=" * 80)


