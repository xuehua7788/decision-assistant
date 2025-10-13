#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  Decision Assistant - 开发环境启动"
echo "========================================"
echo ""

# 检查 Python
echo -e "${BLUE}[1/5] 检查 Python 环境...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 未安装${NC}"
    echo "请安装 Python 3.8+ 并重试"
    exit 1
fi
python3 --version
echo -e "${GREEN}✅ Python 环境正常${NC}"
echo ""

# 检查 Node.js
echo -e "${BLUE}[2/5] 检查 Node.js 环境...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js 未安装${NC}"
    echo "请安装 Node.js 14+ 并重试"
    exit 1
fi
node --version
npm --version
echo -e "${GREEN}✅ Node.js 环境正常${NC}"
echo ""

# 启动后端
echo -e "${BLUE}[3/5] 启动后端服务...${NC}"
cd backend
echo "安装后端依赖..."
pip3 install -r requirements.txt > /dev/null 2>&1

echo -e "${YELLOW}启动后端服务器...${NC}"
uvicorn app.main:app --reload > ../backend.log 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > ../backend.pid
echo -e "${GREEN}✅ 后端服务启动 (PID: $BACKEND_PID)${NC}"
cd ..
sleep 5
echo ""

# 启动前端
echo -e "${BLUE}[4/5] 启动前端服务...${NC}"
cd frontend
echo "安装前端依赖（首次较慢）..."
npm install > /dev/null 2>&1

echo -e "${YELLOW}启动前端服务器...${NC}"
BROWSER=none npm start > ../frontend.log 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > ../frontend.pid
echo -e "${GREEN}✅ 前端服务启动 (PID: $FRONTEND_PID)${NC}"
cd ..
sleep 10
echo ""

# 打开浏览器
echo -e "${BLUE}[5/5] 打开浏览器...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3000
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open &> /dev/null; then
        xdg-open http://localhost:3000
    fi
fi
echo ""

# 显示信息
echo "========================================"
echo -e "  ${GREEN}✅ 所有服务已启动！${NC}"
echo "========================================"
echo ""
echo "📍 访问地址:"
echo "  - 前端界面: http://localhost:3000"
echo "  - 后端 API: http://localhost:8000"
echo "  - API 文档: http://localhost:8000/docs"
echo ""
echo "💡 提示:"
echo "  - 后端日志: tail -f backend.log"
echo "  - 前端日志: tail -f frontend.log"
echo ""
echo "🛑 停止服务:"
echo "  - 运行: ./stop-dev.sh"
echo "  - 或手动: kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📚 文档:"
echo "  - 技术总结: 技术总结-第三方开发者.md"
echo "  - 集成指南: INTEGRATION_GUIDE.md"
echo "  - 快速启动: 快速启动指南.md"
echo ""
echo "========================================"
echo ""

