"""
测试Render数据库连接
"""
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_render_database():
    """测试Render数据库连接"""
    print("=== 测试Render数据库连接 ===")
    
    # 获取环境变量
    database_url = os.getenv('DATABASE_URL')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    print(f"数据库URL: {database_url[:50] if database_url else 'NOT SET'}...")
    print(f"主机: {db_host}")
    print(f"端口: {db_port}")
    print(f"数据库名: {db_name}")
    print(f"用户名: {db_user}")
    print(f"密码: {'*' * len(db_password) if db_password else 'NOT SET'}")
    
    if not database_url:
        print("❌ DATABASE_URL 环境变量未设置")
        return False
    
    try:
        print("\n🔗 正在连接数据库...")
        
        # 测试连接
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()
        
        # 执行简单查询
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        
        print(f"✅ 数据库连接成功！")
        print(f"📊 PostgreSQL版本: {version[0]}")
        
        # 测试创建表
        print("\n📋 测试创建表...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_table (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # 测试插入数据
        cursor.execute("INSERT INTO test_table (name) VALUES (%s);", ("test_data",))
        
        # 测试查询数据
        cursor.execute("SELECT * FROM test_table WHERE name = %s;", ("test_data",))
        result = cursor.fetchone()
        
        if result:
            print("✅ 表创建和数据操作成功！")
            print(f"📝 测试数据: {result}")
        
        # 清理测试数据
        cursor.execute("DROP TABLE IF EXISTS test_table;")
        
        # 关闭连接
        cursor.close()
        conn.close()
        
        print("\n🎉 数据库测试完全成功！")
        return True
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_render_database()
    if success:
        print("\n✅ 可以继续下一步：更新后端代码")
    else:
        print("\n❌ 请检查数据库配置")
