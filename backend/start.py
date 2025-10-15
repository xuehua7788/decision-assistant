#!/usr/bin/env python3
"""
简单的启动脚本
用于 Render 部署
"""
import os
import sys

# 添加当前目录到 Python 路径
sys.path.insert(0, os.path.dirname(__file__))

# 设置环境变量
os.environ.setdefault('FLASK_ENV', 'production')

try:
    # 尝试导入新版本
    from app_new import app
    print("✅ 使用 app_new.py")
except ImportError:
    try:
        # 尝试导入原版本
        from app import app
        print("✅ 使用 app.py")
    except ImportError as e:
        print(f"❌ 无法导入 Flask 应用: {e}")
        sys.exit(1)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(host='0.0.0.0', port=port, debug=False)
