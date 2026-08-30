@echo off
setlocal EnableExtensions
for %%I in ("%~dp0..\..") do set "REPO=%%~fI"
set "PURPOSE=%*"
if not defined PURPOSE set /p "PURPOSE=PPT purpose: "
if not defined PURPOSE exit /b 2
set "PYTHON=python"
where py >nul 2>nul && set "PYTHON=py -3"
set "OUT=%USERPROFILE%\Desktop\SlideMasterPicker_Fallback.html"
%PYTHON% "%REPO%\.claude\skills\ppt-master\scripts\template_gallery_inline_html.py" --source github --purpose %PURPOSE% --lang ko --recommendation-limit 8 --page-size 8 --output "%OUT%"
if errorlevel 1 (
  echo Failed to build Slide Master fallback picker.
  exit /b 1
)
echo READY: %OUT%
start "" "%OUT%"
exit /b 0
