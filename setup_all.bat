@echo off
echo ============================================
echo  PromptEnhancer — Full Build Pipeline
echo ============================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Step 1: Create virtual environment
echo [1/4] Setting up virtual environment...
if not exist "venv\Scripts\python.exe" (
    if exist "C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe" (
        echo [*] Found Python at C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe
        "C:\Users\DELL\AppData\Local\Programs\Python\Python312\python.exe" -m venv venv
    ) else (
        py -3 -m venv venv
    )
    if %ERRORLEVEL% neq 0 (
        echo [X] Failed to create virtual environment!
        echo [X] Make sure Python 3.10+ is installed.
        echo [X] Download from: https://www.python.org/downloads/
        pause
        exit /b 1
    )
)

REM Step 2: Install dependencies
echo [2/4] Installing dependencies...
venv\Scripts\pip.exe install -r requirements.txt
if %ERRORLEVEL% neq 0 (
    echo [X] Failed to install dependencies!
    pause
    exit /b 1
)

REM Step 3: Generate icon
echo [3/4] Generating app icon...
if not exist "assets" mkdir assets
venv\Scripts\python.exe -c "from src.generate_icon import create_icon; create_icon('assets/icon.ico')"
if %ERRORLEVEL% neq 0 (
    echo [!] Icon generation failed (will use fallback).
)

REM Step 4: Build EXE
echo [4/4] Building EXE...
call build.bat

echo.
echo ============================================
echo  Build Complete!
echo ============================================
echo  EXE: dist\PromptEnhancer.exe
echo ============================================
echo.
pause
