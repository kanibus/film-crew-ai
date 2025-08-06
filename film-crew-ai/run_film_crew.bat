@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: ============================================================
:: Film Crew AI - Main Runner (v8.0)
:: Improved with error handling and validation
:: ============================================================

cls
color 0A
echo ============================================================
echo     FILM CREW AI v8.0 - Screenplay to Veo3 Processor
echo ============================================================
echo.

:: Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo [ERROR] Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8 or later from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

:: Install dependencies if needed
if not exist ".deps_installed" (
    echo Installing required packages...
    python -m pip install --upgrade pip >nul 2>&1
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [WARNING] Some packages may not have installed correctly
        echo Attempting to install individually...
        pip install PyPDF2 python-docx chardet
    )
    echo. > .deps_installed
    echo Dependencies installed successfully!
    echo.
)

:: Check for arguments
if "%~1"=="" (
    :: No arguments - interactive mode
    echo Available options:
    echo   1. Process a single screenplay
    echo   2. Batch process all scripts
    echo   3. Run tests
    echo   4. Show help
    echo.
    set /p CHOICE="Select option (1-4): "
    
    if "!CHOICE!"=="1" goto :single
    if "!CHOICE!"=="2" goto :batch
    if "!CHOICE!"=="3" goto :test
    if "!CHOICE!"=="4" goto :help
    
    echo Invalid choice!
    pause
    exit /b 1
)

:: Arguments provided - process directly
python film_crew_ai_main.py %*
goto :end

:single
echo.
echo Enter the path to your screenplay:
set /p SCRIPT="Script path: "
if "!SCRIPT!"=="" (
    echo No script specified!
    pause
    exit /b 1
)
python film_crew_ai_main.py "!SCRIPT!"
goto :end

:batch
echo.
echo Processing all scripts in the scripts folder...
python film_crew_ai_main.py --batch
goto :end

:test
echo.
echo Running unit tests...
python test_film_crew_ai.py
goto :end

:help
echo.
python film_crew_ai_main.py --help
goto :end

:end
echo.
echo ============================================================
echo Process complete!
echo ============================================================
echo.
pause