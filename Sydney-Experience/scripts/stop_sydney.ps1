# ============================================================
#  仅停止本项目 runtime 目录中的 KoboldCpp 进程
# ============================================================
param([switch]$Force)
$ErrorActionPreference = 'Stop'

$SydneyDir = Split-Path -Parent $PSScriptRoot
$ExpectedExe = Join-Path $SydneyDir 'runtime\koboldcpp.exe'
$processes = @(Get-Process -Name koboldcpp -ErrorAction SilentlyContinue | Where-Object {
    try { $_.Path -eq $ExpectedExe } catch { $false }
})

if ($processes.Count -eq 0) {
    Write-Host 'Sydney 当前没有运行。' -ForegroundColor Yellow
    exit 0
}

Write-Host "将停止本项目 KoboldCpp 进程: $($processes.Id -join ', ')" -ForegroundColor Yellow
if (-not $Force) {
    $answer = Read-Host '请输入 STOP 确认'
    if ($answer -cne 'STOP') {
        Write-Host '已取消。'
        exit 0
    }
}

$processIds = @($processes.Id)
Stop-Process -Id $processIds -Force -ErrorAction SilentlyContinue
Start-Sleep -Milliseconds 300
$remaining = @(Get-Process -Id $processIds -ErrorAction SilentlyContinue)
if ($remaining.Count -gt 0) {
    Write-Host "[错误] 以下进程未能停止: $($remaining.Id -join ', ')" -ForegroundColor Red
    exit 1
}
Write-Host 'Sydney 已停止。' -ForegroundColor Green
