#!/usr/bin/env python3
"""立即查看用户注册信息"""
import json
import os

print("\n" + "=" * 80)
print("👥 查看用户注册信息")
print("=" * 80)

# 方法1：检查本地JSON文件
print("\n【方法1】本地 JSON 文件")
print("-" * 80)

json_file = 'backend/users_data.json'

if os.path.exists(json_file):
    try:
        with open(json_file, 'r', encoding='utf-8') as f:
            users = json.load(f)
        
        print(f"✅ 找到文件: {json_file}")
        print(f"📊 用户数量: {len(users)}")
        print()
        
        for i, (username, info) in enumerate(users.items(), 1):
            print(f"[{i}] 用户名: {username}")
            
            # 检查是否有password字段（新格式）
            if 'password' in info:
                print(f"    密码: {info['password'][:20]}...")
                print(f"    创建时间: {info.get('created_at', 'N/A')[:20]}...")
            # 或者是hashed_password（旧格式）
            elif 'hashed_password' in info:
                print(f"    密码哈希: {info['hashed_password'][:20]}...")
                print(f"    状态: {'激活' if info.get('is_active') else '未激活'}")
            
            print()
    except Exception as e:
        print(f"❌ 读取失败: {e}")
else:
    print(f"❌ 文件不存在: {json_file}")

# 方法2：通过API查询（需要网络）
print("\n【方法2】从 Render API 查询")
print("-" * 80)

try:
    import requests
    
    # 尝试健康检查
    response = requests.get(
        "https://decision-assistant-backend.onrender.com/api/stock/health",
        timeout=10
    )
    
    if response.status_code == 200:
        print("✅ Render 后端在线")
        
        # 尝试注册一个测试用户查看效果
        print("\n📝 测试注册功能...")
        
        import time
        test_user = f"check_{int(time.time())}"
        
        reg_response = requests.post(
            "https://decision-assistant-backend.onrender.com/api/auth/register",
            json={
                "username": test_user,
                "password": "test123456"
            },
            timeout=15
        )
        
        print(f"   状态码: {reg_response.status_code}")
        
        if reg_response.status_code == 200:
            data = reg_response.json()
            print(f"   ✅ 注册成功: {data.get('username')}")
            print(f"   Token: {data.get('token', 'N/A')[:30]}...")
        else:
            print(f"   响应: {reg_response.text[:200]}")
            
    else:
        print(f"⚠️  Render 后端状态异常: {response.status_code}")
        
except requests.exceptions.RequestException as e:
    print(f"⚠️  网络请求失败: {e}")
    print("   (这可能是本地网络问题，不影响Render运行)")
except ImportError:
    print("⚠️  需要安装 requests: pip install requests")

# 方法3：检查数据库（如果有DATABASE_URL）
print("\n【方法3】数据库查询 (需要 DATABASE_URL)")
print("-" * 80)

database_url = os.getenv('DATABASE_URL')

if database_url:
    try:
        import psycopg2
        
        print("🔌 连接数据库...")
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 查询用户表
        cursor.execute("SELECT username, email, created_at FROM users ORDER BY created_at DESC LIMIT 10")
        rows = cursor.fetchall()
        
        print(f"✅ 数据库连接成功")
        print(f"📊 最近10个用户:")
        print()
        
        if rows:
            for i, (username, email, created_at) in enumerate(rows, 1):
                print(f"[{i}] {username}")
                print(f"    邮箱: {email or '(无)'}")
                print(f"    注册: {created_at}")
                print()
        else:
            print("   ⚠️  数据库中暂无用户")
        
        cursor.close()
        conn.close()
        
    except ImportError:
        print("⚠️  需要安装 psycopg2: pip install psycopg2-binary")
    except Exception as e:
        print(f"❌ 数据库查询失败: {e}")
else:
    print("⚠️  未设置 DATABASE_URL 环境变量")
    print("   如需查询数据库，请设置环境变量或手动输入")

print("\n" + "=" * 80)
print("📝 总结")
print("=" * 80)

print("\n当前可以看到：")
print("  1. 本地JSON文件中的用户 (admin, bx)")
print("  2. 新注册的用户会保存到数据库")
print("  3. bbb用户如果在数据库中，需要DATABASE_URL才能查询")

print("\n如果想查看 bbb 用户：")
print("  - 方法A: 提供 DATABASE_URL，运行此脚本")
print("  - 方法B: 登录 Render Dashboard → 数据库 → 查询")
print("  - 方法C: 在 Render Shell 运行: python list_registered_users.py")

print("\n" + "=" * 80)


