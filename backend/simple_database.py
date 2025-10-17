"""
简化的数据库功能 - 直接在app.py中使用
避免复杂的模块导入问题
"""
import os
from contextlib import contextmanager
from typing import Optional, Dict, Any

# 延迟导入 psycopg2
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    psycopg2 = None
    RealDictCursor = None

class SimpleDatabase:
    """简化的数据库类"""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        self.use_database = os.getenv('USE_DATABASE', 'false').lower() == 'true'
        self.enable_analytics = os.getenv('ENABLE_ANALYTICS', 'false').lower() == 'true'
    
    def is_available(self) -> bool:
        """检查数据库是否可用"""
        return bool(self.database_url) and self.use_database and PSYCOPG2_AVAILABLE
    
    def test_connection(self) -> Dict[str, Any]:
        """测试数据库连接"""
        if not PSYCOPG2_AVAILABLE:
            return {
                "status": "disabled",
                "message": "psycopg2模块未安装",
                "psycopg2_available": False,
                "database_url": "not_configured" if not self.database_url else "configured",
                "use_database": self.use_database
            }
        
        if not self.is_available():
            return {
                "status": "disabled",
                "message": "数据库未启用",
                "psycopg2_available": PSYCOPG2_AVAILABLE,
                "database_url": "not_configured" if not self.database_url else "configured",
                "use_database": self.use_database
            }
        
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            cursor.close()
            conn.close()
            
            return {
                "status": "success",
                "message": "数据库连接成功",
                "version": version[0] if version else "unknown",
                "psycopg2_available": PSYCOPG2_AVAILABLE,
                "database_url": "configured",
                "use_database": self.use_database
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"数据库连接失败: {str(e)}",
                "psycopg2_available": PSYCOPG2_AVAILABLE,
                "database_url": "configured",
                "use_database": self.use_database
            }
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标"""
        if not self.is_available():
            raise Exception("数据库未启用")
        
        conn = None
        cursor = None
        try:
            conn = psycopg2.connect(self.database_url)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
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

# 全局数据库实例
simple_db = SimpleDatabase()
