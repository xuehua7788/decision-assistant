#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库同步模块 - 将JSON数据同步到PostgreSQL
保持向后兼容，数据库作为备份存储
"""

import os
import psycopg2
from datetime import datetime
import json

class DatabaseSync:
    """数据库同步类"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.use_database = os.getenv('USE_DATABASE', 'false').lower() == 'true'
        self.conn = None
        
        print(f"🔍 DatabaseSync初始化: USE_DATABASE={self.use_database}, DATABASE_URL={'已设置' if self.database_url else '未设置'}")
        
        if self.use_database and self.database_url:
            try:
                print(f"🔄 正在连接数据库...")
                self.conn = psycopg2.connect(self.database_url)
                print("✅ 数据库连接成功！")
            except Exception as e:
                print(f"❌ 数据库连接失败: {type(e).__name__}: {e}")
                self.conn = None
        else:
            if not self.use_database:
                print("⚠️ USE_DATABASE=false，数据库同步已禁用")
            if not self.database_url:
                print("⚠️ DATABASE_URL未设置")
    
    def is_available(self):
        """检查数据库是否可用"""
        return self.conn is not None
    
    def sync_user(self, username, password_hash, created_at=None):
        """同步用户数据到数据库"""
        if not self.is_available():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # 检查用户是否存在
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if result:
                print(f"用户 {username} 已存在，跳过")
                return True
            
            # 插入新用户
            cursor.execute("""
                INSERT INTO users (username, password_hash, created_at)
                VALUES (%s, %s, %s)
                ON CONFLICT (username) DO NOTHING
            """, (username, password_hash, created_at or datetime.now()))
            
            self.conn.commit()
            print(f"✅ 用户 {username} 同步到数据库")
            return True
            
        except Exception as e:
            print(f"❌ 同步用户失败: {e}")
            self.conn.rollback()
            return False
    
    def sync_chat_message(self, session_id, role, content, username=None):
        """同步聊天消息到数据库"""
        if not self.is_available():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # 确保会话存在
            cursor.execute("SELECT id FROM chat_sessions WHERE session_id = %s", (session_id,))
            result = cursor.fetchone()
            
            if not result:
                # 创建会话
                cursor.execute("""
                    INSERT INTO chat_sessions (session_id, username, created_at)
                    VALUES (%s, %s, %s)
                    RETURNING id
                """, (session_id, username, datetime.now()))
                session_db_id = cursor.fetchone()[0]
            else:
                session_db_id = result[0]
            
            # 插入消息
            cursor.execute("""
                INSERT INTO chat_messages (session_id, role, content, created_at)
                VALUES (%s, %s, %s, %s)
            """, (session_db_id, role, content, datetime.now()))
            
            self.conn.commit()
            print(f"✅ 消息同步到数据库 (会话: {session_id})")
            return True
            
        except Exception as e:
            print(f"❌ 同步消息失败: {e}")
            self.conn.rollback()
            return False
    
    def sync_decision_analysis(self, username, question, options, analysis_result):
        """同步决策分析结果到数据库"""
        if not self.is_available():
            return False
        
        try:
            cursor = self.conn.cursor()
            
            # 获取用户ID
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            
            if not result:
                print(f"⚠️ 用户 {username} 不存在，跳过分析同步")
                return False
            
            user_id = result[0]
            
            # 插入分析结果
            cursor.execute("""
                INSERT INTO decision_analyses 
                (user_id, question, options, analysis_result, algorithm_used, created_at)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                user_id,
                question,
                json.dumps(options),
                json.dumps(analysis_result),
                'weighted_scoring',
                datetime.now()
            ))
            
            self.conn.commit()
            print(f"✅ 决策分析同步到数据库 (用户: {username})")
            return True
            
        except Exception as e:
            print(f"❌ 同步分析失败: {e}")
            self.conn.rollback()
            return False
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            print("数据库连接已关闭")

# 全局单例
_db_sync = None

def get_db_sync():
    """获取数据库同步实例"""
    global _db_sync
    if _db_sync is None:
        _db_sync = DatabaseSync()
    return _db_sync

