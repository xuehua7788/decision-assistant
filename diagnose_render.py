#!/usr/bin/env python3
"""诊断Render问题"""
import requests

API_URL = "https://decision-assistant-b.onrender.com"

print("诊断Render部署状态...\n")

# 尝试不同的端点
endpoints = [
    "/",
    "/api/health",
    "/api/stock/AAPL",
    "/api/ml/trading/advice"
]

for endpoint in endpoints:
    try:
        print(f"测试: {endpoint}")
        r = requests.get(f"{API_URL}{endpoint}", timeout=10)
        print(f"  状态码: {r.status_code}")
        print(f"  响应: {r.text[:100]}")
    except Exception as e:
        print(f"  错误: {e}")
    print()

print("\n可能的原因:")
print("1. 导入错误 - ML模块导入失败导致整个应用崩溃")
print("2. 依赖缺失 - numpy/pandas安装失败")
print("3. 语法错误 - Python代码有问题")
print("\n建议：查看Render Dashboard的日志")


