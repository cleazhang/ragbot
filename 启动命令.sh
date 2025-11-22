#!/bin/bash

# RAG智能问答系统 - 一键启动脚本

echo "=========================================="
echo "  RAG智能问答系统 - 快速启动"
echo "=========================================="
echo ""

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到python3，请先安装Python 3.8+"
    exit 1
fi

echo "✅ Python版本: $(python3 --version)"
echo ""

# 检查依赖
echo "📦 检查依赖..."
missing_deps=()
for dep in flask requests langchain openai; do
    if ! python3 -c "import $dep" 2>/dev/null; then
        missing_deps+=($dep)
    fi
done

if [ ${#missing_deps[@]} -gt 0 ]; then
    echo "⚠️  缺少依赖: ${missing_deps[*]}"
    echo "   正在安装..."
    pip3 install flask requests flask-sqlalchemy werkzeug langchain langchain-community langchain-core openai langchain-text-splitters faiss-cpu sentence-transformers pdfplumber beautifulsoup4 --quiet
    echo "✅ 依赖安装完成"
else
    echo "✅ 依赖检查通过"
fi
echo ""

# 检查环境变量
if [ -z "$USE_SILICONFLOW" ] && [ -z "$USE_OPENAI" ]; then
    echo "📝 未设置模型配置，使用硅基流动API（推荐）"
    echo ""
    read -p "是否使用硅基流动API? (y/n, 默认y): " use_sf
    use_sf=${use_sf:-y}
    
    if [ "$use_sf" = "y" ] || [ "$use_sf" = "Y" ]; then
        export USE_SILICONFLOW=true
        if [ -z "$SILICONFLOW_API_KEY" ]; then
            export SILICONFLOW_API_KEY=sk-ziyyhopxmxuffgjgwphatkqjxftfenxvmlhpcycnzisdxyrr
            echo "✅ 已设置默认API密钥"
        fi
        echo "📝 使用硅基流动API模式"
    else
        echo "📝 使用本地模型模式（需要先启动本地模型服务）"
    fi
elif [ "$USE_SILICONFLOW" = "true" ]; then
    echo "📝 使用硅基流动API模式"
    if [ -z "$SILICONFLOW_API_KEY" ]; then
        echo "❌ 错误: USE_SILICONFLOW=true 但未设置 SILICONFLOW_API_KEY"
        exit 1
    fi
elif [ "$USE_OPENAI" = "true" ]; then
    echo "📝 使用OpenAI API模式"
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "❌ 错误: USE_OPENAI=true 但未设置 OPENAI_API_KEY"
        exit 1
    fi
else
    echo "📝 使用本地模型模式"
    echo "   确保本地模型服务运行在 http://localhost:8000"
fi

echo ""
echo "🚀 启动Flask应用..."
echo "   访问地址: http://localhost:5050"
echo ""
echo "按 Ctrl+C 停止服务"
echo "=========================================="
echo ""

# 进入flask_app目录并启动
cd "$(dirname "$0")/flask_app" || exit 1
python3 run.py
