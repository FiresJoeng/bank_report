@echo off
setlocal

:: 加载环境变量
if exist .env (
    for /f "tokens=*" %%a in (.env) do (
        set "%%a"
    )
)

:: 检查 PocketBase 是否已在运行
tasklist /fi "IMAGENAME eq pocketbase.exe" /fo csv 2>nul | find /i "pocketbase.exe" >nul
if "%ERRORLEVEL%"=="0" (
    echo PocketBase is already running.
) else (
    :: 检查端口 8090 是否已被占用
    netstat -an | findstr ":8090" >nul
    if "%ERRORLEVEL%"=="0" (
        echo Port 8090 is already in use.
    ) else (
        echo Starting PocketBase...
        start /b "" ..\pb\pocketbase.exe serve --http=127.0.0.1:8090
    )
)

:: 运行 Python 脚本
python general_process.py

endlocal