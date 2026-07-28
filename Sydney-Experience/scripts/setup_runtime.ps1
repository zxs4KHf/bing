# ============================================================
#  KoboldCpp v1.117.1 Windows CUDA 运行时下载 + 完整性校验
# ============================================================
param([switch]$NetworkConfirmed)
$ErrorActionPreference = 'Stop'

$SydneyDir = Split-Path -Parent $PSScriptRoot
$RuntimeDir = Join-Path $SydneyDir 'runtime'
$RuntimePath = Join-Path $RuntimeDir 'koboldcpp.exe'
$Url = 'https://github.com/LostRuins/koboldcpp/releases/download/v1.117.1/koboldcpp.exe'
$ExpectedSize = 637224341
$ExpectedSha = 'A658AB9A03A2B9E42805368B7D7FC1E25B5DF53E9C1D39DF8A2A8B59B0F0C52E'

if (-not (Test-Path $RuntimeDir)) { New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null }
$currentSize = if (Test-Path $RuntimePath) { (Get-Item $RuntimePath).Length } else { 0 }

if ($currentSize -gt $ExpectedSize) {
    Write-Host "[错误] 运行时文件大于官方资产，可能损坏: $RuntimePath" -ForegroundColor Red
    exit 1
}

if ($currentSize -lt $ExpectedSize) {
    if (-not $NetworkConfirmed) {
        Write-Host '运行时约 637 MB，只允许在 Wi-Fi/固定宽带下下载。' -ForegroundColor Yellow
        $answer = Read-Host '确认当前网络后输入 y'
        if ($answer -ne 'y') { Write-Host '已取消。'; exit 0 }
    }
    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
        Write-Host '[错误] 未找到 curl.exe（Windows 10 1803+ 应自带）。' -ForegroundColor Red
        exit 1
    }
    Write-Host ("[下载] KoboldCpp：已有 {0:N0} / {1:N0} 字节" -f $currentSize, $ExpectedSize) -ForegroundColor Cyan
    & curl.exe -L --fail --retry 8 --retry-delay 5 -C - --progress-bar -o $RuntimePath $Url
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 下载中断（curl 退出码 $LASTEXITCODE）；再次运行可续传。" -ForegroundColor Red
        exit 1
    }
}

$actualSize = (Get-Item $RuntimePath).Length
if ($actualSize -ne $ExpectedSize) {
    Write-Host "[错误] 运行时大小不符：$actualSize / $ExpectedSize" -ForegroundColor Red
    exit 1
}

Write-Host '[校验] 正在计算 KoboldCpp SHA-256...'
$actualSha = (Get-FileHash -Algorithm SHA256 -LiteralPath $RuntimePath).Hash
if ($actualSha -ne $ExpectedSha) {
    Write-Host "[错误] SHA-256 不匹配。实际: $actualSha" -ForegroundColor Red
    exit 1
}

Write-Host '[完成] KoboldCpp v1.117.1 大小与 SHA-256 均正确。' -ForegroundColor Green
