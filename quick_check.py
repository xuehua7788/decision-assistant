"""
快速检查脚本 - 不启动服务器
只检查语法和导入
"""
import os
import sys

def quick_check():
    """快速检查"""
    print("=== 快速检查 ===")
    
    # 设置环境变量
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
    os.environ['USE_DATABASE'] = 'true'
    os.environ['ENABLE_ANALYTICS'] = 'false'
    
    # 检查语法
    print("1. 检查语法...")
    try:
        import py_compile
        py_compile.compile('backend/simple_database.py', doraise=True)
        py_compile.compile('backend/app.py', doraise=True)
        print("✅ 语法检查通过")
    except Exception as e:
        print(f"❌ 语法错误: {e}")
        return False
    
    # 检查导入
    print("2. 检查导入...")
    try:
        sys.path.append('backend')
        from simple_database import simple_db
        from app import DATABASE_AVAILABLE, simple_db as app_db
        print("✅ 导入检查通过")
        print(f"   DATABASE_AVAILABLE: {DATABASE_AVAILABLE}")
        print(f"   simple_db: {simple_db is not None}")
        print(f"   app_db: {app_db is not None}")
    except Exception as e:
        print(f"❌ 导入错误: {e}")
        return False
    
    # 检查数据库配置
    print("3. 检查数据库配置...")
    try:
        print(f"   数据库可用: {simple_db.is_available()}")
        print(f"   使用数据库: {simple_db.use_database}")
        print(f"   启用分析: {simple_db.enable_analytics}")
    except Exception as e:
        print(f"❌ 数据库配置错误: {e}")
        return False
    
    print("✅ 快速检查完成！")
    return True

if __name__ == "__main__":
    quick_check()
