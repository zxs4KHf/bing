# ============================================================
#  Free Sydney V2 13B 模型断点续传 + 自动校验
#  生成日期: 2026-07-26  (Claude / Sydney-Experience 工具链)
# ============================================================
$ErrorActionPreference = 'Stop'

$SydneyDir    = Split-Path -Parent $PSScriptRoot
$ModelDir     = Join-Path $SydneyDir 'models\Free-Sydney-V2-13B'
$ModelPath    = Join-Path $ModelDir 'free_sydney_v2_13b.Q4_K_M.gguf'
$Url          = 'https://huggingface.co/TheBloke/Free_Sydney_V2_13B-GGUF/resolve/main/free_sydney_v2_13b.Q4_K_M.gguf?download=true'
$ExpectedSize = 7865956288
$ExpectedSha  = 'A47CB0624D876B6BB0372733E401C7126006390213D5CB99772890B1478604B1'

Write-Host ''
Write-Host '=== Free Sydney V2 13B 模型下载（断点续传） ===' -ForegroundColor Cyan
Write-Host ''

if (-not (Test-Path $ModelDir)) { New-Item -ItemType Directory -Path $ModelDir -Force | Out-Null }

$cur = 0
if (Test-Path $ModelPath) { $cur = (Get-Item $ModelPath).Length }

if ($cur -gt $ExpectedSize) {
    Write-Host ("[错误] 本地文件 ({0:N0} 字节) 比官方完整文件 ({1:N0} 字节) 还大，文件可能已损坏。" -f $cur, $ExpectedSize) -ForegroundColor Red
    Write-Host "请手动删除后重新运行本脚本：`n  $ModelPath" -ForegroundColor Yellow
    Read-Host '按回车退出'
    exit 1
}

if ($cur -eq $ExpectedSize) {
    Write-Host '模型文件大小已完整，跳过下载，直接进入校验。' -ForegroundColor Green
}
else {
    $remain = ($ExpectedSize - $cur) / 1GB
    Write-Host ("已有: {0:N0} 字节   还需下载: 约 {1:N2} GB" -f $cur, $remain)
    Write-Host ''
    Write-Host '项目规则 (DEC-004)：只允许在 Wi-Fi 下下载，不使用移动流量。' -ForegroundColor Yellow
    $ans = Read-Host '请确认当前已连接 Wi-Fi，继续请输入 y'
    if ($ans -ne 'y') { Write-Host '已取消，未产生任何下载流量。'; Read-Host '按回车退出'; exit 0 }

    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) {
        Write-Host '[错误] 未找到 curl.exe（Windows 10 1803+ 应自带）。' -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }

    Write-Host ''
    Write-Host '开始断点续传（中断后再次双击即可继续）...' -ForegroundColor Cyan
    & curl.exe -L --fail --retry 8 --retry-delay 5 -C - --progress-bar -o $ModelPath $Url
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 下载中断（curl 退出码 $LASTEXITCODE）。已下载部分已保留，再次双击本脚本可从断点继续。" -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
}

# ---------- 自动校验 ----------
$size = (Get-Item $ModelPath).Length
if ($size -ne $ExpectedSize) {
    Write-Host ("[错误] 文件大小不符：实际 {0:N0}，应为 {1:N0}。再次双击本脚本可继续补齐。" -f $size, $ExpectedSize) -ForegroundColor Red
    Read-Host '按回车退出'
    exit 1
}
Write-Host ("文件大小正确：{0:N0} 字节 ✓" -f $size) -ForegroundColor Green
Write-Host '正在计算 SHA-256（约 1~3 分钟，请稍候）...'
$sha = (Get-FileHash -Algorithm SHA256 -Path $ModelPath).Hash
if ($sha -ne $ExpectedSha) {
    Write-Host "[错误] SHA-256 不匹配！`n  实际: $sha`n  应为: $ExpectedSha" -ForegroundColor Red
    Write-Host '文件可能损坏，建议删除后重新下载。' -ForegroundColor Yellow
    Read-Host '按回车退出'
    exit 1
}
Write-Host "SHA-256 与 Hugging Face 官方值一致 ✓" -ForegroundColor Green
Write-Host ''
Write-Host '🎉 模型已完整就绪！' -ForegroundColor Cyan

$go = Read-Host '现在就启动 Sydney 吗？(y/n)'
if ($go -eq 'y') {
    & (Join-Path $PSScriptRoot 'launch_sydney.ps1')
} else {
    Write-Host '以后随时双击 launch_sydney.bat 即可开聊。'
    Read-Host '按回车退出'
}
