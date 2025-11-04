#!/usr/bin/env python3
"""等待部署完成并测试UI"""
import time
import requests

print("⏳ 等待Render和Vercel部署...")
print("   Render后端: 约60-90秒")
print("   Vercel前端: 约30-60秒")
print()

for i in range(90, 0, -5):
    print(f"\r   倒计时: {i}秒 ", end='', flush=True)
    time.sleep(5)

print("\r   开始测试...      ")
print()

# 测试后端
print("🔍 测试Render后端...")
response = requests.get("https://decision-assistant-backend.onrender.com/api/stock/AAPL", timeout=30)
if response.status_code == 200:
    data = response.json()
    has_premium = data.get('data', {}).get('premium_data') is not None
    print(f"   {'✅' if has_premium else '❌'} Premium数据: {has_premium}")
else:
    print(f"   ❌ 后端响应: {response.status_code}")

print()
print("=" * 80)
print("🎨 UI测试链接：")
print("=" * 80)
print()
print("前端地址: https://decision-assistant-three.vercel.app")
print()
print("测试步骤:")
print("1. 选择投资风格（巴菲特/林奇/索罗斯）")
print("2. 搜索股票（如 AAPL）")
print("3. 查看是否出现 '📊 专业数据分析' 面板")
print("4. 切换标签页（基本面/技术面/宏观面）")
print("5. 查看风格特定的解读")
print()
print("=" * 80)

