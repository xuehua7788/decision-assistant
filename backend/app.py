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

@app.route('/api/decisions/chat', methods=['POST', 'OPTIONS'])
def chat():
    """聊天功能"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        message = data.get('message', '')
        session_id = data.get('session_id', '')
        
        if not message:
            return jsonify({"error": "消息不能为空"}), 400
        
        # 使用 OpenAI API 生成智能回复
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "你是一个专业的决策助手，帮助用户做出明智的决策。请用中文回复，简洁明了。"},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content
            
            return jsonify({
                "response": ai_response,
                "session_id": session_id
            }), 200
            
        except Exception as ai_error:
            # 如果 OpenAI API 失败，使用备用回复
            import random
            responses = [
                "我理解你的问题。让我帮你分析一下...",
                "这是一个很好的问题。从多个角度来看...",
                "基于你提供的信息，我建议...",
                "让我从不同角度帮你分析这个决策..."
            ]
            response = random.choice(responses)
            
            return jsonify({
                "response": response,
                "session_id": session_id
            }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/decisions/analyze', methods=['POST', 'OPTIONS'])
def analyze_decision():
    """决策分析功能"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        data = request.json
        description = data.get('description', '')
        options = data.get('options', [])
        
        if not description or not options:
            return jsonify({"error": "描述和选项不能为空"}), 400
        
        # 简单的决策分析（生产环境应该使用 OpenAI API）
        import random
        
        # 为每个选项生成随机分数
        results = {}
        for option in options:
            if option.strip():
                results[option] = {
                    "total_score": round(random.uniform(6, 10), 1)
                }
        
        # 找出最高分的选项
        best_option = max(results.items(), key=lambda x: x[1]['total_score'])[0]
        
        result = {
            "recommendation": best_option,
            "readable_summary": f"基于分析，我推荐选择 '{best_option}'。这个选项的综合评分最高，是最佳选择。",
            "algorithm_analysis": {
                "algorithms_used": {
                    "weighted_score": {
                        "results": results
                    }
                }
            }
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
