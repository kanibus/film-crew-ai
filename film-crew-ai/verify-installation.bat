@echo off
echo ======================================================
echo    FILM CREW AI - INSTALLATION VERIFICATION
echo ======================================================
echo.

set ERRORS=0

echo Checking prerequisites...
echo.

:: Check Node.js
echo [1/6] Checking Node.js...
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo    ❌ Node.js NOT installed
    echo       Install from: https://nodejs.org/
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('node --version') do echo    ✅ Node.js installed: %%i
)

:: Check Claude CLI
echo [2/6] Checking Claude CLI...
where claude >nul 2>nul
if %errorlevel% neq 0 (
    echo    ❌ Claude CLI NOT installed
    echo       Install with: npm install -g @anthropic-ai/claude-code
    set /a ERRORS+=1
) else (
    echo    ✅ Claude CLI installed
)

:: Check Claude Flow
echo [3/6] Checking Claude Flow...
where claude-flow >nul 2>nul
if %errorlevel% neq 0 (
    echo    ❌ Claude Flow NOT installed
    echo       Install with: npm install -g claude-flow@latest
    set /a ERRORS+=1
) else (
    for /f "tokens=*" %%i in ('claude-flow --version 2^>^&1') do (
        echo    ✅ Claude Flow installed
        goto :flow_done
    )
)
:flow_done

:: Check Film Crew agents
echo [4/6] Checking Film Crew agents...
set AGENT_COUNT=0
for %%f in (.claude\agents\*.md) do set /a AGENT_COUNT+=1
if %AGENT_COUNT%==0 (
    echo    ❌ No agents installed in .claude\agents\
    echo       Run: install-film-crew.bat
    set /a ERRORS+=1
) else (
    echo    ✅ %AGENT_COUNT% agents installed
)

:: Check commands
echo [5/6] Checking workflow commands...
set CMD_COUNT=0
for %%f in (.claude\commands\*.md) do set /a CMD_COUNT+=1
if %CMD_COUNT%==0 (
    echo    ⚠️  No commands installed in .claude\commands\
    echo       Run: install-film-crew.bat
) else (
    echo    ✅ %CMD_COUNT% commands installed
)

:: Check test script
echo [6/6] Checking test script...
if not exist "scripts\test-scene.txt" (
    echo    ⚠️  Test script not found
    echo       Creating test script now...
    if not exist "scripts" mkdir "scripts"
    (
        echo FADE IN:
        echo.
        echo INT. COFFEE SHOP - DAY
        echo.
        echo SARAH enters, scanning the crowded room. She spots JOHN at a corner table.
        echo.
        echo FADE OUT.
    ) > "scripts\test-scene.txt"
    echo       Test script created!
) else (
    echo    ✅ Test script exists
)

echo.
echo ======================================================
if %ERRORS%==0 (
    echo ✅ ALL CHECKS PASSED! System ready to use.
    echo.
    echo Next steps:
    echo 1. Run: process-scripts.bat to process scripts
    echo 2. Run: edit-mode.bat for interactive editing
    echo 3. Visit: http://localhost:3000/console for UI
) else (
    echo ❌ %ERRORS% ISSUES FOUND. Please fix before proceeding.
    echo.
    echo Run install-film-crew.bat to fix most issues.
)
echo ======================================================
echo.
pause