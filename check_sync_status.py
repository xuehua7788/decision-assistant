#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查数据库同步状态
"""

import requests

BASE_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 70)
print("检查数据库同步状态")
print("=" * 70)
print()

# 检查数据库配置
print("1. 检查数据库配置...")
try:
    response = requests.get(f"{BASE_URL}/api/database/test", timeout=10)
    
    if response.status_code == 200:
        data = response.json()
        
        print(f"   DATABASE_URL: {data.get('environment_variables', {}).get('DATABASE_URL')}")
        print(f"   数据库可用: {data.get('database_available')}")
        print()
        
        if not data.get('database_available'):
            print("   ⚠️ 数据库未启用！")
            print()
            print("   原因可能是:")
            print("   1. USE_DATABASE 环境变量未设置为 true")
            print("   2. DATABASE_URL 环境变量未设置")
            print()
            print("   解决方法:")
            print("   在Render Dashboard → Environment 中添加:")
            print("   - USE_DATABASE=true")
            print("   - DATABASE_URL=postgresql://...")
            print()
    else:
        print(f"   ❌ 无法获取配置: {response.status_code}")
        
except Exception as e:
    print(f"   ❌ 错误: {e}")

print()
print("=" * 70)
print("说明")
print("=" * 70)
print()
print("如果数据库未启用，聊天记录只会保存到JSON文件，")
print("不会同步到PostgreSQL数据库，因此无法进行用户画像分析。")
print()
print("必须设置 USE_DATABASE=true 才能启用数据库同步功能。")
print()




