#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试资金管理API（本地版本）
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register_user():
    """测试注册用户"""
    print("\n1️⃣ 测试注册用户 bbb...")
    response = requests.post(f"{BASE_URL}/api/auth/register", json={
        "username": "bbb",
        "password": "123456"
    })
    print(f"   状态码: {response.status_code}")
    print(f"   响应: {response.json()}")
    return response.status_code == 200

def test_get_account():
    """测试获取账户信息"""
    print("\n2️⃣ 测试获取账户信息...")
    response = requests.get(f"{BASE_URL}/api/fund/account/bbb")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    return response.status_code == 200

def test_get_positions():
    """测试获取持仓列表"""
    print("\n3️⃣ 测试获取持仓列表...")
    response = requests.get(f"{BASE_URL}/api/fund/positions/bbb")
    print(f"   状态码: {response.status_code}")
    data = response.json()
    print(f"   响应: {json.dumps(data, indent=2, ensure_ascii=False)}")
    return response.status_code == 200

if __name__ == "__main__":
    print("=" * 60)
    print("🧪 资金管理API本地测试")
    print("=" * 60)
    
    # 测试1: 注册用户
    test_register_user()
    
    # 测试2: 获取账户
    if test_get_account():
        print("✅ 账户信息获取成功")
    else:
        print("❌ 账户信息获取失败")
    
    # 测试3: 获取持仓
    if test_get_positions():
        print("✅ 持仓列表获取成功")
    else:
        print("❌ 持仓列表获取失败")
    
    print("\n" + "=" * 60)
    print("✅ 测试完成！")
    print("=" * 60)

