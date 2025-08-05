@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    FILM CREW AI - AUTOMATED SCRIPT PROCESSING
echo ======================================================
echo.

:: Check for scripts
set SCRIPT_COUNT=0
for %%f in (scripts\*.txt) do set /a SCRIPT_COUNT+=1

if %SCRIPT_COUNT%==0 (
    echo ERROR: No scripts found in scripts\ folder
    pause
    exit /b 1
)

echo Found %SCRIPT_COUNT% script(s) to process.
echo.

:: Start Claude Flow
echo [1/4] Starting Claude Flow system...
start /min cmd /c "claude-flow start --ui --port 3000 --enable-swarm >logs\claude-flow.log 2>&1"
timeout /t 5 /nobreak >nul

:: Initialize swarm
echo [2/4] Initializing Film Crew Swarm...
call claude-flow swarm init --queen movie-director --workers "script-breakdown,character-analysis,background-designer,camera-director,lighting-designer,music-director,sound-designer,prompt-combiner" --strategy film-production --parallel-limit 4

:: Create timestamp
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
for /f "tokens=1-2 delims=/: " %%a in ('time /t') do (set mytime=%%a-%%b)
set TIMESTAMP=%mydate%_%mytime: =%

:: Process each script
echo [3/4] Processing scripts...
set PROCESSED=0
for %%f in (scripts\*.txt) do (
    set /a PROCESSED+=1
    echo Processing !PROCESSED! of %SCRIPT_COUNT%: %%~nf
    
    :: Create output directory
    set OUTPUT_DIR=output\%%~nf_%TIMESTAMP%
    mkdir "!OUTPUT_DIR!" 2>nul
    
    :: Auto restore point
    call claude-flow /create-restore-point "auto_%%~nf" "Processing %%~nf"
    
    :: Execute swarm workflow
    call claude-flow /film-swarm "%%f"
    
    :: Export outputs
    move output\veo3_prompts.json "!OUTPUT_DIR!\" >nul
    move output\music_cues.json "!OUTPUT_DIR!\" >nul
    move output\sound_design.json "!OUTPUT_DIR!\" >nul
    move output\continuity.json "!OUTPUT_DIR!\" >nul
    
    echo Complete! Output: !OUTPUT_DIR!
    echo.
)

echo [4/4] All scripts processed!
pause