import requests
import os

os.environ['DEEPSEEK_API_KEY'] = 'sk-d3196d8e68c44690998d79c715ce715d'

api_key = os.getenv('DEEPSEEK_API_KEY')
print(f"API Key: {api_key[:20]}...")

response = requests.post(
    "https://api.deepseek.com/v1/chat/completions",
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    },
    json={
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": "Hello"}
        ]
    },
    timeout=30
)

print(f"Status: {response.status_code}")
print(f"Response: {response.text[:200]}")

