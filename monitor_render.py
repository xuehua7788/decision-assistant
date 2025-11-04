import requests
import time

url = "https://decision-assistant-backend.onrender.com/api/strategy/list"

print("Monitoring Render deployment...")
print("Checking every 15 seconds...\n")

for i in range(15):
    try:
        r = requests.get(url, timeout=10)
        timestamp = time.strftime('%H:%M:%S')
        
        if r.status_code == 200:
            data = r.json()
            print(f"[{timestamp}] SUCCESS! Strategy API is working!")
            print(f"            Strategies count: {data.get('count', 0)}")
            break
        else:
            print(f"[{timestamp}] Status: {r.status_code} (still deploying...)")
    except Exception as e:
        print(f"[{time.strftime('%H:%M:%S')}] Waiting... ({str(e)[:40]})")
    
    if i < 14:
        time.sleep(15)

print("\nDone!")


