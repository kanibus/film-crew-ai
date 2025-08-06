# Film Crew AI - Screenplay to Video Generation System

Transform screenplays into production-ready prompts for AI video generation platforms like Google Veo3, Runway ML, and more.

## Overview

Film Crew AI is an intelligent system that uses 8 specialized AI agents working in coordination to analyze screenplays and generate optimized prompts for AI video generation. It supports multiple screenplay formats, maintains character consistency, integrates voice-overs, and exports to multiple video generation platforms.

## Features

- **8 Specialized AI Agents** working in coordination:
  - Script Breakdown Agent
  - Character Analysis Agent
  - Environment & Props Agent
  - Camera Director Agent
  - Lighting Designer Agent
  - Sound Designer Agent
  - Music Director Agent
  - Prompt Synthesis Agent

- **Multi-Format Support**: PDF, DOC, DOCX, TXT
- **Intelligent Parsing**: Detects scenes, shots, voice-overs, and transitions
- **Character Consistency**: Tracks character profiles across scenes
- **Multi-Platform Export**: Veo3, Runway ML, Pika Labs, Stability AI, Haiper AI
- **Scene Summaries**: Auto-generated scene breakdowns and master summaries
- **Natural Language Output**: Human-readable prompts optimized for each platform

## Quick Start

### Prerequisites

```bash
# Python 3.8 or higher required
python --version

# Install dependencies
pip install -r requirements.txt
```

### Basic Usage

1. **Process a single screenplay:**
```bash
python film_crew_ai_main.py scripts/your_script.pdf
```

2. **Process with specific output directory:**
```bash
python film_crew_ai_main.py scripts/your_script.pdf --output my_output_folder
```

3. **Generate for multiple platforms:**
```bash
python film_crew_ai_main.py scripts/your_script.pdf --platforms veo3 runway pika
```

4. **Batch process multiple scripts:**
```bash
python batch_process.py
```

## Installation

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/film-crew-ai.git
cd film-crew-ai
```

### Step 2: Create Virtual Environment (Recommended)
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation
```bash
python test_film_crew_ai.py
```

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