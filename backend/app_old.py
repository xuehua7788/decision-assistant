from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from functools import wraps

# 显式加载 .env 文件
load_dotenv()

app = Flask(__name__)
# CORS配置
CORS(app, resources={r"/*": {"origins": "*"}})

# 添加CORS响应头（额外保险）
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# 验证 API Key 加载
api_key = "sk-d3196d8e68c44690998d79c715ce715d"
print(f"Loaded API Key: {api_key[:10]}..." if api_key else "API Key not found!")

# DeepSeek API 配置
client = OpenAI(
    api_key=api_key,
    base_url="https://api.deepseek.com"
)

# 会话存储
sessions = {}

# 认证配置 - 使用sha256_crypt替代bcrypt（避免兼容性问题）
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7天
USERS_FILE = Path("users_data.json")

# 认证工具函数
def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码"""
    # bcrypt限制密码最长72字节
    if len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password[:72]
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """加密密码"""
    # bcrypt限制密码最长72字节
    if len(password.encode('utf-8')) > 72:
        password = password[:72]
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    """解码访问令牌"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None

def get_users_db():
    """获取用户数据库"""
    if not USERS_FILE.exists():
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        try:
            return json.load(f)
        except:
            return {}

def save_users_db(users_db):
    """保存用户数据库"""
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users_db, f, ensure_ascii=False, indent=2)

def token_required(f):
    """装饰器：验证JWT令牌"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.replace('Bearer ', '')
        
        if not token:
            return jsonify({'detail': '未提供认证信息'}), 401
        
        payload = decode_access_token(token)
        if not payload:
            return jsonify({'detail': '无效的令牌'}), 401
        
        username = payload.get('sub')
        if not username:
            return jsonify({'detail': '无效的令牌'}), 401
        
        users_db = get_users_db()
        if username not in users_db:
            return jsonify({'detail': '用户不存在'}), 401
        
        return f(users_db[username], *args, **kwargs)
    
    return decorated

@app.route('/api/decisions/chat', methods=['POST'])
def chat():
    data = request.json
    message = data.get('message')
    session_id = data.get('session_id', 'default')

    if session_id not in sessions:
        sessions[session_id] = {
            'messages': [],
            'extracted_params': {}
        }

    session = sessions[session_id]
    session['messages'].append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are a decision-making assistant. Help users think through their decisions by asking clarifying questions and identifying their options."},
                *session['messages']
            ],
            temperature=0.7,
            max_tokens=500
        )

        ai_response = response.choices[0].message.content
        session['messages'].append({"role": "assistant", "content": ai_response})

        return jsonify({
            'response': ai_response,
            'session_id': session_id,
            'extracted_params': session.get('extracted_params', {}),
            'can_analyze': False
        })

    except Exception as e:
        print(f"ERROR in chat: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/decisions/analyze', methods=['POST'])
def analyze():
    data = request.json
    description = data.get('description')
    options = data.get('options', [])

    try:
        prompt = f"""Analyze this decision:

Description: {description}

Options:
{chr(10).join(f"{i+1}. {opt}" for i, opt in enumerate(options))}

Provide:
1. A recommendation
2. Detailed analysis of each option
3. Pros and cons
4. Key factors to consider

Format your response clearly."""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "You are an expert decision analyst."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        ai_analysis = response.choices[0].message.content

        scores = {}
        for i, option in enumerate(options):
            scores[option] = {"total_score": round(10 - i * 0.5, 1)}

        return jsonify({
            'recommendation': options[0] if options else "No option provided",
            'readable_summary': ai_analysis,
            'algorithm_analysis': {
                'algorithms_used': {
                    'weighted_score': {
                        'results': scores
                    }
                }
            },
            'ai_analysis': {
                'response': ai_analysis
            }
        })

    except Exception as e:
        print(f"ERROR in analyze: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok'})

# 认证路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册（简化版，无需邮箱）"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'detail': '请填写用户名和密码'}), 400
    
    users_db = get_users_db()
    
    # 检查用户名是否已存在
    if username in users_db:
        return jsonify({'detail': '用户名已存在'}), 400
    
    # 验证密码长度
    if len(password) < 6:
        return jsonify({'detail': '密码至少需要6个字符'}), 400
    
    # 创建新用户
    hashed_password = get_password_hash(password)
    new_user = {
        "username": username,
        "hashed_password": hashed_password,
        "is_active": True
    }
    
    users_db[username] = new_user
    save_users_db(users_db)
    
    # 创建访问令牌
    token = create_access_token(data={"sub": username})
    
    return jsonify({
        'username': username,
        'token': token
    })

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    if not username or not password:
        return jsonify({'detail': '请输入用户名和密码'}), 400
    
    users_db = get_users_db()
    
    # 检查用户是否存在
    if username not in users_db:
        return jsonify({'detail': '用户名或密码错误'}), 401
    
    user = users_db[username]
    
    # 验证密码
    if not verify_password(password, user["hashed_password"]):
        return jsonify({'detail': '用户名或密码错误'}), 401
    
    # 检查用户是否激活
    if not user.get("is_active", True):
        return jsonify({'detail': '账户已被禁用'}), 401
    
    # 创建访问令牌
    token = create_access_token(data={"sub": username})
    
    return jsonify({
        'username': user["username"],
        'token': token
    })

@app.route('/api/auth/logout', methods=['POST'])
@token_required
def logout(current_user):
    """用户退出（客户端需要删除本地令牌）"""
    return jsonify({'message': '退出成功'})

@app.route('/api/auth/me', methods=['GET'])
@token_required
def get_me(current_user):
    """获取当前用户信息"""
    return jsonify({
        'username': current_user["username"]
    })

# 添加健康检查端点
@app.route('/health')
def health_check():
    return jsonify({"status": "ok", "service": "backend", "ai": "DeepSeek"})

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  Decision Assistant Backend (Flask)")
    print("="*50)
    print(f"  🚀 Server starting on http://127.0.0.1:8000")
    print(f"  📚 API Endpoints:")
    print(f"     - GET  /health              (健康检查)")
    print(f"     - POST /api/auth/register  (用户注册)")
    print(f"     - POST /api/auth/login     (用户登录)")
    print(f"     - POST /api/auth/logout    (用户退出)")
    print(f"     - GET  /api/auth/me        (获取用户信息)")
    print(f"     - POST /api/decisions/chat (聊天)")
    print(f"     - POST /api/decisions/analyze (决策分析)")
    print("="*50 + "\n")
    app.run(debug=True, port=8000)

