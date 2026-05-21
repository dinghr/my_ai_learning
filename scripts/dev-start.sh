#!/bin/bash
# AI助学小程序 - 本地开发一键启动
# 用法: ./scripts/dev-start.sh

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

echo "🦕 启动 AI助学小程序本地开发环境..."
echo ""

# 检查 .env.development
if [ ! -f "$BACKEND_DIR/.env.development" ]; then
    echo "⚠️  backend/.env.development 不存在，从 .env.example 复制..."
    cp "$BACKEND_DIR/.env.example" "$BACKEND_DIR/.env.development"
fi

# 检查 DeepSeek API Key
if ! grep -q "deepseek_api_key=sk-" "$BACKEND_DIR/.env.development" 2>/dev/null; then
    echo "⚠️  请在 backend/.env.development 中配置 deepseek_api_key"
    echo "   示例: deepseek_api_key=sk-your-key"
fi

# 启动后端（后台）
echo "🚀 启动后端服务 (http://localhost:8000)..."
cd "$BACKEND_DIR"
source venv/bin/activate 2>/dev/null || {
    echo "❌ 虚拟环境不存在，请先创建: cd backend && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
}
ENV=development uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# 等待后端启动
sleep 2
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 后端启动成功"
else
    echo "❌ 后端启动失败"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

# 启动前端（前台）
echo ""
echo "🚀 启动前端开发服务器 (http://localhost:10086)..."
cd "$FRONTEND_DIR"
npm run dev:h5 &
FRONTEND_PID=$!

# 等待前端启动
sleep 5
echo ""
echo "🎉 本地开发环境已启动！"
echo ""
echo "  后端 API: http://localhost:8000"
echo "  前端 H5:  http://localhost:10086"
echo "  数据库:   backend/ai_learning_dev.db"
echo ""
echo "按 Ctrl+C 停止所有服务"

# 捕获退出信号
trap 'echo ""; echo "🛑 停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit 0' INT TERM

wait
