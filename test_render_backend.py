#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render后端是否可访问
"""
import requests

RENDER_URL = "https://decision-assistant-backend.onrender.com"

print("="*60)
print("Testing Render Backend")
print("="*60)

# Test 1: Health check
print("\n1. Health Check...")
try:
    response = requests.get(f"{RENDER_URL}/health", timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 2: Strategy list
print("\n2. Strategy List API...")
try:
    response = requests.get(f"{RENDER_URL}/api/strategy/list", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Strategies: {data.get('count', 0)}")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

# Test 3: Stock styles
print("\n3. Stock Styles API...")
try:
    response = requests.get(f"{RENDER_URL}/api/stock/styles", timeout=10)
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"   Styles: {data}")
    else:
        print(f"   Response: {response.text[:200]}")
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("Test Complete")
print("="*60)
