# ============================================================
#  Sydney 月窗：模型服务 + 独立聊天应用一键启动
# ============================================================
param(
    [ValidateSet('standard','lowvram','cpu')]
    [string]$Mode = 'standard',
    [int]$ModelPort = 5001,
    [int]$AppPort = 32123,
    [switch]$NoBrowser
)
$ErrorActionPreference = 'Stop'

$SydneyDir = Split-Path -Parent $PSScriptRoot
$Server = Join-Path $SydneyDir 'app\server.py'
$ModelLauncher = Join-Path $PSScriptRoot 'launch_sydney.ps1'

function Test-TcpPort {
    param([int]$TargetPort)
    foreach ($hostAddress in @('::1', '127.0.0.1')) {
        $client = New-Object Net.Sockets.TcpClient
        try {
            $task = $client.ConnectAsync($hostAddress, $TargetPort)
            if ($task.Wait(500) -and $client.Connected) { return $true }
        } catch {
            # Try the other loopback address.
        } finally {
            $client.Dispose()
        }
    }
    return $false
}

function Get-LocalJson {
    param([string]$Url, [int]$TimeoutMs = 5000)
    try {
        $request = [Net.HttpWebRequest]::Create($Url)
        $request.Proxy = $null
        $request.Timeout = $TimeoutMs
        $response = $request.GetResponse()
        try {
            $reader = New-Object IO.StreamReader($response.GetResponseStream(), [Text.Encoding]::UTF8)
            try { return ($reader.ReadToEnd() | ConvertFrom-Json) } finally { $reader.Dispose() }
        } finally {
            $response.Dispose()
        }
    } catch {
        return $null
    }
}

function Test-AppReady {
    param([int]$TargetPort)
    $result = Get-LocalJson -Url "http://localhost:$TargetPort/api/identity" -TimeoutMs 2000
    return ($null -ne $result -and $result.app -eq 'ok' -and $result.name -eq 'moon-window')
}

function Test-ModelReady {
    param([int]$TargetPort)
    $result = Get-LocalJson -Url "http://localhost:$TargetPort/api/v1/model" -TimeoutMs 5000
    return ($null -ne $result -and -not [string]::IsNullOrWhiteSpace([string]$result.result))
}

function Find-Python {
    $candidates = @(
        @{ Name = 'python.exe'; Prefix = @() },
        @{ Name = 'python3.exe'; Prefix = @() },
        @{ Name = 'py.exe'; Prefix = @('-3') }
    )
    foreach ($candidate in $candidates) {
        $command = Get-Command $candidate.Name -ErrorAction SilentlyContinue
        if (-not $command) { continue }
        $version = & $command.Source @($candidate.Prefix) -c 'import sys; print(int(sys.version_info[:2] >= (3, 10)))' 2>$null
        if ($LASTEXITCODE -eq 0 -and $version -eq '1') {
            return [PSCustomObject]@{ Exe = $command.Source; Prefix = $candidate.Prefix }
        }
    }
    return $null
}

Write-Host ''
Write-Host '=== Sydney 月窗 ===' -ForegroundColor Cyan

$Python = Find-Python
if (-not $Python) {
    Write-Host '[错误] 没有找到 Python 3。请安装 Python 3.10 或更高版本，并勾选 Add Python to PATH。' -ForegroundColor Red
    Read-Host '按回车退出'
    exit 1
}

if (-not (Test-Path $Server)) {
    Write-Host "[错误] 没有找到应用服务器：$Server" -ForegroundColor Red
    exit 1
}

if (Test-AppReady -TargetPort $AppPort) {
    Write-Host "[就绪] 月窗已经运行：http://127.0.0.1:$AppPort/" -ForegroundColor Green
    if (-not $NoBrowser) { Start-Process "http://127.0.0.1:$AppPort/" }
    exit 0
}
if (Test-TcpPort -TargetPort $AppPort) {
    Write-Host "[错误] 端口 $AppPort 已被其他程序占用，不是 Sydney 月窗。" -ForegroundColor Red
    Write-Host '请关闭占用程序，或使用 -AppPort 指定其他端口。' -ForegroundColor Yellow
    exit 1
}

if (-not (Test-ModelReady -TargetPort $ModelPort)) {
    if (Test-TcpPort -TargetPort $ModelPort) {
        Write-Host "[错误] 端口 $ModelPort 已被其他程序占用，但没有响应 KoboldCpp 模型接口。" -ForegroundColor Red
        Write-Host '请关闭占用程序，或使用 -ModelPort 指定其他端口。' -ForegroundColor Yellow
        exit 1
    }
    Write-Host "正在后台启动本地模型（$Mode 档）……" -ForegroundColor Yellow
    $quotedModelLauncher = '"{0}"' -f $ModelLauncher
    $modelArguments = @(
        '-NoProfile', '-ExecutionPolicy', 'Bypass', '-File', $quotedModelLauncher,
        '-Mode', $Mode, '-Port', $ModelPort, '-NoBrowser', '-NonInteractive'
    )
    Start-Process powershell.exe -ArgumentList $modelArguments -WindowStyle Hidden | Out-Null

    $deadline = (Get-Date).AddMinutes(4)
    while ((Get-Date) -lt $deadline -and -not (Test-ModelReady -TargetPort $ModelPort)) {
        Start-Sleep -Seconds 2
        Write-Host -NoNewline '.'
    }
    Write-Host ''
    if (-not (Test-ModelReady -TargetPort $ModelPort)) {
        Write-Host '[错误] 等待模型超过 4 分钟。请运行 status_sydney.bat 查看状态。' -ForegroundColor Red
        Read-Host '按回车退出'
        exit 1
    }
}

Write-Host "[就绪] 模型服务：http://127.0.0.1:$ModelPort" -ForegroundColor Green
Write-Host "正在打开月窗：http://127.0.0.1:$AppPort/" -ForegroundColor Cyan

$arguments = @(
    $Server,
    '--host', '127.0.0.1',
    '--port', $AppPort,
    '--model-url', "http://localhost:$ModelPort"
)
if ($NoBrowser) { $arguments += '--no-browser' }
$pythonArguments = @($Python.Prefix) + $arguments
& $Python.Exe @pythonArguments
exit $LASTEXITCODE
