@echo off
setlocal EnableExtensions EnableDelayedExpansion
title Slide Master Template Picker - Safe Launcher

set "RUNTIME=%USERPROFILE%\Tools\slide-master-picker-runtime"
set "PICKER_HELPER=%RUNTIME%\ops\windows\Run_Picker_Server.cmd"
set "TUNNEL_HELPER=%RUNTIME%\ops\windows\Run_Secure_Tunnel.cmd"
set "VERIFY=%RUNTIME%\ops\windows\Verify_SlideMasterPicker_Runtime.ps1"
set "LOG_DIR=%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%PICKER_HELPER%" goto missing_runtime
if not exist "%TUNNEL_HELPER%" goto missing_runtime
if not exist "%VERIFY%" goto missing_runtime

echo ============================================================
echo Slide Master Template Picker - Safe Startup
 echo Never terminates an existing process.
echo ============================================================
echo.
echo [1/4] Checking existing runtime without restarting anything...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%VERIFY%" -TimeoutSeconds 12 -StableSeconds 3 -SmokeAttempts 1
if not errorlevel 1 goto already_ready

echo.
echo Existing runtime is not fully healthy. Checking port ownership...
set "PORT_BUSY=0"
for %%P in (3000 8080) do (
    netstat -ano | findstr /R /C:":%%P .*LISTENING" >nul
    if not errorlevel 1 (
        echo [ACTION REQUIRED] Port %%P already has a listener.
        set "PORT_BUSY=1"
    )
)
if "!PORT_BUSY!"=="1" goto busy_runtime

echo [2/4] Ports are free. Starting Picker MCP...
start "Slide Master Picker Server" /min cmd /c ""%PICKER_HELPER%""

echo [3/4] Starting Secure Tunnel...
start "Slide Master Secure Tunnel" /min cmd /c ""%TUNNEL_HELPER%""

echo [4/4] Waiting for stable end-to-end readiness...
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%VERIFY%" -TunnelStarted -TimeoutSeconds 120 -StableSeconds 10 -SmokeAttempts 3
if errorlevel 1 goto not_ready

echo.
echo [READY] Picker + tunnel + MCP smoke all passed.
echo Use ChatGPT only after this READY message.
pause
exit /b 0

:already_ready
echo.
echo [READY] Existing Picker runtime is healthy.
echo Nothing was restarted or terminated.
pause
exit /b 0
:busy_runtime
echo.
echo [NOT READY] Existing listener detected while verification failed.
echo This launcher will NOT terminate or replace any process.
echo Finish other work and restart Windows when it is safe, then run this file again.
echo Verification log: %LOG_DIR%\runtime.verify.status.json
pause
exit /b 40

:not_ready
echo.
echo [NOT READY] Startup completed but end-to-end verification did not pass.
echo Do NOT repeatedly retry the ChatGPT app.
echo Verification log: %LOG_DIR%\runtime.verify.status.json
pause
exit /b 50

:missing_runtime
echo.
echo [ERROR] Required Slide Master runtime file is missing.
echo Runtime: %RUNTIME%
pause
exit /b 60
