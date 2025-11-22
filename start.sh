#!/bin/bash

# RAG智能问答系统启动脚本

echo "=========================================="
echo "  RAG智能问答系统启动脚本"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 检查是否在虚拟环境中
if [ -z "$VIRTUAL_ENV" ] && [ -z "$CONDA_DEFAULT_ENV" ]; then
    echo "⚠️  警告: 未检测到虚拟环境"
    echo "   建议使用conda或venv创建虚拟环境"
    echo ""
fi

# 进入flask_app目录
cd "$(dirname "$0")/flask_app" || exit 1

# 检查环境变量
if [ "$USE_SILICONFLOW" = "true" ]; then
    echo "📝 使用硅基流动API模式（推荐）"
    if [ -z "$SILICONFLOW_API_KEY" ]; then
        echo "❌ 错误: USE_SILICONFLOW=true 但未设置 SILICONFLOW_API_KEY"
        echo "   请设置: export SILICONFLOW_API_KEY=your_api_key"
        exit 1
    fi
elif [ "$USE_OPENAI" = "true" ]; then
    echo "📝 使用OpenAI API模式"
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ 错误: USE_OPENAI=true 但未设置 OPENAI_API_KEY"
        echo "   请设置: export OPENAI_API_KEY=your_api_key"
        exit 1
    fi
else
    echo "📝 使用本地模型模式"
    echo "   确保本地模型服务运行在 http://localhost:8000"
    echo "   提示: 可以使用硅基流动API获得更快响应，设置 USE_SILICONFLOW=true"
fi

echo ""
echo "🚀 启动Flask应用..."
echo "   访问地址: http://localhost:5050"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 启动应用
python3 run.py

