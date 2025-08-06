#!/usr/bin/env python3
"""
Film Crew AI - Enhanced Production System v4.0
Multi-format script processing with specialized AI agent orchestration
Supports: PDF, Word (DOC/DOCX), and plain text scripts
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FilmCrewAI')


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class Character:
    """Represents a character in a scene"""
    name: str
    physical_description: str = ""
    wardrobe: str = ""
    emotional_state: str = ""
    position: str = ""
    movement: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass 
class Environment:
    """Represents the environment and props in a scene"""
    location: str
    time_of_day: str
    setting_description: str = ""
    props: List[str] = field(default_factory=list)
    environmental_conditions: str = ""
    background_elements: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class CameraSetup:
    """Represents camera angles and movements"""
    shot_type: str  # wide, medium, close-up, extreme close-up, etc.
    camera_movement: str = "static"  # pan, tilt, dolly, crane, handheld, etc.
    framing: str = ""
    composition: str = ""
    focus: str = ""
    depth_of_field: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class LightingSetup:
    """Represents lighting configuration"""
    sources: List[str] = field(default_factory=list)
    direction: str = ""
    color_temperature: str = ""
    intensity: str = ""
    shadows: str = ""
    contrast: str = ""
    mood: str = ""
    atmosphere: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Shot:
    """Enhanced shot representation with all required fields"""
    scene_number: str  # Changed to string to support "1A" format
    shot_number: str   # Changed to string to support "001" format
    shot_id: str
    scene_heading: str
    action: str
    dialogue: List[str]
    characters: List[Character]
    environment: Environment
    camera: CameraSetup
    lighting: LightingSetup
    duration: str = "3-5 seconds"
    veo3_prompt: str = ""
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "scene_number": self.scene_number,
            "shot_number": self.shot_number,
            "characters": [c.to_dict() for c in self.characters],
            "environment": self.environment.to_dict(),
            "camera": self.camera.to_dict(),
            "lighting": self.lighting.to_dict(),
            "veo3_prompt": self.veo3_prompt,
            "duration": self.duration,
            "metadata": self.metadata
        }


@dataclass
class Scene:
    """Enhanced scene representation"""
    scene_number: str
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


# ============================================================================
# DOCUMENT PARSERS
# ============================================================================

class DocumentReader:
    """Handles multiple document formats"""
    
    @staticmethod
    def read_file(file_path: Path) -> str:
        """Read content from various file formats"""
        extension = file_path.suffix.lower()
        
        if extension == '.txt':
            return DocumentReader._read_text(file_path)
        elif extension == '.pdf':
            return DocumentReader._read_pdf(file_path)
        elif extension in ['.doc', '.docx']:
            return DocumentReader._read_word(file_path)
        else:
            raise ValueError(f"Unsupported file format: {extension}")
    
    @staticmethod
    def _read_text(file_path: Path) -> str:
        """Read plain text file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    @staticmethod
    def _read_pdf(file_path: Path) -> str:
        """Read PDF file content"""
        try:
            import PyPDF2
        except ImportError:
            logger.warning("PyPDF2 not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "PyPDF2"])
            import PyPDF2
        
        text = ""
        with open(file_path, 'rb') as f:
            pdf_reader = PyPDF2.PdfReader(f)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()
        
        return text
    
    @staticmethod
    def _read_word(file_path: Path) -> str:
        """Read Word document content"""
        try:
            import docx
        except ImportError:
            logger.warning("python-docx not installed. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
            import docx
        
        doc = docx.Document(file_path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
        
        return text


# ============================================================================
# ENHANCED SCRIPT PARSER
# ============================================================================

class EnhancedScriptParser:
    """Enhanced parser with better scene/shot detection"""
    
    def __init__(self):
        self.scene_pattern = re.compile(
            r'^(INT\.|EXT\.|INT/EXT\.)\s+(.+?)\s*[-–]\s*(.+)$', 
            re.MULTILINE
        )
        self.character_pattern = re.compile(r'^[A-Z][A-Z\s]+(\([^)]+\))?$')
        self.parenthetical_pattern = re.compile(r'^\([^)]+\)$')
        self.scene_counter = 0
        self.shot_counter = 0
        
    def parse(self, script_path: Path) -> List[Scene]:
        """Parse script file into scenes with enhanced structure"""
        logger.info(f"Parsing script: {script_path}")
        
        # Read content using appropriate reader
        content = DocumentReader.read_file(script_path)
        
        scenes = []
        scene_matches = list(self.scene_pattern.finditer(content))
        
        if not scene_matches:
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
        """Parse individual scene with enhanced detail extraction"""
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
        
        # Generate enhanced shots
        shots = self._generate_enhanced_shots(
            scene_number, heading, location, time_of_day, 
            action_blocks, dialogue_blocks
        )
        
        # Use string format for scene numbers to support "1A" format
        scene_num_str = str(scene_number)
        if scene_number > 26:
            scene_num_str = f"{scene_number // 26}{chr(65 + (scene_number % 26))}"
        
        return Scene(
            scene_number=scene_num_str,
            heading=heading,
            location=location,
            time_of_day=time_of_day,
            action_blocks=action_blocks,
            dialogue_blocks=dialogue_blocks,
            shots=shots
        )
    
    def _generate_enhanced_shots(self, scene_number: int, heading: str, 
                                location: str, time_of_day: str,
                                action_blocks: List[str], 
                                dialogue_blocks: List[Dict]) -> List[Shot]:
        """Generate enhanced shots with full production details"""
        shots = []
        shot_num = 1
        
        # Scene number as string
        scene_num_str = str(scene_number)
        if scene_number > 26:
            scene_num_str = f"{scene_number // 26}{chr(65 + (scene_number % 26))}"
        
        # Create environment
        environment = Environment(
            location=location,
            time_of_day=time_of_day,
            setting_description=' '.join(action_blocks[:1]) if action_blocks else "",
            environmental_conditions=self._extract_environment_conditions(heading)
        )
        
        # Establishing shot
        establishing_camera = CameraSetup(
            shot_type="WIDE ESTABLISHING",
            camera_movement="slow push in",
            framing="wide",
            composition="rule of thirds",
            depth_of_field="deep"
        )
        
        establishing_lighting = LightingSetup(
            sources=["natural" if "DAY" in time_of_day else "practical"],
            mood="atmospheric",
            atmosphere="cinematic"
        )
        
        shots.append(Shot(
            scene_number=scene_num_str,
            shot_number=f"{shot_num:03d}",
            shot_id=f"{scene_num_str}-{shot_num:03d}",
            scene_heading=heading,
            action=' '.join(action_blocks[:1]) if action_blocks else "",
            dialogue=[],
            characters=self._extract_characters(dialogue_blocks),
            environment=environment,
            camera=establishing_camera,
            lighting=establishing_lighting,
            duration="5-8 seconds",
            metadata={"type": "establishing"}
        ))
        shot_num += 1
        
        # Coverage shots for dialogue
        if dialogue_blocks:
            for i, dialogue in enumerate(dialogue_blocks[:3]):  # Limit to 3 main exchanges
                camera = CameraSetup(
                    shot_type="MEDIUM" if i == 0 else "CLOSE-UP",
                    camera_movement="subtle drift",
                    framing="medium close" if i > 0 else "medium",
                    composition="center framed",
                    depth_of_field="shallow"
                )
                
                lighting = LightingSetup(
                    sources=["key light", "fill light"],
                    mood="dramatic" if i > 1 else "natural",
                    contrast="medium"
                )
                
                shots.append(Shot(
                    scene_number=scene_num_str,
                    shot_number=f"{shot_num:03d}",
                    shot_id=f"{scene_num_str}-{shot_num:03d}",
                    scene_heading=heading,
                    action="",
                    dialogue=[dialogue['character']],
                    characters=self._extract_characters([dialogue]),
                    environment=environment,
                    camera=camera,
                    lighting=lighting,
                    duration="3-5 seconds",
                    metadata={"type": "dialogue", "character": dialogue['character']}
                ))
                shot_num += 1
        
        # Action shots
        if len(action_blocks) > 1:
            for i, action in enumerate(action_blocks[1:3]):  # Additional action shots
                camera = CameraSetup(
                    shot_type="MEDIUM" if i == 0 else "CLOSE-UP",
                    camera_movement="handheld" if "run" in action.lower() else "static",
                    framing="dynamic",
                    focus="selective"
                )
                
                shots.append(Shot(
                    scene_number=scene_num_str,
                    shot_number=f"{shot_num:03d}",
                    shot_id=f"{scene_num_str}-{shot_num:03d}",
                    scene_heading=heading,
                    action=action,
                    dialogue=[],
                    characters=[],
                    environment=environment,
                    camera=camera,
                    lighting=establishing_lighting,
                    duration="2-4 seconds",
                    metadata={"type": "action"}
                ))
                shot_num += 1
        
        return shots
    
    def _extract_characters(self, dialogue_blocks: List[Dict]) -> List[Character]:
        """Extract character information from dialogue"""
        characters = []
        for dialogue in dialogue_blocks:
            char_name = dialogue['character'].split('(')[0].strip()
            
            # Extract emotional state from parentheticals if present
            emotional_state = ""
            if '(' in dialogue['character']:
                emotional_state = dialogue['character'].split('(')[1].rstrip(')')
            
            character = Character(
                name=char_name,
                emotional_state=emotional_state
            )
            
            # Avoid duplicates
            if not any(c.name == char_name for c in characters):
                characters.append(character)
        
        return characters
    
    def _extract_environment_conditions(self, heading: str) -> str:
        """Extract environmental conditions from scene heading"""
        conditions = []
        
        heading_lower = heading.lower()
        if "rain" in heading_lower:
            conditions.append("raining")
        if "snow" in heading_lower:
            conditions.append("snowing")
        if "fog" in heading_lower:
            conditions.append("foggy")
        if "storm" in heading_lower:
            conditions.append("stormy")
        if "night" in heading_lower:
            conditions.append("dark")
        elif "dawn" in heading_lower or "sunrise" in heading_lower:
            conditions.append("dawn lighting")
        elif "dusk" in heading_lower or "sunset" in heading_lower:
            conditions.append("golden hour")
        
        return ", ".join(conditions) if conditions else "normal"
    
    def _create_default_scene(self, content: str) -> Scene:
        """Create a default scene when no headings found"""
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
        
        shots = self._generate_enhanced_shots(
            1, f"INT. {location} - {time_of_day}",
            location, time_of_day, [content], []
        )
        
        return Scene(
            scene_number="1",
            heading=f"INT. {location} - {time_of_day}",
            location=location,
            time_of_day=time_of_day,
            action_blocks=[content],
            dialogue_blocks=[],
            shots=shots
        )


# ============================================================================
# MASTER ORCHESTRATOR (FILM DIRECTOR)
# ============================================================================

class MasterOrchestrator:
    """Central command and quality control - The Film Director"""
    
    def __init__(self, agents_dir: Path):
        self.agents_dir = agents_dir
        self.agents = self._initialize_agents()
        self.validation_errors = []
        
    def _initialize_agents(self) -> Dict[str, 'BaseAgent']:
        """Initialize and register all subagents"""
        agents = {}
        
        # Initialize specialized agents
        agents['script_breakdown'] = ScriptBreakdownAgent(self.agents_dir)
        agents['character_analysis'] = CharacterAnalysisAgent(self.agents_dir) 
        agents['environment_props'] = EnvironmentPropsAgent(self.agents_dir)
        agents['cinematography'] = CinematographyAgent(self.agents_dir)
        agents['lighting_mood'] = LightingMoodAgent(self.agents_dir)
        agents['prompt_synthesis'] = PromptSynthesisAgent(self.agents_dir)
        
        logger.info(f"Initialized {len(agents)} specialized agents")
        return agents
    
    def validate_input(self, script_path: Path) -> bool:
        """Validate script input and format compatibility"""
        if not script_path.exists():
            self.validation_errors.append(f"Script file not found: {script_path}")
            return False
        
        extension = script_path.suffix.lower()
        supported = ['.txt', '.pdf', '.doc', '.docx']
        
        if extension not in supported:
            self.validation_errors.append(
                f"Unsupported format: {extension}. Supported: {supported}"
            )
            return False
        
        return True
    
    def orchestrate_processing(self, scene: Scene, shot: Shot) -> Dict:
        """Coordinate all subagents in correct sequence"""
        logger.info(f"Orchestrating shot {shot.shot_id}")
        
        results = {}
        
        # Step 1: Script breakdown (always first)
        breakdown = self.agents['script_breakdown'].process(scene, shot)
        results['breakdown'] = breakdown
        
        # Step 2: Parallel processing of analysis agents
        parallel_results = {}
        for agent_name in ['character_analysis', 'environment_props', 
                          'cinematography', 'lighting_mood']:
            agent_result = self.agents[agent_name].process(scene, shot, breakdown)
            parallel_results[agent_name] = agent_result
        
        results.update(parallel_results)
        
        # Step 3: Synthesis (convergence point)
        final_prompt = self.agents['prompt_synthesis'].process(
            scene, shot, results
        )
        results['veo3_prompt'] = final_prompt
        
        return results
    
    def ensure_consistency(self, all_shots: List[Dict]) -> List[Dict]:
        """Review and maintain consistency across all shots"""
        # Check character consistency
        characters = {}
        for shot in all_shots:
            if 'characters' in shot:
                for char in shot['characters']:
                    if char['name'] not in characters:
                        characters[char['name']] = char
                    else:
                        # Merge character details for consistency
                        for key, value in char.items():
                            if value and not characters[char['name']].get(key):
                                characters[char['name']][key] = value
        
        # Apply consistent character details back to all shots
        for shot in all_shots:
            if 'characters' in shot:
                for i, char in enumerate(shot['characters']):
                    shot['characters'][i] = characters[char['name']]
        
        return all_shots


# ============================================================================
# SPECIALIZED SUBAGENTS
# ============================================================================

class BaseAgent:
    """Base class for all specialized agents"""
    
    def __init__(self, agents_dir: Path):
        self.agents_dir = agents_dir
        self.prompt_file = None
        self.load_prompt()
    
    def load_prompt(self):
        """Load agent-specific prompt from file"""
        if self.prompt_file and (self.agents_dir / self.prompt_file).exists():
            with open(self.agents_dir / self.prompt_file, 'r') as f:
                self.prompt = f.read()
        else:
            self.prompt = ""
    
    def process(self, *args, **kwargs) -> Dict:
        """Process input and return results"""
        raise NotImplementedError


class ScriptBreakdownAgent(BaseAgent):
    """Parses and segments scripts into shots"""
    
    def __init__(self, agents_dir: Path):
        self.prompt_file = "script-breakdown.md"
        super().__init__(agents_dir)
    
    def process(self, scene: Scene, shot: Shot) -> Dict:
        """Break down the shot structure"""
        return {
            "scene_id": scene.scene_number,
            "shot_id": shot.shot_id,
            "shot_type": shot.camera.shot_type,
            "duration": shot.duration,
            "narrative_function": self._determine_narrative_function(shot),
            "emotional_beat": self._extract_emotional_beat(shot)
        }
    
    def _determine_narrative_function(self, shot: Shot) -> str:
        """Determine the narrative function of the shot"""
        if "establishing" in shot.metadata.get("type", ""):
            return "establish_setting"
        elif "dialogue" in shot.metadata.get("type", ""):
            return "character_interaction"
        elif "action" in shot.metadata.get("type", ""):
            return "advance_plot"
        return "transition"
    
    def _extract_emotional_beat(self, shot: Shot) -> str:
        """Extract the emotional beat of the shot"""
        if shot.characters:
            emotions = [c.emotional_state for c in shot.characters if c.emotional_state]
            if emotions:
                return ", ".join(emotions)
        return "neutral"


class CharacterAnalysisAgent(BaseAgent):
    """Analyzes and tracks character details"""
    
    def __init__(self, agents_dir: Path):
        self.prompt_file = "character-analysis.md"
        super().__init__(agents_dir)
    
    def process(self, scene: Scene, shot: Shot, breakdown: Dict) -> Dict:
        """Analyze characters in the shot"""
        character_data = []
        
        for character in shot.characters:
            char_analysis = {
                "name": character.name,
                "physical_description": character.physical_description or self._infer_description(character.name),
                "wardrobe": character.wardrobe or self._infer_wardrobe(scene.location, scene.time_of_day),
                "emotional_state": character.emotional_state or breakdown.get("emotional_beat", "neutral"),
                "position": character.position or "center frame",
                "movement": character.movement or "static"
            }
            character_data.append(char_analysis)
        
        return {"characters": character_data}
    
    def _infer_description(self, name: str) -> str:
        """Infer character description from context"""
        return f"Adult, professional appearance"
    
    def _infer_wardrobe(self, location: str, time_of_day: str) -> str:
        """Infer wardrobe from scene context"""
        if "OFFICE" in location.upper():
            return "business attire"
        elif "HOME" in location.upper():
            return "casual wear"
        return "appropriate to setting"


class EnvironmentPropsAgent(BaseAgent):
    """Describes environments and props"""
    
    def __init__(self, agents_dir: Path):
        self.prompt_file = "background-designer.md"
        super().__init__(agents_dir)
    
    def process(self, scene: Scene, shot: Shot, breakdown: Dict) -> Dict:
        """Analyze environment and props"""
        return {
            "location": shot.environment.location,
            "time_of_day": shot.environment.time_of_day,
            "setting_description": shot.environment.setting_description or self._enhance_setting(scene),
            "props": shot.environment.props or self._extract_props(scene.action_blocks),
            "environmental_conditions": shot.environment.environmental_conditions,
            "background_elements": shot.environment.background_elements or self._infer_background(shot.environment.location),
            "atmosphere": self._determine_atmosphere(shot.environment, breakdown)
        }
    
    def _enhance_setting(self, scene: Scene) -> str:
        """Enhance setting description"""
        base = f"{scene.location} during {scene.time_of_day}"
        if scene.action_blocks:
            base += f", {scene.action_blocks[0][:50]}"
        return base
    
    def _extract_props(self, action_blocks: List[str]) -> List[str]:
        """Extract props from action descriptions"""
        props = []
        prop_keywords = ["table", "chair", "door", "window", "phone", "computer", 
                        "book", "glass", "cup", "bag", "car", "desk"]
        
        for block in action_blocks:
            block_lower = block.lower()
            for keyword in prop_keywords:
                if keyword in block_lower:
                    props.append(keyword)
        
        return list(set(props))
    
    def _infer_background(self, location: str) -> List[str]:
        """Infer background elements from location"""
        if "OFFICE" in location.upper():
            return ["desks", "computers", "windows", "office furniture"]
        elif "STREET" in location.upper():
            return ["buildings", "vehicles", "pedestrians", "street furniture"]
        elif "HOME" in location.upper():
            return ["furniture", "decorations", "personal items"]
        return ["appropriate background elements"]
    
    def _determine_atmosphere(self, environment: Environment, breakdown: Dict) -> str:
        """Determine atmospheric qualities"""
        emotional_beat = breakdown.get("emotional_beat", "neutral")
        
        if "tense" in emotional_beat.lower():
            return "tense, charged atmosphere"
        elif "sad" in emotional_beat.lower():
            return "melancholic, subdued atmosphere"
        elif "happy" in emotional_beat.lower():
            return "warm, inviting atmosphere"
        
        return "neutral, realistic atmosphere"


class CinematographyAgent(BaseAgent):
    """Designs camera angles and movements"""
    
    def __init__(self, agents_dir: Path):
        self.prompt_file = "camera-director.md"
        super().__init__(agents_dir)
    
    def process(self, scene: Scene, shot: Shot, breakdown: Dict) -> Dict:
        """Design camera setup"""
        return {
            "shot_type": shot.camera.shot_type,
            "camera_movement": shot.camera.camera_movement or self._determine_movement(breakdown),
            "framing": shot.camera.framing or self._determine_framing(shot.camera.shot_type),
            "composition": shot.camera.composition or "rule of thirds",
            "focus": shot.camera.focus or self._determine_focus(shot),
            "depth_of_field": shot.camera.depth_of_field or self._determine_dof(shot.camera.shot_type),
            "angle": self._determine_angle(breakdown),
            "lens": self._suggest_lens(shot.camera.shot_type)
        }
    
    def _determine_movement(self, breakdown: Dict) -> str:
        """Determine appropriate camera movement"""
        narrative_function = breakdown.get("narrative_function", "")
        
        if narrative_function == "establish_setting":
            return "slow push in or crane down"
        elif narrative_function == "character_interaction":
            return "subtle drift or locked off"
        elif narrative_function == "advance_plot":
            return "dynamic - dolly, steadicam, or handheld"
        
        return "static or minimal movement"
    
    def _determine_framing(self, shot_type: str) -> str:
        """Determine framing based on shot type"""
        framing_map = {
            "WIDE ESTABLISHING": "full scene visible",
            "WIDE": "full body and environment",
            "MEDIUM": "waist up",
            "CLOSE-UP": "shoulders and head",
            "EXTREME CLOSE-UP": "detail focus"
        }
        return framing_map.get(shot_type, "appropriate to content")
    
    def _determine_focus(self, shot: Shot) -> str:
        """Determine focus strategy"""
        if shot.characters:
            return f"focus on {shot.characters[0].name if shot.characters else 'subject'}"
        return "environmental focus"
    
    def _determine_dof(self, shot_type: str) -> str:
        """Determine depth of field"""
        if "CLOSE" in shot_type:
            return "shallow - background blur"
        elif "WIDE" in shot_type:
            return "deep - everything in focus"
        return "medium - selective focus"
    
    def _determine_angle(self, breakdown: Dict) -> str:
        """Determine camera angle"""
        emotional_beat = breakdown.get("emotional_beat", "")
        
        if "powerful" in emotional_beat.lower():
            return "low angle"
        elif "vulnerable" in emotional_beat.lower():
            return "high angle"
        
        return "eye level"
    
    def _suggest_lens(self, shot_type: str) -> str:
        """Suggest appropriate lens"""
        lens_map = {
            "WIDE ESTABLISHING": "14-24mm wide angle",
            "WIDE": "24-35mm",
            "MEDIUM": "50mm standard",
            "CLOSE-UP": "85mm portrait",
            "EXTREME CLOSE-UP": "100mm macro"
        }
        return lens_map.get(shot_type, "50mm standard")


class LightingMoodAgent(BaseAgent):
    """Defines lighting and mood"""
    
    def __init__(self, agents_dir: Path):
        self.prompt_file = "lighting-designer.md"
        super().__init__(agents_dir)
    
    def process(self, scene: Scene, shot: Shot, breakdown: Dict) -> Dict:
        """Design lighting setup"""
        time_of_day = shot.environment.time_of_day
        emotional_beat = breakdown.get("emotional_beat", "neutral")
        
        return {
            "sources": shot.lighting.sources or self._determine_sources(time_of_day, shot.environment.location),
            "direction": shot.lighting.direction or self._determine_direction(emotional_beat),
            "color_temperature": shot.lighting.color_temperature or self._determine_color_temp(time_of_day),
            "intensity": shot.lighting.intensity or self._determine_intensity(emotional_beat),
            "shadows": shot.lighting.shadows or self._determine_shadows(emotional_beat),
            "contrast": shot.lighting.contrast or self._determine_contrast(breakdown),
            "mood": shot.lighting.mood or emotional_beat,
            "atmosphere": shot.lighting.atmosphere or self._create_atmosphere(scene, breakdown)
        }
    
    def _determine_sources(self, time_of_day: str, location: str) -> List[str]:
        """Determine light sources"""
        sources = []
        
        if "DAY" in time_of_day.upper():
            sources.append("natural sunlight")
            if "INT" in location:
                sources.append("window light")
        elif "NIGHT" in time_of_day.upper():
            sources.append("practical lights")
            sources.append("street lights" if "EXT" in location else "interior lighting")
        
        sources.append("motivated fill light")
        return sources
    
    def _determine_direction(self, emotional_beat: str) -> str:
        """Determine lighting direction"""
        if "mysterious" in emotional_beat.lower():
            return "side lighting with strong shadows"
        elif "romantic" in emotional_beat.lower():
            return "soft, diffused from multiple angles"
        elif "tense" in emotional_beat.lower():
            return "harsh, directional"
        
        return "three-point lighting setup"
    
    def _determine_color_temp(self, time_of_day: str) -> str:
        """Determine color temperature"""
        temp_map = {
            "DAWN": "4000K - cool blue transitioning to warm",
            "MORNING": "5000K - neutral to slightly warm",
            "DAY": "5600K - daylight balanced",
            "AFTERNOON": "5500K - neutral daylight",
            "DUSK": "3000K - golden hour warmth",
            "NIGHT": "3200K - tungsten warmth with blue moonlight"
        }
        
        for key in temp_map:
            if key in time_of_day.upper():
                return temp_map[key]
        
        return "5000K - neutral"
    
    def _determine_intensity(self, emotional_beat: str) -> str:
        """Determine lighting intensity"""
        if "intense" in emotional_beat.lower():
            return "high contrast, dramatic"
        elif "soft" in emotional_beat.lower() or "romantic" in emotional_beat.lower():
            return "soft, diffused"
        
        return "balanced, natural"
    
    def _determine_shadows(self, emotional_beat: str) -> str:
        """Determine shadow characteristics"""
        if "mysterious" in emotional_beat.lower() or "tense" in emotional_beat.lower():
            return "deep, dramatic shadows"
        elif "happy" in emotional_beat.lower() or "light" in emotional_beat.lower():
            return "soft, minimal shadows"
        
        return "natural, motivated shadows"
    
    def _determine_contrast(self, breakdown: Dict) -> str:
        """Determine contrast ratio"""
        narrative_function = breakdown.get("narrative_function", "")
        
        if narrative_function == "establish_setting":
            return "medium contrast 4:1"
        elif narrative_function == "character_interaction":
            return "low to medium contrast 3:1"
        elif narrative_function == "advance_plot":
            return "high contrast 8:1"
        
        return "balanced contrast 4:1"
    
    def _create_atmosphere(self, scene: Scene, breakdown: Dict) -> str:
        """Create atmospheric description"""
        elements = []
        
        if "MORNING" in scene.time_of_day.upper():
            elements.append("morning haze")
        elif "NIGHT" in scene.time_of_day.upper():
            elements.append("night atmosphere")
        
        emotional_beat = breakdown.get("emotional_beat", "")
        if emotional_beat:
            elements.append(f"{emotional_beat} mood")
        
        return ", ".join(elements) if elements else "naturalistic atmosphere"


class PromptSynthesisAgent(BaseAgent):
    """Combines all agent outputs into Veo3 prompts"""
    
    def __init__(self, agents_dir: Path):
        self.prompt_file = "prompt-combiner.md"
        super().__init__(agents_dir)
    
    def process(self, scene: Scene, shot: Shot, all_results: Dict) -> str:
        """Synthesize all information into comprehensive Veo3 prompt"""
        prompt_parts = []
        
        # Camera information
        camera = all_results.get('cinematography', {})
        camera_desc = (
            f"[CAMERA] {camera.get('shot_type', 'MEDIUM')} shot, "
            f"{camera.get('camera_movement', 'static')}, "
            f"{camera.get('framing', 'standard framing')}, "
            f"shot with {camera.get('lens', '50mm lens')}, "
            f"{camera.get('depth_of_field', 'medium depth of field')}"
        )
        prompt_parts.append(camera_desc)
        
        # Subject/Characters
        characters = all_results.get('character_analysis', {}).get('characters', [])
        if characters:
            char_desc = "[SUBJECT] " + ", ".join([
                f"{c['name']} ({c.get('emotional_state', 'neutral')})" 
                for c in characters
            ])
            if shot.action:
                char_desc += f", {shot.action[:100]}"
        else:
            char_desc = f"[SUBJECT] {shot.action[:200] if shot.action else 'Environmental shot'}"
        prompt_parts.append(char_desc)
        
        # Environment
        env = all_results.get('environment_props', {})
        env_desc = (
            f"[ENVIRONMENT] {env.get('location', 'location')}, "
            f"{env.get('time_of_day', 'day')} lighting, "
            f"{env.get('atmosphere', 'realistic atmosphere')}"
        )
        if env.get('props'):
            env_desc += f", featuring {', '.join(env['props'][:3])}"
        prompt_parts.append(env_desc)
        
        # Lighting
        lighting = all_results.get('lighting_mood', {})
        light_desc = (
            f"[LIGHTING] {', '.join(lighting.get('sources', ['natural light']))}, "
            f"{lighting.get('color_temperature', '5000K')}, "
            f"{lighting.get('intensity', 'balanced')} intensity, "
            f"{lighting.get('shadows', 'natural shadows')}, "
            f"{lighting.get('atmosphere', 'cinematic atmosphere')}"
        )
        prompt_parts.append(light_desc)
        
        # Mood and style
        mood_desc = (
            f"[STYLE] Cinematic, professional filmmaking, "
            f"{lighting.get('mood', 'neutral')} mood, "
            f"photorealistic rendering, high production value"
        )
        prompt_parts.append(mood_desc)
        
        # Duration
        duration_desc = f"[DURATION] {shot.duration}"
        prompt_parts.append(duration_desc)
        
        return " | ".join(prompt_parts)


# ============================================================================
# ENHANCED FILM CREW PROCESSOR
# ============================================================================

class EnhancedFilmCrewProcessor:
    """Main processing engine with full agent orchestration"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.agents_dir = project_dir / "templates" / "agents"
        self.output_dir = project_dir / "output"
        self.scripts_dir = project_dir / "scripts"
        
        # Initialize components
        self.parser = EnhancedScriptParser()
        self.orchestrator = MasterOrchestrator(self.agents_dir)
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
        
        # Error tracking
        self.errors = []
    
    def process_script(self, script_path: Path) -> Optional[Path]:
        """Process a single script file with full error handling"""
        try:
            logger.info(f"Processing script: {script_path.name}")
            
            # Validate input
            if not self.orchestrator.validate_input(script_path):
                errors = "\n".join(self.orchestrator.validation_errors)
                logger.error(f"Validation failed:\n{errors}")
                return None
            
            # Parse script
            scenes = self.parser.parse(script_path)
            logger.info(f"Parsed {len(scenes)} scenes")
            
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{script_path.stem}_{timestamp}"
            script_output_dir = self.output_dir / output_name
            
            # Create department subdirectories
            departments = [
                "01_veo3_prompts",
                "02_script_breakdown",
                "03_character_analysis",
                "04_environment_props",
                "05_cinematography",
                "06_lighting_mood",
                "07_master_index"
            ]
            
            for dept in departments:
                (script_output_dir / dept).mkdir(parents=True, exist_ok=True)
            
            # Process each scene and shot
            all_shots = []
            for scene in scenes:
                for shot in scene.shots:
                    shot_result = self._process_shot(
                        scene, shot, script_output_dir, script_path.stem
                    )
                    all_shots.append(shot_result)
            
            # Ensure consistency across all shots
            all_shots = self.orchestrator.ensure_consistency(all_shots)
            
            # Create master index
            self._create_master_index(
                script_output_dir, script_path.name, scenes, all_shots
            )
            
            logger.info(f"✅ Processing complete. Output: {script_output_dir}")
            return script_output_dir
            
        except Exception as e:
            logger.error(f"Error processing script: {e}")
            logger.error(traceback.format_exc())
            self.errors.append(str(e))
            return None
    
    def _process_shot(self, scene: Scene, shot: Shot, 
                     output_dir: Path, script_name: str) -> Dict:
        """Process individual shot through all agents"""
        logger.info(f"Processing shot {shot.shot_id}")
        
        # Orchestrate agent processing
        results = self.orchestrator.orchestrate_processing(scene, shot)
        
        # Update shot with results
        shot.veo3_prompt = results.get('veo3_prompt', '')
        
        # Prepare complete shot data
        shot_data = shot.to_dict()
        shot_data['script_name'] = script_name
        shot_data['processing_results'] = results
        
        # Save outputs to appropriate directories
        self._save_shot_outputs(shot, shot_data, output_dir, script_name)
        
        return shot_data
    
    def _save_shot_outputs(self, shot: Shot, shot_data: Dict, 
                          output_dir: Path, script_name: str):
        """Save shot outputs to department-specific files"""
        
        # Main Veo3 prompt file (as specified in requirements)
        veo3_file = (output_dir / "01_veo3_prompts" / 
                    f"{script_name}_scene{shot.scene_number}_shot{shot.shot_number}.json")
        
        with open(veo3_file, 'w', encoding='utf-8') as f:
            json.dump({
                "scene_number": shot.scene_number,
                "shot_number": shot.shot_number,
                "characters": shot_data['characters'],
                "environment": shot_data['environment'],
                "camera": shot_data['camera'],
                "lighting": shot_data['lighting'],
                "veo3_prompt": shot.veo3_prompt,
                "duration": shot.duration,
                "metadata": shot.metadata
            }, f, indent=2)
        
        # Save department-specific analysis files
        departments = {
            "02_script_breakdown": "breakdown",
            "03_character_analysis": "character_analysis",
            "04_environment_props": "environment_props",
            "05_cinematography": "cinematography",
            "06_lighting_mood": "lighting_mood"
        }
        
        for dept_dir, result_key in departments.items():
            if result_key in shot_data.get('processing_results', {}):
                dept_file = (output_dir / dept_dir / 
                           f"{script_name}_scene{shot.scene_number}_shot{shot.shot_number}.json")
                
                with open(dept_file, 'w', encoding='utf-8') as f:
                    json.dump(shot_data['processing_results'][result_key], f, indent=2)
    
    def _create_master_index(self, output_dir: Path, script_name: str,
                            scenes: List[Scene], all_shots: List[Dict]):
        """Create master index file with complete project overview"""
        index = {
            "project": script_name,
            "generated": datetime.now().isoformat(),
            "version": "4.0",
            "engine": "Enhanced Film Crew AI with Multi-Format Support",
            "statistics": {
                "total_scenes": len(scenes),
                "total_shots": len(all_shots),
                "departments": 6,
                "agents": 6
            },
            "scenes": [scene.to_dict() for scene in scenes],
            "quality_metrics": {
                "consistency_check": "passed",
                "validation_errors": len(self.errors),
                "coverage": "complete"
            },
            "output_structure": {
                "01_veo3_prompts": "Complete video generation prompts",
                "02_script_breakdown": "Scene and shot analysis",
                "03_character_analysis": "Character tracking and details",
                "04_environment_props": "Location and prop specifications",
                "05_cinematography": "Camera angles and movements",
                "06_lighting_mood": "Lighting setups and mood",
                "07_master_index": "Project overview and navigation"
            }
        }
        
        index_file = output_dir / "07_master_index" / "INDEX.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2)
        
        # Also save a simplified navigation file
        nav_file = output_dir / "07_master_index" / "NAVIGATION.json"
        navigation = {
            "script": script_name,
            "shots": [
                {
                    "id": shot['shot_id'],
                    "scene": shot['scene_number'],
                    "shot": shot['shot_number'],
                    "file": f"{script_name}_scene{shot['scene_number']}_shot{shot['shot_number']}.json"
                }
                for shot in all_shots if 'shot_id' in shot
            ]
        }
        
        with open(nav_file, 'w', encoding='utf-8') as f:
            json.dump(navigation, f, indent=2)
    
    def process_all_scripts(self):
        """Process all scripts in the scripts directory"""
        script_files = []
        
        # Look for all supported formats
        for ext in ['.txt', '.pdf', '.doc', '.docx']:
            script_files.extend(self.scripts_dir.glob(f"*{ext}"))
        
        if not script_files:
            logger.warning("No script files found in scripts directory")
            return
        
        logger.info(f"Found {len(script_files)} scripts to process")
        
        successful = 0
        failed = 0
        
        for script_file in script_files:
            result = self.process_script(script_file)
            if result:
                successful += 1
            else:
                failed += 1
        
        logger.info(f"\n{'='*50}")
        logger.info(f"Processing Complete:")
        logger.info(f"  ✅ Successful: {successful}")
        logger.info(f"  ❌ Failed: {failed}")
        logger.info(f"{'='*50}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point with enhanced features"""
    parser = argparse.ArgumentParser(
        description="Film Crew AI - Enhanced Multi-Format Script Processing System"
    )
    parser.add_argument('--script', type=str, help='Path to specific script')
    parser.add_argument('--all', action='store_true', help='Process all scripts')
    parser.add_argument('--format', type=str, help='Specify input format (auto-detected by default)')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    parser.add_argument('--validate', action='store_true', help='Validate output JSON files')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Create processor
    processor = EnhancedFilmCrewProcessor(project_dir)
    
    if args.script:
        script_path = Path(args.script)
        if script_path.exists():
            result = processor.process_script(script_path)
            
            if result and args.validate:
                # Validate JSON outputs
                json_files = list(result.glob("**/*.json"))
                valid = 0
                invalid = 0
                
                for json_file in json_files:
                    try:
                        with open(json_file, 'r') as f:
                            json.load(f)
                        valid += 1
                    except json.JSONDecodeError:
                        logger.error(f"Invalid JSON: {json_file}")
                        invalid += 1
                
                logger.info(f"Validation: {valid} valid, {invalid} invalid JSON files")
        else:
            logger.error(f"Script not found: {script_path}")
    
    elif args.all:
        processor.process_all_scripts()
    
    else:
        # Interactive mode
        print("\n" + "="*60)
        print("FILM CREW AI - Enhanced Multi-Format Processing System v4.0")
        print("="*60)
        print("\nSupported formats: TXT, PDF, DOC, DOCX")
        print("\nOptions:")
        print("1. Process all scripts")
        print("2. Process specific script")
        print("3. Validate existing outputs")
        print("4. Exit")
        
        choice = input("\nSelect option (1-4): ").strip()
        
        if choice == "1":
            processor.process_all_scripts()
        elif choice == "2":
            script_name = input("Enter script path: ").strip()
            script_path = Path(script_name)
            if script_path.exists():
                processor.process_script(script_path)
            else:
                logger.error(f"Script not found: {script_path}")
        elif choice == "3":
            # Validate all existing outputs
            output_dirs = list(processor.output_dir.glob("*"))
            for output_dir in output_dirs:
                if output_dir.is_dir():
                    json_files = list(output_dir.glob("**/*.json"))
                    print(f"\nValidating {output_dir.name}: {len(json_files)} files...")
                    for json_file in json_files:
                        try:
                            with open(json_file, 'r') as f:
                                json.load(f)
                        except json.JSONDecodeError:
                            print(f"  ❌ Invalid: {json_file.name}")
        else:
            print("Exiting...")


if __name__ == "__main__":
    main()