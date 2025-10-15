#!/usr/bin/env python3
"""
WSGI entry point for gunicorn
生产环境入口点
"""
import os
from app_new import app

# 验证配置
try:
    from config import config
    app_config = config.get(os.getenv('FLASK_ENV', 'production'), config['default'])
    app_config.validate_config()
    print("✅ 配置验证成功")
except Exception as e:
    print(f"❌ 配置验证失败: {e}")
    exit(1)

if __name__ == "__main__":
    app.run()
