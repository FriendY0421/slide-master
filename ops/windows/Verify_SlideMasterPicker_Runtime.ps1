param(
    [string]$Runtime = "$env:USERPROFILE\Tools\slide-master-picker-runtime",
    [string]$LogDir = "$env:LOCALAPPDATA\OpenAI\SlideMasterTunnel\logs",
    [switch]$TunnelStarted,
    [int]$SmokeAttempts = 3,
    [int]$TimeoutSeconds = 90,
    [int]$StableSeconds = 10
)
$ErrorActionPreference = 'Stop'
$App = Join-Path $Runtime 'apps\slide-master-picker'
$Node = 'C:\Program Files\nodejs\node.exe'
$StatusFile = Join-Path $LogDir 'runtime.verify.status.json'
$PassMarker = Join-Path $LogDir 'runtime.verify.PASS'
$FailMarker = Join-Path $LogDir 'runtime.verify.FAIL'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
Remove-Item $PassMarker,$FailMarker -Force -ErrorAction SilentlyContinue

function Write-Status([bool]$Ok,[string]$Stage,[string]$Message,[int]$Attempt=0) {
    [ordered]@{timestamp=(Get-Date).ToString('o');ok=$Ok;stage=$Stage;message=$Message;attempt=$Attempt} |
        ConvertTo-Json | Set-Content -Path $StatusFile -Encoding utf8
}
function Fail([string]$Stage,[string]$Message,[int]$Attempt=0) {
    Set-Content -Path $FailMarker -Value ((Get-Date).ToString('o')+' '+$Stage+' '+$Message) -Encoding utf8
    Write-Status $false $Stage $Message $Attempt
    Write-Host ('ERROR: '+$Message) -ForegroundColor Red
    exit 1
}
function Test-TcpPort([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $async = $client.BeginConnect('127.0.0.1',$Port,$null,$null)
        if (-not $async.AsyncWaitHandle.WaitOne(1500)) { return $false }
        $client.EndConnect($async)
        return $true
    } catch { return $false }
    finally { $client.Close() }
}
function Get-EndpointText([string]$Url) {
    try { return (Invoke-WebRequest -UseBasicParsing -TimeoutSec 3 -Uri $Url).Content.Trim() }
    catch { return $null }
}
function Test-LocalRuntime {
    if (-not (Test-TcpPort 3000)) { return $false }
    if (-not (Test-TcpPort 8080)) { return $false }
    $health=Get-EndpointText 'http://127.0.0.1:8080/healthz'
    $ready=Get-EndpointText 'http://127.0.0.1:8080/readyz'
    return ($health -eq 'live' -and $ready -eq 'ready')
}
Write-Status $false 'starting' 'Runtime verification started.'
if (-not (Test-Path (Join-Path $App 'package.json'))) { Fail 'precheck' "Picker app is missing: $App" }
if (-not (Test-Path $Node)) { Fail 'precheck' "node.exe is missing: $Node" }
if ($TimeoutSeconds -lt 1) { Fail 'precheck' 'TimeoutSeconds must be at least 1.' }
if ($StableSeconds -lt 1) { Fail 'precheck' 'StableSeconds must be at least 1.' }
Write-Host '[verify 1/4] Waiting for continuously stable local runtime...'
$deadline=(Get-Date).AddSeconds($TimeoutSeconds)
$stableSince=$null
$stable=$false
while ((Get-Date) -lt $deadline) {
    if (Test-LocalRuntime) {
        if ($null -eq $stableSince) { $stableSince=Get-Date }
        $elapsed=((Get-Date)-$stableSince).TotalSeconds
        Write-Status $false 'stabilizing' ("Stable for {0:N1}/{1}s" -f $elapsed,$StableSeconds)
        if ($elapsed -ge $StableSeconds) { $stable=$true; break }
    } else {
        $stableSince=$null
        Write-Status $false 'warming' 'Waiting for TCP 3000/8080 and tunnel health=live ready=ready.'
    }
    Start-Sleep -Seconds 1
}
if (-not $stable) { Fail 'runtime_stability' "Runtime did not stay healthy for $StableSeconds seconds within $TimeoutSeconds seconds." }

Write-Host '[verify 2/4] Running full MCP protocol smoke...'
$smokePassed=$false
$lastSmoke=''
for($try=1;$try -le $SmokeAttempts;$try++) {
    $out=Join-Path $LogDir ("smoke.$try.stdout.log")
    $err=Join-Path $LogDir ("smoke.$try.stderr.log")
    Remove-Item $out,$err -Force -ErrorAction SilentlyContinue
    Write-Status $false 'smoke' ("Attempt $try/$SmokeAttempts") $try
    $proc=Start-Process -FilePath $Node -ArgumentList @('scripts/mcp-smoke.mjs') -WorkingDirectory $App -Wait -PassThru -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err
    $stdout=if(Test-Path $out){Get-Content $out -Raw}else{''}
    $stderr=if(Test-Path $err){Get-Content $err -Raw}else{''}
    $lastSmoke=$stdout+[Environment]::NewLine+$stderr
    $lastSmoke | Set-Content -Path (Join-Path $LogDir 'smoke.log') -Encoding utf8
    $markersOk=$true
    foreach($marker in @('TOOLS ','PICKER ','RESOURCE_META ','UI ','VALIDATE ')) {
        if(-not $lastSmoke.Contains($marker)){ $markersOk=$false; break }
    }
    if($proc.ExitCode -eq 0 -and $markersOk){ $smokePassed=$true; break }
    if($try -lt $SmokeAttempts){ Start-Sleep -Seconds 3 }
}
if(-not $smokePassed){ Fail 'smoke' 'Full MCP smoke failed after all retry attempts.' $SmokeAttempts }

Write-Host '[verify 3/4] Confirming tunnel stayed ready after MCP smoke...'
if (-not (Test-LocalRuntime)) { Fail 'post_smoke' 'Runtime became unhealthy after MCP smoke.' $try }

Write-Host '[verify 4/4] Runtime identity and final status...'
try { $branch=(& git -C $Runtime branch --show-current 2>$null).Trim(); $head=(& git -C $Runtime rev-parse --short=12 HEAD 2>$null).Trim() }
catch { $branch='unknown'; $head='unknown' }
Remove-Item $FailMarker -Force -ErrorAction SilentlyContinue
Set-Content -Path $PassMarker -Value ((Get-Date).ToString('o')+' READY '+$branch+' '+$head) -Encoding utf8
Write-Status $true 'ready' ("All checks passed. branch=$branch head=$head") $try
Write-Host "RUNTIME_BRANCH=$branch"
Write-Host "RUNTIME_HEAD=$head"
Write-Host 'MCP_SMOKE=PASS'
Write-Host 'TUNNEL_HEALTH=live'
Write-Host 'TUNNEL_READY=ready'
Write-Host 'REMOTE_READY=PASS'
exit 0
