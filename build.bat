@echo off
echo ============================================
echo  PromptEnhancer — Build EXE
echo ============================================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo [!] Virtual environment not found. Run setup_all.bat first.
    pause
    exit /b 1
)

REM Generate icon if it doesn't exist
if not exist "assets\icon.ico" (
    echo [*] Generating app icon...
    venv\Scripts\python.exe -c "from src.generate_icon import create_icon; create_icon('assets/icon.ico')"
)

REM Build with PyInstaller
echo [*] Building EXE with PyInstaller...
venv\Scripts\pyinstaller.exe ^
    --onefile ^
    --noconsole ^
    --name=PromptEnhancer ^
    --icon=assets\icon.ico ^
    --add-data="assets;assets" ^
    --hidden-import=pystray._win32 ^
    --hidden-import=win32clipboard ^
    --hidden-import=win32con ^
    --hidden-import=win32api ^
    --hidden-import=pkg_resources.extern ^
    --clean ^
    --noconfirm ^
    run.py

if %ERRORLEVEL% neq 0 (
    echo [X] Build FAILED!
    pause
    exit /b 1
)

echo.
echo [OK] Build successful!
echo [OK] Output: dist\PromptEnhancer.exe
echo.
pause
