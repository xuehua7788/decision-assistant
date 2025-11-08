#!/usr/bin/env python3
"""通过API查看用户列表（不需要数据库凭证）"""
import requests
import json
from datetime import datetime

# API配置
RENDER_URL = "https://decision-assistant-backend.onrender.com"
LOCAL_URL = "http://localhost:5000"

def list_users_from_api(api_url=RENDER_URL):
    """从API获取用户列表"""
    print("=" * 80)
    print("👥 查询注册用户")
    print("=" * 80)
    print(f"\n🌐 API地址: {api_url}\n")
    
    # 检查后端是否有用户列表API
    # 如果没有，我们需要添加一个
    
    # 方法1：尝试从数据库初始化API获取
    try:
        print("🔍 方法1：尝试从 /api/db/users 获取...")
        response = requests.get(f"{api_url}/api/db/users", timeout=15)
        
        if response.status_code == 200:
            data = response.json()
            users = data.get('users', [])
            print(f"✅ 找到 {len(users)} 个用户\n")
            return users
        else:
            print(f"⚠️  状态码: {response.status_code}\n")
    except Exception as e:
        print(f"⚠️  方法1失败: {e}\n")
    
    # 方法2：读取本地文件（如果有）
    try:
        print("🔍 方法2：尝试读取本地 users_data.json...")
        with open('backend/users_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = data.get('users', [])
            print(f"✅ 找到 {len(users)} 个用户\n")
            return users
    except Exception as e:
        print(f"⚠️  方法2失败: {e}\n")
    
    # 方法3：检查项目根目录的users_data.json
    try:
        print("🔍 方法3：尝试读取根目录 users_data.json...")
        with open('users_data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            users = data.get('users', [])
            print(f"✅ 找到 {len(users)} 个用户\n")
            return users
    except Exception as e:
        print(f"⚠️  方法3失败: {e}\n")
    
    print("❌ 无法获取用户列表")
    print("建议：使用数据库直查方式 (python list_registered_users.py)\n")
    return []

def display_users(users):
    """显示用户信息"""
    if not users:
        print("⚠️  没有找到用户")
        return
    
    print("=" * 80)
    print(f"📋 用户列表 (共 {len(users)} 人)")
    print("=" * 80)
    print()
    
    for i, u in enumerate(users, 1):
        print(f"[{i}] {'-' * 75}")
        print(f"🆔 用户ID: {u.get('user_id', 'N/A')}")
        print(f"👤 用户名: {u.get('username', 'N/A')}")
        print(f"📧 邮箱: {u.get('email', 'N/A')}")
        
        if u.get('created_at'):
            print(f"📅 注册时间: {u['created_at']}")
        
        if u.get('last_login'):
            print(f"🕐 最后登录: {u['last_login']}")
        
        print()
    
    # 统计信息
    print("=" * 80)
    print("📊 统计信息")
    print("=" * 80)
    print(f"总用户数: {len(users)}")
    
    # 统计邮箱域名
    domains = {}
    for u in users:
        email = u.get('email', '')
        if '@' in email:
            domain = email.split('@')[1]
            domains[domain] = domains.get(domain, 0) + 1
    
    if domains:
        print(f"\n邮箱域名分布:")
        for domain, count in sorted(domains.items(), key=lambda x: -x[1]):
            print(f"  {domain}: {count} 人")
    
    print()

def main():
    """主函数"""
    print()
    
    # 选择API地址
    print("选择数据源:")
    print("1. Render生产环境")
    print("2. 本地开发环境")
    print("3. 本地文件")
    
    choice = input("\n请选择 (1-3，默认1): ").strip() or '1'
    
    if choice == '1':
        api_url = RENDER_URL
    elif choice == '2':
        api_url = LOCAL_URL
    else:
        api_url = None
    
    # 获取用户列表
    users = list_users_from_api(api_url) if api_url else list_users_from_api(None)
    
    # 显示用户
    display_users(users)
    
    # 导出选项
    if users:
        export = input("是否导出为JSON? (y/n): ").strip().lower()
        if export == 'y':
            filename = f"users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(users, f, ensure_ascii=False, indent=2)
            print(f"✅ 已导出到: {filename}\n")

if __name__ == "__main__":
    main()


