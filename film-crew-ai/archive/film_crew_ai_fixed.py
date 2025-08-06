#!/usr/bin/env python3
"""
Film Crew AI - Fixed Production System v4.1
Properly separates scenes/shots and coordinates agents
"""

import os
import sys
import json
import re
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import subprocess
from dataclasses import dataclass, asdict, field
import traceback
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FilmCrewAI')


# ============================================================================
# Import all data models from enhanced version
# ============================================================================

from film_crew_ai_enhanced import (
    Character, Environment, CameraSetup, LightingSetup,
    Shot, Scene, DocumentReader, BaseAgent
)


# ============================================================================
# FIXED ENHANCED SCRIPT PARSER
# ============================================================================

class FixedScriptParser:
    """Enhanced parser that properly identifies multiple scenes"""
    
    def __init__(self):
        self.scene_pattern = re.compile(
            r'^(INT\.|EXT\.|INT/EXT\.)\s+(.+?)\s*[-–]\s*(.+)$', 
            re.MULTILINE
        )
        self.character_pattern = re.compile(r'^[A-Z][A-Z\s]+(\([^)]+\))?$')
        self.parenthetical_pattern = re.compile(r'^\([^)]+\)$')
        
    def parse(self, script_path: Path) -> List[Scene]:
        """Parse script file into scenes with proper separation"""
        logger.info(f"Parsing script: {script_path}")
        
        # Read content using appropriate reader
        content = DocumentReader.read_file(script_path)
        
        scenes = []
        scene_matches = list(self.scene_pattern.finditer(content))
        
        logger.info(f"Found {len(scene_matches)} scene headings")
        
        if not scene_matches:
            logger.warning("No scene headings found, treating as single scene")
            scene = self._create_default_scene(content, 1)
            scenes.append(scene)
        else:
            for i, match in enumerate(scene_matches):
                scene_start = match.start()
                scene_end = scene_matches[i + 1].start() if i + 1 < len(scene_matches) else len(content)
                scene_text = content[scene_start:scene_end]
                
                scene = self._parse_scene(i + 1, scene_text)
                scenes.append(scene)
                logger.info(f"Parsed scene {scene.scene_number}: {scene.heading}")
        
        return scenes
    
    def _parse_scene(self, scene_number: int, scene_text: str) -> Scene:
        """Parse individual scene with enhanced detail extraction"""
        lines = scene_text.strip().split('\n')
        
        # Parse scene heading
        heading_match = self.scene_pattern.match(lines[0])
        if heading_match:
            int_ext = heading_match.group(1)
            location = heading_match.group(2).strip()
            time_of_day = heading_match.group(3).strip()
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
        
        # Generate scene number in proper format (1, 2, 3 or 1A, 1B for complex scenes)
        scene_num_str = str(scene_number)
        
        # Generate enhanced shots for this scene
        shots = self._generate_scene_shots(
            scene_num_str, heading, location, time_of_day,
            action_blocks, dialogue_blocks
        )
        
        return Scene(
            scene_number=scene_num_str,
            heading=heading,
            location=location,
            time_of_day=time_of_day,
            action_blocks=action_blocks,
            dialogue_blocks=dialogue_blocks,
            shots=shots
        )
    
    def _generate_scene_shots(self, scene_num: str, heading: str,
                             location: str, time_of_day: str,
                             action_blocks: List[str],
                             dialogue_blocks: List[Dict]) -> List[Shot]:
        """Generate all shots for a specific scene"""
        shots = []
        shot_num = 1
        
        # Create environment for the scene
        environment = Environment(
            location=location,
            time_of_day=time_of_day,
            setting_description=' '.join(action_blocks[:1]) if action_blocks else "",
            environmental_conditions=self._extract_conditions(heading)
        )
        
        # 1. Establishing shot (always first)
        shots.append(self._create_establishing_shot(
            scene_num, shot_num, heading, environment, action_blocks
        ))
        shot_num += 1
        
        # 2. Character/dialogue shots
        if dialogue_blocks:
            for i, dialogue in enumerate(dialogue_blocks[:5]):  # Limit to 5 main exchanges
                shots.append(self._create_dialogue_shot(
                    scene_num, shot_num, heading, environment, dialogue, i
                ))
                shot_num += 1
        
        # 3. Action shots
        if len(action_blocks) > 1:
            for i, action in enumerate(action_blocks[1:3]):  # Additional action shots
                shots.append(self._create_action_shot(
                    scene_num, shot_num, heading, environment, action
                ))
                shot_num += 1
        
        # 4. Closing shot if scene is complex
        if len(shots) > 3:
            shots.append(self._create_closing_shot(
                scene_num, shot_num, heading, environment
            ))
        
        return shots
    
    def _create_establishing_shot(self, scene_num: str, shot_num: int,
                                 heading: str, environment: Environment,
                                 action_blocks: List[str]) -> Shot:
        """Create establishing shot for scene"""
        return Shot(
            scene_number=scene_num,
            shot_number=f"{shot_num:03d}",
            shot_id=f"{scene_num}-{shot_num:03d}",
            scene_heading=heading,
            action=' '.join(action_blocks[:1]) if action_blocks else "Establishing shot",
            dialogue=[],
            characters=[],
            environment=environment,
            camera=CameraSetup(
                shot_type="WIDE ESTABLISHING",
                camera_movement="slow push in or crane down",
                framing="full scene visible",
                composition="rule of thirds",
                depth_of_field="deep focus"
            ),
            lighting=LightingSetup(
                sources=["natural" if "DAY" in environment.time_of_day else "practical"],
                mood="atmospheric",
                atmosphere="cinematic establishing"
            ),
            duration="5-8 seconds",
            metadata={"type": "establishing", "scene": scene_num}
        )
    
    def _create_dialogue_shot(self, scene_num: str, shot_num: int,
                            heading: str, environment: Environment,
                            dialogue: Dict, index: int) -> Shot:
        """Create shot for dialogue"""
        char_name = dialogue['character'].split('(')[0].strip()
        emotional_state = ""
        if '(' in dialogue['character']:
            emotional_state = dialogue['character'].split('(')[1].rstrip(')')
        
        character = Character(
            name=char_name,
            emotional_state=emotional_state
        )
        
        shot_type = "MEDIUM" if index == 0 else "CLOSE-UP" if index > 1 else "MEDIUM CLOSE"
        
        return Shot(
            scene_number=scene_num,
            shot_number=f"{shot_num:03d}",
            shot_id=f"{scene_num}-{shot_num:03d}",
            scene_heading=heading,
            action="",
            dialogue=[' '.join(dialogue.get('lines', []))],
            characters=[character],
            environment=environment,
            camera=CameraSetup(
                shot_type=shot_type,
                camera_movement="subtle drift or locked off",
                framing="character focused",
                composition="center framed with headroom",
                depth_of_field="shallow"
            ),
            lighting=LightingSetup(
                sources=["key light", "fill light", "rim light"],
                mood=emotional_state or "neutral",
                contrast="medium"
            ),
            duration="3-5 seconds",
            metadata={"type": "dialogue", "character": char_name, "scene": scene_num}
        )
    
    def _create_action_shot(self, scene_num: str, shot_num: int,
                          heading: str, environment: Environment,
                          action: str) -> Shot:
        """Create action shot"""
        # Determine camera movement based on action
        if any(word in action.lower() for word in ["run", "chase", "fight", "escape"]):
            movement = "dynamic handheld or steadicam"
            shot_type = "MEDIUM WIDE"
        elif any(word in action.lower() for word in ["sit", "stand", "wait", "look"]):
            movement = "static or subtle drift"
            shot_type = "MEDIUM"
        else:
            movement = "dolly or crane"
            shot_type = "MEDIUM"
        
        return Shot(
            scene_number=scene_num,
            shot_number=f"{shot_num:03d}",
            shot_id=f"{scene_num}-{shot_num:03d}",
            scene_heading=heading,
            action=action,
            dialogue=[],
            characters=[],
            environment=environment,
            camera=CameraSetup(
                shot_type=shot_type,
                camera_movement=movement,
                framing="action focused",
                focus="selective"
            ),
            lighting=LightingSetup(
                mood="dynamic",
                atmosphere="action oriented"
            ),
            duration="2-4 seconds",
            metadata={"type": "action", "scene": scene_num}
        )
    
    def _create_closing_shot(self, scene_num: str, shot_num: int,
                           heading: str, environment: Environment) -> Shot:
        """Create closing shot for scene"""
        return Shot(
            scene_number=scene_num,
            shot_number=f"{shot_num:03d}",
            shot_id=f"{scene_num}-{shot_num:03d}",
            scene_heading=heading,
            action="Scene closing",
            dialogue=[],
            characters=[],
            environment=environment,
            camera=CameraSetup(
                shot_type="WIDE",
                camera_movement="pull back or crane up",
                framing="scene exit",
                composition="closing composition",
                depth_of_field="deep"
            ),
            lighting=LightingSetup(
                mood="transitional",
                atmosphere="scene conclusion"
            ),
            duration="3-5 seconds",
            metadata={"type": "closing", "scene": scene_num}
        )
    
    def _extract_conditions(self, heading: str) -> str:
        """Extract environmental conditions from heading"""
        conditions = []
        heading_lower = heading.lower()
        
        weather_terms = {
            "rain": "raining",
            "snow": "snowing",
            "fog": "foggy",
            "storm": "stormy",
            "wind": "windy"
        }
        
        for term, condition in weather_terms.items():
            if term in heading_lower:
                conditions.append(condition)
        
        return ", ".join(conditions) if conditions else "normal"
    
    def _create_default_scene(self, content: str, scene_num: int) -> Scene:
        """Create default scene when no headings found"""
        location = "INTERIOR" if "INT." in content.upper() else "EXTERIOR"
        time_of_day = "NIGHT" if "NIGHT" in content.upper() else "DAY"
        
        shots = self._generate_scene_shots(
            str(scene_num),
            f"INT. {location} - {time_of_day}",
            location,
            time_of_day,
            [content],
            []
        )
        
        return Scene(
            scene_number=str(scene_num),
            heading=f"INT. {location} - {time_of_day}",
            location=location,
            time_of_day=time_of_day,
            action_blocks=[content],
            dialogue_blocks=[],
            shots=shots
        )


# ============================================================================
# COORDINATED AGENT SYSTEM
# ============================================================================

class CoordinatedAgentSystem:
    """Properly coordinated agent system with inter-agent communication"""
    
    def __init__(self, agents_dir: Path):
        self.agents_dir = agents_dir
        self.agents = {}
        self.shared_context = {}  # Shared context between agents
        self.agent_results = {}   # Store results from each agent
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all agents with coordination capability"""
        from film_crew_ai_enhanced import (
            ScriptBreakdownAgent, CharacterAnalysisAgent,
            EnvironmentPropsAgent, CinematographyAgent,
            LightingMoodAgent, PromptSynthesisAgent
        )
        
        self.agents = {
            'script_breakdown': ScriptBreakdownAgent(self.agents_dir),
            'character_analysis': CharacterAnalysisAgent(self.agents_dir),
            'environment_props': EnvironmentPropsAgent(self.agents_dir),
            'cinematography': CinematographyAgent(self.agents_dir),
            'lighting_mood': LightingMoodAgent(self.agents_dir),
            'prompt_synthesis': PromptSynthesisAgent(self.agents_dir)
        }
        
        logger.info(f"Initialized {len(self.agents)} coordinated agents")
    
    def process_shot_coordinated(self, scene: Scene, shot: Shot) -> Dict:
        """Process shot with proper agent coordination and communication"""
        logger.info(f"Coordinated processing for shot {shot.shot_id}")
        
        # Clear previous context
        self.agent_results.clear()
        
        # Phase 1: Script Breakdown (Foundation)
        logger.debug("Phase 1: Script breakdown analysis")
        breakdown = self.agents['script_breakdown'].process(scene, shot)
        self.agent_results['breakdown'] = breakdown
        self.shared_context.update(breakdown)
        
        # Phase 2: Parallel Analysis (with shared context)
        logger.debug("Phase 2: Parallel agent analysis")
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            
            # Submit parallel tasks
            for agent_name in ['character_analysis', 'environment_props',
                             'cinematography', 'lighting_mood']:
                future = executor.submit(
                    self._process_with_context,
                    agent_name, scene, shot, breakdown
                )
                futures[future] = agent_name
            
            # Collect results
            for future in as_completed(futures):
                agent_name = futures[future]
                try:
                    result = future.result()
                    self.agent_results[agent_name] = result
                    # Share relevant info with other agents
                    self._update_shared_context(agent_name, result)
                except Exception as e:
                    logger.error(f"Agent {agent_name} failed: {e}")
                    self.agent_results[agent_name] = {}
        
        # Phase 3: Synthesis (with all context)
        logger.debug("Phase 3: Prompt synthesis")
        final_prompt = self.agents['prompt_synthesis'].process(
            scene, shot, self.agent_results
        )
        self.agent_results['veo3_prompt'] = final_prompt
        
        # Phase 4: Quality check and coordination
        self._ensure_consistency()
        
        return self.agent_results
    
    def _process_with_context(self, agent_name: str, scene: Scene,
                             shot: Shot, breakdown: Dict) -> Dict:
        """Process with agent while maintaining context"""
        return self.agents[agent_name].process(scene, shot, breakdown)
    
    def _update_shared_context(self, agent_name: str, result: Dict):
        """Update shared context for inter-agent communication"""
        if agent_name == 'character_analysis' and 'characters' in result:
            self.shared_context['active_characters'] = result['characters']
        elif agent_name == 'environment_props' and 'atmosphere' in result:
            self.shared_context['scene_atmosphere'] = result['atmosphere']
        elif agent_name == 'cinematography' and 'camera' in result:
            self.shared_context['camera_setup'] = result
        elif agent_name == 'lighting_mood' and 'mood' in result:
            self.shared_context['lighting_mood'] = result['mood']
    
    def _ensure_consistency(self):
        """Ensure consistency across all agent outputs"""
        # Check character consistency
        if 'character_analysis' in self.agent_results:
            characters = self.agent_results['character_analysis'].get('characters', [])
            # Ensure all agents reference same characters
            for agent_name, result in self.agent_results.items():
                if isinstance(result, dict) and 'characters' in result:
                    result['characters'] = characters
        
        # Ensure mood consistency
        if 'lighting_mood' in self.agent_results:
            mood = self.agent_results['lighting_mood'].get('mood', 'neutral')
            # Apply mood to other relevant outputs
            if 'cinematography' in self.agent_results:
                self.agent_results['cinematography']['mood_influence'] = mood


# ============================================================================
# FIXED FILM CREW PROCESSOR
# ============================================================================

class FixedFilmCrewProcessor:
    """Fixed processor with proper scene/shot separation and agent coordination"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.agents_dir = project_dir / "templates" / "agents"
        self.output_dir = project_dir / "output"
        self.scripts_dir = project_dir / "scripts"
        
        # Initialize components
        self.parser = FixedScriptParser()
        self.agent_system = CoordinatedAgentSystem(self.agents_dir)
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
        
        self.errors = []
    
    def process_script(self, script_path: Path) -> Optional[Path]:
        """Process script with proper scene/shot organization"""
        try:
            logger.info(f"Processing script: {script_path.name}")
            
            # Parse script into scenes
            scenes = self.parser.parse(script_path)
            logger.info(f"Parsed {len(scenes)} distinct scenes")
            
            # Create main output directory for this script
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{script_path.stem}_{timestamp}"
            script_output_dir = self.output_dir / output_name
            script_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Process each scene separately
            all_scene_data = []
            for scene in scenes:
                logger.info(f"Processing Scene {scene.scene_number}: {scene.heading}")
                scene_data = self._process_scene(
                    scene, script_output_dir, script_path.stem
                )
                all_scene_data.append(scene_data)
            
            # Create master index
            self._create_master_index(
                script_output_dir, script_path.name, scenes, all_scene_data
            )
            
            logger.info(f"✅ Processing complete. Output: {script_output_dir}")
            return script_output_dir
            
        except Exception as e:
            logger.error(f"Error processing script: {e}")
            logger.error(traceback.format_exc())
            self.errors.append(str(e))
            return None
    
    def _process_scene(self, scene: Scene, output_dir: Path, 
                      script_name: str) -> Dict:
        """Process individual scene with all its shots"""
        # Create scene-specific directory
        scene_dir = output_dir / f"Scene_{scene.scene_number}"
        scene_dir.mkdir(exist_ok=True)
        
        # Create subdirectories for this scene
        subdirs = [
            "veo3_prompts",
            "camera_setups",
            "lighting",
            "characters",
            "environment",
            "breakdown"
        ]
        
        for subdir in subdirs:
            (scene_dir / subdir).mkdir(exist_ok=True)
        
        # Process each shot in the scene
        scene_shots = []
        for shot in scene.shots:
            logger.info(f"  Processing Shot {shot.shot_number}")
            shot_data = self._process_shot(
                scene, shot, scene_dir, script_name
            )
            scene_shots.append(shot_data)
        
        # Create scene summary
        scene_summary = {
            "scene_number": scene.scene_number,
            "heading": scene.heading,
            "location": scene.location,
            "time_of_day": scene.time_of_day,
            "total_shots": len(scene.shots),
            "shots": scene_shots
        }
        
        # Save scene summary
        summary_file = scene_dir / f"SCENE_{scene.scene_number}_SUMMARY.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(scene_summary, f, indent=2)
        
        return scene_summary
    
    def _process_shot(self, scene: Scene, shot: Shot,
                     scene_dir: Path, script_name: str) -> Dict:
        """Process individual shot with coordinated agents"""
        
        # Use coordinated agent system
        results = self.agent_system.process_shot_coordinated(scene, shot)
        
        # Update shot with results
        shot.veo3_prompt = results.get('veo3_prompt', '')
        
        # Prepare complete shot data
        shot_data = shot.to_dict()
        shot_data['script_name'] = script_name
        shot_data['processing_results'] = results
        
        # Save shot outputs to scene-specific directories
        self._save_shot_outputs(shot, shot_data, scene_dir, script_name)
        
        return shot_data
    
    def _save_shot_outputs(self, shot: Shot, shot_data: Dict,
                          scene_dir: Path, script_name: str):
        """Save shot outputs to scene-organized directories"""
        
        # Main Veo3 prompt file (in scene-specific folder)
        veo3_file = scene_dir / "veo3_prompts" / f"{script_name}_scene{shot.scene_number}_shot{shot.shot_number}.json"
        
        with open(veo3_file, 'w', encoding='utf-8') as f:
            json.dump({
                "script": script_name,
                "scene_number": shot.scene_number,
                "shot_number": shot.shot_number,
                "shot_id": shot.shot_id,
                "characters": shot_data['characters'],
                "environment": shot_data['environment'],
                "camera": shot_data['camera'],
                "lighting": shot_data['lighting'],
                "veo3_prompt": shot.veo3_prompt,
                "duration": shot.duration,
                "metadata": shot.metadata
            }, f, indent=2)
        
        # Save department-specific files
        departments = {
            "camera_setups": "cinematography",
            "lighting": "lighting_mood",
            "characters": "character_analysis",
            "environment": "environment_props",
            "breakdown": "breakdown"
        }
        
        for dept_dir, result_key in departments.items():
            if result_key in shot_data.get('processing_results', {}):
                dept_file = scene_dir / dept_dir / f"shot_{shot.shot_number}.json"
                
                with open(dept_file, 'w', encoding='utf-8') as f:
                    data = {
                        "shot_id": shot.shot_id,
                        "shot_number": shot.shot_number,
                        **shot_data['processing_results'][result_key]
                    }
                    json.dump(data, f, indent=2)
    
    def _create_master_index(self, output_dir: Path, script_name: str,
                            scenes: List[Scene], all_scene_data: List[Dict]):
        """Create master index with scene organization"""
        # Calculate total shots
        total_shots = sum(len(scene.shots) for scene in scenes)
        
        index = {
            "project": script_name,
            "generated": datetime.now().isoformat(),
            "version": "4.1-FIXED",
            "engine": "Fixed Film Crew AI with Coordinated Agents",
            "statistics": {
                "total_scenes": len(scenes),
                "total_shots": total_shots,
                "departments": 6,
                "agents": 6,
                "coordination": "enabled"
            },
            "scene_breakdown": all_scene_data,
            "file_organization": {
                "structure": "Organized by scene",
                "scene_folders": [f"Scene_{scene.scene_number}" for scene in scenes],
                "departments_per_scene": [
                    "veo3_prompts",
                    "camera_setups",
                    "lighting",
                    "characters",
                    "environment",
                    "breakdown"
                ]
            },
            "agent_coordination": {
                "phases": [
                    "1. Script Breakdown (Foundation)",
                    "2. Parallel Analysis (4 agents)",
                    "3. Prompt Synthesis (Convergence)",
                    "4. Quality Check (Consistency)"
                ],
                "communication": "Shared context between agents",
                "consistency": "Enforced across all outputs"
            }
        }
        
        # Save master index
        index_file = output_dir / "MASTER_INDEX.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
        
        # Create scene navigation file
        navigation = {
            "script": script_name,
            "scenes": []
        }
        
        for scene_data in all_scene_data:
            scene_nav = {
                "scene_number": scene_data['scene_number'],
                "heading": scene_data['heading'],
                "folder": f"Scene_{scene_data['scene_number']}",
                "shots": [
                    {
                        "shot_number": shot['shot_number'],
                        "shot_id": shot.get('shot_id', ''),
                        "veo3_file": f"Scene_{scene_data['scene_number']}/veo3_prompts/{script_name}_scene{scene_data['scene_number']}_shot{shot['shot_number']}.json"
                    }
                    for shot in scene_data.get('shots', [])
                ]
            }
            navigation['scenes'].append(scene_nav)
        
        nav_file = output_dir / "SCENE_NAVIGATION.json"
        with open(nav_file, 'w', encoding='utf-8') as f:
            json.dump(navigation, f, indent=2)
        
        logger.info(f"Created master index with {len(scenes)} scenes and {total_shots} total shots")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for fixed system"""
    parser = argparse.ArgumentParser(
        description="Film Crew AI v4.1 - Fixed Scene/Shot Organization with Coordinated Agents"
    )
    parser.add_argument('--script', type=str, help='Path to specific script')
    parser.add_argument('--all', action='store_true', help='Process all scripts')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Create processor
    processor = FixedFilmCrewProcessor(project_dir)
    
    if args.script:
        script_path = Path(args.script)
        if script_path.exists():
            result = processor.process_script(script_path)
            if result:
                print(f"\n✅ Success! Output saved to: {result}")
                print(f"📁 Scenes are organized in separate folders")
                print(f"🤝 Agents worked in coordination")
        else:
            logger.error(f"Script not found: {script_path}")
    
    elif args.all:
        # Process all scripts
        script_files = []
        for ext in ['.txt', '.pdf', '.doc', '.docx']:
            script_files.extend(processor.scripts_dir.glob(f"*{ext}"))
        
        if script_files:
            for script_file in script_files:
                processor.process_script(script_file)
        else:
            logger.warning("No scripts found")
    
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("FILM CREW AI v4.1 - FIXED VERSION")
        print("With Proper Scene Separation & Agent Coordination")
        print("="*60)
        print("\nOptions:")
        print("1. Process all scripts")
        print("2. Process specific script")
        print("3. Exit")
        
        choice = input("\nSelect option (1-3): ").strip()
        
        if choice == "1":
            processor.process_script(Path("scripts/test_script.txt"))
        elif choice == "2":
            script_name = input("Enter script path: ").strip()
            processor.process_script(Path(script_name))


if __name__ == "__main__":
    main()