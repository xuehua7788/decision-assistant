#!/usr/bin/env python3
"""测试股票搜索功能"""
import requests

LOCAL_URL = "http://localhost:5000"

def test_search():
    """测试搜索API"""
    test_cases = [
        "Apple",      # 公司名
        "TSLA",       # 股票代码
        "微软",       # 中文名
        "amazon",     # 小写公司名
        "阿里巴巴"    # 中文名
    ]
    
    print("=" * 60)
    print("📊 测试股票搜索功能")
    print("=" * 60)
    
    for keyword in test_cases:
        print(f"\n🔍 搜索关键词: {keyword}")
        print("-" * 60)
        
        try:
            response = requests.get(
                f"{LOCAL_URL}/api/stock/search",
                params={'keywords': keyword},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('status') == 'success':
                    results = data.get('results', [])
                    print(f"✅ 找到 {len(results)} 个结果")
                    
                    for i, result in enumerate(results[:3], 1):  # 只显示前3个
                        print(f"\n   [{i}] {result['symbol']}")
                        print(f"       公司名: {result['name']}")
                        print(f"       类型: {result['type']}")
                        print(f"       地区: {result['region']}")
                        print(f"       匹配度: {result['match_score']}")
                else:
                    print(f"⚠️  状态: {data.get('status')}")
                    print(f"   消息: {data.get('message')}")
            else:
                print(f"❌ HTTP错误: {response.status_code}")
                print(f"   响应: {response.text[:200]}")
                
        except requests.Timeout:
            print("⏱️  请求超时")
        except Exception as e:
            print(f"❌ 错误: {e}")

if __name__ == "__main__":
    test_search()

