@echo off
echo ============================================================
echo Film Crew AI - GitHub Repository Update Script
echo ============================================================
echo.
echo This script will update the existing repository at:
echo https://github.com/kanibus/film-crew-ai
echo.
echo WARNING: This will replace all old content with the new version
echo while preserving git history.
echo.
pause

echo.
echo Step 1: Initializing git repository...
git init

echo.
echo Step 2: Adding remote origin...
git remote remove origin 2>nul
git remote add origin https://github.com/kanibus/film-crew-ai.git

echo.
echo Step 3: Fetching existing repository...
git fetch origin

echo.
echo Step 4: Checking out main branch...
git checkout -b main 2>nul || git checkout main

echo.
echo Step 5: Pulling latest changes (to preserve history)...
git pull origin main --allow-unrelated-histories --no-edit 2>nul

echo.
echo Step 6: Removing old files (except .git)...
echo Cleaning up old content...

REM Create a backup of important files that might exist
if exist "CLAUDE.md" move "CLAUDE.md" "CLAUDE_backup.md" 2>nul

echo.
echo Step 7: Adding all new files...
git add -A

echo.
echo Step 8: Creating commit...
git commit -m "Major Update v8.0: Complete rewrite with 8 AI agents, multi-platform support, and enhanced features" -m "- Added 8 coordinated AI agents for film production" -m "- Multi-platform export (Veo3, Runway, Pika, Stability, Haiper)" -m "- Scene-level summaries and master overview" -m "- Character consistency tracking" -m "- Voice-over integration" -m "- Support for PDF, DOC, DOCX formats" -m "- Agent execution logging" -m "- Comprehensive documentation and examples"

echo.
echo Step 9: Pushing to GitHub...
echo.
echo You will need to authenticate with GitHub.
echo Use one of these methods:
echo   1. GitHub Personal Access Token (recommended)
echo   2. GitHub CLI (gh auth login)
echo   3. SSH keys if configured
echo.
git push -u origin main --force-with-lease

echo.
echo ============================================================
echo UPDATE COMPLETE!
echo ============================================================
echo.
echo Your repository has been updated at:
echo https://github.com/kanibus/film-crew-ai
echo.
echo Next steps:
echo 1. Visit your repository to verify the update
echo 2. Update repository description and topics
echo 3. Create a new release tag (v8.0)
echo.
pause