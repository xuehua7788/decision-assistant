import requests
import time

BASE = 'https://decision-assistant-backend.onrender.com'
USERNAME = 'bbb'

print("等待Render部署...")
print("(约1-2分钟)\n")

for i in range(1, 13):
    print(f"[{i}/12] 测试策略推荐API...")
    
    try:
        r = requests.get(f"{BASE}/api/profile/{USERNAME}/recommendations", timeout=10)
        
        if r.status_code == 200:
            data = r.json()
            print(f"\n✅ 修复成功！")
            print(f"状态: {data.get('status')}")
            print(f"推荐数量: {len(data.get('recommendations', []))}")
            
            if len(data.get('recommendations', [])) == 0:
                print("\n💡 暂无推荐记录（这是正常的，因为还没有生成过策略推荐）")
                print("   用户画像中已包含推荐信息")
            break
            
        elif r.status_code == 500:
            error = r.json().get('message', '')
            if 'strategy_name' in error:
                print("   ⏳ 旧代码还在运行，等待新版本部署...")
            else:
                print(f"   ❌ 其他错误: {error[:100]}")
        else:
            print(f"   状态码: {r.status_code}")
            
    except Exception as e:
        print(f"   ⏳ 等待服务...")
    
    if i < 12:
        time.sleep(10)
else:
    print("\n⚠️ 超时，请稍后手动测试")

print("\n" + "=" * 60)
print("测试命令: python test_all_profile_features.py")






