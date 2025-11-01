#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试Render后端股票API是否可用
"""

import requests
import json

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def test_health():
    """测试健康检查"""
    print("\n" + "="*60)
    print("🏥 测试健康检查")
    print("="*60)
    
    try:
        url = f"{RENDER_URL}/api/stock/health"
        print(f"请求: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ 股票API健康检查通过")
            print(f"响应: {response.json()}")
            return True
        else:
            print(f"❌ 健康检查失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_stock_data():
    """测试获取股票数据"""
    print("\n" + "="*60)
    print("📊 测试获取股票数据")
    print("="*60)
    
    try:
        url = f"{RENDER_URL}/api/stock/AAPL"
        print(f"请求: {url}")
        
        response = requests.get(url, timeout=30)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            if data['status'] == 'success':
                print("✅ 获取股票数据成功")
                print(f"   股票: {data['data']['quote']['name']}")
                print(f"   价格: ${data['data']['quote']['price']}")
                return True
            else:
                print(f"❌ API返回错误: {data.get('message')}")
                return False
        elif response.status_code == 404:
            print("❌ 404错误 - API端点不存在")
            print("   可能原因:")
            print("   1. Render后端还在部署中")
            print("   2. 股票分析模块没有正确注册")
            return False
        else:
            print(f"❌ 请求失败: {response.status_code}")
            print(f"   响应: {response.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def test_trending():
    """测试获取热门股票"""
    print("\n" + "="*60)
    print("🔥 测试获取热门股票")
    print("="*60)
    
    try:
        url = f"{RENDER_URL}/api/stock/trending"
        print(f"请求: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("✅ 获取热门股票成功")
            print(f"   数量: {len(data.get('trending', []))}")
            return True
        else:
            print(f"❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 请求失败: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🌐 Render后端股票API测试")
    print("="*60)
    print(f"后端URL: {RENDER_URL}")
    
    # 测试健康检查
    health_ok = test_health()
    
    # 测试股票数据
    stock_ok = test_stock_data()
    
    # 测试热门股票
    trending_ok = test_trending()
    
    # 总结
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    print(f"健康检查: {'✅ 通过' if health_ok else '❌ 失败'}")
    print(f"股票数据: {'✅ 通过' if stock_ok else '❌ 失败'}")
    print(f"热门股票: {'✅ 通过' if trending_ok else '❌ 失败'}")
    
    if health_ok and stock_ok and trending_ok:
        print("\n🎉 所有测试通过！Render后端正常工作")
        return 0
    else:
        print("\n⚠️ 部分测试失败")
        print("\n💡 建议:")
        print("1. 等待2-3分钟让Render完成部署")
        print("2. 检查Render控制台的部署日志")
        print("3. 确认环境变量已正确配置")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())

