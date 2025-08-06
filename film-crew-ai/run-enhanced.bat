@echo off
echo ============================================================
echo    FILM CREW AI - Enhanced Multi-Format System v4.0
echo ============================================================
echo.
echo Checking dependencies...

REM Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing required packages...
pip install -q PyPDF2 python-docx 2>nul

echo.
echo ============================================================
echo             Ready to Process Scripts
echo ============================================================
echo.
echo Supported formats: TXT, PDF, DOC, DOCX
echo.
echo Options:
echo   1. Process all scripts (all formats)
echo   2. Process specific script
echo   3. Validate existing outputs
echo   4. Test with sample script
echo   5. Exit
echo.
set /p choice="Select option (1-5): "

if "%choice%"=="1" (
    echo.
    echo Processing all scripts...
    python film_crew_ai_enhanced.py --all
    pause
) else if "%choice%"=="2" (
    echo.
    set /p scriptpath="Enter script path (or drag file here): "
    echo.
    echo Processing %scriptpath%...
    python film_crew_ai_enhanced.py --script "%scriptpath%"
    pause
) else if "%choice%"=="3" (
    echo.
    echo Validating outputs...
    python film_crew_ai_enhanced.py --validate
    pause
) else if "%choice%"=="4" (
    echo.
    echo Testing with sample script...
    python film_crew_ai_enhanced.py --script scripts/test_script.txt --validate
    pause
) else (
    echo Exiting...
    timeout /t 2 >nul
)