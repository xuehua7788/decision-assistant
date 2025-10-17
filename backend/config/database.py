"""
数据库配置 - 与现有项目完全兼容
"""
import os
from typing import Optional

class DatabaseConfig:
    """数据库配置类 - 严格审核版本"""
    
    # 环境变量名（与现有不冲突）
    DATABASE_URL = os.getenv('DATABASE_URL')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    DB_NAME = os.getenv('DB_NAME', 'decision_assistant')
    DB_USER = os.getenv('DB_USER', 'decision_user')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    
    # 功能开关（渐进式迁移）
    USE_DATABASE = os.getenv('USE_DATABASE', 'false').lower() == 'true'
    ENABLE_ANALYTICS = os.getenv('ENABLE_ANALYTICS', 'false').lower() == 'true'
    
    # 现有环境变量（保持不变）
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    PORT = int(os.environ.get('PORT', 8000))
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    
    @classmethod
    def get_database_url(cls) -> Optional[str]:
        """获取数据库连接URL"""
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        if all([cls.DB_HOST, cls.DB_USER, cls.DB_PASSWORD, cls.DB_NAME]):
            return f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        
        return None
    
    @classmethod
    def is_database_available(cls) -> bool:
        """检查数据库是否可用"""
        return cls.get_database_url() is not None and cls.USE_DATABASE
    
    @classmethod
    def get_config_summary(cls) -> dict:
        """获取配置摘要（用于调试）"""
        return {
            "database_configured": cls.is_database_available(),
            "use_database": cls.USE_DATABASE,
            "enable_analytics": cls.ENABLE_ANALYTICS,
            "deepseek_configured": bool(cls.DEEPSEEK_API_KEY),
            "flask_env": cls.FLASK_ENV,
            "port": cls.PORT
        }
