"""
数据库连接 - 与现有项目完全兼容
严格审核：变量名、接口名、配置名
"""
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager
from typing import Optional, Generator, Dict, Any
from ..config.database import DatabaseConfig

class DatabaseConnection:
    """数据库连接管理 - 严格审核版本"""
    
    def __init__(self):
        self.config = DatabaseConfig()
        self._connection = None
    
    def get_connection(self):
        """获取数据库连接"""
        if not self.config.is_database_available():
            raise Exception("数据库未配置或未启用")
        
        database_url = self.config.get_database_url()
        if not database_url:
            raise Exception("数据库连接URL未配置")
        
        try:
            self._connection = psycopg2.connect(
                database_url,
                cursor_factory=RealDictCursor
            )
            return self._connection
        except Exception as e:
            raise Exception(f"数据库连接失败: {str(e)}")
    
    @contextmanager
    def get_cursor(self) -> Generator[Any, None, None]:
        """获取数据库游标（上下文管理器）"""
        conn = None
        cursor = None
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            yield cursor
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()
                
                return {
                    "status": "success",
                    "message": "数据库连接成功",
                    "version": version['version'] if version else "unknown",
                    "config": self.config.get_config_summary()
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"数据库连接失败: {str(e)}",
                "config": self.config.get_config_summary()
            }
    
    def close(self):
        """关闭数据库连接"""
        if self._connection:
            self._connection.close()
            self._connection = None

# 全局数据库连接实例
db_connection = DatabaseConnection()

def get_database_connection() -> DatabaseConnection:
    """获取数据库连接实例"""
    return db_connection

def test_database_connection() -> Dict[str, Any]:
    """测试数据库连接（用于API接口）"""
    return db_connection.test_connection()
