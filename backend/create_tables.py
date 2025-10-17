"""
创建数据库表结构
设计可扩展的数据模型，支持未来的分析算法
"""
import os
from simple_database import simple_db

def create_tables():
    """创建所有数据库表"""
    
    if not simple_db.is_available():
        print("❌ 数据库不可用")
        return False
    
    print("=== 创建数据库表结构 ===\n")
    
    try:
        with simple_db.get_cursor() as cursor:
            
            # 1. 用户表
            print("1. 创建用户表 (users)...")
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
            print("   ✅ 用户表创建成功")
            
            # 2. 聊天会话表
            print("\n2. 创建聊天会话表 (chat_sessions)...")
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
            print("   ✅ 聊天会话表创建成功")
            
            # 3. 聊天消息表
            print("\n3. 创建聊天消息表 (chat_messages)...")
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
            print("   ✅ 聊天消息表创建成功")
            
            # 4. 决策分析表
            print("\n4. 创建决策分析表 (decision_analyses)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS decision_analyses (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    description TEXT NOT NULL,
                    options JSONB NOT NULL,
                    recommendation VARCHAR(255),
                    analysis_result JSONB NOT NULL,
                    algorithm_used VARCHAR(100),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata JSONB DEFAULT '{}'
                );
                
                CREATE INDEX IF NOT EXISTS idx_decision_analyses_user_id ON decision_analyses(user_id);
                CREATE INDEX IF NOT EXISTS idx_decision_analyses_created_at ON decision_analyses(created_at);
                CREATE INDEX IF NOT EXISTS idx_decision_analyses_algorithm ON decision_analyses(algorithm_used);
            """)
            print("   ✅ 决策分析表创建成功")
            
            # 5. 用户行为日志表（用于分析）
            print("\n5. 创建用户行为日志表 (user_actions)...")
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_actions (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    action_type VARCHAR(50) NOT NULL CHECK (action_type IN ('login', 'register', 'chat', 'analyze', 'view')),
                    action_data JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    ip_address VARCHAR(45),
                    user_agent TEXT
                );
                
                CREATE INDEX IF NOT EXISTS idx_user_actions_user_id ON user_actions(user_id);
                CREATE INDEX IF NOT EXISTS idx_user_actions_action_type ON user_actions(action_type);
                CREATE INDEX IF NOT EXISTS idx_user_actions_created_at ON user_actions(created_at);
            """)
            print("   ✅ 用户行为日志表创建成功")
            
            # 6. 分析算法配置表（用于扩展）
            print("\n6. 创建分析算法配置表 (analysis_algorithms)...")
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
            print("   ✅ 分析算法配置表创建成功")
            
            # 验证表创建
            print("\n7. 验证表结构...")
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            print(f"   已创建的表: {len(tables)}个")
            for table in tables:
                print(f"   - {table['table_name']}")
            
            print("\n🎉 所有表创建成功！")
            return True
            
    except Exception as e:
        print(f"\n❌ 创建表失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = create_tables()
    if success:
        print("\n✅ 数据库表结构创建完成，可以开始使用数据库功能")
    else:
        print("\n❌ 数据库表创建失败，请检查错误信息")
