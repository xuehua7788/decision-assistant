"""
调试导入问题 - 检查所有模块导入
"""
import os
import sys

def debug_imports():
    """调试所有导入"""
    print("=== 调试导入问题 ===")
    
    # 设置环境变量
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost:5432/test'
    os.environ['USE_DATABASE'] = 'true'
    os.environ['ENABLE_ANALYTICS'] = 'false'
    
    print("1. 检查Python路径...")
    print(f"   sys.path: {sys.path[:3]}...")
    
    print("\n2. 检查当前目录...")
    print(f"   当前目录: {os.getcwd()}")
    print(f"   文件列表: {os.listdir('.')}")
    
    print("\n3. 检查simple_database.py...")
    try:
        if os.path.exists('simple_database.py'):
            print("   ✅ simple_database.py 文件存在")
            with open('simple_database.py', 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"   文件大小: {len(content)} 字符")
        else:
            print("   ❌ simple_database.py 文件不存在")
    except Exception as e:
        print(f"   ❌ 读取文件失败: {e}")
    
    print("\n4. 测试psycopg2导入...")
    try:
        import psycopg2
        print("   ✅ psycopg2 导入成功")
    except Exception as e:
        print(f"   ❌ psycopg2 导入失败: {e}")
    
    print("\n5. 测试simple_database导入...")
    try:
        from simple_database import simple_db
        print("   ✅ simple_database 导入成功")
        print(f"   simple_db: {simple_db}")
        print(f"   is_available: {simple_db.is_available()}")
    except Exception as e:
        print(f"   ❌ simple_database 导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n6. 测试app.py导入...")
    try:
        # 尝试导入app.py中的变量
        import importlib.util
        spec = importlib.util.spec_from_file_location("app", "app.py")
        app_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(app_module)
        
        print(f"   DATABASE_AVAILABLE: {getattr(app_module, 'DATABASE_AVAILABLE', 'NOT_FOUND')}")
        print(f"   simple_db: {getattr(app_module, 'simple_db', 'NOT_FOUND')}")
        print("   ✅ app.py 导入成功")
        
    except Exception as e:
        print(f"   ❌ app.py 导入失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== 调试完成 ===")

if __name__ == "__main__":
    debug_imports()
