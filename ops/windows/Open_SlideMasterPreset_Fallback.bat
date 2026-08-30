@echo off
setlocal
set "ROOT=%~dp0..\.."
set "SCRIPT=%ROOT%\.claude\skills\ppt-master\scripts\production_preset_picker.py"
set "OUT=%USERPROFILE%\Desktop\SlideMasterPreset_Fallback.html"
set "PURPOSE=%*"
if "%PURPOSE%"=="" set "PURPOSE=New presentation"
where python >nul 2>nul
if %errorlevel%==0 (
  python "%SCRIPT%" --purpose "%PURPOSE%" --output "%OUT%"
) else (
  py -3 "%SCRIPT%" --purpose "%PURPOSE%" --output "%OUT%"
)
if errorlevel 1 exit /b 1
start "" "%OUT%"
echo READY: %OUT%
endlocal
