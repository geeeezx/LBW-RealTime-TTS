@echo off
echo 正在使用uv设置Qwen流式文本生成环境...

REM 检查是否已安装uv
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo 未检测到uv，正在安装...
    powershell -Command "Invoke-WebRequest -Uri https://github.com/astral-sh/uv/releases/download/0.1.21/uv-x86_64-pc-windows-msvc.zip -OutFile uv.zip"
    powershell -Command "Expand-Archive -Path uv.zip -DestinationPath uv-temp"
    powershell -Command "Move-Item -Path uv-temp\uv.exe -Destination ."
    powershell -Command "Remove-Item -Path uv-temp -Recurse -Force"
    powershell -Command "Remove-Item -Path uv.zip -Force"
    echo uv已安装到当前目录
    set PATH=%CD%;%PATH%
) else (
    echo 已检测到uv...
)

REM 创建虚拟环境
if not exist .venv (
    echo 正在创建虚拟环境...
    uv venv
) else (
    echo 虚拟环境已存在...
)

REM 激活虚拟环境并安装依赖
echo 正在安装依赖...
call .venv\Scripts\activate.bat
uv pip install -r requirements.txt

echo 环境设置完成！
echo 可以通过以下命令启动服务：
echo python main.py 