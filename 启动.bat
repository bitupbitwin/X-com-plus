@echo off
chcp 65001 >nul
cd /d "%~dp0"

REM 检查依赖，缺失则自动安装
python -c "import PySide6, serial, openpyxl" 2>nul
if errorlevel 1 (
    echo 正在安装依赖...
    python -m pip install -r requirements.txt
)

python run.py
if errorlevel 1 (
    echo.
    echo 程序异常退出，详情见 xcom_error.log
    pause
)
