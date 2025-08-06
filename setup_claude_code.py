#!/usr/bin/env python3
"""
Setup Claude Code Integration for Film Crew AI
Configures the 8 film production agents as Claude Code sub-agents
"""

import sys
import json
import subprocess
from pathlib import Path

# Add film-crew-ai to path
sys.path.append(str(Path(__file__).parent / 'film-crew-ai'))

from claude_code_integration import ClaudeCodeAgentSystem, setup_claude_code_integration

def check_claude_code_installed():
    """Check if Claude Code CLI is installed"""
    try:
        result = subprocess.run(['claude-code', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ Claude Code is installed: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass
    
    print("✗ Claude Code CLI not found")
    print("\nTo install Claude Code:")
    print("1. Install Node.js from https://nodejs.org")
    print("2. Run: npm install -g @anthropic/claude-code")
    print("3. Authenticate: claude-code auth login")
    return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("    Film Crew AI - Claude Code Integration Setup")
    print("=" * 60)
    print()
    
    # Check Claude Code installation
    claude_code_available = check_claude_code_installed()
    
    # Setup Film Crew AI integration
    print("\nSetting up Film Crew AI agents...")
    
    # Navigate to film-crew-ai directory
    film_crew_dir = Path(__file__).parent / 'film-crew-ai'
    if film_crew_dir.exists():
        import os
        os.chdir(film_crew_dir)
    
    # Run setup
    if setup_claude_code_integration():
        print("\n" + "=" * 60)
        print("✓ Setup Complete!")
        print("=" * 60)
        
        print("\n📋 Next Steps:")
        
        if not claude_code_available:
            print("\n1. Install Claude Code CLI:")
            print("   npm install -g @anthropic/claude-code")
            print("\n2. Authenticate:")
            print("   claude-code auth login")
            print("\n3. Initialize project:")
            print("   claude-code init")
        else:
            print("\n1. Initialize Claude Code in this project:")
            print("   claude-code init")
            print("\n2. List available agents:")
            print("   claude-code agent list")
        
        print("\n📖 Usage Examples:")
        print("\nProcess screenplay with Claude Code agents:")
        print("   claude-code run workflow --input scripts/your_script.txt")
        
        print("\nInvoke specific agent:")
        print("   claude-code agent run script-breakdown --file scripts/your_script.txt")
        
        print("\nUse in Claude Code chat:")
        print("   /agent camera-director plan shots for scene 5")
        
        print("\n🎬 The 8 Film Production Agents:")
        agents = [
            "script-breakdown - Analyzes screenplay structure",
            "character-analysis - Tracks characters and arcs",
            "environment-props - Identifies locations and props",
            "camera-director - Plans shots and movements",
            "lighting-designer - Creates lighting moods",
            "sound-designer - Designs soundscapes",
            "music-director - Plans musical themes",
            "prompt-synthesis - Combines into Veo3 prompts"
        ]
        for agent in agents:
            print(f"   • {agent}")
        
        print("\n📁 Configuration files created:")
        print("   • .claude/agents/ - Individual agent configs")
        print("   • .claude/config.json - Main configuration")
        print("   • .claude/workflow.json - Workflow definition")
        print("   • CLAUDE_CODE_SETUP.md - Detailed instructions")
        
        print("\n✨ Ready to use Film Crew AI with Claude Code!")
        
    else:
        print("\n✗ Setup failed. Please check the error messages above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())