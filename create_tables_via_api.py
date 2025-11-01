#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通过API远程创建数据库表
"""

import requests
import time

BASE_URL = "https://decision-assistant-backend.onrender.com"

print("=" * 70)
print("远程创建用户画像数据库表")
print("=" * 70)
print()

# 方法1: 尝试通过数据库初始化API
print("方法1: 尝试数据库初始化API...")
try:
    response = requests.post(f"{BASE_URL}/api/database/init", timeout=30)
    print(f"状态码: {response.status_code}")
    if response.status_code == 200:
        print("✅ 数据库初始化成功")
    else:
        print(f"⚠️ 响应: {response.text[:200]}")
except Exception as e:
    print(f"❌ 失败: {e}")

print()
print("=" * 70)
print("说明")
print("=" * 70)
print()
print("由于安全原因，数据库表创建需要在Render Shell中手动执行。")
print()
print("请按以下步骤操作:")
print()
print("1. 进入 Render Dashboard")
print("   https://dashboard.render.com")
print()
print("2. 选择你的 Web Service")
print()
print("3. 点击左侧的 'Shell' 标签")
print()
print("4. 在Shell中运行:")
print("   cd backend")
print("   python create_user_profile_tables.py")
print()
print("5. 看到 '🎉 所有表创建/更新成功！' 即可")
print()
print("6. 然后再次运行: python auto_test_render.py")
print()


