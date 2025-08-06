@echo off
echo ============================================================
echo          FILM CREW AI - Production System v3.0
echo ============================================================
echo.
echo This system transforms screenplays into comprehensive
echo prompts for Google Veo 3 video generation.
echo.
echo Options:
echo   1. Process all scripts in scripts/ folder
echo   2. Process specific script
echo   3. Exit
echo.
set /p choice="Select option (1-3): "

if "%choice%"=="1" (
    echo.
    echo Processing all scripts...
    python film_crew_ai.py --all
    pause
) else if "%choice%"=="2" (
    echo.
    set /p scriptname="Enter script filename (from scripts/ folder): "
    echo.
    echo Processing %scriptname%...
    python film_crew_ai.py --script "scripts/%scriptname%"
    pause
) else (
    echo Exiting...
    timeout /t 2 >nul
)