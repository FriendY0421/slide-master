@echo off
setlocal EnableExtensions
title Slide Master Picker Runtime Installer

set "REPO=https://github.com/FriendY0421/slide-master.git"
set "RUNTIME=%USERPROFILE%\Tools\slide-master-picker-runtime"
set "APP=%RUNTIME%\apps\slide-master-picker"
set "FALLBACK_BRANCH=feat/apps-sdk-template-picker-20260827"

where git >nul 2>&1 || goto missing_git
where npm >nul 2>&1 || goto missing_npm
where python >nul 2>&1 || goto missing_python

if exist "%RUNTIME%\.git" (
  echo [1/5] Updating existing runtime...
  git -C "%RUNTIME%" fetch --all --prune || goto git_error
  git -C "%RUNTIME%" checkout main || goto git_error
  git -C "%RUNTIME%" pull --ff-only origin main || goto git_error
) else (
  echo [1/5] Cloning slide-master...
  if exist "%RUNTIME%" rmdir /s /q "%RUNTIME%"
  git clone "%REPO%" "%RUNTIME%" || goto git_error
)

if not exist "%APP%\package.json" (
  echo [2/5] Picker app not on main yet. Using fallback branch...
  git -C "%RUNTIME%" fetch origin "%FALLBACK_BRANCH%" || goto git_error
  git -C "%RUNTIME%" checkout -B "%FALLBACK_BRANCH%" "origin/%FALLBACK_BRANCH%" || goto git_error
) else (
  echo [2/5] Picker app found on main.
)

if not exist "%APP%\package.json" goto missing_app

echo [3/5] Installing locked Node dependencies...
cd /d "%APP%"
npm ci || goto npm_error

echo [4/5] Running local checks...
npm run check || goto npm_error
npm run build || goto npm_error

echo [5/5] Creating Desktop launcher...
copy /Y "%RUNTIME%\ops\windows\Start_SlideMasterPicker.bat" "%USERPROFILE%\Desktop\Start_SlideMasterPicker.bat" >nul

echo.
echo Runtime install complete.
echo Next: configure tunnel-client and runtime_key.txt using docs\ops\SLIDE_MASTER_PICKER_WINDOWS_RECOVERY.md
pause
exit /b 0

:missing_git
echo ERROR: Git for Windows is required.
goto fail
:missing_npm
echo ERROR: Node.js/npm is required.
goto fail
:missing_python
echo ERROR: Python is required and must be on PATH.
goto fail
:missing_app
echo ERROR: apps\slide-master-picker was not found on main or fallback branch.
goto fail
:git_error
echo ERROR: Git clone/update failed.
goto fail
:npm_error
echo ERROR: npm install/check/build failed.
goto fail
:fail
pause
exit /b 1
