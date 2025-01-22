# 导入环境变量（假设.env文件使用的是标准格式）
$envFilePath = ".\.env"
if (Test-Path $envFilePath) {
    $envFileContent = Get-Content $envFilePath
    foreach ($line in $envFileContent) {
        if ($line -match '^\s*([^=]+)=(.*)') {
            $key = $Matches[1].Trim()
            $value = $Matches[2].Trim()
            [Environment]::SetEnvironmentVariable($key, $value, [EnvironmentVariableTarget]::Process)
        }
    }
} else {
    Write-Error ".env file not found!"
    exit
}

# 检查 PocketBase 是否正在运行
$process = Get-Process -Name "pocketbase" -ErrorAction SilentlyContinue
if ($null -eq $process) {
    # 检查端口 8090 是否被占用
    $portInUse = Get-NetTCPConnection -LocalPort 8090 -ErrorAction SilentlyContinue
    if ($null -eq $portInUse) {
        Write-Host "Starting PocketBase..."
        Start-Process -FilePath "../pb/pocketbase.exe" -ArgumentList "serve", "--http=127.0.0.1:8090" -NoNewWindow
        Start-Sleep -Seconds 5
    } else {
        Write-Host "Port 8090 is already in use."
    }
} else {
    Write-Host "PocketBase is already running."
}

# import os
# load_dotenv()
# wiseflow_logger.info(f"PB_API_AUTH: {os.getenv('PB_API_AUTH')}")



# 运行 Python 脚本
python .\general_process.py