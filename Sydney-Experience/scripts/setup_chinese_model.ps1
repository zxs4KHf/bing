# ============================================================
#  月窗中文增强：检查或安装 Ollama qwen3:8b
#  大模型下载前每次都要求明确确认 Wi-Fi / 固定宽带。
# ============================================================
param([string]$Model = 'qwen3:8b')
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '=== Sydney 月窗 · 中文增强模型 ===' -ForegroundColor Cyan

$Ollama = Get-Command ollama.exe -ErrorAction SilentlyContinue
if (-not $Ollama) {
    Write-Host '[未安装] 没有找到 Ollama。' -ForegroundColor Yellow
    Write-Host '请先从 https://ollama.com/download/windows 安装 Windows 版 Ollama，再重新运行本脚本。'
    Read-Host '按回车退出'
    exit 1
}

$installed = & $Ollama.Source list 2>$null
if ($LASTEXITCODE -eq 0 -and ($installed -match "(?m)^$([regex]::Escape($Model))\s")) {
    Write-Host "[已就绪] $Model 已安装，月窗会自动把中文对话交给它。" -ForegroundColor Green
    exit 0
}

Write-Host "即将通过 Ollama 下载 $Model（约 5.2 GB）。" -ForegroundColor Yellow
Write-Host '只有当前正在使用 Wi-Fi 或固定宽带时才能继续。'
$answer = Read-Host '确认网络合适后输入 YES；其他输入取消'
if ($answer -cne 'YES') {
    Write-Host '已取消；没有开始下载。' -ForegroundColor Yellow
    exit 1
}

& $Ollama.Source pull $Model
if ($LASTEXITCODE -ne 0) {
    Write-Host "[错误] Ollama 下载失败，退出码 $LASTEXITCODE。再次运行可继续。" -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host "[完成] $Model 已就绪。现在可以双击 launch_sydney_app.bat。" -ForegroundColor Green
