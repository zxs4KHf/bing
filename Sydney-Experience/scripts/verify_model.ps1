# ============================================================
#  模型完整性独立校验（大小 + SHA-256）
#  生成日期: 2026-07-26
# ============================================================
$ErrorActionPreference = 'Stop'
$SydneyDir    = Split-Path -Parent $PSScriptRoot
$ModelPath    = Join-Path $SydneyDir 'models\Free-Sydney-V2-13B\free_sydney_v2_13b.Q4_K_M.gguf'
$ExpectedSize = 7865956288
$ExpectedSha  = 'A47CB0624D876B6BB0372733E401C7126006390213D5CB99772890B1478604B1'

Write-Host ''
Write-Host '=== Free Sydney V2 13B 模型校验 ===' -ForegroundColor Cyan

if (-not (Test-Path $ModelPath)) {
    Write-Host '[错误] 模型文件不存在，请先运行 resume_download.bat。' -ForegroundColor Red
    Read-Host '按回车退出'; exit 1
}
$size = (Get-Item $ModelPath).Length
if ($size -ne $ExpectedSize) {
    Write-Host ("[未完成] 当前 {0:N0} / {1:N0} 字节（{2:P1}）。运行 resume_download.bat 可断点续传。" -f $size, $ExpectedSize, ($size / $ExpectedSize)) -ForegroundColor Yellow
    Read-Host '按回车退出'; exit 1
}
Write-Host ("大小正确：{0:N0} 字节 ✓" -f $size) -ForegroundColor Green
Write-Host '正在计算 SHA-256（约 1~3 分钟）...'
$sha = (Get-FileHash -Algorithm SHA256 -Path $ModelPath).Hash
if ($sha -ne $ExpectedSha) {
    Write-Host "[错误] SHA-256 不匹配！`n  实际: $sha`n  应为: $ExpectedSha" -ForegroundColor Red
    Read-Host '按回车退出'; exit 1
}
Write-Host 'SHA-256 与官方值一致 ✓  模型完整可用。' -ForegroundColor Green
Read-Host '按回车退出'
