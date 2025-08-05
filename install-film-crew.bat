@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    FILM CREW AI - AUTOMATED INSTALLATION SCRIPT
echo ======================================================
echo.

:: Check if Node.js is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed. Please install Node.js first.
    echo Download from: https://nodejs.org/
    pause
    exit /b 1
)

:: Check if Claude CLI is installed
where claude >nul 2>nul
if %errorlevel% neq 0 (
    echo NOTICE: Claude CLI not found. Will install it now for full swarm features.
    echo.
) else (
    echo Claude CLI already installed. Good!
    echo.
)

echo [1/9] Installing Claude CLI (required for swarm features)...
call npm install -g @anthropic-ai/claude-code
if %errorlevel% neq 0 (
    echo WARNING: Claude CLI installation failed. Some features may be limited.
    echo You can install it manually later with: npm install -g @anthropic-ai/claude-code
    echo.
)

echo.
echo [2/9] Installing Claude Flow globally...
call npm install -g claude-flow@latest

echo.
echo [3/9] Initializing Claude Flow with SPARC and permissions...
call npx claude-flow@latest init --sparc --dangerously-skip-permissions

echo.
echo [4/9] Creating project directory structure...
if not exist ".claude\agents" mkdir ".claude\agents"
if not exist ".claude\commands" mkdir ".claude\commands"
if not exist ".claude\memory" mkdir ".claude\memory"
if not exist ".claude\versions" mkdir ".claude\versions"
if not exist "scripts" mkdir "scripts"
if not exist "output\prompts" mkdir "output\prompts"
if not exist "output\music" mkdir "output\music"
if not exist "output\sound" mkdir "output\sound"
if not exist "output\continuity" mkdir "output\continuity"
if not exist "logs" mkdir "logs"

echo.
echo [5/9] Installing AI agents...
set AGENT_COUNT=0
if not exist "templates\agents\*.md" (
    echo    No agent templates found. Skipping...
) else (
    for %%f in (templates\agents\*.md) do (
        set /a AGENT_COUNT+=1
        echo    Installing agent: %%~nf
        copy "%%f" ".claude\agents\" >nul 2>&1
    )
    echo    Total agents installed: !AGENT_COUNT!
)

echo.
echo [6/9] Installing workflow commands...
if not exist "templates\commands\*.md" (
    echo    No command templates found. Skipping...
) else (
    for %%f in (templates\commands\*.md) do (
        echo    Installing command: %%~nf
        copy "%%f" ".claude\commands\" >nul 2>&1
    )
)

echo.
echo [7/9] Setting up swarm configuration...
call claude-flow --dangerously-skip-permissions swarm init --queen movie-director --workers 8 >nul 2>&1

echo.
echo [8/9] Creating test script...
(
echo FADE IN:
echo.
echo INT. COFFEE SHOP - DAY
echo.
echo SARAH enters, scanning the crowded room. She spots JOHN at a corner table.
echo.
echo FADE OUT.
) > "scripts\test-scene.txt"

echo.
echo [9/9] Installation complete!
echo.
pause