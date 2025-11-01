import requests
import time
from datetime import datetime

API_BASE = 'https://decision-assistant-githubv3.onrender.com'

print("🔍 持续监控Render部署状态...")
print("按 Ctrl+C 停止监控\n")

while True:
    now = datetime.now().strftime("%H:%M:%S")
    
    try:
        # 测试Profile API
        r = requests.get(f"{API_BASE}/api/profile/stats", timeout=5)
        
        if r.status_code == 200:
            print(f"[{now}] ✅ Profile API已部署！")
            print(f"响应: {r.json()}")
            print("\n🎉 部署成功！可以开始测试了")
            break
        elif r.status_code == 404:
            print(f"[{now}] ⏳ 服务在线，但Profile API未就绪...")
        else:
            print(f"[{now}] ⏳ 状态码: {r.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"[{now}] ⏳ 请求超时，服务可能在重启...")
    except requests.exceptions.ConnectionError:
        print(f"[{now}] ⏳ 连接失败，服务正在启动...")
    except Exception as e:
        print(f"[{now}] ⚠️ 错误: {str(e)[:50]}")
    
    time.sleep(10)






