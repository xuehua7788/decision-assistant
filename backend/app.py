import os
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

load_dotenv()

app = Flask(__name__)

# CORS configuration
CORS(app, origins=["*"])

# OpenAI configuration
openai.api_key = os.getenv('OPENAI_API_KEY')

# 简单的用户存储（生产环境应该使用数据库）
USERS_FILE = 'users_data.json'

def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_users(users):
    """保存用户数据"""
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

@app.route('/')
def home():
    return jsonify({"status": "Decision Assistant API", "version": "1.0"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/auth/register', methods=['POST', 'OPTIONS'])
def register():
    """用户注册"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"detail": "用户名和密码不能为空"}), 400
        
        if len(password) < 6:
            return jsonify({"detail": "密码至少需要6个字符"}), 400
        
        users = load_users()
        
        if username in users:
            return jsonify({"detail": "用户名已存在"}), 400
        
        # 简单的密码存储（生产环境应该使用哈希）
        users[username] = {
            "password": password,
            "created_at": str(os.urandom(16).hex())
        }
        save_users(users)
        
        # 生成简单的 token（生产环境应该使用 JWT）
        token = os.urandom(32).hex()
        
        return jsonify({
            "username": username,
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route('/api/auth/login', methods=['POST', 'OPTIONS'])
def login():
    """用户登录"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"detail": "用户名和密码不能为空"}), 400
        
        users = load_users()
        
        if username not in users:
            return jsonify({"detail": "用户名或密码错误"}), 401
        
        if users[username]['password'] != password:
            return jsonify({"detail": "用户名或密码错误"}), 401
        
        # 生成简单的 token（生产环境应该使用 JWT）
        token = os.urandom(32).hex()
        
        return jsonify({
            "username": username,
            "token": token
        }), 200
        
    except Exception as e:
        return jsonify({"detail": str(e)}), 500

@app.route('/api/decision', methods=['POST', 'OPTIONS'])
def analyze_decision():
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Decision analysis logic
        result = {
            "status": "success",
            "analysis": "Decision analysis completed",
            "recommendations": ["Option 1", "Option 2", "Option 3"],
            "risk_score": 0.7
        }
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
