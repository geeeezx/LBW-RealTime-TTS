#!/bin/bash
echo "正在使用uv设置Qwen流式文本生成环境..."

# 检查是否已安装uv
if ! command -v uv &> /dev/null; then
    echo "未检测到uv，正在安装..."
    curl -sSf https://install.ultraviolet.rs | sh
    # 添加uv到PATH（可能需要重启终端）
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "已检测到uv..."
fi

# 创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "正在创建虚拟环境..."
    uv venv
else
    echo "虚拟环境已存在..."
fi

# 激活虚拟环境并安装依赖
echo "正在安装依赖..."
source .venv/bin/activate && uv pip install -r requirements.txt

echo "环境设置完成！"
echo "可以通过以下命令启动服务："
echo "cd LLM"
echo "python main.py" 