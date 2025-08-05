# Film Crew AI - Automated Script-to-Veo3 Processing System

An intelligent swarm-based film production system that transforms scripts into comprehensive Veo 3 prompts with full audio design, using Claude Code's sub-agent architecture.

## 🎬 Overview

Film Crew AI orchestrates a team of specialized AI agents that analyze scripts through the lens of experienced filmmakers, creating rich, cinematic prompts that go beyond literal descriptions to capture visual poetry, emotional depth, and strategic audio design.

## 🚀 Quick Start

### Prerequisites

- Windows 10/11
- Node.js installed ([Download here](https://nodejs.org/))
- Claude CLI (will be installed automatically, or manually: `npm install -g @anthropic-ai/claude-code`)
- Claude API access (via Claude Code)

### Installation

1. Navigate to the `film-crew-ai` folder
2. Run the installation script:
   ```batch
   install-film-crew.bat
   ```
3. Verify installation:
   ```batch
   verify-installation.bat
   ```
   
   This will:
   - Install Claude CLI for swarm features
   - Install Claude Flow globally
   - Initialize the SPARC system with 64+ agents
   - Create all necessary directories
   - Install Film Crew AI agent templates
   - Set up the swarm configuration
   - Copy agents to `.claude/agents/` for activation
   - Create a test script for verification

## 📝 Adding Scripts

Place your script files in the `scripts/` folder with `.txt` extension.

### Script Format Example:
```
FADE IN:

INT. COFFEE SHOP - DAY

SARAH (30s, tired eyes) enters, scanning the crowded room. 
She spots JOHN at a corner table, nervously tapping his fingers.

SARAH
(hesitant)
We need to talk about what happened.

JOHN looks up, his coffee untouched.

FADE OUT.
```

## 🎯 Processing Scripts

### Automated Batch Processing

To process all scripts in the `scripts/` folder:

```batch
process-scripts.bat
```

This will:
1. Start the Claude Flow system
2. Initialize the Film Crew Swarm with 8 specialized agents
3. Create automatic restore points for each script
4. Process each script through all production phases
5. Generate timestamped output folders

### What Gets Processed

Each script goes through:

**Phase 1: Script Analysis**
- Dramatic structure identification
- Emotional arc mapping
- Visual storytelling opportunities

**Phase 2: Visual Team (Parallel)**
- Character design with emotion cards
- Environment and production design
- Camera angles and movements
- Lighting design for mood

**Phase 3: Audio Team (Parallel)**
- Strategic music placement
- Sound design with off-screen elements
- Silence architecture

**Phase 4: Synthesis**
- Comprehensive Veo 3 prompt generation
- Necessity testing for each element
- Continuity tracking

## ✏️ Edit Mode

For interactive editing after initial processing:

```batch
edit-mode.bat
```

### Edit Mode Features:

1. **Edit Single Shot** - Modify specific aspects of any shot
2. **Edit Multiple Shots** - Batch edit a range of shots
3. **Create Restore Point** - Manual version save
4. **List Versions** - View all saved versions
5. **Restore Version** - Rollback to any previous state
6. **Exit** - Return to command line

### Edit Options:
- `camera` - Reprocess camera angles
- `character` - Update character emotions/actions
- `background` - Modify environment
- `lighting` - Change mood/atmosphere
- `music` - Adjust score/silence
- `sound` - Modify soundscape
- `complete` - Full shot reanalysis

## 📁 Output Structure

After processing, find your outputs in:

```
output/
├── [script-name]_[timestamp]/
│   ├── veo3_prompts.json      # Complete Veo 3 prompts
│   ├── music_cues.json        # Music timing and themes
│   ├── sound_design.json      # Sound layers and perspective
│   └── continuity.json        # Character/scene tracking
```

### Output File Descriptions:

**veo3_prompts.json**
- Comprehensive prompts for each shot
- Includes camera, lighting, environment, and audio
- Ready for Veo 3 generation

**music_cues.json**
- Musical decisions for each shot
- Strategic silence placements
- Tempo, instrumentation, and dynamics

**sound_design.json**
- On-screen and off-screen audio
- Environmental ambience
- Perspective (objective/subjective)

**continuity.json**
- Character appearance tracking
- Scene-to-scene consistency notes
- Props and environmental continuity

## 🎨 Customization

### Project Settings

Edit `config/project-settings.json` to customize:

```json
{
  "genre": "Drama/Comedy/Thriller/Horror",
  "tone": "Cinematic/Light/Dark/Realistic",
  "visual_style": "High contrast/Soft/Naturalistic",
  "poetry_preferences": {
    "level": "high/medium/low",
    "literal_vs_lyrical": "30/70"
  }
}
```

### Adding Custom Agents

Create new agents in `templates/agents/` following the format:

```markdown
---
name: agent-name
description: Clear description of purpose. Use PROACTIVELY when...
---

You are a [Role] who [Philosophy]...

## Process:
1. Step one
2. Step two

## Output Format:
{
  "field": "value"
}
```

## 🔧 Troubleshooting

### Common Issues:

**"Node.js is not installed"**
- Download and install Node.js from https://nodejs.org/

**"Claude CLI not found" or "spawn claude ENOENT"**
- Install Claude CLI: `npm install -g @anthropic-ai/claude-code`
- Verify installation: `claude --version`
- If still issues, check PATH environment variable includes npm global folder

**"No scripts found"**
- Ensure your scripts are in `scripts/` folder
- Files must have `.txt` extension

**"Claude Flow not found"**
- Run `install-film-crew.bat` first
- Or manually install: `npm install -g claude-flow@latest`
- Check `logs/claude-flow.log` for errors

**"Failed to launch Claude Code"**
- Ensure Claude CLI is installed: `npm install -g @anthropic-ai/claude-code`
- Check if running: `claude --version`
- Try running with: `claude-flow swarm "task" --no-claude` to skip CLI

**Processing seems stuck**
- Check if Claude Flow UI is running at http://localhost:3000/console
- Review `logs/` folder for error messages
- Try stopping (Ctrl+C) and restarting the process

## 📊 Version Control

The system automatically creates restore points:
- Before each script processing
- Available through Edit Mode
- Stored in `.claude/versions/`

To manually create a restore point:
```batch
edit-mode.bat
> Select option 3
> Enter version name and description
```

## 🎭 Agent Roster

- **script-breakdown**: Dramatic structure analysis
- **character-analysis**: Style and emotion cards
- **background-designer**: Environmental storytelling
- **camera-director**: Cinematography choices
- **lighting-designer**: Mood through illumination
- **music-director**: Score and silence decisions
- **sound-designer**: 3D soundscape creation
- **prompt-combiner**: Final synthesis and testing

## 💡 Tips for Best Results

1. **Script Formatting**: Use standard screenplay format for best analysis
2. **Scene Headers**: Include INT/EXT, location, and time of day
3. **Action Lines**: Be descriptive but concise
4. **Dialogue**: Include character names and parentheticals
5. **Transitions**: Use FADE IN/OUT, CUT TO, etc.

## 🚦 System Requirements

### Hardware:
- **RAM**: 8GB minimum, 16GB recommended
- **Storage**: 1GB for installation + space for outputs
- **Network**: Internet connection for Claude API

### Software:
- **Operating System**: Windows 10/11, macOS, or Linux
- **Node.js**: Version 16.x or higher ([Download](https://nodejs.org/))
- **Claude CLI**: Latest version (auto-installed or `npm install -g @anthropic-ai/claude-code`)
- **Claude Flow**: Latest alpha version (auto-installed or `npm install -g claude-flow@latest`)
- **Git**: Optional, for version control ([Download](https://git-scm.com/))

## 📝 License

This system is designed for creative film production use. The AI agents follow cinematic best practices while maintaining artistic vision.

---

**Ready to transform your scripts into cinematic visions?** Start with `install-film-crew.bat` and let the Film Crew AI bring your stories to life!