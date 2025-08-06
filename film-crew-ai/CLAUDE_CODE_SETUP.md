
# Claude Code Integration Instructions for Film Crew AI

## Prerequisites
1. Install Claude Code CLI:
   ```bash
   npm install -g @anthropic/claude-code
   ```

2. Authenticate with Claude Code:
   ```bash
   claude-code auth login
   ```

## Setup Film Crew AI with Claude Code

1. Navigate to your project:
   ```bash
   cd film-crew-ai
   ```

2. Initialize Claude Code project:
   ```bash
   claude-code init --project "Film Crew AI"
   ```

3. Install Film Crew agents:
   ```bash
   python claude_code_integration.py --setup
   ```

## Using Sub-Agents

### Automatic Workflow
Process a screenplay with all agents:
```bash
claude-code run workflow --input scripts/your_script.txt
```

### Manual Agent Invocation
Invoke specific agents:
```bash
# Script analysis
claude-code agent run script-breakdown --file scripts/your_script.txt

# Character analysis
claude-code agent run character-analysis --file scripts/your_script.txt

# Full production pipeline
claude-code agent run-all --workflow production
```

## Agent Commands in Claude Code

When using Claude Code interactively, you can invoke agents:

```
/agent script-breakdown analyze this screenplay
/agent character-analysis track character Sarah
/agent camera-director plan shots for scene 5
/agent prompt-synthesis combine all analyses
```

## Workflow Stages

The Film Crew AI workflow runs in 3 stages:

1. **Analysis Stage** (Parallel)
   - Script Breakdown Agent
   - Character Analysis Agent
   - Environment & Props Agent

2. **Production Stage** (Parallel)
   - Camera Director Agent
   - Lighting Designer Agent
   - Sound Designer Agent
   - Music Director Agent

3. **Synthesis Stage**
   - Prompt Synthesis Agent

## Output Structure

```
output/
├── [timestamp]_claude_code/
│   ├── analysis/
│   │   ├── script_breakdown.json
│   │   ├── characters.json
│   │   └── environments.json
│   ├── production/
│   │   ├── camera_plans.json
│   │   ├── lighting_design.json
│   │   ├── sound_design.json
│   │   └── music_cues.json
│   └── synthesis/
│       ├── veo3_prompts/
│       └── scene_summaries/
```

## Best Practices

1. **Context Preservation**: Each agent maintains its own context
2. **Parallel Processing**: Analysis and Production stages run in parallel
3. **Error Recovery**: Failed agents automatically retry
4. **Incremental Updates**: Modify single scenes without full reprocessing

## Troubleshooting

- **Agent not found**: Run `claude-code agent list` to see available agents
- **Workflow fails**: Check `claude-code logs` for detailed error messages
- **Permission denied**: Ensure Claude Code has file access permissions

## Integration with IDEs

### VS Code
Install the Claude Code extension and use the command palette:
- `Claude Code: Run Workflow`
- `Claude Code: Invoke Agent`

### Command Line
Use the CLI for batch processing:
```bash
for script in scripts/*.txt; do
    claude-code run workflow --input "$script"
done
```
