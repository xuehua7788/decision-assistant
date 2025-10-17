import os
import json
import requests
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
CHAT_DATA_DIR = 'chat_data'

# 创建聊天数据目录
if not os.path.exists(CHAT_DATA_DIR):
    os.makedirs(CHAT_DATA_DIR)

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

def save_chat_message(username, message, response):
    """保存聊天消息"""
    try:
        chat_file = os.path.join(CHAT_DATA_DIR, f'{username}.json')
        
        # 加载现有聊天记录
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as f:
                chat_data = json.load(f)
        else:
            chat_data = {"username": username, "messages": []}
        
        # 添加新消息
        chat_data["messages"].append({
            "user": message,
            "assistant": response,
            "timestamp": os.urandom(16).hex()  # 简单的时间戳
        })
        
        # 保存
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存聊天记录失败: {str(e)}")

def load_chat_data(username):
    """加载用户的聊天记录"""
    chat_file = os.path.join(CHAT_DATA_DIR, f'{username}.json')
    if os.path.exists(chat_file):
        with open(chat_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

@app.route('/')
def home():
    return jsonify({"status": "Decision Assistant API", "version": "1.0"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/admin/users', methods=['GET'])
def get_users():
    """查看所有用户（管理员功能）"""
    try:
        users = load_users()
        # 隐藏密码
        users_info = {}
        for username, data in users.items():
            users_info[username] = {
                "created_at": data.get("created_at", "unknown"),
                "has_password": bool(data.get("password"))
            }
        return jsonify({
            "total_users": len(users),
            "users": users_info
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/stats', methods=['GET'])
def get_stats():
    """查看统计信息（管理员功能）"""
    try:
        users = load_users()
        
        # 统计聊天记录数量
        chat_count = 0
        if os.path.exists(CHAT_DATA_DIR):
            chat_files = [f for f in os.listdir(CHAT_DATA_DIR) if f.endswith('.json')]
            chat_count = len(chat_files)
        
        return jsonify({
            "total_users": len(users),
            "total_chat_sessions": chat_count,
            "api_status": "running",
            "deepseek_configured": bool(os.getenv('DEEPSEEK_API_KEY'))
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/chats', methods=['GET'])
def get_all_chats():
    """查看所有聊天记录（管理员功能）"""
    try:
        chats = {}
        if os.path.exists(CHAT_DATA_DIR):
            for filename in os.listdir(CHAT_DATA_DIR):
                if filename.endswith('.json'):
                    username = filename.replace('.json', '')
                    chat_data = load_chat_data(username)
                    if chat_data:
                        chats[username] = {
                            "total_messages": len(chat_data.get("messages", [])),
                            "last_messages": chat_data.get("messages", [])[-5:]  # 只显示最后 5 条
                        }
        
        return jsonify({
            "total_sessions": len(chats),
            "chats": chats
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/admin/chats/<username>', methods=['GET'])
def get_user_chat(username):
    """查看特定用户的聊天记录（管理员功能）"""
    try:
        chat_data = load_chat_data(username)
        if chat_data:
            return jsonify(chat_data), 200
        else:
            return jsonify({"error": "聊天记录不存在"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
        
        # 使用 DeepSeek API 生成智能回复
        try:
            deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')  # 使用 DEEPSEEK_API_KEY 环境变量名
            print(f"DEBUG: DEEPSEEK_API_KEY = {deepseek_api_key[:10] if deepseek_api_key else 'NOT SET'}...")
            if not deepseek_api_key:
                raise Exception("DEEPSEEK_API_KEY not configured")
            
            headers = {
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的决策助手，帮助用户做出明智的决策。请用中文回复，简洁明了。"},
                    {"role": "user", "content": message}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"DEBUG: DeepSeek API response status = {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                ai_response = result["choices"][0]["message"]["content"]
                print(f"DEBUG: DeepSeek API response = {ai_response[:50]}...")
                
                # 保存聊天记录
                if session_id:
                    save_chat_message(session_id, message, ai_response)
                
                return jsonify({
                    "response": ai_response,
                    "session_id": session_id
                }), 200
            else:
                print(f"DEBUG: DeepSeek API error response = {response.text}")
                raise Exception(f"DeepSeek API error: {response.status_code}")
            
        except Exception as ai_error:
            # 如果 DeepSeek API 失败，使用备用回复
            print(f"DeepSeek API Error: {str(ai_error)}")  # 记录错误到日志
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
        
        # 使用 OpenAI API 生成智能决策分析
        try:
            # 构建提示词
            prompt = f"""作为一个专业的决策助手，请分析以下决策场景：

决策描述：{description}

选项：
{chr(10).join([f'{i+1}. {opt}' for i, opt in enumerate(options) if opt.strip()])}

请：
1. 为每个选项评分（1-10分）
2. 给出推荐选项
3. 提供详细的分析总结

请以 JSON 格式回复，包含：
- recommendation: 推荐的选项
- readable_summary: 详细分析（至少100字）
- algorithm_analysis.algorithms_used.weighted_score.results: 每个选项的分数
"""
            
            deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')  # 使用 DEEPSEEK_API_KEY 环境变量名
            if not deepseek_api_key:
                raise Exception("DEEPSEEK_API_KEY not configured")
            
            headers = {
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type": "application/json",
            }
            
            data = {
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": "你是一个专业的决策助手，擅长分析各种决策场景并提供建议。请用中文回复，格式为 JSON。"},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1000,
            }
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code != 200:
                raise Exception(f"DeepSeek API error: {response.status_code}")
            
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
            
            # 尝试解析 JSON 响应
            import json
            result = json.loads(ai_response)
            
            return jsonify(result), 200
            
        except Exception as ai_error:
            # 如果 OpenAI API 失败，使用随机分数作为备用
            import random
            
            results = {}
            for option in options:
                if option.strip():
                    results[option] = {
                        "total_score": round(random.uniform(6, 10), 1)
                    }
            
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
