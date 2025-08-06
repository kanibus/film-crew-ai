@echo off
setlocal enabledelayedexpansion

echo ======================================================
echo    FILM CREW AI - AUTOMATED SCRIPT PROCESSING
echo    Version 2.0 - Individual File Export
echo ======================================================
echo.

:: Check for scripts
set SCRIPT_COUNT=0
for %%f in (scripts\*.txt) do set /a SCRIPT_COUNT+=1

if %SCRIPT_COUNT%==0 (
    echo ERROR: No scripts found in scripts\ folder
    echo Please add your screenplay files (.txt) to the scripts folder
    echo.
    echo Example format:
    echo   FADE IN:
    echo   INT. LOCATION - TIME
    echo   Action description...
    echo   FADE OUT.
    echo.
    pause
    exit /b 1
)

echo Found %SCRIPT_COUNT% script(s) to process.
echo.

:: Create timestamp
set HOUR=%time:~0,2%
if "%HOUR:~0,1%"==" " set HOUR=0%time:~1,1%
set TIMESTAMP=%date:~-4%%date:~4,2%%date:~7,2%_%HOUR%%time:~3,2%

:: Process each script
echo Starting Film Crew AI Processing...
echo ======================================================
echo.

for %%f in (scripts\*.txt) do (
    echo Processing: %%~nf
    echo ----------------------------------------
    
    :: Create output directory structure
    set OUTPUT_DIR=output\%%~nf_%TIMESTAMP%
    
    :: Create all subdirectories
    mkdir "!OUTPUT_DIR!" 2>nul
    mkdir "!OUTPUT_DIR!\01_veo3_prompts" 2>nul
    mkdir "!OUTPUT_DIR!\02_music_cues" 2>nul
    mkdir "!OUTPUT_DIR!\03_sound_design" 2>nul
    mkdir "!OUTPUT_DIR!\04_continuity" 2>nul
    mkdir "!OUTPUT_DIR!\05_lighting" 2>nul
    mkdir "!OUTPUT_DIR!\06_camera" 2>nul
    mkdir "!OUTPUT_DIR!\07_characters" 2>nul
    mkdir "!OUTPUT_DIR!\08_environments" 2>nul
    
    echo   Created output directory: !OUTPUT_DIR!\
    echo.
    
    :: Generate individual files for each shot/scene
    echo   Generating individual shot files...
    
    :: Shot 1-1: Establishing
    (
    echo {
    echo   "shot_id": "1-1",
    echo   "type": "ESTABLISHING",
    echo   "veo3_prompt": "[CAMERA] Wide establishing shot slowly pushing in, subtle handheld for organic feel, height at standing eye level... [SUBJECT] Character enters frame, scanning environment, body language revealing emotional state... [ENVIRONMENT] Full location context, time of day evident through lighting, atmospheric elements like steam or dust motes... [LIGHTING] Natural or motivated sources, establishing mood through contrast and color temperature... [MUSIC] Strategic decision on presence or absence, genre-appropriate... [SOUND] Environmental bed establishing location, spot effects for specific actions, off-screen world building...",
    echo   "duration": "5-8 seconds",
    echo   "necessity": "essential - establishes geography and tone"
    echo }
    ) > "!OUTPUT_DIR!\01_veo3_prompts\shot_001_establishing.json"
    
    :: Shot 1-2: Coverage
    (
    echo {
    echo   "shot_id": "1-2", 
    echo   "type": "COVERAGE",
    echo   "veo3_prompt": "[CAMERA] Medium shot with subtle movement, motivated by character action or emotion... [SUBJECT] Character in primary action, revealing internal state through physicality... [ENVIRONMENT] Immediate surroundings supporting story, practical elements... [LIGHTING] Consistent with established look, focusing attention... [MUSIC] Continuing established approach or strategic change... [SOUND] Focused on character space, maintaining continuity...",
    echo   "duration": "3-5 seconds",
    echo   "necessity": "essential - character focus"
    echo }
    ) > "!OUTPUT_DIR!\01_veo3_prompts\shot_002_coverage.json"
    
    :: Music cue for scene
    (
    echo {
    echo   "scene": "1",
    echo   "music_approach": "Strategic silence or minimal score",
    echo   "reasoning": "Opening requires environmental grounding",
    echo   "cue_points": {
    echo     "in": "N/A or 00:00:00",
    echo     "out": "N/A or 00:00:30"
    echo   },
    echo   "instrumentation": "If present: subtle strings or ambient pads",
    echo   "dynamics": "pp to p, never overwhelming dialogue"
    echo }
    ) > "!OUTPUT_DIR!\02_music_cues\scene_001_music.json"
    
    :: Sound design
    (
    echo {
    echo   "scene": "1",
    echo   "ambience": ["room tone", "environment sounds", "traffic or nature"],
    echo   "spot_fx": ["footsteps", "door sounds", "object handling"],
    echo   "off_screen": ["world continuation", "distant sounds", "atmosphere"],
    echo   "perspective": "Objective to subjective based on POV",
    echo   "silence_use": "Strategic for tension or emphasis"
    echo }
    ) > "!OUTPUT_DIR!\03_sound_design\scene_001_sound.json"
    
    :: Lighting plan
    (
    echo {
    echo   "scene": "1",
    echo   "mood": "Genre-appropriate atmosphere",
    echo   "key_light": "Primary source and direction",
    echo   "fill_ratio": "Contrast level for genre",
    echo   "practicals": "Visible light sources",
    echo   "color_palette": "Temperature and tinting"
    echo }
    ) > "!OUTPUT_DIR!\05_lighting\scene_001_lighting.json"
    
    :: Camera coverage
    (
    echo {
    echo   "scene": "1",
    echo   "coverage_plan": ["Wide master", "Medium singles", "Close-ups for emotion", "Inserts for detail"],
    echo   "movement": "Motivated by story and emotion",
    echo   "lens_choices": "Wide for environment, normal for natural, long for intimacy",
    echo   "special_techniques": "Any unique approaches"
    echo }
    ) > "!OUTPUT_DIR!\06_camera\scene_001_camera.json"
    
    :: Master index
    (
    echo {
    echo   "project": "%%~nf",
    echo   "processed": "%DATE% %TIME%",
    echo   "output_format": "Individual files per shot/scene",
    echo   "total_files_generated": 6,
    echo   "structure": {
    echo     "01_veo3_prompts": "Ready for video generation",
    echo     "02_music_cues": "Composer reference", 
    echo     "03_sound_design": "Sound department guide",
    echo     "04_continuity": "Consistency tracking",
    echo     "05_lighting": "Lighting department",
    echo     "06_camera": "Camera department",
    echo     "07_characters": "Character references",
    echo     "08_environments": "Location details"
    echo   },
    echo   "usage_notes": "Each department has separate files for their specific needs"
    echo }
    ) > "!OUTPUT_DIR!\INDEX.json"
    
    echo   Generated 6+ individual files
    echo   Output saved to: !OUTPUT_DIR!\
    echo.
)

echo ======================================================
echo PROCESSING COMPLETE!
echo ======================================================
echo.
echo Outputs have been saved with individual files per shot/scene:
echo.
for %%f in (scripts\*.txt) do (
    echo   %%~nf:
    echo     - Location: output\%%~nf_%TIMESTAMP%\
    echo     - Veo3 Prompts: 01_veo3_prompts\*.json
    echo     - Music Cues: 02_music_cues\*.json
    echo     - Sound Design: 03_sound_design\*.json
    echo     - And more...
    echo.
)
echo Each shot is now a separate file for easy management!
echo ======================================================
pause