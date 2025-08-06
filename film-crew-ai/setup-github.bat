@echo off
echo ======================================================
echo    GITHUB CLI SETUP FOR FILM CREW AI
echo ======================================================
echo.

:: Check if gh is available
where gh >nul 2>nul
if %errorlevel% neq 0 (
    :: Try the full path
    if exist "C:\Program Files\GitHub CLI\gh.exe" (
        set GH="C:\Program Files\GitHub CLI\gh.exe"
        echo Using GitHub CLI from Program Files
    ) else (
        echo ERROR: GitHub CLI not found!
        echo Please install it with: winget install --id GitHub.cli
        pause
        exit /b 1
    )
) else (
    set GH=gh
    echo GitHub CLI found in PATH
)

echo.
echo Checking authentication status...
%GH% auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo You need to authenticate with GitHub.
    echo.
    echo Choose authentication method:
    echo 1. Login with browser (recommended)
    echo 2. Login with token (if you have one ready)
    echo.
    choice /c 12 /m "Select option"
    
    if errorlevel 2 (
        echo.
        echo Starting token authentication...
        echo Make sure you have a GitHub Personal Access Token ready
        echo with repo, workflow, and read:org permissions.
        echo.
        %GH% auth login --with-token
    ) else (
        echo.
        echo Starting browser authentication...
        %GH% auth login --web
    )
) else (
    echo ✅ Already authenticated!
    %GH% auth status
)

echo.
echo Setting up GitHub for Film Crew AI...
echo.

:: Test GitHub access
echo Testing GitHub API access...
%GH% api user --jq .login >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Failed to access GitHub API
    echo Please check your authentication and permissions
) else (
    for /f "tokens=*" %%i in ('%GH% api user --jq .login') do (
        echo ✅ Authenticated as: %%i
    )
)

echo.
echo GitHub setup complete!
echo.
echo You can now use GitHub features with Film Crew AI:
echo - Create repositories with: gh repo create
echo - Clone repositories with: gh repo clone
echo - Work with issues: gh issue list
echo - Create pull requests: gh pr create
echo.
pause