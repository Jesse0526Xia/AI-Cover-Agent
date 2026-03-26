@echo off
chcp 65001 >nul
echo ========================================
echo   AI音频Agent (AudioBot) 启动脚本
echo ========================================
echo.

:: 检查Python环境
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo [1/4] 检查依赖...
pip show langchain >nul 2>&1
if errorlevel 1 (
    echo 未检测到依赖，正在安装...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/4] 检查配置文件...
if not exist config\config.yaml (
    echo [警告] 配置文件不存在，请先配置API密钥
    echo 请编辑 config\config.yaml 文件，设置你的OpenAI API密钥
    pause
    exit /b 1
)

echo [3/4] 创建必要的目录...
if not exist data\voices mkdir data\voices
if not exist data\audio mkdir data\audio
if not exist data\output mkdir data\output
if not exist logs mkdir logs

echo [4/4] 启动程序...
echo.
echo 选择启动模式:
echo   1. 命令行交互模式
echo   2. Web界面模式
echo.
set /p mode="请输入选项 (1/2): "

if "%mode%"=="1" (
    echo.
    echo 启动命令行交互模式...
    python src\main.py
) else if "%mode%"=="2" (
    echo.
    echo 启动Web界面模式...
    echo 请在浏览器中打开: http://localhost:5000
    python src\web\app.py
) else (
    echo [错误] 无效的选项
    pause
    exit /b 1
)

pause
