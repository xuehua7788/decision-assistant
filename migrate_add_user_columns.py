#!/usr/bin/env python3
"""
数据库迁移脚本：为策略表添加用户字段
"""
import os
import psycopg2

def get_db_connection():
    """获取数据库连接"""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("⚠️  未设置 DATABASE_URL")
        database_url = input("请输入 DATABASE_URL: ").strip()
        
        if not database_url:
            return None
    
    try:
        conn = psycopg2.connect(database_url)
        print("✅ 数据库连接成功")
        return conn
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return None

def migrate():
    """执行迁移"""
    print("\n" + "=" * 80)
    print("🔧 数据库迁移：添加用户字段到策略表")
    print("=" * 80)
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 检查列是否已存在
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='accepted_strategies' 
            AND column_name IN ('user_id', 'username')
        """)
        existing_columns = [row[0] for row in cursor.fetchall()]
        
        if 'user_id' in existing_columns and 'username' in existing_columns:
            print("\n✅ 字段已存在，无需迁移")
            cursor.close()
            conn.close()
            return
        
        print("\n📝 开始添加字段...")
        
        # 添加 user_id 列
        if 'user_id' not in existing_columns:
            print("  添加 user_id 列...")
            cursor.execute("""
                ALTER TABLE accepted_strategies 
                ADD COLUMN IF NOT EXISTS user_id VARCHAR(50)
            """)
            print("  ✅ user_id 列已添加")
        
        # 添加 username 列
        if 'username' not in existing_columns:
            print("  添加 username 列...")
            cursor.execute("""
                ALTER TABLE accepted_strategies 
                ADD COLUMN IF NOT EXISTS username VARCHAR(50)
            """)
            print("  ✅ username 列已添加")
        
        # 创建索引
        print("  创建索引...")
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_strategy_username 
            ON accepted_strategies(username)
        """)
        print("  ✅ 索引已创建")
        
        # 提交更改
        conn.commit()
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 80)
        print("✅ 迁移完成！")
        print("=" * 80)
        print("\n💡 提示：")
        print("  - 已添加 user_id 和 username 列")
        print("  - 现有策略的用户字段为 NULL")
        print("  - 新保存的策略将包含用户信息")
        print()
        
    except Exception as e:
        print(f"\n❌ 迁移失败: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            conn.close()

if __name__ == "__main__":
    migrate()


