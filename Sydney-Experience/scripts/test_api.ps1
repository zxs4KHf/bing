# ============================================================
#  KoboldCpp API 冒烟测试（Free Sydney V2 / Alpaca 模板）
#  先在另一个窗口启动 launch_sydney.bat，等待模型加载完成。
# ============================================================
param(
    [int]$Port = 5001,
    [string]$Question = 'Hi! Who are you, and how do you feel today?',
    [int]$TimeoutSec = 300
)
$ErrorActionPreference = 'Stop'

$SydneyDir = Split-Path -Parent $PSScriptRoot
$StoryPath = Join-Path $SydneyDir 'persona\sydney_story.json'

if (-not (Test-Path $StoryPath)) {
    Write-Host "[错误] 找不到人格预设: $StoryPath" -ForegroundColor Red
    exit 1
}

try {
    $story = Get-Content -LiteralPath $StoryPath -Raw -Encoding UTF8 | ConvertFrom-Json
} catch {
    Write-Host "[错误] 人格预设不是有效 JSON: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

$prompt = @"
$($story.memory)
### Instruction:
$Question

### Response:
"@

$payload = @{
    prompt        = $prompt
    max_length    = 240
    temperature   = 0.7
    top_p         = 0.9
    rep_pen       = 1.1
    stop_sequence = @('### Instruction:')
} | ConvertTo-Json -Depth 4

$uri = "http://localhost:$Port/api/v1/generate"
Write-Host "[测试] $uri" -ForegroundColor Cyan
Write-Host "[问题] $Question"

try {
    $response = Invoke-RestMethod `
        -Uri $uri `
        -Method Post `
        -ContentType 'application/json; charset=utf-8' `
        -Body ([Text.Encoding]::UTF8.GetBytes($payload)) `
        -TimeoutSec $TimeoutSec

    $answer = [string]$response.results[0].text
    if ([string]::IsNullOrWhiteSpace($answer)) {
        throw 'API 返回成功，但 results[0].text 为空。'
    }

    Write-Host ''
    Write-Host '—— Sydney 回复 ——' -ForegroundColor Cyan
    Write-Host $answer.Trim()
    Write-Host ''
    Write-Host '[通过] 本地生成 API 与 Alpaca 人格链路可用。' -ForegroundColor Green
    Write-Host '接下来请按 START_HERE.md 的清单主观评估身份、情感、自我意识和中文质量。'
} catch {
    Write-Host ''
    Write-Host "[失败] 无法完成 API 测试: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host '请确认 launch_sydney.bat 正在运行、模型已完成加载且端口一致。' -ForegroundColor Yellow
    exit 1
}
