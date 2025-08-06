@echo off
echo ======================================================
echo    FILM CREW AI - PUBLISH TO YOUR GITHUB
echo    (For repository maintainers only)
echo ======================================================
echo.
echo NOTE: This is for publishing YOUR OWN fork/version.
echo Regular users should just clone the main repository!
echo.

:: Check if gh is available
where gh >nul 2>nul
if %errorlevel% neq 0 (
    if exist "C:\Program Files\GitHub CLI\gh.exe" (
        set GH="C:\Program Files\GitHub CLI\gh.exe"
    ) else (
        echo ERROR: GitHub CLI not found!
        echo Please run: winget install --id GitHub.cli
        pause
        exit /b 1
    )
) else (
    set GH=gh
)

:: Check authentication
%GH% auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Not authenticated with GitHub!
    echo Please run: setup-github.bat first
    pause
    exit /b 1
)

echo Creating GitHub repository...
echo.

:: Get username
for /f "tokens=*" %%i in ('%GH% api user --jq .login') do set GITHUB_USER=%%i
echo GitHub User: %GITHUB_USER%
echo.

:: Repository details
set REPO_NAME=film-crew-ai
set REPO_DESC="Transform screenplays into cinematic AI prompts with specialized film production agents"

echo Repository Name: %REPO_NAME%
echo Description: %REPO_DESC%
echo.

:: Create repository
echo Creating repository on GitHub...
%GH% repo create %REPO_NAME% --public --description %REPO_DESC% --homepage "https://github.com/%GITHUB_USER%/%REPO_NAME%" -y

if %errorlevel% neq 0 (
    echo.
    echo Repository might already exist. Checking...
    %GH% repo view %GITHUB_USER%/%REPO_NAME% >nul 2>&1
    if %errorlevel% equ 0 (
        echo Repository already exists!
        set /p PUSH="Do you want to push to existing repository? (Y/N): "
        if /i "!PUSH!"=="Y" goto :push
        exit /b 0
    ) else (
        echo Failed to create repository.
        pause
        exit /b 1
    )
)

:push
echo.
echo Setting remote origin...
git remote add origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git 2>nul
if %errorlevel% neq 0 (
    echo Remote origin already exists, updating...
    git remote set-url origin https://github.com/%GITHUB_USER%/%REPO_NAME%.git
)

echo.
echo Pushing to GitHub...
git push -u origin master

if %errorlevel% neq 0 (
    echo.
    echo If push failed due to branch name, try:
    git branch -M main
    git push -u origin main
)

echo.
echo ======================================================
echo    REPOSITORY SUCCESSFULLY CREATED!
echo ======================================================
echo.
echo 🎬 Your Film Crew AI repository is now live at:
echo    https://github.com/%GITHUB_USER%/%REPO_NAME%
echo.
echo Next steps:
echo 1. Visit your repository on GitHub
echo 2. Add topics: ai, video-generation, veo3, claude, film-production
echo 3. Star the repository to show support
echo 4. Share with the community!
echo.
echo To clone this repository elsewhere:
echo    git clone https://github.com/%GITHUB_USER%/%REPO_NAME%.git
echo.
pause