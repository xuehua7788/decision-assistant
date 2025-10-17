"""
测试Render数据库连接
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_database_connection():
    """测试数据库连接"""
    try:
        # 从环境变量获取连接信息
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            print("❌ DATABASE_URL 环境变量未设置")
            return False
            
        print(f"🔗 连接数据库: {database_url[:50]}...")
        
        # 测试连接
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ 数据库连接成功！")
        print(f"📊 PostgreSQL版本: {version[0]}")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    print("=== 测试Render数据库连接 ===")
    test_database_connection()
