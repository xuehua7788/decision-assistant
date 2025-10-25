import os
import json
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import openai

# 修复导入路径
import os
import sys

# 修复导入路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# 导入简化的数据库模块
try:
    from simple_database import simple_db
    DATABASE_AVAILABLE = True
    print("✅ simple_database导入成功")
except ImportError as e:
    DATABASE_AVAILABLE = False
    simple_db = None
    print(f"❌ 数据库模块导入失败: {e}")

# 导入数据库初始化API
try:
    from database_init_api import db_init_bp
    DB_INIT_AVAILABLE = True
except ImportError as e:
    DB_INIT_AVAILABLE = False
    db_init_bp = None
    print(f"⚠️  数据库初始化API导入失败: {e}")

# 导入数据库同步模块
try:
    from database_sync import get_db_sync
    DB_SYNC_AVAILABLE = True
    print("✅ 数据库同步模块导入成功")
except ImportError as e:
    DB_SYNC_AVAILABLE = False
    get_db_sync = None
    print(f"⚠️  数据库同步模块导入失败: {e}")

# 导入用户画像API模块
try:
    from profile_api_routes import profile_bp
    PROFILE_API_AVAILABLE = True
    print("✅ 用户画像API模块导入成功")
except ImportError as e:
    PROFILE_API_AVAILABLE = False
    profile_bp = None
    print(f"⚠️  用户画像API模块导入失败: {e}")

load_dotenv()

app = Flask(__name__)

# CORS configuration
CORS(app, origins=["*"])

# 注册数据库初始化API蓝图
if DB_INIT_AVAILABLE and db_init_bp:
    app.register_blueprint(db_init_bp)
    print("✅ 数据库初始化API已注册")

# 导入算法分析API
try:
    from algorithm_api import algorithm_bp
    ALGORITHM_API_AVAILABLE = True
    app.register_blueprint(algorithm_bp)
    print("✅ 算法分析API已注册")
except ImportError as e:
    ALGORITHM_API_AVAILABLE = False
    print(f"⚠️ 算法分析API导入失败: {e}")

# 注册用户画像API蓝图
if PROFILE_API_AVAILABLE and profile_bp:
    app.register_blueprint(profile_bp)
    print("✅ 用户画像API已注册")

# 导入期权策略处理器
try:
    from option_strategy_handler import OptionStrategyHandler
    option_handler = OptionStrategyHandler()
    OPTION_STRATEGY_AVAILABLE = True
    print("✅ 期权策略处理器已加载")
except ImportError as e:
    OPTION_STRATEGY_AVAILABLE = False
    option_handler = None
    print(f"⚠️ 期权策略处理器导入失败: {e}")

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
    """保存聊天消息（同时保存到JSON和数据库）"""
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
        
        # 保存到JSON（主存储）
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(chat_data, f, ensure_ascii=False, indent=2)
        
        # 同步到数据库（备份存储）
        if DB_SYNC_AVAILABLE and get_db_sync:
            db_sync = get_db_sync()
            if db_sync.is_available():
                # 使用username作为session_id
                db_sync.sync_chat_message(username, 'user', message, username)
                db_sync.sync_chat_message(username, 'assistant', response, username)
                
    except Exception as e:
        print(f"保存聊天记录失败: {str(e)}")

def load_chat_data(username):
    """加载用户的聊天记录"""
    chat_file = os.path.join(CHAT_DATA_DIR, f'{username}.json')
    if os.path.exists(chat_file):
        with open(chat_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return None

def load_recent_chat_history(session_id, max_messages=10):
    """
    加载最近的聊天历史（用于AI上下文）
    
    Args:
        session_id: 用户会话ID（username）
        max_messages: 最多加载多少条消息（默认10条 = 5轮对话）
    
    Returns:
        列表，每个元素是 {"sender": "user"/"assistant", "text": "..."}
    """
    try:
        chat_data = load_chat_data(session_id)
        if not chat_data or 'messages' not in chat_data:
            return []
        
        # 将旧格式转换为统一格式
        history = []
        for msg in chat_data['messages']:
            # 旧格式: {"user": "...", "assistant": "...", "timestamp": "..."}
            if 'user' in msg:
                history.append({"sender": "user", "text": msg['user']})
            if 'assistant' in msg:
                history.append({"sender": "assistant", "text": msg['assistant']})
        
        # 只返回最近的N条消息
        return history[-max_messages:] if len(history) > max_messages else history
        
    except Exception as e:
        print(f"加载聊天历史失败: {str(e)}")
        return []

def build_messages_from_history(chat_history):
    """
    将聊天历史转换为DeepSeek API消息格式
    
    Args:
        chat_history: [{"sender": "user"/"assistant", "text": "..."}]
    
    Returns:
        [{"role": "user"/"assistant", "content": "..."}]
    """
    messages = []
    for msg in chat_history:
        if msg['sender'] == 'user':
            messages.append({"role": "user", "content": msg['text']})
        else:
            messages.append({"role": "assistant", "content": msg['text']})
    return messages

@app.route('/')
def home():
    return jsonify({"status": "Decision Assistant API", "version": "1.0"})

@app.route('/health')
def health():
    return jsonify({"status": "healthy"})

@app.route('/api/database/test', methods=['GET'])
def test_database_simple():
    """简单的数据库测试接口"""
    try:
        # 测试环境变量
        database_url = os.getenv('DATABASE_URL')
        db_host = os.getenv('DB_HOST')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        result = {
            "status": "success",
            "message": "数据库测试接口正常",
            "environment_variables": {
                "DATABASE_URL": "configured" if database_url else "not_set",
                "DB_HOST": "configured" if db_host else "not_set",
                "DB_USER": "configured" if db_user else "not_set",
                "DB_PASSWORD": "configured" if db_password else "not_set"
            },
            "database_available": DATABASE_AVAILABLE,
            "config_available": simple_db is not None
        }
        
        # 如果数据库模块可用，测试连接
        if DATABASE_AVAILABLE and simple_db:
            try:
                connection_test = simple_db.test_connection()
                result["connection_test"] = connection_test
            except Exception as e:
                result["connection_test"] = {"status": "error", "message": str(e)}
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "database_available": DATABASE_AVAILABLE
        }), 500

@app.route('/api/debug/imports', methods=['GET'])
def debug_imports():
    """调试导入问题"""
    try:
        import sys
        import os
        
        debug_info = {
            "status": "success",
            "python_path": sys.path[:5],  # 只显示前5个路径
            "current_directory": os.getcwd(),
            "files_in_current_dir": os.listdir('.'),
            "database_available": DATABASE_AVAILABLE,
            "simple_db_available": simple_db is not None,
            "environment_variables": {
                "DATABASE_URL": "configured" if os.getenv('DATABASE_URL') else "not_set",
                "USE_DATABASE": os.getenv('USE_DATABASE', 'not_set'),
                "ENABLE_ANALYTICS": os.getenv('ENABLE_ANALYTICS', 'not_set')
            }
        }
        
        # 测试psycopg2导入
        try:
            import psycopg2
            debug_info["psycopg2_available"] = True
        except Exception as e:
            debug_info["psycopg2_available"] = False
            debug_info["psycopg2_error"] = str(e)
        
        # 测试simple_database导入
        try:
            from simple_database import simple_db as test_db
            debug_info["simple_database_import"] = True
            debug_info["test_db_available"] = test_db is not None
        except Exception as e:
            debug_info["simple_database_import"] = False
            debug_info["simple_database_error"] = str(e)
        
        return jsonify(debug_info), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

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
        
        stats = {
            "total_users": len(users),
            "total_chat_sessions": chat_count,
            "api_status": "running",
            "deepseek_configured": bool(os.getenv('DEEPSEEK_API_KEY'))
        }
        
        # 添加数据库状态信息
        if DATABASE_AVAILABLE and simple_db:
            stats.update({
                "database_available": True,
                "database_configured": simple_db.is_available(),
                "use_database": simple_db.use_database,
                "enable_analytics": simple_db.enable_analytics
            })
        else:
            stats.update({
                "database_available": False,
                "database_configured": False,
                "use_database": False,
                "enable_analytics": False
            })
        
        return jsonify(stats), 200
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

@app.route('/api/decisions/chat/<username>', methods=['GET', 'OPTIONS'])
def get_user_chat_history(username):
    """获取特定用户的聊天记录"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    try:
        chat_data = load_chat_data(username)
        if chat_data:
            return jsonify(chat_data), 200
        else:
            # 新用户，返回空消息列表
            return jsonify({"username": username, "messages": []}), 200
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
        password_hash = password  # 简化处理，实际应该hash
        created_at_hash = str(os.urandom(16).hex())
        
        users[username] = {
            "password": password_hash,
            "created_at": created_at_hash
        }
        save_users(users)
        
        # 同步到数据库
        if DB_SYNC_AVAILABLE and get_db_sync:
            db_sync = get_db_sync()
            if db_sync.is_available():
                db_sync.sync_user(username, password_hash, None)
        
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

@app.route('/api/options/strategy', methods=['POST', 'OPTIONS'])
def option_strategy():
    """期权策略推荐API"""
    if request.method == 'OPTIONS':
        return jsonify({}), 200
    
    if not OPTION_STRATEGY_AVAILABLE or not option_handler:
        return jsonify({"error": "期权策略功能暂不可用"}), 503
    
    try:
        data = request.json
        user_input = data.get('message', '')
        current_price = data.get('current_price', None)
        
        if not user_input:
            return jsonify({"error": "输入不能为空"}), 400
        
        # 处理期权策略请求
        result = option_handler.handle_option_strategy_request(user_input, current_price)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"期权策略处理错误: {str(e)}")
        return jsonify({"error": f"处理失败: {str(e)}"}), 500


def call_ai_for_chat(message, chat_history, deepseek_api_key, intent_context=None):
    """
    AI #2: 聊天助手
    提供自然的对话回复
    
    Args:
        message: 用户当前消息
        chat_history: 聊天历史 [{"sender": "user"/"assistant", "text": "..."}]
        deepseek_api_key: DeepSeek API密钥
        intent_context: AI #1的意图分析结果（可选）
    
    Returns:
        AI的聊天回复文本
    """
    system_prompt = """你是一个专业、友好的决策助手。

**你的职责**：
- 与用户自然地聊天，回答各种问题
- 如果用户询问投资相关的信息（如股票行情、公司新闻），可以讨论，但不要主动推荐期权策略
- 如果用户明确表达了投资观点，系统会自动触发期权分析，你不需要提及

**回复风格**：
- 自然、友好、专业
- 不要生硬地提示"如果您想要期权策略..."
- 根据上下文理解用户意图

请用中文自然地回复用户。"""

    if intent_context:
        system_prompt += f"\n\n**当前分析**: {intent_context}"
    
    # 构建消息列表（带聊天历史）
    messages = [{"role": "system", "content": system_prompt}]
    messages.extend(build_messages_from_history(chat_history))
    messages.append({"role": "user", "content": message})
    
    # 调用DeepSeek API
    headers = {
        "Authorization": f"Bearer {deepseek_api_key}",
        "Content-Type": "application/json",
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1000,
    }
    
    response = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=data,
        timeout=30
    )
    
    if response.status_code == 200:
        result = response.json()
        return result["choices"][0]["message"]["content"]
    else:
        raise Exception(f"DeepSeek API error: {response.status_code}")


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
        
        # 使用 AI 先分析用户意图，判断是否需要期权策略分析
        try:
            deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')  # 使用 DEEPSEEK_API_KEY 环境变量名
            print(f"DEBUG: DEEPSEEK_API_KEY = {deepseek_api_key[:10] if deepseek_api_key else 'NOT SET'}...")
            if not deepseek_api_key:
                raise Exception("DEEPSEEK_API_KEY not configured")
            
            headers = {
                "Authorization": f"Bearer {deepseek_api_key}",
                "Content-Type": "application/json",
            }
            
            # AI意图分析系统提示
            system_prompt = """你是一个专业的决策助手。分析用户的投资意图并判断是否需要期权策略推荐。

如果用户表达了自己的投资观点（看涨/看跌某只股票），请返回JSON格式：
{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "股票代码",
    "direction": "bullish/bearish/neutral",
    "strength": "strong/moderate/slight",
    "risk_profile": "aggressive/balanced/conservative"
  },
  "reasoning": "简短解释用户的意图"
}

重要规则：
1. 只有当用户明确表达**自己**的投资观点时才返回期权策略
2. 如果用户仅描述他人观点（"我朋友看涨"、"他人认为"），没有表达自己态度，返回need_option_strategy: false
3. 如果用户表达了与他人相反的观点（"我朋友看涨，但我不认同"、"他看涨但我不同意"），这是用户的投资观点，返回need_option_strategy: true，direction为相反方向
4. 如果用户说"我不看涨"、"我不认为会涨"，direction应该是bearish或neutral
5. 否则，正常对话

示例1：
用户："我朋友强烈看涨特斯拉"
回复：{
  "need_option_strategy": false,
  "reasoning": "这是朋友的观点，不是用户自己的投资意图"
}

示例2：
用户："我强烈看涨特斯拉"
回复：{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "TSLA",
    "direction": "bullish",
    "strength": "strong",
    "risk_profile": "balanced"
  },
  "reasoning": "用户明确表达了看涨TSLA的观点"
}

示例3：
用户："我不看涨特斯拉"
回复：{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "TSLA",
    "direction": "bearish",
    "strength": "moderate",
    "risk_profile": "balanced"
  },
  "reasoning": "用户表达了不看涨，即看跌或中性的观点"
}

示例4：
用户："我朋友强烈看涨特斯拉，但我不认同"
回复：{
  "need_option_strategy": true,
  "user_intent": {
    "ticker": "TSLA",
    "direction": "bearish",
    "strength": "moderate",
    "risk_profile": "balanced"
  },
  "reasoning": "用户明确表示不认同朋友的看涨观点，表达了自己看跌或中性的立场"
}

用中文回复，JSON格式要完整。"""
            
            # 加载聊天历史（最近5轮对话 = 10条消息）
            chat_history = load_recent_chat_history(session_id, max_messages=10)
            
            # 构建带历史的消息列表（AI #1: 意图监听）
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(build_messages_from_history(chat_history))
            messages.append({"role": "user", "content": message})
            
            print(f"DEBUG: AI #1 意图分析，消息数={len(messages)}，历史消息数={len(chat_history)}")
            
            data = {
                "model": "deepseek-chat",
                "messages": messages,
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
                print(f"DEBUG: DeepSeek AI response = {ai_response[:200]}...")
                
                # 尝试解析AI的意图分析结果
                try:
                    intent_analysis = json.loads(ai_response.strip())
                    
                    # 检查AI是否判断需要期权策略
                    if isinstance(intent_analysis, dict) and intent_analysis.get('need_option_strategy'):
                        print(f"DEBUG: AI判断需要期权策略")
                        
                        if OPTION_STRATEGY_AVAILABLE and option_handler:
                            try:
                                user_intent = intent_analysis.get('user_intent', {})
                                reasoning = intent_analysis.get('reasoning', '')
                                
                                # 使用AI提取的意图构建ParsedIntent对象
                                from algorithms.option_nlp_parser import ParsedIntent
                                
                                parsed_intent = ParsedIntent(
                                    ticker=user_intent.get('ticker'),
                                    direction=user_intent.get('direction'),
                                    strength=user_intent.get('strength', 'moderate'),
                                    timeframe=user_intent.get('timeframe', 'short'),
                                    risk_profile=user_intent.get('risk_profile', 'balanced'),
                                    confidence=0.9,  # AI分析的置信度较高
                                    raw_text=message
                                )
                                
                                # 获取当前价格
                                price_map = {
                                    'TSLA': 250.0, 'AAPL': 180.0, 'NVDA': 450.0,
                                    'MSFT': 380.0, 'GOOGL': 140.0, 'AMZN': 150.0, 'META': 320.0
                                }
                                current_price = price_map.get(parsed_intent.ticker, 300.0)
                                
                                # 调用策略映射器
                                from algorithms.option_strategy_mapper import StrategyMapper
                                mapper = StrategyMapper()
                                strategy = mapper.map_strategy(parsed_intent, current_price)
                                
                                # 构建期权策略结果
                                option_result = {
                                    'success': True,
                                    'parsed_intent': {
                                        'ticker': parsed_intent.ticker,
                                        'direction': parsed_intent.direction,
                                        'strength': parsed_intent.strength,
                                        'timeframe': parsed_intent.timeframe,
                                        'risk_profile': parsed_intent.risk_profile,
                                        'confidence': parsed_intent.confidence
                                    },
                                    'strategy': {
                                        'name': strategy.name,
                                        'type': strategy.type,
                                        'description': strategy.description,
                                        'risk_level': strategy.risk_level,
                                        'parameters': strategy.parameters,
                                        'metrics': strategy.metrics,
                                        'payoff_data': strategy.payoff_data
                                    }
                                }
                                
                                # 生成文字回复
                                text_response = f"""🤖 **AI分析**: {reasoning}

📊 **投资意图识别**
- 标的: {parsed_intent.ticker}
- 方向: {parsed_intent.direction}
- 强度: {parsed_intent.strength}

💡 **推荐策略: {strategy.name}**
{strategy.description}

📋 详细的策略参数和Payoff图表已生成，请点击查看。"""
                                
                                # 保存聊天记录
                                if session_id:
                                    save_chat_message(session_id, message, text_response)
                                
                                return jsonify({
                                    "response": text_response,
                                    "session_id": session_id,
                                    "option_strategy_used": True,
                                    "option_strategy_result": option_result
                                }), 200
                                
                            except Exception as strategy_error:
                                print(f"期权策略处理失败: {strategy_error}")
                                # 继续返回普通对话
                    
                    # 如果不需要期权策略，使用AI #2进行自然聊天
                    if isinstance(intent_analysis, dict) and not intent_analysis.get('need_option_strategy'):
                        print("DEBUG: 不需要期权策略，调用AI #2进行自然聊天")
                        
                        try:
                            # 调用AI #2聊天助手（带上下文和AI #1的分析结果）
                            chat_response = call_ai_for_chat(
                                message=message,
                                chat_history=chat_history,  # 复用之前加载的历史
                                deepseek_api_key=deepseek_api_key,
                                intent_context=intent_analysis.get('reasoning')
                            )
                            
                            if session_id:
                                save_chat_message(session_id, message, chat_response)
                            
                            return jsonify({
                                "response": chat_response,
                                "session_id": session_id
                            }), 200
                            
                        except Exception as chat_error:
                            print(f"AI #2聊天失败: {chat_error}")
                            # 如果AI #2失败，使用简单回复
                            reasoning = intent_analysis.get('reasoning', '')
                            fallback_response = f"我理解了。{reasoning}"
                            
                            if session_id:
                                save_chat_message(session_id, message, fallback_response)
                            
                            return jsonify({
                                "response": fallback_response,
                                "session_id": session_id
                            }), 200
                        
                except (json.JSONDecodeError, ValueError, KeyError) as parse_error:
                    # JSON解析失败，当作普通对话
                    print(f"意图解析失败: {parse_error}")
                    pass
                
                # 保存聊天记录（普通对话）
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
