"""
检查后端部署状态和API可用性
"""
import requests
import time

BACKEND_URL = 'https://decision-assistant-githubv3.onrender.com'

def check_health():
    """检查健康状态"""
    try:
        response = requests.get(f'{BACKEND_URL}/api/stock/health', timeout=10)
        print(f"✅ 健康检查: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ 健康检查失败: {e}")
        return False

def check_new_apis():
    """检查新API端点"""
    endpoints = [
        '/api/fund/account/bbb',
        '/api/fund/positions/bbb',
        '/api/dual-strategy/generate',
    ]
    
    results = {}
    for endpoint in endpoints:
        try:
            url = f'{BACKEND_URL}{endpoint}'
            response = requests.get(url, timeout=10)
            results[endpoint] = {
                'status': response.status_code,
                'available': response.status_code != 404
            }
            print(f"{'✅' if response.status_code != 404 else '❌'} {endpoint}: {response.status_code}")
        except Exception as e:
            results[endpoint] = {
                'status': 'ERROR',
                'available': False
            }
            print(f"❌ {endpoint}: {e}")
    
    return results

if __name__ == '__main__':
    print("🔍 检查后端部署状态...")
    print(f"目标: {BACKEND_URL}\n")
    
    print("1. 健康检查:")
    health_ok = check_health()
    
    print("\n2. 新API端点检查:")
    api_results = check_new_apis()
    
    print("\n" + "="*60)
    if health_ok and all(r['available'] for r in api_results.values()):
        print("✅ 后端已成功部署，所有API可用！")
    elif health_ok:
        print("⚠️ 后端在线，但部分新API不可用（可能是旧版本）")
        print("   建议：等待Render自动部署或手动触发部署")
    else:
        print("❌ 后端不可用或正在部署中")
        print("   建议：等待2-5分钟后重试")

