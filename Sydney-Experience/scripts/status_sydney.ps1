# ============================================================
#  Sydney 运行状态检查（进程 + 端口）
# ============================================================
param(
    [ValidateRange(1, 65535)]
    [int]$Port = 5001
)
$ErrorActionPreference = 'Stop'

$SydneyDir = Split-Path -Parent $PSScriptRoot
$ExpectedExe = Join-Path $SydneyDir 'runtime\koboldcpp.exe'
$processes = @(Get-Process -Name koboldcpp -ErrorAction SilentlyContinue | Where-Object {
    try { $_.Path -eq $ExpectedExe } catch { $false }
})

$listening = $false
$endpoints = @(
    @('::1', [Net.Sockets.AddressFamily]::InterNetworkV6),
    @('127.0.0.1', [Net.Sockets.AddressFamily]::InterNetwork)
)
foreach ($endpoint in $endpoints) {
    $client = $null
    try {
        $client = New-Object Net.Sockets.TcpClient($endpoint[1])
        $task = $client.ConnectAsync($endpoint[0], $Port)
        if ($task.Wait(1000) -and $client.Connected) {
            $listening = $true
            break
        }
    } catch {
        # Try the other address family.
    } finally {
        if ($null -ne $client) { $client.Dispose() }
    }
}

Write-Host ''
Write-Host '=== Sydney 运行状态 ===' -ForegroundColor Cyan
if ($processes.Count -gt 0) {
    Write-Host "[运行中] KoboldCpp 进程: $($processes.Id -join ', ')" -ForegroundColor Green
    foreach ($process in $processes) {
        Write-Host ("  PID {0}: 内存 {1:N0} MiB，CPU {2:N1}s" -f $process.Id, ($process.WorkingSet64 / 1MB), $process.CPU)
    }
} else {
    Write-Host '[未运行] 没有发现本项目的 KoboldCpp 进程。' -ForegroundColor Yellow
}

if ($listening) {
    Write-Host "[就绪] http://localhost:$Port" -ForegroundColor Green
} else {
    Write-Host "[未就绪] 端口 $Port 没有监听。" -ForegroundColor Yellow
}

if (Get-Command nvidia-smi -ErrorAction SilentlyContinue) {
    Write-Host ''
    & nvidia-smi --query-gpu=name,memory.used,memory.total,utilization.gpu --format=csv,noheader
}

if ($processes.Count -eq 0 -or -not $listening) { exit 1 }
