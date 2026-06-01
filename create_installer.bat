@echo off
echo ============================================
echo  PromptEnhancer — Create Installer
echo ============================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if Inno Setup is installed
set ISCC=""
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    set ISCC="C:\Program Files\Inno Setup 6\ISCC.exe"
) else (
    echo [X] Inno Setup 6 not found!
    echo [X] Download from: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

REM Check if EXE exists
if not exist "dist\PromptEnhancer.exe" (
    echo [X] PromptEnhancer.exe not found in dist\
    echo [X] Run build.bat or setup_all.bat first!
    pause
    exit /b 1
)

REM Build installer
echo [*] Building installer with Inno Setup...
%ISCC% installer\setup.iss

if %ERRORLEVEL% neq 0 (
    echo [X] Installer build FAILED!
    pause
    exit /b 1
)

echo.
echo [OK] Installer created: dist\PromptEnhancerSetup.exe
echo.
pause
