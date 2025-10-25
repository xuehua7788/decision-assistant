#!/bin/bash
# 用户画像系统快速部署脚本

echo "========================================================================"
echo "用户画像系统快速部署"
echo "========================================================================"
echo ""

# 检查Python版本
echo "1. 检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python 3未安装"
    exit 1
fi
echo "✅ Python已安装"
echo ""

# 检查环境变量
echo "2. 检查环境变量..."
if [ -z "$DATABASE_URL" ]; then
    echo "⚠️ DATABASE_URL未设置"
    echo "   请设置: export DATABASE_URL='postgresql://...'"
else
    echo "✅ DATABASE_URL已设置"
fi

if [ -z "$DEEPSEEK_API_KEY" ]; then
    echo "⚠️ DEEPSEEK_API_KEY未设置"
    echo "   请设置: export DEEPSEEK_API_KEY='sk-...'"
else
    echo "✅ DEEPSEEK_API_KEY已设置"
fi
echo ""

# 安装依赖
echo "3. 安装Python依赖..."
pip3 install psycopg2-binary requests
if [ $? -eq 0 ]; then
    echo "✅ 依赖安装成功"
else
    echo "❌ 依赖安装失败"
    exit 1
fi
echo ""

# 创建数据库表
echo "4. 创建数据库表..."
python3 create_user_profile_tables.py
if [ $? -eq 0 ]; then
    echo "✅ 数据库表创建成功"
else
    echo "❌ 数据库表创建失败"
    exit 1
fi
echo ""

# 运行测试
echo "5. 运行系统测试..."
python3 test_profile_system.py
if [ $? -eq 0 ]; then
    echo "✅ 系统测试通过"
else
    echo "⚠️ 部分测试失败，请查看上述错误"
fi
echo ""

echo "========================================================================"
echo "部署完成！"
echo "========================================================================"
echo ""
echo "下一步:"
echo "1. 分析用户: python3 scheduled_profile_analysis.py --user <username>"
echo "2. 查看文档: cat USER_PROFILE_SYSTEM_GUIDE.md"
echo "3. 启动服务: python3 app.py"
echo ""

