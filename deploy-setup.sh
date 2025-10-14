#!/bin/bash

# Decision Assistant 一键部署配置脚本
# 使用方法: chmod +x deploy-setup.sh && ./deploy-setup.sh

set -e

echo "=========================================="
echo "Decision Assistant 部署配置向导"
echo "=========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查必要工具
check_tools() {
    echo "检查必要工具..."
    
    if ! command -v git &> /dev/null; then
        echo -e "${RED}错误: 未安装 Git${NC}"
        exit 1
    fi
    
    if ! command -v node &> /dev/null; then
        echo -e "${RED}错误: 未安装 Node.js${NC}"
        exit 1
    fi
    
    if ! command -v npm &> /dev/null; then
        echo -e "${RED}错误: 未安装 npm${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 工具检查完成${NC}"
    echo ""
}

# 选择部署方案
select_deployment() {
    echo "请选择部署方案:"
    echo "1) Vercel + Render (免费，推荐新手)"
    echo "2) Vercel + Railway (付费，稳定)"
    echo "3) Cloudflare Pages + Fly.io (高性价比)"
    echo "4) 仅本地测试"
    echo ""
    read -p "请输入选项 (1-4): " deployment_choice
    
    case $deployment_choice in
        1)
            PLATFORM_FRONTEND="vercel"
            PLATFORM_BACKEND="render"
            ;;
        2)
            PLATFORM_FRONTEND="vercel"
            PLATFORM_BACKEND="railway"
            ;;
        3)
            PLATFORM_FRONTEND="cloudflare"
            PLATFORM_BACKEND="flyio"
            ;;
        4)
            PLATFORM_FRONTEND="local"
            PLATFORM_BACKEND="local"
            ;;
        *)
            echo -e "${RED}无效选项${NC}"
            exit 1
            ;;
    esac
    
    echo -e "${GREEN}选择: 前端=${PLATFORM_FRONTEND}, 后端=${PLATFORM_BACKEND}${NC}"
    echo ""
}

# 收集环境变量
collect_env_vars() {
    echo "=========================================="
    echo "环境变量配置"
    echo "=========================================="
    echo ""
    
    # DeepSeek API Key
    read -p "请输入 DeepSeek API Key (sk-...): " DEEPSEEK_KEY
    if [[ ! $DEEPSEEK_KEY == sk-* ]]; then
        echo -e "${YELLOW}警告: API Key 格式可能不正确${NC}"
    fi
    
    # 后端 URL (如果不是本地)
    if [ "$PLATFORM_BACKEND" != "local" ]; then
        read -p "后端部署完成后的 URL (留空则稍后配置): " BACKEND_URL
    else
        BACKEND_URL="http://localhost:8000"
    fi
    
    # 前端 URL (如果不是本地)
    if [ "$PLATFORM_FRONTEND" != "local" ]; then
        read -p "前端部署完成后的 URL (留空则稍后配置): " FRONTEND_URL
    else
        FRONTEND_URL="http://localhost:3000"
    fi
    
    echo ""
    echo -e "${GREEN}环境变量收集完成${NC}"
    echo ""
}

# 创建环境变量文件
create_env_files() {
    echo "创建环境变量文件..."
    
    # 后端 .env
    cat > backend/.env << EOF
# DeepSeek API Configuration
DEEPSEEK_API_KEY=${DEEPSEEK_KEY}

# CORS Configuration
ALLOWED_ORIGINS=["${FRONTEND_URL}","http://localhost:3000"]

# Chat Storage
CHAT_STORAGE_DIR=chat_data
MAX_HISTORY_MESSAGES=20
EOF
    
    echo -e "${GREEN}✓ 创建 backend/.env${NC}"
    
    # 前端 .env
    cat > frontend/.env << EOF
# Backend API URL
REACT_APP_API_URL=${BACKEND_URL}
EOF
    
    echo -e "${GREEN}✓ 创建 frontend/.env${NC}"
    
    # .env.example 文件
    cat > backend/.env.example << EOF
DEEPSEEK_API_KEY=sk-your-deepseek-api-key-here
ALLOWED_ORIGINS=["http://localhost:3000","https://your-frontend-domain.com"]
CHAT_STORAGE_DIR=chat_data
MAX_HISTORY_MESSAGES=20
EOF
    
    cat > frontend/.env.example << EOF
REACT_APP_API_URL=http://localhost:8000
EOF
    
    echo ""
}

# 安装依赖
install_dependencies() {
    echo "=========================================="
    echo "安装依赖"
    echo "=========================================="
    echo ""
    
    # 前端依赖
    echo "安装前端依赖..."
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ 前端依赖安装完成${NC}"
    echo ""
    
    # 后端依赖
    echo "安装后端依赖..."
    if command -v python3 &> /dev/null; then
        PYTHON=python3
    else
        PYTHON=python
    fi
    
    cd backend
    $PYTHON -m pip install -r requirements.txt
    cd ..
    echo -e "${GREEN}✓ 后端依赖安装完成${NC}"
    echo ""
}

# 部署指引
deployment_guide() {
    echo "=========================================="
    echo "部署指引"
    echo "=========================================="
    echo ""
    
    if [ "$PLATFORM_BACKEND" == "render" ]; then
        echo -e "${YELLOW}后端部署到 Render:${NC}"
        echo "1. 访问 https://render.com"
        echo "2. 点击 'New +' -> 'Web Service'"
        echo "3. 连接您的 GitHub 仓库"
        echo "4. 配置:"
        echo "   - Root Directory: backend"
        echo "   - Build Command: pip install -r requirements.txt"
        echo "   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port \$PORT"
        echo "5. 环境变量:"
        echo "   - DEEPSEEK_API_KEY=${DEEPSEEK_KEY}"
        echo ""
    fi
    
    if [ "$PLATFORM_BACKEND" == "railway" ]; then
        echo -e "${YELLOW}后端部署到 Railway:${NC}"
        echo "1. 访问 https://railway.app"
        echo "2. 导入 GitHub 仓库"
        echo "3. 选择 'backend' 目录"
        echo "4. 环境变量:"
        echo "   - DEEPSEEK_API_KEY=${DEEPSEEK_KEY}"
        echo "   - PORT=8000"
        echo ""
    fi
    
    if [ "$PLATFORM_BACKEND" == "flyio" ]; then
        echo -e "${YELLOW}后端部署到 Fly.io:${NC}"
        echo "运行以下命令:"
        echo "  cd backend"
        echo "  fly auth login"
        echo "  fly launch"
        echo "  fly secrets set DEEPSEEK_API_KEY=${DEEPSEEK_KEY}"
        echo "  fly deploy"
        echo ""
    fi
    
    if [ "$PLATFORM_FRONTEND" == "vercel" ]; then
        echo -e "${YELLOW}前端部署到 Vercel:${NC}"
        echo "运行以下命令:"
        echo "  npm install -g vercel"
        echo "  cd frontend"
        echo "  vercel login"
        echo "  vercel --prod"
        echo ""
        echo "或访问 https://vercel.com 使用 GitHub 集成"
        echo ""
    fi
    
    if [ "$PLATFORM_FRONTEND" == "cloudflare" ]; then
        echo -e "${YELLOW}前端部署到 Cloudflare Pages:${NC}"
        echo "1. 访问 Cloudflare Dashboard"
        echo "2. Pages -> Create a project"
        echo "3. 连接 GitHub 仓库"
        echo "4. 配置:"
        echo "   - Build command: cd frontend && npm run build"
        echo "   - Build output directory: frontend/build"
        echo ""
    fi
    
    if [ "$PLATFORM_FRONTEND" == "local" ] && [ "$PLATFORM_BACKEND" == "local" ]; then
        echo -e "${YELLOW}本地运行:${NC}"
        echo ""
        echo "启动后端:"
        echo "  cd backend"
        echo "  uvicorn app.main:app --reload"
        echo ""
        echo "启动前端 (新终端):"
        echo "  cd frontend"
        echo "  npm start"
        echo ""
        echo "访问: http://localhost:3000"
        echo ""
    fi
}

# 创建部署脚本
create_deploy_scripts() {
    echo "创建部署脚本..."
    
    # 本地启动脚本 (Linux/Mac)
    cat > start-local.sh << 'EOF'
#!/bin/bash

echo "启动 Decision Assistant..."

# 启动后端
echo "启动后端..."
cd backend
uvicorn app.main:app --reload &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端
echo "启动前端..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "后端运行在: http://localhost:8000"
echo "前端运行在: http://localhost:3000"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待中断
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
EOF
    chmod +x start-local.sh
    echo -e "${GREEN}✓ 创建 start-local.sh${NC}"
    
    # 测试脚本
    cat > test-deployment.sh << 'EOF'
#!/bin/bash

# 测试部署脚本

echo "测试部署..."
echo ""

# 检查后端
echo "测试后端健康检查..."
BACKEND_URL=${1:-http://localhost:8000}
curl -s "${BACKEND_URL}/health" | jq .

if [ $? -eq 0 ]; then
    echo "✓ 后端正常"
else
    echo "✗ 后端异常"
fi

echo ""

# 检查前端
echo "测试前端..."
FRONTEND_URL=${2:-http://localhost:3000}
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "${FRONTEND_URL}")

if [ "$HTTP_STATUS" == "200" ]; then
    echo "✓ 前端正常"
else
    echo "✗ 前端异常 (HTTP ${HTTP_STATUS})"
fi

echo ""
echo "测试完成"
EOF
    chmod +x test-deployment.sh
    echo -e "${GREEN}✓ 创建 test-deployment.sh${NC}"
    
    echo ""
}

# 生成部署报告
generate_report() {
    cat > DEPLOYMENT_INFO.md << EOF
# 部署信息

**部署日期:** $(date)
**方案:** 前端=${PLATFORM_FRONTEND}, 后端=${PLATFORM_BACKEND}

## 环境变量

### 后端
\`\`\`
DEEPSEEK_API_KEY=${DEEPSEEK_KEY:0:10}...
ALLOWED_ORIGINS=["${FRONTEND_URL}"]
\`\`\`

### 前端
\`\`\`
REACT_APP_API_URL=${BACKEND_URL}
\`\`\`

## URL

- 前端: ${FRONTEND_URL}
- 后端: ${BACKEND_URL}

## 下一步

1. 部署后端到 ${PLATFORM_BACKEND}
2. 部署前端到 ${PLATFORM_FRONTEND}
3. 运行测试: \`./test-deployment.sh ${BACKEND_URL} ${FRONTEND_URL}\`

## 文档

- [部署方案完整指南](部署方案完整指南.md)
- [部署快速检查](部署快速检查.md)

---
生成时间: $(date)
EOF
    
    echo -e "${GREEN}✓ 生成部署报告: DEPLOYMENT_INFO.md${NC}"
    echo ""
}

# 主函数
main() {
    clear
    
    echo ""
    echo "  ____            _     _               "
    echo " |  _ \\ ___  ___(_)___(_) ___  _ __  "
    echo " | | | / _ \\/ __| / __| |/ _ \\| '_ \\ "
    echo " | |_| |  __/ (__| \\__ \\ | (_) | | | |"
    echo " |____/ \\___|\\___|_|___/_|\\___/|_| |_|"
    echo "                                        "
    echo "       Assistant Deployment Setup      "
    echo ""
    
    check_tools
    select_deployment
    collect_env_vars
    create_env_files
    install_dependencies
    create_deploy_scripts
    generate_report
    deployment_guide
    
    echo "=========================================="
    echo -e "${GREEN}配置完成！${NC}"
    echo "=========================================="
    echo ""
    echo "下一步:"
    echo "1. 查看部署信息: cat DEPLOYMENT_INFO.md"
    echo "2. 查看详细指南: cat 部署方案完整指南.md"
    echo ""
    
    if [ "$PLATFORM_FRONTEND" == "local" ] && [ "$PLATFORM_BACKEND" == "local" ]; then
        echo "本地运行:"
        echo "  ./start-local.sh"
        echo ""
    else
        echo "开始部署:"
        echo "  按照上面的部署指引操作"
        echo ""
    fi
    
    echo -e "${GREEN}祝部署顺利！${NC}"
}

# 运行主函数
main

