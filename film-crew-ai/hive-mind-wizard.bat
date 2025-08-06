@echo off
echo ============================================================
echo       FILM CREW AI - Hive Mind Configuration Wizard
echo ============================================================
echo.

REM Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js from https://nodejs.org/
    pause
    exit /b 1
)

REM Run the hive-mind initialization
node hive-mind-init.js

pause