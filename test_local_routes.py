import requests

print("Testing LOCAL backend routes...")

# Test strategy list
try:
    r = requests.get("http://127.0.0.1:8000/api/strategy/list", timeout=5)
    print(f"Strategy List: {r.status_code}")
    if r.status_code == 200:
        print(f"  Count: {r.json().get('count')}")
except Exception as e:
    print(f"Strategy List: ERROR - {e}")

# Test strategy save
try:
    r = requests.post("http://127.0.0.1:8000/api/strategy/save", 
                     json={"symbol": "TEST", "investment_style": "buffett", 
                           "recommendation": "买入", "target_price": 100, 
                           "current_price": 90},
                     timeout=5)
    print(f"Strategy Save: {r.status_code}")
except Exception as e:
    print(f"Strategy Save: ERROR - {e}")

print("\nTesting RENDER backend routes...")

# Test Render
try:
    r = requests.get("https://decision-assistant-backend.onrender.com/api/strategy/list", timeout=10)
    print(f"Render Strategy List: {r.status_code}")
except Exception as e:
    print(f"Render Strategy List: ERROR - {e}")


