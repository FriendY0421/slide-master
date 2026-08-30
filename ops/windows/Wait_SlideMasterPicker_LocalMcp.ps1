param(
    [string]$Runtime = "$env:USERPROFILE\Tools\slide-master-picker-runtime",
    [string]$LogDir = "$env:LOCALAPPDATA\OpenAI\SlideMasterTunnel\logs",
    [int]$TimeoutSeconds = 60
)
$ErrorActionPreference = 'Stop'
$App = Join-Path $Runtime 'apps\slide-master-picker'
$Node = 'C:\Program Files\nodejs\node.exe'
$Probe = Join-Path $App 'scripts\mcp-ready.mjs'
$Out = Join-Path $LogDir 'pre_tunnel_ready.stdout.log'
$Err = Join-Path $LogDir 'pre_tunnel_ready.stderr.log'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null

if (-not (Test-Path $Probe)) {
    Write-Host '[ERROR] Local MCP readiness probe is missing.' -ForegroundColor Red
    exit 2
}
if (-not (Test-Path $Node)) {
    Write-Host '[ERROR] node.exe is missing.' -ForegroundColor Red
    exit 3
}

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$attempt = 0
Write-Host '[pre-tunnel] Waiting for Picker MCP protocol readiness...'
while ((Get-Date) -lt $deadline) {
    $attempt++
    Remove-Item $Out,$Err -Force -ErrorAction SilentlyContinue
    $proc = Start-Process -FilePath $Node -ArgumentList @('scripts/mcp-ready.mjs') -WorkingDirectory $App -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput $Out -RedirectStandardError $Err
    $stdout = if (Test-Path $Out) { Get-Content $Out -Raw } else { '' }
    if ($proc.ExitCode -eq 0 -and $stdout.Contains('MCP_READY PASS')) {
        Write-Host ("LOCAL_MCP_READY=PASS attempt={0}" -f $attempt)
        exit 0
    }
    Start-Sleep -Seconds 1
}

Write-Host ("[ERROR] Picker MCP did not become protocol-ready within {0} seconds." -f $TimeoutSeconds) -ForegroundColor Red
if (Test-Path $Err) { Get-Content $Err -Tail 12 }
Write-Host ("Readiness stderr: {0}" -f $Err)
exit 1
