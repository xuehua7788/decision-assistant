#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
创建策略存储表
"""

import psycopg2
from database.connection import get_db_connection

def create_strategy_table():
    """创建accepted_strategies表"""
    
    conn = get_db_connection()
    if not conn:
        print("❌ 无法连接数据库")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 创建策略表
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS accepted_strategies (
                id SERIAL PRIMARY KEY,
                strategy_id VARCHAR(100) UNIQUE NOT NULL,
                symbol VARCHAR(10) NOT NULL,
                company_name VARCHAR(100),
                investment_style VARCHAR(20) NOT NULL,
                recommendation VARCHAR(20) NOT NULL,
                target_price DECIMAL(10, 2) NOT NULL,
                stop_loss DECIMAL(10, 2),
                position_size VARCHAR(10),
                score INTEGER,
                strategy_text TEXT,
                analysis_summary TEXT,
                current_price DECIMAL(10, 2) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'active',
                INDEX idx_symbol (symbol),
                INDEX idx_created_at (created_at)
            )
        """)
        
        conn.commit()
        print("✅ accepted_strategies表创建成功")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"❌ 创建表失败: {e}")
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("创建策略存储表")
    print("=" * 60)
    
    if create_strategy_table():
        print("\n✅ 数据库表创建完成！")
    else:
        print("\n❌ 创建失败！")


