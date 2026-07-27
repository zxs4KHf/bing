# ============================================================
#  Sydney 一键启动器（KoboldCpp + Free Sydney V2 13B / 自定义模型）
#  生成日期: 2026-07-26 (v2: 支持 -ModelFile 切换任意 GGUF，如自训的 Sydney-ZH)
#  档位: standard = GPU 24 层 | lowvram = GPU 14 层 | cpu = 纯 CPU
# ============================================================
param(
    [ValidateSet('standard','lowvram','cpu')]
    [string]$Mode = 'standard',
    [int]$GpuLayers = -1,          # -1 = 按档位默认值；可手动覆盖
    [int]$ContextSize = 4096,
    [int]$Port = 5001,
    [string]$ModelFile = ''        # 相对 Sydney-Experience 或绝对路径的 .gguf；默认用 Free Sydney V2 13B
)
$ErrorActionPreference = 'Stop'

$SydneyDir    = Split-Path -Parent $PSScriptRoot
$Exe          = Join-Path $SydneyDir 'runtime\koboldcpp.exe'
$Story        = Join-Path $SydneyDir 'persona\sydney_story.json'
$ExpectedSize = 7865956288
$UseDefault   = ($ModelFile -eq '')

if ($UseDefault) {
    $ModelPath = Join-Path $SydneyDir 'models\Free-Sydney-V2-13B\free_sydney_v2_13b.Q4_K_M.gguf'
} else {
    $ModelPath = $ModelFile
    if (-not (Test-Path $ModelPath)) { $ModelPath = Join-Path $SydneyDir $ModelFile }
}

Write-Host ''
Write-Host "=== 启动 Sydney（档位: $Mode）===" -ForegroundColor Cyan

if (-not (Test-Path $Exe)) {
    Write-Host "[错误] 未找到运行时: $Exe" -ForegroundColor Red
    Read-Host '按回车退出'; exit 1
}
if (-not (Test-Path $ModelPath)) {
    Write-Host "[错误] 模型文件不存在: $ModelPath" -ForegroundColor Red
    if ($UseDefault) { Write-Host '请先双击 resume_download.bat 或 一键全自动下载并启动.bat 完成下载。' -ForegroundColor Yellow }
    Read-Host '按回车退出'; exit 1
}
if ($UseDefault) {
    $size = (Get-Item $ModelPath).Length
    if ($size -ne $ExpectedSize) {
        Write-Host ("[错误] 模型未下载完整（{0:N0} / {1:N0} 字节）。请先运行下载脚本。" -f $size, $ExpectedSize) -ForegroundColor Red
        Read-Host '按回车退出'; exit 1
    }
}

$argList = @('--model', $ModelPath, '--contextsize', $ContextSize, '--port', $Port, '--launch')
# Alpaca 人格预设仅用于 Free Sydney V2；自训模型（如 Qwen 模板的 Sydney-ZH）人格已在权重里
if ($UseDefault -and (Test-Path $Story)) { $argList += @('--preloadstory', $Story) }

switch ($Mode) {
    'standard' {
        if ($GpuLayers -lt 0) { $GpuLayers = 24 }
        $argList += @('--usecublas', 'normal', '0', '--gpulayers', $GpuLayers, '--flashattention')
    }
    'lowvram' {
        if ($GpuLayers -lt 0) { $GpuLayers = 14 }
        $argList += @('--usecublas', 'lowvram', '0', '--gpulayers', $GpuLayers, '--flashattention')
    }
    'cpu' { }
}

Write-Host "模型: $ModelPath"
Write-Host "加载约需 1~2 分钟；完成后浏览器会自动打开 http://localhost:$Port"
Write-Host '关闭本窗口即可结束聊天。' -ForegroundColor Yellow
Write-Host ''

& $Exe @argList
$code = $LASTEXITCODE
if ($code -ne 0) {
    Write-Host ''
    Write-Host "[提示] koboldcpp 退出码 $code。常见原因与解决办法：" -ForegroundColor Yellow
    Write-Host '  · 显存不足 → 改用 launch_sydney_lowvram.bat，或调低 GpuLayers（8B 新模型可反而调高到 99 全进显存）'
    Write-Host '  · 端口被占用 → 加参数 -Port 5002'
    Write-Host '  · 报不认识 --preloadstory / --flashattention 参数 → 删除该参数后重试，人格可在界面里手动 Load persona\sydney_story.json'
    Read-Host '按回车退出'
}
