import requests

BASE = 'https://decision-assistant-githubv3.onrender.com'

print("测试所有API端点:\n")

endpoints = {
    'Profile Stats': '/api/profile/stats',
    'Profile bbb': '/api/profile/bbb',
    'Auth Login': '/api/auth/login',
    'Chat': '/api/decisions/chat',
    'Algorithms': '/api/algorithms/list'
}

for name, path in endpoints.items():
    try:
        r = requests.get(f"{BASE}{path}", timeout=10)
        print(f"{name:20} {path:30} -> {r.status_code}")
    except Exception as e:
        print(f"{name:20} {path:30} -> ERROR: {e}")






