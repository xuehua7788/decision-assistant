"""
数据库初始化API - 通过HTTP接口创建表
可以在Render环境中远程调用
"""
from flask import Blueprint, jsonify
from simple_database import simple_db

# 创建数据库初始化API蓝图
db_init_bp = Blueprint('db_init', __name__, url_prefix='/api/database')

@db_init_bp.route('/init-tables', methods=['POST'])
def init_tables():
    """初始化数据库表结构"""
    
    if not simple_db.is_available():
        return jsonify({
            "status": "error",
            "message": "数据库不可用",
            "database_configured": simple_db.database_url is not None,
            "use_database": simple_db.use_database
        }), 400
    
    try:
        with simple_db.get_cursor() as cursor:
            tables_created = []
            
            # 1. 用户表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(255) NOT NULL,
                    email VARCHAR(255),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata JSONB DEFAULT '{}'
                );
                
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
                CREATE INDEX IF NOT EXISTS idx_users_created_at ON users(created_at);
            """)
            tables_created.append("users")
            
            # 2. 聊天会话表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_sessions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    session_id VARCHAR(100) UNIQUE NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    metadata JSONB DEFAULT '{}'
                );
                
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_session_id ON chat_sessions(session_id);
                CREATE INDEX IF NOT EXISTS idx_chat_sessions_created_at ON chat_sessions(created_at);
            """)
            tables_created.append("chat_sessions")
            
            # 3. 聊天消息表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id SERIAL PRIMARY KEY,
                    session_id INTEGER REFERENCES chat_sessions(id) ON DELETE CASCADE,
                    role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                );
                
                CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
                CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON chat_messages(created_at);
            """)
            tables_created.append("chat_messages")
            
            # 4. 决策分析表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_analyses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    description TEXT NOT NULL,
                    options JSONB NOT NULL,
                    recommendation VARCHAR(255),
                    analysis_result JSONB NOT NULL,
                    algorithm_used VARCHAR(100),
                    score FLOAT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                );
                
                CREATE INDEX IF NOT EXISTS idx_decision_analyses_user_id ON decision_analyses(user_id);
                CREATE INDEX IF NOT EXISTS idx_decision_analyses_created_at ON decision_analyses(created_at);
                CREATE INDEX IF NOT EXISTS idx_decision_analyses_algorithm ON decision_analyses(algorithm_used);
            """)
            tables_created.append("decision_analyses")
            
            # 5. 用户行为日志表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_actions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    action_type VARCHAR(50) NOT NULL,
                    action_data JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_actions_action_type ON user_actions(action_type);
                CREATE INDEX IF NOT EXISTS idx_user_actions_created_at ON user_actions(created_at);
            """)
            tables_created.append("user_actions")
            
            # 6. 分析算法配置表
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_algorithms (
                    id SERIAL PRIMARY KEY,
                    algorithm_name VARCHAR(100) UNIQUE NOT NULL,
                    algorithm_type VARCHAR(50) NOT NULL,
                    description TEXT,
                    parameters JSONB DEFAULT '{}',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_analysis_algorithms_name ON analysis_algorithms(algorithm_name);
                CREATE INDEX IF NOT EXISTS idx_analysis_algorithms_type ON analysis_algorithms(algorithm_type);
            """)
            tables_created.append("analysis_algorithms")
            
            # 验证表创建
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            all_tables = cursor.fetchall()
            
            return jsonify({
                "status": "success",
                "message": "数据库表初始化成功",
                "tables_created": tables_created,
                "total_tables": len(all_tables),
                "all_tables": [t['table_name'] for t in all_tables]
            }), 200
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"创建表失败: {str(e)}"
        }), 500

@db_init_bp.route('/check-tables', methods=['GET'])
def check_tables():
    """检查数据库表结构"""
    
    if not simple_db.is_available():
        return jsonify({
            "status": "error",
            "message": "数据库不可用"
        }), 400
    
    try:
        with simple_db.get_cursor() as cursor:
            # 查询所有表
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            
            # 查询每个表的行数
            table_info = {}
            for table in tables:
                table_name = table['table_name']
                cursor.execute(f"SELECT COUNT(*) as count FROM {table_name};")
                count = cursor.fetchone()
                table_info[table_name] = count['count'] if count else 0
            
            return jsonify({
                "status": "success",
                "total_tables": len(tables),
                "tables": table_info
            }), 200
            
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"检查表失败: {str(e)}"
        }), 500
