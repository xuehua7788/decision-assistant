"""
配置管理模块
处理环境变量和应用程序配置
"""
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class Config:
    """基础配置类"""
    
    # 服务器配置
    PORT = int(os.getenv('PORT', 8000))
    HOST = os.getenv('HOST', '0.0.0.0')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    ENV = os.getenv('FLASK_ENV', 'production')
    
    # API 配置
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # 安全配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    
    # CORS 配置
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
    
    # 数据库配置
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///decision_assistant.db')
    
    # 日志配置
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate_config(cls):
        """验证必要的配置项"""
        required_vars = ['OPENAI_API_KEY']
        missing_vars = []
        
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"缺少必要的环境变量: {', '.join(missing_vars)}")
        
        return True

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    ENV = 'development'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    ENV = 'production'

# 根据环境选择配置
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': ProductionConfig
}
