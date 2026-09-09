#!/bin/bash

echo "🚀 启动数据分析系统..."

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装"
    exit 1
fi

# 安装依赖
echo "📦 安装依赖..."
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 启动服务
echo "🔧 启动后端服务..."
python main.py &
BACKEND_PID=$!

echo "🎨 启动前端界面..."
streamlit run streamlit_app.py --server.port=8501 --server.address=0.0.0.0 &
FRONTEND_PID=$!

echo "✅ 服务已启动!"
echo "📊 前端界面: http://localhost:8501"
echo "📡 API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"

# 等待进程
wait $BACKEND_PID $FRONTEND_PID