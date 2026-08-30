@echo off
setlocal EnableExtensions
set "RUNTIME=%USERPROFILE%\Tools\slide-master-picker-runtime"
set "APP=%RUNTIME%\apps\slide-master-picker"
set "LOG_DIR=%LOCALAPPDATA%\OpenAI\SlideMasterTunnel\logs"

if not exist "%LOG_DIR%" mkdir "%LOG_DIR%"
if not exist "%APP%\package.json" (
  echo Picker app not found: %APP%
  exit /b 3
)
where npm >nul 2>&1 || (
  echo npm is not installed or not on PATH.
  exit /b 4
)
cd /d "%APP%"
set "PICKER_SOURCE=github"
npm start >> "%LOG_DIR%\picker.log" 2>&1
