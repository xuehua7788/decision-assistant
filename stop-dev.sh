#!/bin/bash

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo ""
echo "========================================"
echo "  Decision Assistant - 停止服务"
echo "========================================"
echo ""

# 停止后端
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    echo -e "${BLUE}停止后端服务 (PID: $BACKEND_PID)...${NC}"
    
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        kill $BACKEND_PID
        echo -e "${GREEN}✅ 后端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  后端服务未运行${NC}"
    fi
    
    rm backend.pid
else
    echo -e "${YELLOW}⚠️  未找到后端 PID 文件${NC}"
fi

echo ""

# 停止前端
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    echo -e "${BLUE}停止前端服务 (PID: $FRONTEND_PID)...${NC}"
    
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        kill $FRONTEND_PID
        echo -e "${GREEN}✅ 前端服务已停止${NC}"
    else
        echo -e "${YELLOW}⚠️  前端服务未运行${NC}"
    fi
    
    rm frontend.pid
else
    echo -e "${YELLOW}⚠️  未找到前端 PID 文件${NC}"
fi

echo ""

# 清理日志文件（可选）
read -p "是否删除日志文件? (y/N): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -f backend.log ]; then
        rm backend.log
        echo -e "${GREEN}✅ 已删除 backend.log${NC}"
    fi
    if [ -f frontend.log ]; then
        rm frontend.log
        echo -e "${GREEN}✅ 已删除 frontend.log${NC}"
    fi
fi

echo ""
echo "========================================"
echo -e "  ${GREEN}✅ 服务已停止${NC}"
echo "========================================"
echo ""

