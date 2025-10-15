"""
决策助手后端 API
Flask 应用程序，提供决策分析和聊天功能
"""
import os
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
from passlib.context import CryptContext
from jose import JWTError, jwt

from config import config

# 创建 Flask 应用
app = Flask(__name__)

# 获取配置
app_config = config.get(os.getenv('FLASK_ENV', 'production'), config['default'])
app.config.from_object(app_config)

# 配置 CORS
CORS(app, origins=app_config.ALLOWED_ORIGINS, supports_credentials=True)

# 配置日志
logging.basicConfig(level=getattr(logging, app_config.LOG_LEVEL))
logger = logging.getLogger(__name__)

# 初始化 OpenAI 客户端
openai_client = None
if app_config.OPENAI_API_KEY:
    openai_client = OpenAI(api_key=app_config.OPENAI_API_KEY)
    logger.info("OpenAI 客户端初始化成功")
else:
    logger.warning("OpenAI API Key 未设置")

# 密码加密
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# 聊天记录存储目录
CHAT_DATA_DIR = Path("chat_data")
CHAT_DATA_DIR.mkdir(exist_ok=True)

# 用户数据存储
USERS_FILE = "users_data.json"

def load_users():
    """加载用户数据"""
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载用户数据失败: {e}")
    return {}

def save_users(users):
    """保存用户数据"""
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存用户数据失败: {e}")

def create_access_token(data: dict, expires_delta: timedelta = None):
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, app_config.JWT_SECRET_KEY, algorithm="HS256")
    return encoded_jwt

def verify_token(token: str):
    """验证访问令牌"""
    try:
        payload = jwt.decode(token, app_config.JWT_SECRET_KEY, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

def get_current_user():
    """获取当前用户"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return None
    
    token = auth_header.split(' ')[1]
    payload = verify_token(token)
    if payload:
        return payload.get('username')
    return None

def save_chat_data(session_id: str, messages: list):
    """保存聊天数据"""
    try:
        chat_file = CHAT_DATA_DIR / f"{session_id}.json"
        chat_data = {
            "session_id": session_id,
            "messages": messages,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"保存聊天数据失败: {e}")

def load_chat_data(session_id: str):
    """加载聊天数据"""
    try:
        chat_file = CHAT_DATA_DIR / f"{session_id}.json"
        if chat_file.exists():
            with open(chat_file, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"加载聊天数据失败: {e}")
    return None

# API 路由

@app.route('/', methods=['GET'])
def home():
    """首页 - API 状态"""
    return jsonify({
        "message": "决策助手 API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "decision": "/api/decision",
            "test": "/api/test",
            "auth": {
                "register": "/api/auth/register",
                "login": "/api/auth/login",
                "logout": "/api/auth/logout",
                "me": "/api/auth/me"
            }
        }
    })

@app.route('/health', methods=['GET'])
def health_check():
    """健康检查端点"""
    return jsonify({
        "status": "ok",
        "service": "backend",
        "ai": "OpenAI" if openai_client else "Not configured",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/test', methods=['GET'])
def test_endpoint():
    """测试端点"""
    return jsonify({
        "message": "测试成功",
        "timestamp": datetime.now().isoformat(),
        "config": {
            "debug": app_config.DEBUG,
            "environment": app_config.ENV,
            "cors_origins": app_config.ALLOWED_ORIGINS
        }
    })

@app.route('/api/auth/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        users = load_users()
        if username in users:
            return jsonify({"error": "用户名已存在"}), 400
        
        # 加密密码
        hashed_password = pwd_context.hash(password)
        users[username] = {
            "username": username,
            "password": hashed_password,
            "created_at": datetime.now().isoformat()
        }
        save_users(users)
        
        # 创建访问令牌
        access_token = create_access_token({"username": username})
        
        return jsonify({
            "message": "注册成功",
            "access_token": access_token,
            "token_type": "bearer"
        })
        
    except Exception as e:
        logger.error(f"注册失败: {e}")
        return jsonify({"error": "注册失败"}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        if not username or not password:
            return jsonify({"error": "用户名和密码不能为空"}), 400
        
        users = load_users()
        user = users.get(username)
        
        if not user or not pwd_context.verify(password, user['password']):
            return jsonify({"error": "用户名或密码错误"}), 401
        
        # 创建访问令牌
        access_token = create_access_token({"username": username})
        
        return jsonify({
            "message": "登录成功",
            "access_token": access_token,
            "token_type": "bearer"
        })
        
    except Exception as e:
        logger.error(f"登录失败: {e}")
        return jsonify({"error": "登录失败"}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """用户退出"""
    return jsonify({"message": "退出成功"})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user_info():
    """获取当前用户信息"""
    username = get_current_user()
    if not username:
        return jsonify({"error": "未授权"}), 401
    
    return jsonify({"username": username})

@app.route('/api/decision', methods=['POST'])
def analyze_decision():
    """决策分析端点"""
    try:
        if not openai_client:
            return jsonify({"error": "OpenAI API 未配置"}), 500
        
        data = request.get_json()
        description = data.get('description', '')
        options = data.get('options', [])
        
        if not description:
            return jsonify({"error": "决策描述不能为空"}), 400
        
        # 构建提示词
        prompt = f"""
        请帮我分析以下决策问题：

        决策描述：{description}
        
        可选方案：{', '.join(options) if options else '请提供建议'}
        
        请从以下角度进行分析：
        1. 问题分析
        2. 各方案优缺点
        3. 风险评估
        4. 推荐方案
        5. 实施建议
        
        请用中文回答，结构清晰，逻辑严谨。
        """
        
        # 调用 OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个专业的决策分析顾问，擅长帮助用户做出明智的决策。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            temperature=0.7
        )
        
        analysis = response.choices[0].message.content
        
        return jsonify({
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"决策分析失败: {e}")
        return jsonify({"error": "决策分析失败"}), 500

@app.route('/api/chat', methods=['POST'])
def chat():
    """聊天端点"""
    try:
        if not openai_client:
            return jsonify({"error": "OpenAI API 未配置"}), 500
        
        data = request.get_json()
        message = data.get('message', '')
        session_id = data.get('session_id', 'default')
        
        if not message:
            return jsonify({"error": "消息不能为空"}), 400
        
        # 加载聊天历史
        chat_data = load_chat_data(session_id)
        messages = chat_data.get('messages', []) if chat_data else []
        
        # 添加用户消息
        messages.append({"role": "user", "content": message})
        
        # 调用 OpenAI API
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "你是一个友好的决策助手，帮助用户解决各种问题。"}
            ] + messages[-10:],  # 只保留最近10条消息
            max_tokens=500,
            temperature=0.7
        )
        
        assistant_message = response.choices[0].message.content
        messages.append({"role": "assistant", "content": assistant_message})
        
        # 保存聊天记录
        save_chat_data(session_id, messages)
        
        return jsonify({
            "response": assistant_message,
            "session_id": session_id,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        logger.error(f"聊天失败: {e}")
        return jsonify({"error": "聊天失败"}), 500

@app.errorhandler(404)
def not_found(error):
    """404 错误处理"""
    return jsonify({"error": "端点不存在"}), 404

@app.errorhandler(500)
def internal_error(error):
    """500 错误处理"""
    logger.error(f"内部服务器错误: {error}")
    return jsonify({"error": "内部服务器错误"}), 500

if __name__ == '__main__':
    try:
        # 验证配置
        app_config.validate_config()
        
        print("\n" + "="*60)
        print("  🤖 决策助手后端 API (Flask)")
        print("="*60)
        print(f"  🚀 服务器启动: http://{app_config.HOST}:{app_config.PORT}")
        print(f"  🌍 环境: {app_config.ENV}")
        print(f"  🔧 调试模式: {app_config.DEBUG}")
        print(f"  🔑 OpenAI: {'已配置' if openai_client else '未配置'}")
        print(f"  🌐 CORS 来源: {', '.join(app_config.ALLOWED_ORIGINS)}")
        print("\n  📚 API 端点:")
        print("     - GET  /                    (API 状态)")
        print("     - GET  /health              (健康检查)")
        print("     - GET  /api/test            (测试端点)")
        print("     - POST /api/decision        (决策分析)")
        print("     - POST /api/chat            (聊天)")
        print("     - POST /api/auth/register   (用户注册)")
        print("     - POST /api/auth/login      (用户登录)")
        print("     - GET  /api/auth/me         (用户信息)")
        print("="*60 + "\n")
        
        app.run(
            host=app_config.HOST,
            port=app_config.PORT,
            debug=app_config.DEBUG
        )
        
    except Exception as e:
        logger.error(f"启动失败: {e}")
        print(f"❌ 启动失败: {e}")
        exit(1)
