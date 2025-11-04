#!/usr/bin/env python3
"""
自动数据库迁移脚本
部署到Render后会自动执行
"""
import os
import psycopg2

DATABASE_URL = os.getenv('DATABASE_URL')

def migrate():
    """执行数据库迁移"""
    if not DATABASE_URL:
        print("⚠️  DATABASE_URL not found, skipping migration")
        return
    
    try:
        conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        cur = conn.cursor()
        
        print("🔄 Starting migration...")
        
        # 1. 添加字段
        print("  [1/4] Adding accepted_strategies column...")
        cur.execute("""
            ALTER TABLE users 
            ADD COLUMN IF NOT EXISTS accepted_strategies JSONB DEFAULT '[]'::jsonb
        """)
        conn.commit()
        print("  ✅ Column added")
        
        # 2. 检查旧表是否存在
        print("  [2/4] Checking for old table...")
        cur.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'accepted_strategies'
            )
        """)
        table_exists = cur.fetchone()[0]
        
        if not table_exists:
            print("  ℹ️  Old table already deleted, skipping migration")
            cur.close()
            conn.close()
            return
        
        # 3. 迁移数据
        print("  [3/4] Migrating strategies...")
        cur.execute("""
            UPDATE users 
            SET accepted_strategies = (
                SELECT jsonb_agg(
                    jsonb_build_object(
                        'strategy_id', strategy_id,
                        'symbol', symbol,
                        'company_name', company_name,
                        'investment_style', investment_style,
                        'recommendation', recommendation,
                        'target_price', target_price,
                        'stop_loss', stop_loss,
                        'position_size', position_size,
                        'score', score,
                        'strategy_text', strategy_text,
                        'analysis_summary', analysis_summary,
                        'current_price', current_price,
                        'option_strategy', option_strategy,
                        'created_at', created_at,
                        'status', status
                    )
                )
                FROM accepted_strategies
                WHERE accepted_strategies.username = users.username
            )
            WHERE EXISTS (
                SELECT 1 FROM accepted_strategies 
                WHERE accepted_strategies.username = users.username
            )
        """)
        conn.commit()
        print("  ✅ Data migrated")
        
        # 4. 删除旧表
        print("  [4/4] Dropping old table...")
        cur.execute("DROP TABLE accepted_strategies CASCADE")
        conn.commit()
        print("  ✅ Old table dropped")
        
        # 验证
        cur.execute("""
            SELECT username, jsonb_array_length(accepted_strategies) 
            FROM users 
            WHERE jsonb_array_length(accepted_strategies) > 0
        """)
        results = cur.fetchall()
        
        print("\n✅ Migration complete!")
        print("📊 Users with strategies:")
        for username, count in results:
            print(f"   - {username}: {count} strategies")
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        raise

if __name__ == '__main__':
    migrate()

