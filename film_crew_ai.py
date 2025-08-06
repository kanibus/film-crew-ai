#!/usr/bin/env python3
"""
Film Crew AI - Robust Production System
A professional-grade script processing system with AI agent orchestration
"""

import os
import sys
import json
import re
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import subprocess
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FilmCrewAI')


@dataclass
class Shot:
    """Represents a single shot in the script"""
    shot_id: str
    scene_number: int
    shot_number: int
    scene_heading: str
    action: str
    dialogue: List[str]
    shot_type: str = "MEDIUM"
    duration: str = "3-5 seconds"
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Scene:
    """Represents a scene in the script"""
    scene_number: int
    heading: str
    location: str
    time_of_day: str
    action_blocks: List[str]
    dialogue_blocks: List[Dict]
    shots: List[Shot]
    
    def to_dict(self) -> Dict:
        return {
            'scene_number': self.scene_number,
            'heading': self.heading,
            'location': self.location,
            'time_of_day': self.time_of_day,
            'shots': [shot.to_dict() for shot in self.shots]
        }


class ScriptParser:
    """Parses screenplay format into structured data"""
    
    def __init__(self):
        self.scene_pattern = re.compile(r'^(INT\.|EXT\.|INT/EXT\.)\s+(.+?)\s*[-–]\s*(.+)$', re.MULTILINE)
        self.character_pattern = re.compile(r'^[A-Z][A-Z\s]+(\([^)]+\))?$')
        self.parenthetical_pattern = re.compile(r'^\([^)]+\)$')
        
    def parse(self, script_path: Path) -> List[Scene]:
        """Parse script file into scenes"""
        logger.info(f"Parsing script: {script_path}")
        
        with open(script_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        scenes = []
        scene_matches = list(self.scene_pattern.finditer(content))
        
        if not scene_matches:
            # If no scene headings found, treat entire script as one scene
            logger.warning("No scene headings found, treating as single scene")
            scene = self._create_default_scene(content)
            scenes.append(scene)
        else:
            for i, match in enumerate(scene_matches):
                scene_start = match.start()
                scene_end = scene_matches[i + 1].start() if i + 1 < len(scene_matches) else len(content)
                scene_text = content[scene_start:scene_end]
                
                scene = self._parse_scene(i + 1, scene_text)
                scenes.append(scene)
        
        return scenes
    
    def _parse_scene(self, scene_number: int, scene_text: str) -> Scene:
        """Parse individual scene"""
        lines = scene_text.strip().split('\n')
        
        # Parse scene heading
        heading_match = self.scene_pattern.match(lines[0])
        if heading_match:
            int_ext = heading_match.group(1)
            location = heading_match.group(2)
            time_of_day = heading_match.group(3)
        else:
            int_ext = "INT."
            location = "UNKNOWN"
            time_of_day = "DAY"
        
        heading = f"{int_ext} {location} - {time_of_day}"
        
        # Parse action and dialogue
        action_blocks = []
        dialogue_blocks = []
        current_block = []
        
        for line in lines[1:]:
            line = line.strip()
            if not line:
                if current_block:
                    action_blocks.append(' '.join(current_block))
                    current_block = []
            elif self.character_pattern.match(line):
                # Start of dialogue
                if current_block:
                    action_blocks.append(' '.join(current_block))
                    current_block = []
                dialogue_blocks.append({'character': line, 'lines': []})
            elif dialogue_blocks and not self.parenthetical_pattern.match(line):
                dialogue_blocks[-1]['lines'].append(line)
            else:
                current_block.append(line)
        
        if current_block:
            action_blocks.append(' '.join(current_block))
        
        # Generate shots based on content
        shots = self._generate_shots(scene_number, heading, action_blocks, dialogue_blocks)
        
        return Scene(
            scene_number=scene_number,
            heading=heading,
            location=location,
            time_of_day=time_of_day,
            action_blocks=action_blocks,
            dialogue_blocks=dialogue_blocks,
            shots=shots
        )
    
    def _create_default_scene(self, content: str) -> Scene:
        """Create a default scene when no headings found"""
        # Simple heuristic: look for FADE IN/OUT
        location = "LOCATION"
        time_of_day = "DAY"
        
        if "INT." in content.upper():
            location = "INTERIOR"
        elif "EXT." in content.upper():
            location = "EXTERIOR"
        
        if "NIGHT" in content.upper():
            time_of_day = "NIGHT"
        elif "MORNING" in content.upper():
            time_of_day = "MORNING"
        
        return Scene(
            scene_number=1,
            heading=f"INT. {location} - {time_of_day}",
            location=location,
            time_of_day=time_of_day,
            action_blocks=[content],
            dialogue_blocks=[],
            shots=self._generate_shots(1, f"INT. {location} - {time_of_day}", [content], [])
        )
    
    def _generate_shots(self, scene_number: int, heading: str, 
                       action_blocks: List[str], dialogue_blocks: List[Dict]) -> List[Shot]:
        """Generate shots based on scene content"""
        shots = []
        
        # Always start with establishing shot
        shots.append(Shot(
            shot_id=f"{scene_number}-1",
            scene_number=scene_number,
            shot_number=1,
            scene_heading=heading,
            action=' '.join(action_blocks[:1]) if action_blocks else "",
            dialogue=[],
            shot_type="WIDE ESTABLISHING",
            duration="5-8 seconds"
        ))
        
        # Add coverage shots based on content
        if len(action_blocks) > 1 or dialogue_blocks:
            shots.append(Shot(
                shot_id=f"{scene_number}-2",
                scene_number=scene_number,
                shot_number=2,
                scene_heading=heading,
                action=' '.join(action_blocks[1:2]) if len(action_blocks) > 1 else "",
                dialogue=[d['character'] for d in dialogue_blocks[:2]],
                shot_type="MEDIUM",
                duration="3-5 seconds"
            ))
        
        # Add close-ups for dialogue
        if len(dialogue_blocks) > 2:
            shots.append(Shot(
                shot_id=f"{scene_number}-3",
                scene_number=scene_number,
                shot_number=3,
                scene_heading=heading,
                action="",
                dialogue=[d['character'] for d in dialogue_blocks[2:]],
                shot_type="CLOSE-UP",
                duration="2-4 seconds"
            ))
        
        return shots


class AgentOrchestrator:
    """Orchestrates AI agent processing"""
    
    def __init__(self, agents_dir: Path):
        self.agents_dir = agents_dir
        self.agents = self._load_agents()
        
    def _load_agents(self) -> Dict[str, Dict]:
        """Load agent configurations"""
        agents = {}
        for agent_file in self.agents_dir.glob("*.md"):
            agent_name = agent_file.stem
            with open(agent_file, 'r', encoding='utf-8') as f:
                content = f.read()
            agents[agent_name] = {
                'name': agent_name,
                'content': content,
                'file': str(agent_file)
            }
        logger.info(f"Loaded {len(agents)} agents")
        return agents
    
    def process_with_agent(self, agent_name: str, scene: Scene, shot: Shot) -> Dict:
        """Process shot with specific agent"""
        if agent_name not in self.agents:
            logger.warning(f"Agent {agent_name} not found")
            return {}
        
        # In production, this would call actual AI
        # For now, return structured output based on agent type
        return self._generate_agent_output(agent_name, scene, shot)
    
    def _generate_agent_output(self, agent_name: str, scene: Scene, shot: Shot) -> Dict:
        """Generate agent-specific output"""
        
        if agent_name == "script-breakdown":
            return {
                "analysis": {
                    "genre": "Drama",
                    "tone": "Intimate",
                    "pacing": "Measured",
                    "emotional_arc": "Discovery to tension"
                },
                "shot_breakdown": {
                    "shot_id": shot.shot_id,
                    "necessity": "essential",
                    "dramatic_purpose": "Establish character state and environment"
                }
            }
        
        elif agent_name == "camera-director":
            return {
                "shot_id": shot.shot_id,
                "camera": {
                    "shot_size": shot.shot_type,
                    "angle": "Eye level" if "ESTABLISHING" in shot.shot_type else "Slight low angle",
                    "movement": "Slow push in" if "ESTABLISHING" in shot.shot_type else "Static or subtle drift",
                    "lens": "24mm" if "WIDE" in shot.shot_type else "50mm"
                },
                "visual_purpose": {
                    "literal": "Show character and environment",
                    "poetic": "Isolation within crowd",
                    "emotional": "Anticipation and searching"
                }
            }
        
        elif agent_name == "lighting-designer":
            return {
                "shot_id": shot.shot_id,
                "lighting_design": {
                    "emotional_goal": "Natural realism with subtle mood",
                    "key_light": "Window light - soft, directional",
                    "fill_ratio": "2:1 for gentle contrast",
                    "practicals": ["Overhead fixtures", "Window light"],
                    "color": "5600K daylight mixed with 3200K practicals"
                }
            }
        
        elif agent_name == "sound-designer":
            return {
                "shot_id": shot.shot_id,
                "soundscape": {
                    "on_screen": ["Footsteps", "Breathing", "Clothing rustle"],
                    "off_screen": ["Traffic", "Distant conversations"],
                    "ambience": ["Room tone", "HVAC hum"],
                    "spot_effects": ["Door close", "Chair scrape"]
                },
                "perspective": "Objective transitioning to subjective"
            }
        
        elif agent_name == "music-director":
            return {
                "shot_id": shot.shot_id,
                "music_decision": {
                    "presence": "silence",
                    "reasoning": "Let environment and tension speak"
                },
                "if_silence": {
                    "type": "complete",
                    "duration": "entire shot",
                    "break": "none"
                }
            }
        
        elif agent_name == "character-analysis":
            return {
                "shot_id": shot.shot_id,
                "characters": self._extract_characters(shot),
                "emotional_state": "Searching, tired, anticipatory",
                "physical_markers": "Shoulders tense, scanning motion"
            }
        
        elif agent_name == "background-designer":
            return {
                "shot_id": shot.shot_id,
                "environment": {
                    "location": scene.location,
                    "atmosphere": "Lived-in, authentic",
                    "time_markers": scene.time_of_day,
                    "weather": "Clear" if scene.time_of_day == "DAY" else "Overcast"
                },
                "design_layers": {
                    "foreground": ["Tables", "Characters"],
                    "midground": ["Other patrons", "Counter"],
                    "background": ["Windows", "Street view"],
                    "movement": ["Steam", "People passing"]
                }
            }
        
        else:  # prompt-combiner
            return {
                "shot_id": shot.shot_id,
                "veo3_prompt": self._generate_veo3_prompt(scene, shot),
                "necessity_verdict": "essential",
                "technical_summary": {
                    "camera": shot.shot_type,
                    "lighting": "Natural/motivated",
                    "audio": "Diegetic focus"
                }
            }
    
    def _extract_characters(self, shot: Shot) -> List[str]:
        """Extract character names from shot"""
        characters = []
        for dialogue in shot.dialogue:
            # Extract character name (remove parentheticals)
            char_name = dialogue.split('(')[0].strip()
            if char_name and char_name not in characters:
                characters.append(char_name)
        return characters if characters else ["SUBJECT"]
    
    def _generate_veo3_prompt(self, scene: Scene, shot: Shot) -> str:
        """Generate comprehensive Veo3 prompt"""
        prompt_parts = []
        
        # Camera
        camera_desc = {
            "WIDE ESTABLISHING": "Wide establishing shot, slow push-in, subtle handheld movement for organic feel",
            "MEDIUM": "Medium shot, minimal movement, slight drift for life",
            "CLOSE-UP": "Close-up, locked off or minimal float, intimate framing"
        }.get(shot.shot_type, "Medium shot with motivated movement")
        prompt_parts.append(f"[CAMERA] {camera_desc}")
        
        # Subject
        if shot.dialogue:
            subject = f"Characters: {', '.join(shot.dialogue[:2])}, in conversation"
        elif shot.action:
            subject = shot.action[:100]
        else:
            subject = "Environmental shot"
        prompt_parts.append(f"[SUBJECT] {subject}")
        
        # Environment
        env = f"{scene.location}, {scene.time_of_day} lighting"
        prompt_parts.append(f"[ENVIRONMENT] {env}, lived-in details, atmospheric depth")
        
        # Lighting
        lighting = "Natural daylight" if "DAY" in scene.time_of_day else "Practical sources, moody"
        prompt_parts.append(f"[LIGHTING] {lighting}, motivated sources, cinematic contrast")
        
        # Music
        prompt_parts.append("[MUSIC] No score, environmental sound only")
        
        # Sound
        prompt_parts.append("[SOUND] Layered ambience, specific spot effects, off-screen world")
        
        return "... ".join(prompt_parts) + "..."


class FilmCrewProcessor:
    """Main processing engine for Film Crew AI"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.agents_dir = project_dir / "templates" / "agents"
        self.output_dir = project_dir / "output"
        self.scripts_dir = project_dir / "scripts"
        
        self.parser = ScriptParser()
        self.orchestrator = AgentOrchestrator(self.agents_dir)
        
        # Create directories if they don't exist
        self.output_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
    
    def process_script(self, script_path: Path) -> Path:
        """Process a single script file"""
        logger.info(f"Processing script: {script_path.name}")
        
        # Parse script
        scenes = self.parser.parse(script_path)
        logger.info(f"Parsed {len(scenes)} scenes")
        
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        output_name = f"{script_path.stem}_{timestamp}"
        script_output_dir = self.output_dir / output_name
        
        # Create department subdirectories
        departments = [
            "01_veo3_prompts",
            "02_music_cues", 
            "03_sound_design",
            "04_continuity",
            "05_lighting",
            "06_camera",
            "07_characters",
            "08_environments"
        ]
        
        for dept in departments:
            (script_output_dir / dept).mkdir(parents=True, exist_ok=True)
        
        # Process each scene and shot
        all_outputs = []
        for scene in scenes:
            for shot in scene.shots:
                shot_outputs = self._process_shot(scene, shot, script_output_dir)
                all_outputs.append(shot_outputs)
        
        # Create master index
        self._create_index(script_output_dir, script_path.name, scenes, all_outputs)
        
        logger.info(f"Processing complete. Output: {script_output_dir}")
        return script_output_dir
    
    def _process_shot(self, scene: Scene, shot: Shot, output_dir: Path) -> Dict:
        """Process individual shot through all agents"""
        logger.info(f"Processing shot {shot.shot_id}")
        
        outputs = {}
        
        # Process through each agent
        for agent_name in ["script-breakdown", "camera-director", "lighting-designer",
                          "sound-designer", "music-director", "character-analysis",
                          "background-designer", "prompt-combiner"]:
            
            agent_output = self.orchestrator.process_with_agent(agent_name, scene, shot)
            outputs[agent_name] = agent_output
        
        # Save outputs to appropriate directories
        self._save_shot_outputs(shot, outputs, output_dir)
        
        return outputs
    
    def _save_shot_outputs(self, shot: Shot, outputs: Dict, output_dir: Path):
        """Save shot outputs to files"""
        
        # Veo3 prompt
        if "prompt-combiner" in outputs:
            prompt_file = output_dir / "01_veo3_prompts" / f"shot_{shot.shot_id.replace('-', '_')}.json"
            with open(prompt_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "shot_id": shot.shot_id,
                    "shot_type": shot.shot_type,
                    "duration": shot.duration,
                    **outputs["prompt-combiner"]
                }, f, indent=2)
        
        # Camera setup
        if "camera-director" in outputs:
            camera_file = output_dir / "06_camera" / f"shot_{shot.shot_id.replace('-', '_')}_camera.json"
            with open(camera_file, 'w', encoding='utf-8') as f:
                json.dump(outputs["camera-director"], f, indent=2)
        
        # Lighting
        if "lighting-designer" in outputs:
            lighting_file = output_dir / "05_lighting" / f"shot_{shot.shot_id.replace('-', '_')}_lighting.json"
            with open(lighting_file, 'w', encoding='utf-8') as f:
                json.dump(outputs["lighting-designer"], f, indent=2)
        
        # Sound design
        if "sound-designer" in outputs:
            sound_file = output_dir / "03_sound_design" / f"scene_{shot.scene_number}_sound.json"
            with open(sound_file, 'w', encoding='utf-8') as f:
                json.dump(outputs["sound-designer"], f, indent=2)
        
        # Music
        if "music-director" in outputs:
            music_file = output_dir / "02_music_cues" / f"scene_{shot.scene_number}_music.json"
            with open(music_file, 'w', encoding='utf-8') as f:
                json.dump(outputs["music-director"], f, indent=2)
    
    def _create_index(self, output_dir: Path, script_name: str, 
                     scenes: List[Scene], all_outputs: List[Dict]):
        """Create master index file"""
        index = {
            "project": script_name,
            "generated": datetime.now().isoformat(),
            "version": "3.0",
            "engine": "Python-based Film Crew AI",
            "structure": {
                "total_scenes": len(scenes),
                "total_shots": sum(len(scene.shots) for scene in scenes),
                "departments": 8
            },
            "scenes": [scene.to_dict() for scene in scenes],
            "output_directories": {
                "01_veo3_prompts": "Video generation prompts",
                "02_music_cues": "Music timing and direction",
                "03_sound_design": "Sound layers and ambience",
                "04_continuity": "Continuity tracking",
                "05_lighting": "Lighting setups",
                "06_camera": "Camera coverage",
                "07_characters": "Character details",
                "08_environments": "Location details"
            }
        }
        
        index_file = output_dir / "INDEX.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
    
    def process_all_scripts(self):
        """Process all scripts in the scripts directory"""
        script_files = list(self.scripts_dir.glob("*.txt"))
        
        if not script_files:
            logger.warning("No script files found in scripts directory")
            return
        
        logger.info(f"Found {len(script_files)} scripts to process")
        
        for script_file in script_files:
            try:
                self.process_script(script_file)
            except Exception as e:
                logger.error(f"Error processing {script_file}: {e}")
                continue


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Film Crew AI - Script Processing System")
    parser.add_argument('--script', type=str, help='Path to specific script to process')
    parser.add_argument('--all', action='store_true', help='Process all scripts in scripts folder')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Create processor
    processor = FilmCrewProcessor(project_dir)
    
    if args.script:
        script_path = Path(args.script)
        if script_path.exists():
            processor.process_script(script_path)
        else:
            logger.error(f"Script not found: {script_path}")
    elif args.all:
        processor.process_all_scripts()
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("FILM CREW AI - Professional Script Processing System")
        print("="*60)
        print("\nOptions:")
        print("1. Process all scripts in scripts/ folder")
        print("2. Process specific script")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            processor.process_all_scripts()
        elif choice == "2":
            script_name = input("Enter script filename (in scripts/ folder): ").strip()
            script_path = project_dir / "scripts" / script_name
            if script_path.exists():
                processor.process_script(script_path)
            else:
                logger.error(f"Script not found: {script_path}")
        else:
            print("Exiting...")


if __name__ == "__main__":
    main()