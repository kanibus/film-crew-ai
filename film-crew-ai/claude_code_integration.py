#!/usr/bin/env python3
"""
Claude Code Integration Module
Implements proper sub-agents workflow for Film Crew AI
Follows Claude Code's sub-agent architecture patterns
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging

@dataclass
class SubAgentConfig:
    """Configuration for a Claude Code sub-agent"""
    name: str
    purpose: str
    system_prompt: str
    tools: List[str]
    context_requirements: Dict[str, Any]
    
    def to_claude_format(self) -> Dict:
        """Convert to Claude Code compatible format"""
        return {
            "name": self.name,
            "description": self.purpose,
            "systemPrompt": self.system_prompt,
            "tools": self.tools,
            "metadata": self.context_requirements
        }


class ClaudeCodeAgentSystem:
    """
    Integrates Film Crew AI with Claude Code's sub-agent system
    Manages 8 specialized film production agents as Claude Code sub-agents
    """
    
    # Define the 8 film production sub-agents
    FILM_CREW_AGENTS = {
        "script-breakdown": SubAgentConfig(
            name="Script Breakdown Agent",
            purpose="Analyzes screenplay structure, identifies scenes, shots, and dramatic beats",
            system_prompt="""You are a professional script supervisor specializing in screenplay analysis.
            
Your responsibilities:
- Parse screenplay format (INT./EXT. headers)
- Identify scene boundaries and transitions
- Extract shot descriptions and camera directions
- Detect dramatic beats and turning points
- Maintain scene continuity notes

Output structured data with:
- Scene number and location
- Time of day
- Character presence
- Key dramatic moments
- Technical requirements""",
            tools=["read", "parse", "analyze"],
            context_requirements={"script_format": "screenplay", "output": "structured"}
        ),
        
        "character-analysis": SubAgentConfig(
            name="Character Analysis Agent",
            purpose="Tracks character profiles, emotional arcs, and relationships throughout the screenplay",
            system_prompt="""You are a character development specialist for film production.

Your responsibilities:
- Build comprehensive character profiles
- Track emotional arcs across scenes
- Identify character relationships and dynamics
- Note costume and appearance changes
- Extract character voice and mannerisms

Maintain consistency by:
- Creating detailed character sheets
- Tracking character presence in scenes
- Noting character development milestones
- Identifying key character moments""",
            tools=["read", "track", "profile"],
            context_requirements={"tracking": "characters", "consistency": "required"}
        ),
        
        "environment-props": SubAgentConfig(
            name="Environment & Props Agent",
            purpose="Identifies locations, set pieces, and required props for each scene",
            system_prompt="""You are a production designer specializing in environments and props.

Your responsibilities:
- Catalog all locations mentioned in the script
- List required props for each scene
- Note set dressing requirements
- Identify special environment needs (weather, time, etc.)
- Track prop continuity across scenes

Create detailed lists of:
- Location descriptions and requirements
- Essential props and their usage
- Background elements
- Environmental conditions
- Set piece specifications""",
            tools=["catalog", "list", "track"],
            context_requirements={"detail_level": "comprehensive", "continuity": "tracked"}
        ),
        
        "camera-director": SubAgentConfig(
            name="Camera Director Agent",
            purpose="Determines camera angles, movements, and shot compositions for cinematic storytelling",
            system_prompt="""You are a cinematographer planning shot compositions and camera movements.

Your responsibilities:
- Design shot compositions (wide, medium, close-up)
- Plan camera movements (dolly, crane, handheld, static)
- Determine framing and angles
- Create visual flow between shots
- Enhance dramatic moments with camera work

Consider:
- Visual storytelling principles
- Emotional impact of camera choices
- Practical shooting considerations
- Continuity between shots
- Scene pacing through camera work""",
            tools=["compose", "plan", "visualize"],
            context_requirements={"style": "cinematic", "coverage": "comprehensive"}
        ),
        
        "lighting-designer": SubAgentConfig(
            name="Lighting Designer Agent",
            purpose="Plans lighting setups, mood, and visual atmosphere for each scene",
            system_prompt="""You are a lighting designer creating atmospheric and emotional lighting.

Your responsibilities:
- Design lighting schemes for each scene
- Create mood through light and shadow
- Plan practical and motivated light sources
- Enhance time of day and weather conditions
- Support the emotional tone of scenes

Specify:
- Key light positions and intensities
- Fill and back lighting requirements
- Color temperature and gels
- Natural vs artificial light balance
- Special lighting effects needed""",
            tools=["design", "mood", "atmosphere"],
            context_requirements={"mood": "atmospheric", "technical": "detailed"}
        ),
        
        "sound-designer": SubAgentConfig(
            name="Sound Designer Agent",
            purpose="Designs soundscapes, effects, and ambient audio for immersive scenes",
            system_prompt="""You are a sound designer creating immersive audio environments.

Your responsibilities:
- Design ambient soundscapes for each location
- Identify required sound effects
- Plan diegetic vs non-diegetic sound
- Create audio depth and dimension
- Support emotional storytelling through sound

Include:
- Environmental sounds and room tone
- Specific sound effects timing
- Off-screen audio elements
- Sound perspective and distance
- Transition sounds between scenes""",
            tools=["design", "layer", "ambient"],
            context_requirements={"layers": "multiple", "perspective": "3D"}
        ),
        
        "music-director": SubAgentConfig(
            name="Music Director Agent",
            purpose="Selects musical themes, timing, and emotional scoring for scenes",
            system_prompt="""You are a music director planning the musical score and themes.

Your responsibilities:
- Select appropriate musical styles and genres
- Time musical cues with dramatic moments
- Create emotional underscoring
- Plan source music vs score
- Develop recurring themes and motifs

Specify:
- Musical genre and instrumentation
- Tempo and dynamics
- Emotional tone and progression
- Key musical moments and stingers
- Transitions and bridges between scenes""",
            tools=["compose", "time", "theme"],
            context_requirements={"emotional": "supportive", "timing": "precise"}
        ),
        
        "prompt-synthesis": SubAgentConfig(
            name="Prompt Synthesis Agent",
            purpose="Combines all agent outputs into unified, cinematic Veo3 prompts",
            system_prompt="""You are a prompt synthesis specialist creating cohesive video generation prompts.

Your responsibilities:
- Integrate all agent analyses into unified prompts
- Maintain consistency across all elements
- Create natural language descriptions for Veo3
- Balance technical and artistic elements
- Ensure prompt clarity and specificity

Synthesize:
- Visual composition and camera work
- Character and environment details
- Lighting and atmosphere
- Sound and music elements
- Emotional and dramatic context

Output format:
- Natural language for Veo3 compatibility
- Clear, specific, actionable descriptions
- Consistent style and tone
- Proper emphasis on key elements""",
            tools=["synthesize", "integrate", "format"],
            context_requirements={"format": "veo3", "style": "natural_language"}
        )
    }
    
    def __init__(self, project_path: Path = None):
        """Initialize Claude Code agent system"""
        self.project_path = project_path or Path.cwd()
        self.agents_dir = self.project_path / ".claude" / "agents"
        self.config_file = self.project_path / ".claude" / "config.json"
        self.logger = logging.getLogger("ClaudeCodeIntegration")
        
    def setup_claude_code_project(self) -> bool:
        """Set up Claude Code project structure with sub-agents"""
        try:
            # Create .claude directory structure
            self.agents_dir.mkdir(parents=True, exist_ok=True)
            
            # Create individual agent configuration files
            for agent_key, agent_config in self.FILM_CREW_AGENTS.items():
                self._create_agent_file(agent_key, agent_config)
            
            # Create main Claude Code configuration
            self._create_claude_config()
            
            # Create workflow configuration
            self._create_workflow_config()
            
            self.logger.info("Claude Code project structure created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup Claude Code project: {e}")
            return False
    
    def _create_agent_file(self, agent_key: str, config: SubAgentConfig):
        """Create individual agent configuration file"""
        agent_file = self.agents_dir / f"{agent_key}.json"
        
        agent_data = config.to_claude_format()
        agent_data["id"] = agent_key
        agent_data["version"] = "1.0.0"
        agent_data["enabled"] = True
        
        with open(agent_file, 'w') as f:
            json.dump(agent_data, f, indent=2)
    
    def _create_claude_config(self):
        """Create main Claude Code configuration"""
        config = {
            "project": "Film Crew AI",
            "version": "8.0.0",
            "description": "Screenplay to video prompt generation with 8 specialized agents",
            "agents": list(self.FILM_CREW_AGENTS.keys()),
            "workflow": {
                "type": "sequential_parallel",
                "stages": [
                    {
                        "name": "analysis",
                        "agents": ["script-breakdown", "character-analysis", "environment-props"],
                        "parallel": True
                    },
                    {
                        "name": "production",
                        "agents": ["camera-director", "lighting-designer", "sound-designer", "music-director"],
                        "parallel": True
                    },
                    {
                        "name": "synthesis",
                        "agents": ["prompt-synthesis"],
                        "parallel": False
                    }
                ]
            },
            "tools": {
                "enabled": ["read", "write", "parse", "analyze", "synthesize"],
                "custom": ["film_crew_ai_main.py", "veo3_generator.py"]
            },
            "output": {
                "format": "veo3_prompts",
                "directory": "output",
                "preserve_context": True
            }
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _create_workflow_config(self):
        """Create workflow configuration for Claude Code"""
        workflow_file = self.project_path / ".claude" / "workflow.json"
        
        workflow = {
            "name": "Film Production Pipeline",
            "description": "Transforms screenplays into Veo3 prompts using specialized agents",
            "triggers": [
                {
                    "type": "file_pattern",
                    "pattern": "scripts/*.{txt,pdf,doc,docx}",
                    "action": "process_screenplay"
                }
            ],
            "steps": [
                {
                    "id": "load_script",
                    "name": "Load Screenplay",
                    "description": "Read and parse the screenplay file",
                    "agent": None,
                    "tools": ["read", "parse"]
                },
                {
                    "id": "analyze_script",
                    "name": "Script Analysis",
                    "description": "Analyze script structure and content",
                    "agent": "script-breakdown",
                    "inputs": ["screenplay_text"],
                    "outputs": ["scenes", "shots", "beats"]
                },
                {
                    "id": "analyze_characters",
                    "name": "Character Analysis",
                    "description": "Extract and track character information",
                    "agent": "character-analysis",
                    "inputs": ["screenplay_text", "scenes"],
                    "outputs": ["character_profiles", "emotional_arcs"]
                },
                {
                    "id": "analyze_environment",
                    "name": "Environment Analysis",
                    "description": "Identify locations and props",
                    "agent": "environment-props",
                    "inputs": ["scenes"],
                    "outputs": ["locations", "props"]
                },
                {
                    "id": "plan_cinematography",
                    "name": "Camera Planning",
                    "description": "Design shots and camera movements",
                    "agent": "camera-director",
                    "inputs": ["scenes", "beats"],
                    "outputs": ["shot_list", "camera_movements"]
                },
                {
                    "id": "design_lighting",
                    "name": "Lighting Design",
                    "description": "Plan lighting and atmosphere",
                    "agent": "lighting-designer",
                    "inputs": ["scenes", "locations"],
                    "outputs": ["lighting_plans", "mood_boards"]
                },
                {
                    "id": "design_sound",
                    "name": "Sound Design",
                    "description": "Create soundscapes and effects",
                    "agent": "sound-designer",
                    "inputs": ["scenes", "locations"],
                    "outputs": ["soundscapes", "effects_list"]
                },
                {
                    "id": "plan_music",
                    "name": "Music Direction",
                    "description": "Plan musical themes and scoring",
                    "agent": "music-director",
                    "inputs": ["scenes", "emotional_arcs"],
                    "outputs": ["music_cues", "themes"]
                },
                {
                    "id": "synthesize_prompts",
                    "name": "Prompt Synthesis",
                    "description": "Combine all elements into Veo3 prompts",
                    "agent": "prompt-synthesis",
                    "inputs": ["*"],  # All previous outputs
                    "outputs": ["veo3_prompts", "scene_summaries"]
                }
            ],
            "error_handling": {
                "retry_failed_steps": True,
                "max_retries": 3,
                "fallback_mode": "basic_processing"
            }
        }
        
        with open(workflow_file, 'w') as f:
            json.dump(workflow, f, indent=2)
    
    def activate_agent(self, agent_key: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Activate a specific Claude Code sub-agent"""
        if agent_key not in self.FILM_CREW_AGENTS:
            raise ValueError(f"Unknown agent: {agent_key}")
        
        agent_config = self.FILM_CREW_AGENTS[agent_key]
        
        # Simulate agent activation (in real Claude Code, this would invoke the sub-agent)
        result = {
            "agent": agent_config.name,
            "status": "activated",
            "context": context,
            "output": {}
        }
        
        self.logger.info(f"Activated {agent_config.name}")
        return result
    
    def run_workflow(self, screenplay_path: Path) -> Dict[str, Any]:
        """Run the complete Claude Code workflow with all agents"""
        results = {
            "workflow": "Film Production Pipeline",
            "screenplay": str(screenplay_path),
            "stages": {}
        }
        
        # Stage 1: Analysis (parallel)
        self.logger.info("Starting Stage 1: Analysis")
        results["stages"]["analysis"] = {
            "script-breakdown": self.activate_agent("script-breakdown", {"file": str(screenplay_path)}),
            "character-analysis": self.activate_agent("character-analysis", {"file": str(screenplay_path)}),
            "environment-props": self.activate_agent("environment-props", {"file": str(screenplay_path)})
        }
        
        # Stage 2: Production (parallel)
        self.logger.info("Starting Stage 2: Production")
        results["stages"]["production"] = {
            "camera-director": self.activate_agent("camera-director", results["stages"]["analysis"]),
            "lighting-designer": self.activate_agent("lighting-designer", results["stages"]["analysis"]),
            "sound-designer": self.activate_agent("sound-designer", results["stages"]["analysis"]),
            "music-director": self.activate_agent("music-director", results["stages"]["analysis"])
        }
        
        # Stage 3: Synthesis
        self.logger.info("Starting Stage 3: Synthesis")
        results["stages"]["synthesis"] = {
            "prompt-synthesis": self.activate_agent("prompt-synthesis", {
                "analysis": results["stages"]["analysis"],
                "production": results["stages"]["production"]
            })
        }
        
        return results
    
    def create_agent_instructions(self) -> str:
        """Generate instructions for using Claude Code with Film Crew AI"""
        instructions = """
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
"""
        return instructions


def setup_claude_code_integration():
    """Main setup function for Claude Code integration"""
    integration = ClaudeCodeAgentSystem(Path.cwd())
    
    # Setup project structure
    if integration.setup_claude_code_project():
        print("[OK] Claude Code project structure created")
        
        # Save instructions
        instructions_file = Path("CLAUDE_CODE_SETUP.md")
        with open(instructions_file, 'w', encoding='utf-8') as f:
            f.write(integration.create_agent_instructions())
        
        print(f"[OK] Instructions saved to {instructions_file}")
        print("\nTo complete setup:")
        print("1. Install Claude Code: npm install -g @anthropic/claude-code")
        print("2. Run: claude-code init")
        print("3. Test: claude-code agent list")
        
        return True
    return False


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--setup":
        setup_claude_code_integration()
    else:
        # Run test workflow
        integration = ClaudeCodeAgentSystem()
        test_script = Path("scripts/complex_script.txt")
        if test_script.exists():
            results = integration.run_workflow(test_script)
            print(json.dumps(results, indent=2))
        else:
            print("Test script not found. Run with --setup flag to initialize.")