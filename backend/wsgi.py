#!/usr/bin/env python3
"""
WSGI entry point for gunicorn
生产环境入口点
"""
import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app_new import app
    print("✅ Flask 应用导入成功")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    # 尝试导入原始 app
    try:
        from app import app
        print("✅ 使用原始 app.py")
    except ImportError as e2:
        print(f"❌ 原始 app.py 也导入失败: {e2}")
        raise

if __name__ == "__main__":
    app.run()
