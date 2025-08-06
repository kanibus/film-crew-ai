#!/bin/bash

echo "============================================================"
echo "           FILM CREW AI - QUICK START SETUP"
echo "============================================================"
echo ""
echo "This will set up Film Crew AI on your computer."
echo ""
echo "Press Enter to continue..."
read

echo ""
echo "Step 1: Checking Python installation..."
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo ""
    echo "ERROR: Python is not installed!"
    echo ""
    echo "Please install Python from: https://www.python.org/downloads/"
    echo "Or use your package manager:"
    echo "  Ubuntu/Debian: sudo apt install python3 python3-pip"
    echo "  macOS: brew install python3"
    echo ""
    exit 1
fi
echo "Python is installed! Using: $PYTHON_CMD"

echo ""
echo "Step 2: Installing required libraries..."
$PYTHON_CMD -m pip install PyPDF2 python-docx chardet
if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install libraries."
    echo "Try running: $PYTHON_CMD -m pip install --user PyPDF2 python-docx chardet"
    exit 1
fi

echo ""
echo "Step 3: Creating scripts folder..."
if [ ! -d "film-crew-ai/scripts" ]; then
    mkdir -p "film-crew-ai/scripts"
    echo "Scripts folder created!"
else
    echo "Scripts folder already exists!"
fi

echo ""
echo "Step 4: Testing with example script..."
cd film-crew-ai
if [ -f "scripts/complex_script.txt" ]; then
    echo ""
    echo "Running example script..."
    $PYTHON_CMD film_crew_ai_main.py scripts/complex_script.txt
    echo ""
    echo "============================================================"
    echo "                    SETUP COMPLETE!"
    echo "============================================================"
    echo ""
    echo "Your video prompts are in:"
    echo "  film-crew-ai/output/[newest folder]/Veo3_Natural_Prompts/"
    echo ""
    echo "To process your own script:"
    echo "  1. Put your script in: film-crew-ai/scripts/"
    echo "  2. Run: $PYTHON_CMD film_crew_ai_main.py scripts/your_script.txt"
    echo ""
else
    echo ""
    echo "Example script not found. Setup complete!"
    echo ""
    echo "To use Film Crew AI:"
    echo "  1. Put your script in: film-crew-ai/scripts/"
    echo "  2. Run: $PYTHON_CMD film_crew_ai_main.py scripts/your_script.txt"
    echo ""
fi