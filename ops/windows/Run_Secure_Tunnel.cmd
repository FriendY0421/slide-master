@echo off
setlocal EnableExtensions
set "TUNNEL_EXE=%USERPROFILE%\Tools\tunnel-client\v0.0.13\full\tunnel-client.exe"
set "LOG_DIR=%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%TUNNEL_EXE%" (
  echo tunnel-client not found: %TUNNEL_EXE%
  exit /b 4
)
"%TUNNEL_EXE%" run --profile slide-master-picker >> "%LOG_DIR%\tunnel.log" 2>&1
