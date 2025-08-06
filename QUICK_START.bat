@echo off
echo ============================================================
echo           FILM CREW AI - QUICK START SETUP
echo ============================================================
echo.
echo This will set up Film Crew AI on your computer.
echo.
pause

echo.
echo Step 1: Checking Python installation...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
echo Python is installed!

echo.
echo Step 2: Installing required libraries...
pip install PyPDF2 python-docx chardet
if %errorlevel% neq 0 (
    echo.
    echo ERROR: Failed to install libraries.
    echo Try running: python -m pip install PyPDF2 python-docx chardet
    pause
    exit /b 1
)

echo.
echo Step 3: Creating scripts folder...
if not exist "film-crew-ai\scripts" (
    mkdir "film-crew-ai\scripts"
    echo Scripts folder created!
) else (
    echo Scripts folder already exists!
)

echo.
echo Step 4: Testing with example script...
cd film-crew-ai
if exist "scripts\complex_script.txt" (
    echo.
    echo Running example script...
    python film_crew_ai_main.py scripts\complex_script.txt
    echo.
    echo ============================================================
    echo                    SETUP COMPLETE!
    echo ============================================================
    echo.
    echo Your video prompts are in:
    echo   film-crew-ai\output\[newest folder]\Veo3_Natural_Prompts\
    echo.
    echo To process your own script:
    echo   1. Put your script in: film-crew-ai\scripts\
    echo   2. Run: python film_crew_ai_main.py scripts\your_script.txt
    echo.
) else (
    echo.
    echo Example script not found. Setup complete!
    echo.
    echo To use Film Crew AI:
    echo   1. Put your script in: film-crew-ai\scripts\
    echo   2. Run: python film_crew_ai_main.py scripts\your_script.txt
    echo.
)

pause