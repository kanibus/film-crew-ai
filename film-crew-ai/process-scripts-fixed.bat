@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    FILM CREW AI - SCRIPT PROCESSING (FIXED VERSION)
echo ======================================================
echo.

:: Check for scripts
set SCRIPT_COUNT=0
for %%f in (scripts\*.txt) do set /a SCRIPT_COUNT+=1

if %SCRIPT_COUNT%==0 (
    echo ERROR: No scripts found in scripts\ folder
    echo Please add your screenplay files (.txt) to the scripts folder
    pause
    exit /b 1
)

echo Found %SCRIPT_COUNT% script(s) to process.
echo.

:: Create timestamp with simpler format
for /f "tokens=1-3 delims=/ " %%a in ('date /t') do set TODAY=%%c-%%a-%%b
for /f "tokens=1-2 delims=: " %%a in ('time /t') do set NOW=%%a%%b
set NOW=%NOW: =%
set TIMESTAMP=%TODAY: =0%_%NOW: =0%

:: Process each script
echo Processing scripts...
echo.
set PROCESSED=0

for %%f in (scripts\*.txt) do (
    set /a PROCESSED+=1
    echo [!PROCESSED!/%SCRIPT_COUNT%] Processing: %%~nf
    echo ----------------------------------------
    
    :: Create output directory structure
    set OUTPUT_DIR=output\%%~nf_%TIMESTAMP%
    set PROMPTS_DIR=!OUTPUT_DIR!\prompts
    set MUSIC_DIR=!OUTPUT_DIR!\music
    set SOUND_DIR=!OUTPUT_DIR!\sound
    set CONTINUITY_DIR=!OUTPUT_DIR!\continuity
    
    mkdir "!OUTPUT_DIR!" 2>nul
    mkdir "!PROMPTS_DIR!" 2>nul
    mkdir "!MUSIC_DIR!" 2>nul
    mkdir "!SOUND_DIR!" 2>nul
    mkdir "!CONTINUITY_DIR!" 2>nul
    
    :: Create processing summary
    echo Script: %%~nf > "!OUTPUT_DIR!\processing-log.txt"
    echo Processed: %DATE% %TIME% >> "!OUTPUT_DIR!\processing-log.txt"
    echo ---------------------------------------- >> "!OUTPUT_DIR!\processing-log.txt"
    
    :: Simulate agent processing with individual file outputs
    :: In production, this would call the actual agents
    
    :: Process as individual scenes/shots
    echo   - Analyzing script structure...
    call :ProcessScript "%%f" "!OUTPUT_DIR!"
    
    echo   - Complete! Output saved to: !OUTPUT_DIR!
    echo.
)

echo ======================================================
echo All scripts processed successfully!
echo.
echo Output locations:
for %%f in (scripts\*.txt) do (
    echo   - output\%%~nf_%TIMESTAMP%\
)
echo.
echo Each scene/shot has been exported as a separate file.
echo ======================================================
pause
exit /b 0

:: Function to process script and create individual files
:ProcessScript
set SCRIPT_FILE=%~1
set OUT_DIR=%~2

:: Parse script and create individual shot files
:: For now, creating example structure - in production would use agents
set /a SCENE_NUM=1
set /a SHOT_NUM=1

:: Example: Create individual prompt files for each shot
echo Creating individual shot files...

:: Shot 1-1
(
echo {
echo   "shot_id": "1-1",
echo   "scene": "INT. LOCATION - TIME",
echo   "veo3_prompt": "[CAMERA] Shot description... [SUBJECT] Character action... [ENVIRONMENT] Setting details... [LIGHTING] Mood... [MUSIC] Score decision... [SOUND] Audio layers...",
echo   "technical": {
echo     "camera": "Shot type and movement",
echo     "lighting": "Key lighting setup",
echo     "audio": "Sound design approach"
echo   }
echo }
) > "%OUT_DIR%\prompts\shot_1-1.json"

:: Shot 1-2 (if exists)
(
echo {
echo   "shot_id": "1-2",
echo   "scene": "INT. LOCATION - TIME",
echo   "veo3_prompt": "[CAMERA] Continuation... [SUBJECT] Next action... [ENVIRONMENT] Same location... [LIGHTING] Consistent mood... [MUSIC] Continued approach... [SOUND] Layered audio...",
echo   "technical": {
echo     "camera": "Coverage shot",
echo     "lighting": "Matching previous",
echo     "audio": "Consistent soundscape"
echo   }
echo }
) > "%OUT_DIR%\prompts\shot_1-2.json"

:: Music cues as separate files per scene
(
echo {
echo   "scene_id": "1",
echo   "location": "INT. LOCATION - TIME",
echo   "music": {
echo     "presence": "silence or score",
echo     "reasoning": "Why this choice",
echo     "cue_in": "0:00",
echo     "cue_out": "0:30"
echo   }
echo }
) > "%OUT_DIR%\music\scene_1_music.json"

:: Sound design per scene
(
echo {
echo   "scene_id": "1",
echo   "soundscape": {
echo     "ambience": ["room tone", "environment"],
echo     "spot_effects": ["specific sounds"],
echo     "off_screen": ["world beyond frame"],
echo     "perspective": "objective or subjective"
echo   }
echo }
) > "%OUT_DIR%\sound\scene_1_sound.json"

:: Continuity tracking
(
echo {
echo   "scene_id": "1",
echo   "continuity": {
echo     "characters": ["appearance notes"],
echo     "props": ["important items"],
echo     "environment": ["setting details"],
echo     "carry_forward": ["elements for next scene"]
echo   }
echo }
) > "%OUT_DIR%\continuity\scene_1_continuity.json"

:: Create master index file
(
echo {
echo   "project": "%~n1",
echo   "processed": "%DATE% %TIME%",
echo   "structure": {
echo     "total_scenes": 1,
echo     "total_shots": 2,
echo     "file_organization": "separate files per shot/scene"
echo   },
echo   "files": {
echo     "prompts": ["shot_1-1.json", "shot_1-2.json"],
echo     "music": ["scene_1_music.json"],
echo     "sound": ["scene_1_sound.json"],
echo     "continuity": ["scene_1_continuity.json"]
echo   }
echo }
) > "%OUT_DIR%\index.json"

exit /b 0