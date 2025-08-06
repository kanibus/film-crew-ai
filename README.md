# Film Crew AI - Screenplay to Video Generation System

Transform your screenplays into AI video generation prompts using 8 specialized AI agents. Works with Google Veo3, Runway ML, Pika Labs, and more.

## 🎬 What This Does

Film Crew AI reads your screenplay and automatically generates prompts that you can paste directly into AI video generation tools like Google Veo3. It breaks down your script into individual shots with detailed descriptions ready for video generation.

### 🎭 8 Specialized AI Agents Working Together

When using Claude Code integration, your screenplay is processed by:
1. **Script Breakdown Agent** - Analyzes structure and dramatic beats
2. **Character Analysis Agent** - Tracks profiles and emotional arcs  
3. **Environment & Props Agent** - Identifies locations and props
4. **Camera Director Agent** - Plans shots and movements
5. **Lighting Designer Agent** - Creates lighting moods
6. **Sound Designer Agent** - Designs soundscapes
7. **Music Director Agent** - Plans musical themes
8. **Prompt Synthesis Agent** - Combines everything into Veo3 prompts

## ⚡ Fastest Setup (Automatic)

**Windows Users:** Double-click `QUICK_START.bat`

**Mac/Linux Users:** Run `bash QUICK_START.sh`

This will automatically install everything and run a test script!

### 🤖 Advanced: Claude Code Integration (Optional)

For enhanced AI agent coordination using Claude Code:

1. **Install Claude Code CLI:**
```bash
npm install -g @anthropic/claude-code
```

2. **Setup Film Crew agents:**
```bash
python setup_claude_code.py
```

3. **Use with Claude Code:**
```bash
claude-code run workflow --input scripts/your_script.txt
```

This activates 8 specialized sub-agents working in parallel!

---

## 📋 Manual Step-by-Step Installation Guide

### Step 1: Download the Project

**Option A: Download as ZIP (Easiest)**
1. Click the green "Code" button above
2. Select "Download ZIP"
3. Extract the ZIP file to your desired location
4. Open the extracted folder

**Option B: Use Git**
```bash
git clone https://github.com/kanibus/film-crew-ai.git
cd film-crew-ai
```

### Step 2: Install Python (If Not Already Installed)

1. Go to https://www.python.org/downloads/
2. Download Python 3.8 or newer
3. During installation, ✅ **CHECK "Add Python to PATH"**
4. Verify installation:
```bash
python --version
```
You should see: `Python 3.x.x`

### Step 3: Install Required Libraries

Open Command Prompt (Windows) or Terminal (Mac/Linux) in the film-crew-ai folder and run:

```bash
pip install PyPDF2 python-docx chardet
```

If you get an error, try:
```bash
python -m pip install PyPDF2 python-docx chardet
```

### Step 4: Prepare Your Screenplay

1. Navigate to the `film-crew-ai` subfolder
2. Create a folder called `scripts` if it doesn't exist
3. Place your screenplay file in the `scripts` folder
4. Supported formats: `.txt`, `.pdf`, `.doc`, `.docx`

### Step 5: Run the Program

In the `film-crew-ai` subfolder, run:

```bash
python film_crew_ai_main.py scripts/your_screenplay.txt
```

Replace `your_screenplay.txt` with your actual filename.

## 🚀 Simple Usage Examples

### Example 1: Process the Sample Script
```bash
cd film-crew-ai
python film_crew_ai_main.py scripts/complex_script.txt
```

### Example 2: Process Your Own Script
1. Copy your script to the `scripts` folder
2. Run:
```bash
python film_crew_ai_main.py scripts/my_script.pdf
```

### Example 3: Batch Process Multiple Scripts
If you have multiple scripts:
```bash
python batch_process.py
```
This will process ALL scripts in the scripts folder at once.

## 📁 Where to Find Your Output

After running the program, your generated prompts will be in:
```
film-crew-ai/
└── output/
    └── [your_script_name]_[timestamp]/
        ├── Veo3_Natural_Prompts/    ← Your video prompts are here!
        ├── Scene_Summaries/         ← Scene breakdowns
        └── Agent_Logs/              ← Processing details
```

**To use with Google Veo3:**
1. Go to the `Veo3_Natural_Prompts` folder
2. Open any `.txt` file
3. Copy the content
4. Paste into Google Veo3

## 🎯 Quick Troubleshooting

### "Python not found" Error
- Make sure Python is installed and added to PATH
- Try using `python3` instead of `python`

### "Module not found" Error
Run this command:
```bash
pip install PyPDF2 python-docx chardet
```

### "No scripts folder" Error
1. Create a folder called `scripts` inside the `film-crew-ai` folder
2. Put your screenplay files there

### Script Not Processing
- Make sure your script is in `.txt`, `.pdf`, `.doc`, or `.docx` format
- Check that the file is in the `scripts` folder
- Try the sample script first: `scripts/complex_script.txt`

## 🎬 Working with Different Platforms

### For Google Veo3 (Default)
```bash
python film_crew_ai_main.py scripts/your_script.txt
```
Output: Natural language prompts in `Veo3_Natural_Prompts` folder

### For Multiple Platforms
Coming soon! The system can export to:
- Runway ML Gen-2
- Pika Labs
- Stability AI
- Haiper AI

## 📝 Screenplay Format Tips

### Standard Format (Recommended)
```
INT. COFFEE SHOP - DAY

SARAH enters the busy coffee shop.

SARAH
(nervous)
Is anyone here?

JAMES (V.O.)
I knew this day would come...
```

### Simple Format Also Works
```
Scene: Coffee shop, daytime
Sarah walks in looking nervous
Sarah: "Is anyone here?"
Voice Over: "I knew this day would come..."
```

## 🚦 Complete Working Example

1. **Download and extract the project**

2. **Open Command Prompt in the film-crew-ai folder**

3. **Install dependencies:**
```bash
pip install PyPDF2 python-docx chardet
```

4. **Process the example script:**
```bash
cd film-crew-ai
python film_crew_ai_main.py scripts/complex_script.txt
```

5. **Find your prompts:**
- Navigate to `output` folder
- Open the newest folder (named with timestamp)
- Go to `Veo3_Natural_Prompts`
- Open any `.txt` file
- Copy and paste into Google Veo3!

## 💡 Tips for Best Results

1. **Use clear scene headers**: INT. or EXT. helps the AI understand locations
2. **Include character names**: Write CHARACTER NAME in caps before dialogue
3. **Add action descriptions**: Describe what's happening in the scene
4. **Voice-overs**: Mark as (V.O.) or "VO:" for proper detection

## 🆘 Need Help?

1. **Try the example script first** - It's already included and tested
2. **Check the output folder** - Your results will always be there
3. **Look for error messages** - They usually tell you what's wrong
4. **File an issue** on GitHub if you're stuck

## Project Structure

```
film-crew-ai/
├── scripts/                     # Place your screenplay files here
├── output/                      # Generated outputs
│   ├── [script_name]_[timestamp]/
│   │   ├── 01_Script_Analysis/  # Scene breakdowns
│   │   ├── 02_Characters/       # Character profiles
│   │   ├── 03_Voice_Overs/      # Extracted voice-overs
│   │   ├── 04_Shots/            # Shot lists by scene
│   │   ├── 05_Veo3_Prompts/     # JSON format prompts
│   │   ├── Veo3_Natural_Prompts/# Natural language prompts
│   │   ├── Veo3_Enhanced_Prompts/# Enhanced with VO integration
│   │   ├── Scene_Summaries/     # Scene-by-scene summaries
│   │   ├── Agent_Logs/          # AI agent execution logs
│   │   └── [Platform]_Exports/  # Platform-specific exports
├── film_crew_ai_main.py         # Main entry point
├── requirements.txt             # Python dependencies
└── README.md                    # This file
```

## Supported Screenplay Formats

### Traditional Screenplay Format
```
INT. COFFEE SHOP - DAY

SARAH (30s) enters nervously.

SARAH
Is anyone here?

JAMES (V.O.)
I had no choice...
```

### Vignette Format
```
Video: Wide shot of city street
VO: The city never sleeps...
```

## Configuration

### Platform Selection

Edit `film_crew_ai_main.py` to set default platforms:

```python
DEFAULT_PLATFORMS = ['veo3', 'runway', 'pika']
```

Available platforms:
- `veo3` - Google Veo3
- `runway` - Runway ML Gen-2
- `pika` - Pika Labs
- `stability` - Stability AI Video
- `haiper` - Haiper AI

### Processing Options

```python
# In film_crew_ai_main.py
pipeline.process_script(
    script_path="scripts/my_script.pdf",
    output_dir="output",
    generate_enhanced=True,  # Generate enhanced prompts
    generate_natural=True,   # Generate natural language prompts
    platforms=['veo3', 'runway']  # Target platforms
)
```

## API Usage

```python
from film_crew_ai_main import FilmCrewAIPipeline

# Initialize pipeline
pipeline = FilmCrewAIPipeline(verbose=True)

# Process screenplay
result = pipeline.process_script(
    script_path="path/to/screenplay.pdf",
    output_dir="output",
    generate_enhanced=True,
    generate_natural=True
)

# Access generated data
if result:
    print(f"Output saved to: {result}")
```

## Command Line Options

```bash
python film_crew_ai_main.py [OPTIONS] script_file

Options:
  script_file          Path to screenplay file (required)
  --output DIR         Output directory (default: ./output)
  --verbose           Enable verbose logging
  --platforms LIST     Space-separated list of platforms
  --no-enhanced       Skip enhanced prompt generation
  --no-natural        Skip natural language generation
  --batch             Process all scripts in directory
```

## Examples

### Example 1: Basic Processing
```bash
python film_crew_ai_main.py scripts/my_screenplay.pdf
```

### Example 2: Multi-Platform Export
```bash
python film_crew_ai_main.py scripts/action_movie.pdf --platforms veo3 runway pika
```

### Example 3: Batch Processing
```bash
# Process all scripts in the scripts folder
python batch_process.py
```

### Example 4: Custom Output Directory
```bash
python film_crew_ai_main.py scripts/drama.docx --output productions/drama_output
```

## Output Files

### Scene Summaries
- `[script]_MASTER_SUMMARY.json` - Complete script overview
- `[script]_OVERVIEW.txt` - Human-readable summary
- `[script]_scene[N]_summary.json` - Individual scene summaries

### Veo3 Prompts
- Natural language format optimized for Google Veo3
- JSON structured format for programmatic access
- Enhanced prompts with voice-over integration

### Platform Exports
- Each platform gets optimized prompts in its preferred format
- Comparison report showing differences between platforms

### Agent Logs
- Detailed logs of each AI agent's contribution
- Performance metrics and execution times
- Scene coverage analysis

## Troubleshooting

### Common Issues

1. **Import Error: No module named 'PyPDF2'**
   ```bash
   pip install PyPDF2
   ```

2. **Encoding Issues with Scripts**
   - The system auto-detects encoding (UTF-8, Latin-1, CP1252)
   - Save scripts as UTF-8 for best compatibility

3. **No Scenes Detected**
   - Ensure screenplay follows standard format
   - Check for INT./EXT. scene headers
   - For vignettes, use "Video:" and "VO:" markers

4. **Memory Issues with Large Scripts**
   - Process in smaller batches
   - Increase Python memory limit
   - Use `--no-enhanced` flag to reduce memory usage

## Testing

Run the test suite:
```bash
python test_film_crew_ai.py
```

Test specific components:
```bash
python test_advanced_parser.py
python test_veo3_generator.py
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Requirements

- Python 3.8+
- PyPDF2
- python-docx
- chardet
- dataclasses (Python 3.7+)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Claude Code assistance
- Optimized for Google Veo3 and other AI video platforms
- Uses SPARC development methodology

## Support

For issues, questions, or contributions:
- Open an issue on GitHub
- Check existing issues for solutions
- Read the documentation thoroughly

## Changelog

### Version 8.0 (Current)
- Added 8 coordinated AI agents
- Multi-platform export support
- Scene summary generation
- Agent execution logging
- Enhanced character consistency
- Voice-over integration
- Support for PDF, DOC, DOCX formats

### Version 7.0
- Advanced screenplay parsing
- Natural language prompt generation
- Character tracking across scenes

### Version 6.0
- Initial vignette format support
- Basic Veo3 prompt generation

---

**Film Crew AI** - Transforming screenplays into cinematic AI video prompts