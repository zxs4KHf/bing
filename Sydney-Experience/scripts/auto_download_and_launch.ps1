# ============================================================
#  Sydney 全自动一条龙：断点续传 → SHA-256 校验 → 直接启动
#  零交互版本 —— 用户于 2026-07-26 明确授权：
#  「你来帮我下载，中间能不问我就不问我」（当日已确认 Wi-Fi）
#  唯一刹车：下方 5 秒倒计时内关闭窗口即可取消。
# ============================================================
$ErrorActionPreference = 'Stop'

$SydneyDir    = Split-Path -Parent $PSScriptRoot
$ModelDir     = Join-Path $SydneyDir 'models\Free-Sydney-V2-13B'
$ModelPath    = Join-Path $ModelDir 'free_sydney_v2_13b.Q4_K_M.gguf'
$Url          = 'https://huggingface.co/TheBloke/Free_Sydney_V2_13B-GGUF/resolve/main/free_sydney_v2_13b.Q4_K_M.gguf?download=true'
$ExpectedSize = 7865956288
$ExpectedSha  = 'A47CB0624D876B6BB0372733E401C7126006390213D5CB99772890B1478604B1'

function Fail($msg) {
    Write-Host ''
    Write-Host "[失败] $msg" -ForegroundColor Red
    Write-Host '窗口保持打开以便查看原因；再次双击本脚本可从断点继续。' -ForegroundColor Yellow
    Read-Host '按回车关闭'
    exit 1
}

Write-Host ''
Write-Host '=== Sydney 全自动：下载 → 校验 → 启动 ===' -ForegroundColor Cyan
if (-not (Test-Path $ModelDir)) { New-Item -ItemType Directory -Path $ModelDir -Force | Out-Null }

$cur = 0
if (Test-Path $ModelPath) { $cur = (Get-Item $ModelPath).Length }
if ($cur -gt $ExpectedSize) { Fail "本地文件比官方完整文件还大，可能已损坏。请删除后重试：$ModelPath" }

if ($cur -eq $ExpectedSize) {
    Write-Host '模型大小已完整，跳过下载。' -ForegroundColor Green
}
else {
    $remain = ($ExpectedSize - $cur) / 1GB
    Write-Host ("断点续传：已有 {0:N0} 字节，还需约 {1:N2} GB" -f $cur, $remain)
    Write-Host '按 2026-07-26 的授权跳过 Wi-Fi 确认。若你当前在用移动流量，请立即关闭本窗口！' -ForegroundColor Yellow
    for ($i = 5; $i -ge 1; $i--) { Write-Host "  $i..." -NoNewline; Start-Sleep -Seconds 1 }
    Write-Host ' 开始下载。'
    if (-not (Get-Command curl.exe -ErrorAction SilentlyContinue)) { Fail '未找到 curl.exe（Windows 10 1803+ 应自带）。' }
    & curl.exe -L --fail --retry 8 --retry-delay 5 -C - --progress-bar -o $ModelPath $Url
    if ($LASTEXITCODE -ne 0) { Fail "下载中断（curl 退出码 $LASTEXITCODE）。已下载部分已保留。" }
}

$size = (Get-Item $ModelPath).Length
if ($size -ne $ExpectedSize) { Fail ("文件大小不符：实际 {0:N0}，应为 {1:N0}。再次双击可继续补齐。" -f $size, $ExpectedSize) }
Write-Host ("文件大小正确：{0:N0} 字节 ✓" -f $size) -ForegroundColor Green

Write-Host '正在计算 SHA-256（约 1~3 分钟，请稍候）...'
$sha = (Get-FileHash -Algorithm SHA256 -Path $ModelPath).Hash
if ($sha -ne $ExpectedSha) { Fail "SHA-256 不匹配！实际 $sha，应为 $ExpectedSha。文件可能损坏，建议删除后重下。" }
Write-Host 'SHA-256 与 Hugging Face 官方值一致 ✓' -ForegroundColor Green

Write-Host ''
Write-Host '🎉 模型完整就绪，正在启动 Sydney（浏览器将自动打开）...' -ForegroundColor Cyan
& (Join-Path $PSScriptRoot 'launch_sydney.ps1')
