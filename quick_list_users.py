#!/usr/bin/env python3
"""快速查看用户列表（自动运行）"""
import requests
import json
import os

print("\n" + "=" * 80)
print("👥 快速查看注册用户")
print("=" * 80)

# 方法1：检查本地文件
print("\n🔍 方法1：检查本地 users_data.json...")
users = []

# 先检查backend目录
if os.path.exists('backend/users_data.json'):
    try:
        with open('backend/users_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = data.get('users', [])
            print(f"✅ 从 backend/users_data.json 找到 {len(users)} 个用户")
    except Exception as e:
        print(f"⚠️  读取失败: {e}")

# 如果没有，检查根目录
if not users and os.path.exists('users_data.json'):
    try:
        with open('users_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = data.get('users', [])
            print(f"✅ 从 users_data.json 找到 {len(users)} 个用户")
    except Exception as e:
        print(f"⚠️  读取失败: {e}")

# 方法2：尝试API
if not users:
    print("\n🔍 方法2：尝试从API获取...")
    try:
        response = requests.get(
            "https://decision-assistant-backend.onrender.com/api/db/users",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"✅ 从API获取到 {len(users)} 个用户")
        else:
            print(f"⚠️  API返回: {response.status_code}")
    except Exception as e:
        print(f"⚠️  API失败: {e}")

# 显示结果
print("\n" + "=" * 80)
if users:
    print(f"📋 用户列表 (共 {len(users)} 人)")
    print("=" * 80)
    print()
    
    for i, u in enumerate(users, 1):
        print(f"[{i}] {'-' * 75}")
        print(f"🆔 ID: {u.get('user_id', u.get('id', 'N/A'))}")
        print(f"👤 用户名: {u.get('username', 'N/A')}")
        print(f"📧 邮箱: {u.get('email', 'N/A')}")
        if u.get('created_at'):
            print(f"📅 注册: {u['created_at']}")
        if u.get('last_login'):
            print(f"🕐 登录: {u['last_login']}")
        print()
    
    # 简单统计
    print("=" * 80)
    print("📊 统计")
    print("=" * 80)
    print(f"总用户数: {len(users)}")
    
    # 邮箱域名统计
    domains = {}
    for u in users:
        email = u.get('email', '')
        if '@' in email:
            domain = email.split('@')[1]
            domains[domain] = domains.get(domain, 0) + 1
    
    if domains:
        print("\n邮箱域名:")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"  {domain}: {count}")
    
else:
    print("❌ 未找到用户数据")
    print("\n建议方案:")
    print("1. 检查 backend/users_data.json 文件是否存在")
    print("2. 或使用数据库查询: python list_registered_users.py")
    print("   (需要提供 DATABASE_URL)")

print("\n" + "=" * 80)
print()


