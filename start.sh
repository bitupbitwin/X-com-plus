#!/usr/bin/env bash
# Linux / macOS 启动脚本
cd "$(dirname "$0")" || exit 1

if ! python3 -c "import PySide6, serial, openpyxl" 2>/dev/null; then
    echo "正在安装依赖..."
    python3 -m pip install -r requirements.txt
fi

python3 run.py
