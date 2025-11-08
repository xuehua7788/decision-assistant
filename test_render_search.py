#!/usr/bin/env python3
"""测试Render部署的股票搜索功能"""
import requests
import time

RENDER_URL = "https://decision-assistant-backend.onrender.com"

def test_search():
    """测试搜索API"""
    print("=" * 60)
    print("📊 测试Render股票搜索功能")
    print("=" * 60)
    
    # 先测试健康检查
    print("\n1️⃣ 测试健康检查...")
    try:
        response = requests.get(f"{RENDER_URL}/api/stock/health", timeout=15)
        if response.status_code == 200:
            print("✅ 后端健康")
        else:
            print(f"⚠️  后端状态: {response.status_code}")
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return
    
    # 测试搜索功能
    test_cases = [
        ("Apple", "搜索公司名"),
        ("TSLA", "搜索股票代码"),
        ("Microsoft", "搜索微软"),
        ("Amazon", "搜索亚马逊"),
        ("alibaba", "搜索阿里巴巴")
    ]
    
    for keyword, desc in test_cases:
        print(f"\n🔍 {desc}: {keyword}")
        print("-" * 60)
        
        try:
            response = requests.get(
                f"{RENDER_URL}/api/stock/search",
                params={'keywords': keyword},
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    results = data.get('results', [])
                    print(f"✅ 找到 {len(results)} 个结果")
                    
                    for i, result in enumerate(results[:3], 1):  # 只显示前3个
                        print(f"\n   [{i}] {result['symbol']}")
                        print(f"       📝 公司名: {result['name']}")
                        print(f"       📊 类型: {result['type']}")
                        print(f"       🌍 地区: {result['region']}")
                        print(f"       ⭐ 匹配度: {result['match_score']}")
                else:
                    print(f"⚠️  状态: {data.get('status')}")
                    print(f"   消息: {data.get('message')}")
            elif response.status_code == 503:
                print("⚠️  服务暂不可用（可能正在部署）")
                print("   请等待1-2分钟后重试")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                
        except requests.Timeout:
            print("⏱️  请求超时（可能正在冷启动）")
        except Exception as e:
            print(f"❌ 错误: {e}")
        
        time.sleep(1)  # 避免API限制

if __name__ == "__main__":
    print("⏳ 等待30秒让Render部署...")
    time.sleep(30)
    test_search()


