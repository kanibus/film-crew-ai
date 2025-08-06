#!/usr/bin/env python3
"""
Update GitHub Repository Script
Updates the existing film-crew-ai repository with new content
"""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd, capture=False):
    """Run a shell command"""
    print(f"Running: {cmd}")
    if capture:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    else:
        return subprocess.run(cmd, shell=True).returncode == 0

def main():
    """Main update process"""
    
    print("=" * 60)
    print("Film Crew AI - GitHub Repository Update")
    print("=" * 60)
    print("\nThis will update: https://github.com/kanibus/film-crew-ai")
    print("\nWARNING: This will replace old content with v8.0")
    
    response = input("\nContinue? (y/n): ")
    if response.lower() != 'y':
        print("Update cancelled")
        return
    
    print("\n1. Initializing git repository...")
    run_command("git init")
    
    print("\n2. Configuring remote...")
    run_command("git remote remove origin", capture=True)
    run_command("git remote add origin https://github.com/kanibus/film-crew-ai.git")
    
    print("\n3. Setting up branch...")
    # Try to fetch and checkout main
    run_command("git fetch origin", capture=True)
    
    # Check if we're on main branch
    current_branch = run_command("git branch --show-current", capture=True)
    if current_branch != "main":
        run_command("git checkout -b main", capture=True)
    
    print("\n4. Pulling existing history...")
    run_command("git pull origin main --allow-unrelated-histories --no-edit", capture=True)
    
    print("\n5. Staging all files...")
    run_command("git add -A")
    
    print("\n6. Creating commit...")
    commit_message = """Major Update v8.0: Complete rewrite with 8 AI agents, multi-platform support, and enhanced features

- Added 8 coordinated AI agents for film production
- Multi-platform export (Veo3, Runway, Pika, Stability, Haiper)
- Scene-level summaries and master overview
- Character consistency tracking
- Voice-over integration
- Support for PDF, DOC, DOCX formats
- Agent execution logging
- Comprehensive documentation and examples
- Complete project restructure
- Added batch processing
- Enhanced screenplay parsing
- Natural language prompt generation"""
    
    # Create commit
    run_command(f'git commit -m "{commit_message}"')
    
    print("\n7. Pushing to GitHub...")
    print("\nYou'll need to authenticate with GitHub.")
    print("Options:")
    print("  1. Use Personal Access Token")
    print("  2. Use GitHub CLI: gh auth login")
    print("  3. Use SSH if configured")
    print()
    
    # Try to push
    success = run_command("git push -u origin main --force-with-lease")
    
    if success:
        print("\n" + "=" * 60)
        print("SUCCESS! Repository updated")
        print("=" * 60)
        print("\nView your updated repository at:")
        print("https://github.com/kanibus/film-crew-ai")
        print("\nRecommended next steps:")
        print("1. Create a new release (v8.0)")
        print("2. Update repository description")
        print("3. Add topics: screenplay, video-generation, ai, veo3, runway")
    else:
        print("\n" + "=" * 60)
        print("PUSH FAILED - Manual steps needed:")
        print("=" * 60)
        print("\n1. Set up authentication:")
        print("   - Create Personal Access Token at GitHub")
        print("   - Or run: gh auth login")
        print("\n2. Then run:")
        print("   git push -u origin main --force-with-lease")

if __name__ == "__main__":
    main()