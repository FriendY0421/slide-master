@echo off
setlocal EnableExtensions
title Slide Master Template Picker Launcher

set "RUNTIME=%USERPROFILE%\Tools\slide-master-picker-runtime"
set "PICKER_HELPER=%RUNTIME%\ops\windows\Run_Picker_Server.cmd"
set "TUNNEL_HELPER=%RUNTIME%\ops\windows\Run_Secure_Tunnel.cmd"
set "LOG_DIR=%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%PICKER_HELPER%" goto missing_picker
if not exist "%TUNNEL_HELPER%" goto missing_tunnel

echo [1/4] Checking Picker MCP...
netstat -ano | findstr /R /C:":3000 .*LISTENING" >nul
if errorlevel 1 (
  echo       Starting Picker MCP...
  start "" /min "%PICKER_HELPER%"
  ping 127.0.0.1 -n 3 >nul
) else (
  echo       Picker MCP is already running.
)

echo [2/4] Checking Secure Tunnel...
netstat -ano | findstr /R /C:":8080 .*LISTENING" >nul
if errorlevel 1 (
  echo       Starting Secure Tunnel...
  start "" /min "%TUNNEL_HELPER%"
) else (
  echo       Secure Tunnel is already running.
)

echo [3/4] Waiting for READY...
set /a TRY=0
:wait_ready
set /a TRY+=1
curl.exe -fsS --max-time 2 http://127.0.0.1:8080/readyz 2>nul | findstr /I /C:"ready" >nul
if not errorlevel 1 goto ready
if %TRY% GEQ 15 goto not_ready
ping 127.0.0.1 -n 2 >nul
goto wait_ready

:ready
echo [4/4] READY - Slide Master Template Picker is available.
echo       Use @Slide Master Template Picker in ChatGPT.
ping 127.0.0.1 -n 4 >nul
exit /b 0

:not_ready
echo ERROR: Secure Tunnel did not become READY within 15 seconds.
echo Check log: %LOG_DIR%\tunnel.log
pause
exit /b 2

:missing_picker
echo ERROR: Picker helper is missing.
echo %PICKER_HELPER%
pause
exit /b 3

:missing_tunnel
echo ERROR: Tunnel helper is missing.
echo %TUNNEL_HELPER%
pause
exit /b 4
