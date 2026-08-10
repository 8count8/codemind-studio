@echo off
chcp 65001 > nul
set PYTHONIOENCODING=utf-8
echo 正在初始化部署环境...

REM 获取脚本所在目录路径
cd /d "%~dp0"

REM 检查虚拟环境完整性
if exist venv\ (
    echo 检测到现有虚拟环境，正在验证完整性...
    if not exist "venv\Scripts\activate.bat" (
        echo 虚拟环境不完整，正在删除重建...
        rmdir /s /q venv
    ) else if not exist "venv\Scripts\python.exe" (
        echo 虚拟环境不完整，正在删除重建...
        rmdir /s /q venv
    ) else if not exist "venv\Scripts\pip.exe" (
        echo 虚拟环境不完整，正在删除重建...
        rmdir /s /q venv
    ) else (
        echo 虚拟环境验证通过，跳过创建步骤
        goto activate_venv
    )
)

echo 正在创建虚拟环境...
python -m venv venv
if %errorlevel% neq 0 (
    echo 错误：创建虚拟环境失败，请检查Python环境
    pause
    exit /b 1
)
echo 虚拟环境创建成功！

:activate_venv
REM 激活虚拟环境并安装依赖
echo 正在激活虚拟环境...
call venv\Scripts\activate.bat
echo 虚拟环境激活成功

echo 正在升级pip工具...
python -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://mirrors.aliyun.com/pypi/simple/
if %errorlevel% neq 0 (
    echo 错误：pip升级失败，请检查网络连接
    pause
    exit /b 1
)
echo pip升级成功！

echo 正在验证依赖完整性...
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --extra-index-url https://mirrors.aliyun.com/pypi/simple/
if %errorlevel% neq 0 (
    echo 错误：依赖安装失败，请检查requirements.txt
    pause
    exit /b 1
)
echo 所有依赖已验证安装！

echo 安装完成，按任意键退出...
pause