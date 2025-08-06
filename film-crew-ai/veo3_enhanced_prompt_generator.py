#!/usr/bin/env python3
"""
Enhanced Veo3 Natural Language Prompt Generator
Includes character consistency and voice-over integration
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
import logging
from collections import defaultdict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Veo3EnhancedGenerator')


@dataclass
class CharacterProfile:
    """Complete character profile with consistency tracking"""
    name: str
    age: str = ""
    ethnicity: str = ""
    gender: str = ""
    physical_description: str = ""
    wardrobe_style: str = ""
    personality_traits: List[str] = field(default_factory=list)
    emotional_arc: Dict[str, str] = field(default_factory=dict)  # scene_number: emotional_state
    relationships: Dict[str, str] = field(default_factory=dict)  # other_character: relationship
    voice_over_lines: List[Dict] = field(default_factory=list)  # scene, text
    
    def get_description(self, scene_number: str = None) -> str:
        """Get character description for a specific scene"""
        elements = []
        
        # Basic description
        if self.age and self.gender:
            elements.append(f"{self.name}, {self.age}, {self.gender}")
        else:
            elements.append(self.name)
        
        if self.ethnicity:
            elements.append(self.ethnicity)
        
        if self.physical_description:
            elements.append(self.physical_description)
        
        # Scene-specific emotional state
        if scene_number and scene_number in self.emotional_arc:
            elements.append(f"({self.emotional_arc[scene_number]})")
        
        # Wardrobe
        if self.wardrobe_style:
            elements.append(f"wearing {self.wardrobe_style}")
        
        return ", ".join(elements)


@dataclass
class EnhancedVeo3Prompt:
    """Enhanced Veo3 prompt with character and VO support"""
    subject: str
    characters: str  # NEW: Dedicated character descriptions
    context: str
    action: str
    dialogue_and_vo: str  # NEW: Dialogue and voice-over content
    style: str
    camera_motion: str
    composition: str
    ambiance: str
    texture: str
    environment: str
    
    def to_text(self) -> str:
        """Convert to enhanced natural language format"""
        sections = []
        
        if self.subject:
            sections.append(f"Subject: {self.subject}")
        
        if self.characters:
            sections.append(f"Characters: {self.characters}")
        
        if self.context:
            sections.append(f"Context: {self.context}")
        
        if self.action:
            sections.append(f"Action: {self.action}")
        
        if self.dialogue_and_vo:
            sections.append(f"Dialogue/VO: {self.dialogue_and_vo}")
        
        if self.style:
            sections.append(f"Style: {self.style}")
        
        if self.camera_motion:
            sections.append(f"Camera Motion: {self.camera_motion}")
        
        if self.composition:
            sections.append(f"Composition: {self.composition}")
        
        if self.ambiance:
            sections.append(f"Ambiance: {self.ambiance}")
        
        if self.texture:
            sections.append(f"Texture: {self.texture}")
        
        if self.environment:
            sections.append(f"Environment: {self.environment}")
        
        return "\n".join(sections)


class CharacterConsistencyTracker:
    """Tracks and maintains character consistency across scenes"""
    
    def __init__(self):
        self.characters: Dict[str, CharacterProfile] = {}
        self.character_appearances: Dict[str, List[str]] = defaultdict(list)  # character: [scene_numbers]
        
    def load_character_profiles(self, profiles_data: Dict):
        """Load character profiles from script analysis"""
        # Example profiles for the ES Health Vignettes
        default_profiles = {
            "Dr. Jalen Roy": CharacterProfile(
                name="Dr. Jalen Roy",
                age="40s",
                ethnicity="African-American",
                gender="male",
                physical_description="professional appearance, tired eyes in 2025, rejuvenated in 2035",
                wardrobe_style="white coat over business casual",
                personality_traits=["dedicated", "overworked", "compassionate"],
                emotional_arc={
                    "1": "exhausted",
                    "2": "overwhelmed", 
                    "3": "hopeful",
                    "4": "empowered"
                }
            ),
            "Dr. Roy": CharacterProfile(  # Alias for Dr. Jalen Roy
                name="Dr. Roy",
                age="40s",
                ethnicity="African-American",
                gender="male",
                physical_description="professional appearance",
                wardrobe_style="white coat over business casual"
            ),
            "Michael": CharacterProfile(
                name="Michael",
                age="62",
                ethnicity="Hispanic",
                gender="male",
                physical_description="overweight, weathered from farm work",
                wardrobe_style="practical work clothes",
                personality_traits=["resilient", "independent"],
                emotional_arc={
                    "2": "concerned about health",
                    "3": "relieved"
                }
            ),
            "Lanie": CharacterProfile(
                name="Lanie",
                age="40s",
                ethnicity="white",
                gender="female",
                physical_description="dark hair, average build",
                wardrobe_style="casual mom attire",
                personality_traits=["caring", "overwhelmed", "multitasking"],
                emotional_arc={
                    "3": "stressed but managing"
                }
            ),
            "Priya": CharacterProfile(
                name="Priya",
                age="76",
                ethnicity="South Asian",
                gender="female",
                physical_description="relatively healthy senior",
                wardrobe_style="comfortable home wear",
                personality_traits=["independent", "tech-savvy for her age"],
                emotional_arc={
                    "4": "content and secure"
                }
            ),
            "Sarah": CharacterProfile(
                name="Sarah",
                age="30s",
                gender="female",
                physical_description="tired eyes, worn backpack",
                wardrobe_style="casual professional",
                personality_traits=["determined", "conflicted"],
                emotional_arc={
                    "1": "searching",
                    "2": "anxious",
                    "3": "confrontational",
                    "4": "vulnerable",
                    "5": "torn"
                }
            ),
            "James": CharacterProfile(
                name="James",
                age="40s",
                gender="male",
                physical_description="worn, nervous energy",
                wardrobe_style="business suit, slightly disheveled",
                personality_traits=["guilt-ridden", "desperate"],
                emotional_arc={
                    "1": "nervous",
                    "2": "pleading",
                    "3": "defensive",
                    "4": "hopeful"
                }
            )
        }
        
        # Merge with provided profiles or use defaults
        if profiles_data:
            for name, data in profiles_data.items():
                if name in default_profiles:
                    # Update existing profile
                    profile = default_profiles[name]
                    for key, value in data.items():
                        if hasattr(profile, key):
                            setattr(profile, key, value)
                else:
                    # Create new profile
                    default_profiles[name] = CharacterProfile(name=name, **data)
        
        self.characters = default_profiles
    
    def track_appearance(self, character_name: str, scene_number: str):
        """Track character appearance in a scene"""
        self.character_appearances[character_name].append(scene_number)
    
    def get_character_description(self, character_name: str, scene_number: str) -> str:
        """Get consistent character description for a scene"""
        # Handle character name variations
        if character_name == "Dr. Roy":
            character_name = "Dr. Jalen Roy"
        
        if character_name in self.characters:
            return self.characters[character_name].get_description(scene_number)
        
        # Return basic name if no profile
        return character_name
    
    def add_voice_over(self, character_name: str, scene_number: str, vo_text: str):
        """Add voice-over line to character profile"""
        if character_name in self.characters:
            self.characters[character_name].voice_over_lines.append({
                'scene': scene_number,
                'text': vo_text
            })


class EnhancedVeo3PromptSynthesizer:
    """Enhanced synthesizer with character consistency and VO support"""
    
    def __init__(self):
        self.character_tracker = CharacterConsistencyTracker()
        self.character_tracker.load_character_profiles({})
        
    def synthesize_enhanced_prompt(self,
                                  scene_data: Dict,
                                  shot_data: Dict,
                                  agent_outputs: Dict,
                                  voice_overs: List[Dict] = None) -> EnhancedVeo3Prompt:
        """Create enhanced prompt with character consistency and VOs"""
        
        # Extract scene number
        scene_number = str(scene_data.get('scene_number', '1'))
        
        # Extract character data
        characters_in_shot = self._extract_characters(shot_data, agent_outputs)
        
        # Build character descriptions with consistency
        character_descriptions = self._build_character_descriptions(
            characters_in_shot, scene_number
        )
        
        # Extract voice-overs
        vo_content = self._extract_voice_overs(voice_overs, scene_number)
        
        # Build standard elements
        subject = self._build_subject(shot_data, characters_in_shot, agent_outputs.get('environment', {}))
        context = self._build_context(scene_data, agent_outputs.get('environment', {}), agent_outputs.get('lighting', {}))
        action = self._build_action(shot_data, characters_in_shot, agent_outputs.get('environment', {}))
        
        # Build dialogue and VO section
        dialogue_and_vo = self._build_dialogue_and_vo(shot_data, vo_content)
        
        # Style elements
        style = self._build_style(scene_data, agent_outputs.get('lighting', {}), agent_outputs.get('camera', {}))
        camera_motion = self._build_camera_motion(agent_outputs.get('camera', {}), shot_data)
        composition = self._build_composition(agent_outputs.get('camera', {}), characters_in_shot, agent_outputs.get('environment', {}))
        ambiance = self._build_ambiance(agent_outputs.get('lighting', {}), agent_outputs.get('sound', {}), scene_data)
        texture = self._build_texture(agent_outputs.get('environment', {}), agent_outputs.get('lighting', {}), characters_in_shot)
        environment = self._build_environment(agent_outputs.get('environment', {}), scene_data)
        
        return EnhancedVeo3Prompt(
            subject=subject,
            characters=character_descriptions,
            context=context,
            action=action,
            dialogue_and_vo=dialogue_and_vo,
            style=style,
            camera_motion=camera_motion,
            composition=composition,
            ambiance=ambiance,
            texture=texture,
            environment=environment
        )
    
    def _extract_characters(self, shot_data: Dict, agent_outputs: Dict) -> List[Dict]:
        """Extract all characters in the shot"""
        characters = []
        
        # From shot data
        if 'characters' in shot_data:
            characters.extend(shot_data['characters'])
        
        # From agent outputs
        if 'characters' in agent_outputs:
            characters.extend(agent_outputs['characters'])
        
        # From dialogue
        if 'dialogue' in shot_data:
            for dialogue_line in shot_data.get('dialogue', []):
                if isinstance(dialogue_line, dict) and 'character' in dialogue_line:
                    char_name = dialogue_line['character'].split('(')[0].strip()
                    if not any(c.get('name') == char_name for c in characters):
                        characters.append({'name': char_name})
        
        return characters
    
    def _build_character_descriptions(self, characters: List[Dict], scene_number: str) -> str:
        """Build consistent character descriptions"""
        if not characters:
            return ""
        
        descriptions = []
        
        for char_data in characters:
            char_name = char_data.get('name', '')
            if char_name:
                # Track appearance
                self.character_tracker.track_appearance(char_name, scene_number)
                
                # Get consistent description
                description = self.character_tracker.get_character_description(
                    char_name, scene_number
                )
                descriptions.append(description)
        
        if len(descriptions) == 1:
            return descriptions[0]
        elif len(descriptions) == 2:
            return f"{descriptions[0]} and {descriptions[1]}"
        else:
            return f"{', '.join(descriptions[:-1])}, and {descriptions[-1]}"
    
    def _extract_voice_overs(self, voice_overs: List[Dict], scene_number: str) -> List[Dict]:
        """Extract and process voice-overs"""
        if not voice_overs:
            return []
        
        processed_vos = []
        for vo in voice_overs:
            char_name = vo.get('character', 'Narrator')
            vo_text = vo.get('text', '')
            
            # Track in character profile
            self.character_tracker.add_voice_over(char_name, scene_number, vo_text)
            
            processed_vos.append({
                'character': char_name,
                'text': vo_text,
                'timing': vo.get('timing', 'during_scene')
            })
        
        return processed_vos
    
    def _build_dialogue_and_vo(self, shot_data: Dict, vo_content: List[Dict]) -> str:
        """Build dialogue and voice-over section"""
        elements = []
        
        # Add dialogue
        dialogue = shot_data.get('dialogue', [])
        if dialogue:
            if isinstance(dialogue[0], str):
                # Simple dialogue list
                if len(dialogue) == 1:
                    elements.append(f"Dialogue: \"{dialogue[0][:100]}...\"")
                else:
                    elements.append("Characters exchange dialogue")
            elif isinstance(dialogue[0], dict):
                # Structured dialogue
                for d in dialogue[:2]:  # Limit to first 2 exchanges
                    char = d.get('character', 'Character')
                    line = d.get('line', '')[:100]
                    elements.append(f"{char}: \"{line}...\"")
        
        # Add voice-overs
        if vo_content:
            for vo in vo_content[:2]:  # Limit to first 2 VOs
                char = vo['character']
                text = vo['text'][:150]
                timing = vo.get('timing', 'during_scene')
                
                if timing == 'transitional':
                    elements.append(f"Voice-over (transition) - {char}: \"{text}...\"")
                else:
                    elements.append(f"Voice-over - {char}: \"{text}...\"")
        
        return " | ".join(elements) if elements else "No dialogue in this shot."
    
    # Inherit other build methods from original synthesizer
    def _build_subject(self, shot_data: Dict, characters: List, environment: Dict) -> str:
        """Build subject with character focus"""
        elements = []
        
        # Shot type prefix
        shot_type = shot_data.get('shot_type', 'medium shot')
        if 'ESTABLISHING' in shot_type.upper():
            elements.append("Establishing shot:")
        elif 'CLOSE' in shot_type.upper():
            elements.append("Close-up:")
        elif 'WIDE' in shot_type.upper():
            elements.append("Wide shot:")
        
        # Character focus
        if characters:
            char_names = [c.get('name', 'Character') for c in characters[:2]]
            if len(char_names) == 1:
                elements.append(f"Focus on {char_names[0]}")
            else:
                elements.append(f"Focus on {' and '.join(char_names)}")
        
        # Location context
        location = environment.get('location', 'location')
        time_of_day = environment.get('time_of_day', 'day')
        elements.append(f"in {location} during {time_of_day}")
        
        return ' '.join(elements) + '.'
    
    def _build_context(self, scene_data: Dict, environment: Dict, lighting: Dict) -> str:
        """Build context with scene details"""
        elements = []
        
        location = environment.get('location', 'space')
        setting_desc = environment.get('setting_description', '')
        
        # Main setting
        if setting_desc:
            elements.append(setting_desc)
        else:
            elements.append(f"The scene takes place in {location}")
        
        # Time period for flashbacks
        if scene_data.get('scene_type') == 'FLASHBACK':
            elements.append("(FLASHBACK SEQUENCE)")
        
        # Environmental details
        if 'INT' in scene_data.get('heading', ''):
            elements.append("Interior location with")
            if 'OFFICE' in location.upper():
                elements.append("professional furnishings and work environment")
            elif 'HOME' in location.upper():
                elements.append("residential comfort and personal touches")
            elif 'COFFEE' in location.upper():
                elements.append("public space ambiance and casual seating")
        else:
            elements.append("Exterior location featuring")
            if 'STREET' in location.upper():
                elements.append("urban environment and city activity")
            elif 'FARM' in location.upper():
                elements.append("rural landscape and agricultural setting")
        
        # Lighting context
        light_sources = lighting.get('sources', [])
        if light_sources:
            if 'natural' in str(light_sources).lower():
                elements.append("Natural lighting dominates the scene")
            elif 'practical' in str(light_sources).lower():
                elements.append("Practical lights provide motivated illumination")
        
        return '. '.join(elements) + '.'
    
    def _build_action(self, shot_data: Dict, characters: List, environment: Dict) -> str:
        """Build action with character movements"""
        elements = []
        
        # Primary action
        action = shot_data.get('action', '')
        if action:
            elements.append(action[:200])
        
        # Character-specific actions
        for char in characters:
            char_name = char.get('name', '')
            movement = char.get('movement', '')
            emotional_state = char.get('emotional_state', '')
            
            if movement:
                elements.append(f"{char_name} {movement}")
            if emotional_state:
                elements.append(f"{char_name} displays {emotional_state}")
        
        # Environmental movement
        time_of_day = environment.get('time_of_day', 'DAY')
        if 'DAWN' in time_of_day.upper():
            elements.append("Dawn light gradually reveals details")
        elif 'DUSK' in time_of_day.upper():
            elements.append("Sunset colors paint the scene")
        
        return '. '.join(elements) if elements else "Subtle movement maintains visual interest."
    
    def _build_style(self, scene_data: Dict, lighting: Dict, camera: Dict) -> str:
        """Build visual style description"""
        elements = []
        
        mood = lighting.get('mood', 'naturalistic')
        scene_type = scene_data.get('scene_type', 'PRESENT')
        
        # Base style
        if scene_type == 'FLASHBACK':
            elements.append("Flashback treatment with memory-like quality")
        elif scene_type == 'DREAM':
            elements.append("Dream sequence with ethereal atmosphere")
        else:
            elements.append(f"{mood.capitalize()} visual treatment")
        
        # Color grading
        if lighting.get('color_temperature'):
            temp = lighting['color_temperature']
            if '3' in str(temp)[:1]:
                elements.append("warm tones")
            elif '6' in str(temp)[:1]:
                elements.append("cool palette")
            else:
                elements.append("neutral colors")
        
        return '. '.join(elements) + '.'
    
    def _build_camera_motion(self, camera: Dict, shot_data: Dict) -> str:
        """Build camera movement description"""
        movement = camera.get('camera_movement', 'static')
        shot_type = camera.get('shot_type', 'MEDIUM')
        
        if 'ESTABLISHING' in shot_type.upper():
            return "Slow, revealing camera movement establishes the space with cinematic grandeur."
        elif 'static' in movement.lower():
            return "Locked-off camera holds steady, letting performance drive the scene."
        elif 'dolly' in movement.lower():
            return "Smooth dolly movement adds dimensional depth to the composition."
        elif 'handheld' in movement.lower():
            return "Handheld camera work creates intimate, documentary-style immediacy."
        else:
            return f"Camera employs {movement} to enhance visual storytelling."
    
    def _build_composition(self, camera: Dict, characters: List, environment: Dict) -> str:
        """Build composition description"""
        elements = []
        
        framing = camera.get('framing', 'balanced framing')
        elements.append(f"Composition features {framing}")
        
        if characters:
            if len(characters) == 1:
                elements.append("with single subject prominence")
            elif len(characters) == 2:
                elements.append("balancing two-shot dynamics")
            else:
                elements.append("orchestrating ensemble staging")
        
        depth = camera.get('depth_of_field', 'medium')
        if 'shallow' in depth.lower():
            elements.append("Shallow focus isolates subjects")
        elif 'deep' in depth.lower():
            elements.append("Deep focus reveals layered space")
        
        return '. '.join(elements) + '.'
    
    def _build_ambiance(self, lighting: Dict, sound: Dict, scene_data: Dict) -> str:
        """Build ambiance with mood"""
        mood = lighting.get('mood', 'neutral')
        time = scene_data.get('time_of_day', 'day')
        
        elements = []
        
        if 'NIGHT' in time.upper():
            elements.append("Nocturnal atmosphere")
        elif 'DAWN' in time.upper():
            elements.append("Dawn's quiet anticipation")
        elif 'DUSK' in time.upper():
            elements.append("Golden hour magic")
        else:
            elements.append("Daylight clarity")
        
        elements.append(f"creates {mood} mood")
        
        if sound and 'ambience' in sound:
            elements.append(f"with {', '.join(sound['ambience'][:2])}")
        
        return '. '.join(elements) + '.'
    
    def _build_texture(self, environment: Dict, lighting: Dict, characters: List) -> str:
        """Build texture description"""
        elements = []
        
        location = environment.get('location', 'space')
        
        # Surface textures
        if 'INT' in location.upper():
            elements.extend(["Interior surfaces", "furniture textures"])
        else:
            elements.extend(["Natural textures", "environmental materials"])
        
        # Character clothing
        for char in characters[:2]:
            if 'wardrobe' in char:
                elements.append(f"{char['name']}'s {char['wardrobe']}")
        
        # Light quality
        intensity = lighting.get('intensity', 'balanced')
        elements.append(f"{intensity} light quality")
        
        return ', '.join(elements[:5]) + '.'
    
    def _build_environment(self, environment: Dict, scene_data: Dict) -> str:
        """Build environment summary"""
        location = environment.get('location', 'location')
        time = environment.get('time_of_day', 'day')
        
        elements = []
        
        if 'INT' in scene_data.get('heading', ''):
            elements.append(f"Interior {location}")
        else:
            elements.append(f"Exterior {location}")
        
        elements.append(f"during {time}")
        
        # Scene type modifier
        scene_type = scene_data.get('scene_type', 'PRESENT')
        if scene_type == 'FLASHBACK':
            elements.append("(memory sequence)")
        elif scene_type == 'DREAM':
            elements.append("(dream state)")
        
        elements.append("provides narrative setting")
        
        return '. '.join(elements) + '.'


class EnhancedVeo3Processor:
    """Process scripts with enhanced character and VO support"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.synthesizer = EnhancedVeo3PromptSynthesizer()
        
    def process_with_enhancement(self):
        """Process all shots with character consistency and VOs"""
        
        # Create enhanced output directory
        enhanced_dir = self.output_dir / "Veo3_Enhanced_Prompts"
        enhanced_dir.mkdir(exist_ok=True)
        
        # Load voice-overs if available
        voice_overs = self._load_voice_overs()
        
        # Find all shot files
        shot_files = []
        
        # Check different possible locations
        if (self.output_dir / "02_Shots").exists():
            shot_files = list((self.output_dir / "02_Shots").glob("*.json"))
        elif (self.output_dir / "05_Veo3_Prompts").exists():
            shot_files = list((self.output_dir / "05_Veo3_Prompts").glob("*.json"))
        
        logger.info(f"Processing {len(shot_files)} shots with character enhancement")
        
        for shot_file in shot_files:
            try:
                with open(shot_file, 'r') as f:
                    shot_data = json.load(f)
                
                # Extract scene number from filename or data
                scene_number = self._extract_scene_number(shot_file.name, shot_data)
                
                # Get VOs for this scene
                scene_vos = [vo for vo in voice_overs if vo.get('scene') == scene_number]
                
                # Create mock agent outputs
                agent_outputs = self._extract_agent_data(shot_data)
                
                # Generate enhanced prompt
                enhanced_prompt = self.synthesizer.synthesize_enhanced_prompt(
                    scene_data={'scene_number': scene_number, 
                               'heading': shot_data.get('scene_heading', ''),
                               'time_of_day': shot_data.get('time_of_day', 'DAY'),
                               'scene_type': shot_data.get('scene_type', 'PRESENT')},
                    shot_data=shot_data,
                    agent_outputs=agent_outputs,
                    voice_overs=scene_vos
                )
                
                # Save enhanced prompt
                output_file = enhanced_dir / f"{shot_file.stem}_enhanced.txt"
                with open(output_file, 'w') as f:
                    f.write(enhanced_prompt.to_text())
                
                logger.info(f"Generated enhanced prompt: {output_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {shot_file}: {e}")
        
        # Create master file
        self._create_master_file(enhanced_dir)
    
    def _load_voice_overs(self) -> List[Dict]:
        """Load voice-overs from output directory"""
        voice_overs = []
        
        # Check for VO files
        vo_dir = self.output_dir / "03_VoiceOvers"
        if vo_dir.exists():
            vo_file = vo_dir / "all_voiceovers.json"
            if vo_file.exists():
                with open(vo_file, 'r') as f:
                    voice_overs = json.load(f)
                logger.info(f"Loaded {len(voice_overs)} voice-overs")
        
        # Also check VO segments directory
        vo_segments_dir = self.output_dir / "03_VO_Segments"
        if vo_segments_dir.exists():
            for vo_file in vo_segments_dir.glob("*.json"):
                with open(vo_file, 'r') as f:
                    vo_data = json.load(f)
                    if 'content' in vo_data:
                        voice_overs.append({
                            'character': vo_data.get('characters_mentioned', ['Narrator'])[0] if vo_data.get('characters_mentioned') else 'Narrator',
                            'text': vo_data['content'],
                            'scene': self._extract_scene_from_filename(vo_file.name)
                        })
        
        return voice_overs
    
    def _extract_scene_number(self, filename: str, data: Dict) -> str:
        """Extract scene number from filename or data"""
        # Try from data first
        if 'scene_number' in data:
            return str(data['scene_number'])
        
        # Try from filename
        match = re.search(r'scene(\d+)', filename)
        if match:
            return match.group(1)
        
        # Try vignette pattern
        match = re.search(r'vignette(\d+)', filename)
        if match:
            return match.group(1)
        
        return "1"
    
    def _extract_scene_from_filename(self, filename: str) -> str:
        """Extract scene number from VO filename"""
        match = re.search(r'vignette(\d+)|scene(\d+)', filename)
        if match:
            return match.group(1) or match.group(2)
        return "1"
    
    def _extract_agent_data(self, shot_data: Dict) -> Dict:
        """Extract agent-like data from shot"""
        return {
            'camera': shot_data.get('camera', {}),
            'lighting': shot_data.get('lighting', {}),
            'environment': shot_data.get('environment', {}),
            'characters': shot_data.get('characters', []),
            'sound': shot_data.get('sound', {})
        }
    
    def _create_master_file(self, enhanced_dir: Path):
        """Create master file with all enhanced prompts"""
        all_prompts = []
        
        for txt_file in sorted(enhanced_dir.glob("*.txt")):
            if txt_file.name != "ALL_ENHANCED_PROMPTS.txt":
                with open(txt_file, 'r') as f:
                    content = f.read()
                    all_prompts.append(f"\n{'='*60}\n{txt_file.stem}\n{'='*60}\n\n{content}\n")
        
        master_file = enhanced_dir / "ALL_ENHANCED_PROMPTS.txt"
        with open(master_file, 'w') as f:
            f.write("ENHANCED VEO3 PROMPTS WITH CHARACTER CONSISTENCY & VOICE-OVERS\n")
            f.write("="*60 + "\n\n")
            f.write("".join(all_prompts))
        
        logger.info(f"Created master enhanced file: {master_file}")


def main():
    """Test enhanced prompt generation"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate enhanced Veo3 prompts with character consistency and VOs"
    )
    parser.add_argument('--output-dir', type=str, help='Path to script output directory')
    parser.add_argument('--test', action='store_true', help='Run test mode')
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode
        synthesizer = EnhancedVeo3PromptSynthesizer()
        
        test_scene = {
            'scene_number': '1',
            'heading': 'INT. COFFEE SHOP - DAY',
            'time_of_day': 'MORNING',
            'scene_type': 'PRESENT'
        }
        
        test_shot = {
            'shot_type': 'MEDIUM',
            'shot_id': '1-002',
            'action': 'Sarah enters the coffee shop',
            'dialogue': [{'character': 'Sarah', 'line': 'Is James here?'}],
            'characters': [{'name': 'Sarah'}, {'name': 'James'}]
        }
        
        test_vos = [
            {
                'character': 'Sarah',
                'text': 'I knew this was a mistake. Some wounds are better left closed.',
                'scene': '1'
            }
        ]
        
        test_agents = {
            'camera': {'shot_type': 'MEDIUM', 'camera_movement': 'dolly in'},
            'lighting': {'mood': 'tense', 'sources': ['natural window light']},
            'environment': {'location': 'Coffee Shop', 'time_of_day': 'MORNING'},
            'characters': [{'name': 'Sarah'}, {'name': 'James'}]
        }
        
        prompt = synthesizer.synthesize_enhanced_prompt(
            test_scene, test_shot, test_agents, test_vos
        )
        
        print("\n" + "="*60)
        print("ENHANCED VEO3 PROMPT TEST")
        print("="*60 + "\n")
        print(prompt.to_text())
        print("\n" + "="*60)
    
    elif args.output_dir:
        output_path = Path(args.output_dir)
        if output_path.exists():
            processor = EnhancedVeo3Processor(output_path)
            processor.process_with_enhancement()
        else:
            print(f"Output directory not found: {output_path}")
    else:
        print("Use --output-dir or --test")


if __name__ == "__main__":
    main()