param(
    [int]$BackendPort = 8001,
    [int]$ProxyPort = 8000
)

# Simple Windows runner: starts backend (uvicorn) and the aiohttp proxy and logs output.
# Calculate directories reliably: $PSScriptRoot is the script folder; repo root is its parent.
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $ScriptDir
Set-Location $RepoRoot

$logsDir = Join-Path $RepoRoot 'logs'
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

$python = 'python'

Write-Output "Using python: $python"
Write-Output "Starting backend on 127.0.0.1:$BackendPort (logs -> $logsDir\backend.log)"

# Start backend using argument array for Start-Process
$backendArgs = @('-m','uvicorn','simple_backend:app','--host','127.0.0.1','--port',$BackendPort)
Start-Process -FilePath $python -ArgumentList $backendArgs -RedirectStandardOutput (Join-Path $logsDir 'backend.log') -RedirectStandardError (Join-Path $logsDir 'backend.err') -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Output "Starting proxy on 127.0.0.1:$ProxyPort (logs -> $logsDir\proxy.log)"

# Locate proxy script next to this PS1 file
$proxyScript = Join-Path $ScriptDir 'server_proxy_switch.py'
if (-Not (Test-Path $proxyScript)) {
    Write-Error "Proxy script not found at $proxyScript"
    exit 1
}

$proxyArgs = @($proxyScript, $ProxyPort.ToString(), '127.0.0.1', $BackendPort.ToString())
Start-Process -FilePath $python -ArgumentList $proxyArgs -RedirectStandardOutput (Join-Path $logsDir 'proxy.log') -RedirectStandardError (Join-Path $logsDir 'proxy.err') -WindowStyle Hidden

Write-Output "Started backend and proxy. Tail logs from $logsDir for details."
param(
    [int]$BackendPort = 8001,
    [int]$ProxyPort = 8000
)

# Simple Windows runner: starts backend (uvicorn) and proxy (server_proxy_switch.py) and logs output.
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $RepoRoot

$logsDir = Join-Path $RepoRoot 'logs'
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

$python = 'python'

Write-Output "Using python: $python"
Write-Output "Starting backend on 127.0.0.1:$BackendPort (logs -> $logsDir\backend.log)"

$backendArgs = "-m uvicorn simple_backend:app --host 127.0.0.1 --port $BackendPort"
Start-Process -FilePath $python -ArgumentList $backendArgs -RedirectStandardOutput (Join-Path $logsDir 'backend.log') -RedirectStandardError (Join-Path $logsDir 'backend.err') -WindowStyle Hidden

Start-Sleep -Seconds 2

Write-Output "Starting proxy on 127.0.0.1:$ProxyPort (logs -> $logsDir\proxy.log)"

$proxyScript = Join-Path $RepoRoot 'scripts' 'server_proxy_switch.py'
if (-Not (Test-Path $proxyScript)) {
    Write-Error "Proxy script not found at $proxyScript"
    exit 1
}

$proxyArgs = "$ProxyPort 127.0.0.1 $BackendPort"
Start-Process -FilePath $python -ArgumentList @($proxyScript, $ProxyPort, '127.0.0.1', $BackendPort) -RedirectStandardOutput (Join-Path $logsDir 'proxy.log') -RedirectStandardError (Join-Path $logsDir 'proxy.err') -WindowStyle Hidden

Write-Output "Started backend and proxy. Tail logs from $logsDir for details."
