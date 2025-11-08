#!/usr/bin/env python3
"""显示users_data.json中的用户"""
import json

print("\n" + "=" * 80)
print("👥 注册用户列表")
print("=" * 80)

with open('backend/users_data.json', 'r', encoding='utf-8') as f:
    users_data = json.load(f)

print(f"\n📊 总用户数: {len(users_data)}")
print("\n" + "=" * 80)

for i, (username, data) in enumerate(users_data.items(), 1):
    print(f"\n[{i}] 用户信息:")
    print(f"  👤 用户名: {username}")
    print(f"  🔐 密码哈希: {data['hashed_password'][:30]}...")
    print(f"  ✅ 状态: {'激活' if data.get('is_active') else '未激活'}")

print("\n" + "=" * 80)
print()


