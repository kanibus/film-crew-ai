# 🚀 Film Crew AI - Quick Start Guide

Get your first script processed in under 5 minutes! 🎬

## 📦 Installation (2 minutes)

### Windows Users

1. **Download the project**:
   ```bash
   git clone https://github.com/yourusername/film-crew-ai.git
   cd film-crew-ai
   ```

2. **Run the installer**:
   ```bash
   install-film-crew.bat
   ```
   This installs everything you need automatically! ✨

3. **Verify installation**:
   ```bash
   verify-installation.bat
   ```
   
   You should see:
   ```
   ✅ Node.js installed
   ✅ Claude CLI installed
   ✅ Claude Flow installed
   ✅ 8 agents installed
   ✅ Test script exists
   ```

### macOS/Linux Users

```bash
# Clone repository
git clone https://github.com/yourusername/film-crew-ai.git
cd film-crew-ai

# Install dependencies
npm install -g @anthropic-ai/claude-code
npm install -g claude-flow@latest

# Initialize
npx claude-flow@latest init --sparc

# Copy agents
cp templates/agents/*.md .claude/agents/
cp templates/commands/*.md .claude/commands/
```

## 🎬 Process Your First Script (1 minute)

### Step 1: Add Your Script

Create a file `scripts/my-first-scene.txt`:

```screenplay
FADE IN:

INT. ABANDONED WAREHOUSE - NIGHT

Moonlight streams through broken windows. DETECTIVE SARAH CHEN (40s, weathered) enters cautiously, gun drawn.

A SHADOW moves in the darkness.

SARAH
(whispered)
I know you're here.

FADE OUT.
```

### Step 2: Run Processing

```bash
process-scripts.bat
```

### Step 3: Get Your Output!

Check `output/my-first-scene_[timestamp]/`:

**veo3_prompts.json** will contain:
```json
{
  "shot_id": "1-1",
  "veo3_prompt": "[CAMERA] Wide establishing shot slowly pushing in, handheld tension... [SUBJECT] Detective Sarah Chen, 40s, weathered face showing years of cases, enters abandoned warehouse with professional caution, gun drawn but low... [ENVIRONMENT] Moonlight shafts through broken windows creating dramatic light pools, dust particles floating, industrial decay, shadows suggesting hidden threats... [LIGHTING] High contrast noir lighting, moonlight as key, deep shadows hiding 80% of space... [MUSIC] Silence except for environmental tension... [SOUND] Footsteps on debris, distant dripping water, Sarah's controlled breathing, fabric rustling in darkness...",
  "necessity_verdict": "essential"
}
```

## 🎯 Understanding the Output

### File Breakdown

| File | Purpose | Use Case |
|------|---------|----------|
| **veo3_prompts.json** | Complete prompts for Veo 3 | Copy directly to Veo 3 |
| **music_cues.json** | Music timing and mood | For composers/music AI |
| **sound_design.json** | Sound layers and effects | For sound designers |
| **continuity.json** | Tracking between shots | Maintain consistency |

### Using with Veo 3

1. Open Google Veo 3
2. Copy the `veo3_prompt` content
3. Paste into Veo 3's prompt field
4. Generate your video!

## ✏️ Quick Edits

Need to change something? Use Edit Mode:

```bash
edit-mode.bat
```

Select options:
- `1` - Edit single shot (change camera angle, lighting, etc.)
- `3` - Save current version before changes
- `5` - Restore previous version if needed

### Example: Change Camera Angle

```
Select option: 1
Shot ID: 1-1
Edit what: camera
```

The system will reprocess just that shot's camera work while keeping everything else!

## 🎨 Customize Your Style

Edit `config/project-settings.json`:

### For Dark Thriller:
```json
{
  "genre": "Thriller",
  "tone": "Dark",
  "visual_style": "High contrast, noir",
  "audio_philosophy": {
    "silence_usage": "strategic",
    "music_presence": "minimal"
  }
}
```

### For Bright Comedy:
```json
{
  "genre": "Comedy",  
  "tone": "Light",
  "visual_style": "Bright, colorful",
  "audio_philosophy": {
    "silence_usage": "rare",
    "music_presence": "upbeat"
  }
}
```

## 📊 Monitor Progress

Open the Web UI to see real-time processing:

```bash
# In a new terminal:
claude-flow start --ui
```

Then visit: `http://localhost:3000/console`

## 🔥 Pro Tips

### Batch Processing
Put multiple scripts in `scripts/` folder:
```
scripts/
├── scene-01.txt
├── scene-02.txt
└── scene-03.txt
```
Run once to process all!

### Quick Test
Use the included test scene:
```bash
# Already created during installation
scripts/test-scene.txt
```

### Version Control
Before major edits:
```bash
edit-mode.bat
> Option 3 (Create restore point)
> Name: "before-camera-changes"
```

### Genre Templates
Switch genres quickly:
```bash
# Edit config/project-settings.json
# Change "genre": "Horror"
# Reprocess for horror-style output!
```

## ❓ Common Questions

**Q: How long does processing take?**
A: 30-60 seconds for a typical scene (5-10 shots)

**Q: Can I process feature-length scripts?**
A: Yes! The system handles any length, processing in parallel

**Q: What video AI tools work with this?**
A: Optimized for Google Veo 3, but works with Runway, Pika, Stability AI

**Q: Can I add my own agents?**
A: Yes! See [Creating Custom Agents](AGENTS.md#creating-custom-agents)

## 🚨 Quick Troubleshooting

### "Command not found"
```bash
# Reinstall dependencies
npm install -g @anthropic-ai/claude-code
npm install -g claude-flow@latest
```

### "No agents found"
```bash
# Copy agents manually
cp templates/agents/*.md .claude/agents/
```

### "Processing stuck"
```bash
# Restart the system
Ctrl+C
claude-flow start --ui
```

## 🎉 Next Steps

1. 📚 Read [Full Documentation](README.md)
2. 🤖 Explore [Agent Capabilities](AGENTS.md)
3. 🎬 Learn [Film Production Tips](FILM-PRODUCTION.md)
4. 🤝 [Contribute](../CONTRIBUTING.md) to the project!

---

**Need help?** Join our [Discord](https://discord.gg/filmcrewai) or open an [issue](https://github.com/yourusername/film-crew-ai/issues)!

Happy filming! 🎬✨