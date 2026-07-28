# ============================================================
#  Sydney 一键准备运行时 → 下载模型 → 校验 → 启动
#  下载前只询问一次当前网络；授权不会跨运行保存。
# ============================================================
$ErrorActionPreference = 'Stop'

Write-Host ''
Write-Host '=== Sydney 一键准备并启动 ===' -ForegroundColor Cyan
Write-Host '可能下载约 637 MB 运行时和 7.87 GB 模型；已完成的文件只校验、不重下。' -ForegroundColor Yellow
$answer = Read-Host '请确认当前已连接 Wi-Fi/固定宽带，继续请输入 y'
if ($answer -ne 'y') {
    Write-Host '已取消，未产生任何下载流量。'
    Read-Host '按回车退出'
    exit 0
}

$runtimeScript = Join-Path $PSScriptRoot 'setup_runtime.ps1'
$modelScript = Join-Path $PSScriptRoot 'resume_download.ps1'
foreach ($script in @($runtimeScript, $modelScript)) {
    if (-not (Test-Path $script)) {
        Write-Host "[错误] 找不到脚本: $script" -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
}

& $runtimeScript -NetworkConfirmed
if (-not $?) { exit 1 }
& $modelScript -NetworkConfirmed -LaunchAfterVerify
if (-not $?) { exit 1 }
exit 0
