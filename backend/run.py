#!/usr/bin/env python3
"""
最简单的启动脚本
"""
import os
import sys

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

# 导入 Flask 应用
try:
    from app_new import app
except ImportError:
    from app import app

# 启动应用
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
