#!/bin/bash
# 在Render Shell中运行此脚本测试用户画像系统

echo "======================================================================"
echo "Render Shell - 用户画像系统测试"
echo "======================================================================"
echo ""

# 1. 检查环境变量
echo "1. 检查环境变量"
echo "----------------------------------------------------------------------"
if [ -z "$DATABASE_URL" ]; then
    echo "   ❌ DATABASE_URL 未设置"
else
    echo "   ✅ DATABASE_URL 已设置"
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "   ❌ DEEPSEEK_API_KEY 未设置"
else
    echo "   ✅ DEEPSEEK_API_KEY 已设置"
fi
echo ""

# 2. 创建数据库表
echo "2. 创建数据库表"
echo "----------------------------------------------------------------------"
python create_user_profile_tables.py
echo ""

# 3. 运行系统测试
echo "3. 运行系统测试"
echo "----------------------------------------------------------------------"
python test_profile_system.py
echo ""

# 4. 查看现有用户
echo "4. 查看现有用户"
echo "----------------------------------------------------------------------"
python -c "
import os
import json
chat_dir = 'chat_data'
if os.path.exists(chat_dir):
    files = [f for f in os.listdir(chat_dir) if f.endswith('.json')]
    print(f'   找到 {len(files)} 个用户会话文件')
    for f in files[:5]:
        username = f.replace('.json', '')
        print(f'      - {username}')
else:
    print('   暂无用户数据')
"
echo ""

echo "======================================================================"
echo "测试完成"
echo "======================================================================"
echo ""
echo "如果所有测试通过，用户画像系统已准备就绪！"
echo ""

