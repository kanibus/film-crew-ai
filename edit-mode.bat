@echo off
:MENU
cls
echo ======================================================
echo    FILM CREW AI - EDIT MODE
echo ======================================================
echo.
echo 1. Edit single shot
echo 2. Edit multiple shots  
echo 3. Create restore point
echo 4. List versions
echo 5. Restore version
echo 6. Exit
echo.

choice /c 123456 /m "Select option"

if %errorlevel%==1 (
    set /p SHOT="Shot ID: "
    set /p ASPECT="Edit what (camera/character/background/lighting/music/sound/complete): "
    call claude-flow /edit-shot !SHOT! !ASPECT!
    pause
    goto MENU
)

if %errorlevel%==2 (
    set /p RANGE="Shot range (e.g. 3-* or 2-1:2-5): "
    set /p EDIT="Edit type: "
    call claude-flow /edit-shots-batch "!RANGE!" "!EDIT!"
    pause
    goto MENU
)

if %errorlevel%==3 (
    set /p NAME="Version name: "
    set /p DESC="Description: "
    call claude-flow /create-restore-point "!NAME!" "!DESC!"
    echo Restore point created: !NAME!
    pause
    goto MENU
)

if %errorlevel%==4 (
    echo.
    echo Available versions:
    echo.
    dir /b ".claude\versions"
    echo.
    pause
    goto MENU
)

if %errorlevel%==5 (
    echo.
    echo Available versions:
    dir /b ".claude\versions"
    echo.
    set /p VERSION="Version to restore: "
    call claude-flow /restore-version "!VERSION!"
    echo Restored to version: !VERSION!
    pause
    goto MENU
)

if %errorlevel%==6 (
    echo Exiting edit mode...
    exit /b 0
)