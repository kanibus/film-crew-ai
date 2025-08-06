#!/usr/bin/env python3
"""
Veo3 Natural Language Prompt Generator
Combines all agent outputs into cohesive, narrative-style prompts
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Veo3PromptGenerator')


@dataclass
class Veo3NaturalPrompt:
    """Represents a complete Veo3 prompt in natural language format"""
    subject: str
    context: str
    action: str
    style: str
    camera_motion: str
    composition: str
    ambiance: str
    texture: str
    environment: str
    
    def to_text(self) -> str:
        """Convert to natural language format"""
        sections = []
        
        if self.subject:
            sections.append(f"Subject: {self.subject}")
        
        if self.context:
            sections.append(f"Context: {self.context}")
        
        if self.action:
            sections.append(f"Action: {self.action}")
        
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


class Veo3PromptSynthesizer:
    """Synthesizes all agent outputs into natural language Veo3 prompts"""
    
    def __init__(self):
        self.consistency_tracker = {}
        
    def synthesize_prompt(self, 
                         scene_data: Dict,
                         shot_data: Dict,
                         agent_outputs: Dict) -> Veo3NaturalPrompt:
        """Combine all agent outputs into a cohesive natural language prompt"""
        
        # Extract data from different agents
        camera = agent_outputs.get('camera', {})
        lighting = agent_outputs.get('lighting', {})
        environment = agent_outputs.get('environment', {})
        characters = agent_outputs.get('characters', [])
        sound = agent_outputs.get('sound', {})
        
        # Build Subject
        subject = self._build_subject(shot_data, characters, environment)
        
        # Build Context
        context = self._build_context(scene_data, environment, lighting)
        
        # Build Action
        action = self._build_action(shot_data, characters, environment)
        
        # Build Style
        style = self._build_style(scene_data, lighting, camera)
        
        # Build Camera Motion
        camera_motion = self._build_camera_motion(camera, shot_data)
        
        # Build Composition
        composition = self._build_composition(camera, characters, environment)
        
        # Build Ambiance
        ambiance = self._build_ambiance(lighting, sound, scene_data)
        
        # Build Texture
        texture = self._build_texture(environment, lighting, characters)
        
        # Build Environment
        environment_desc = self._build_environment(environment, scene_data)
        
        return Veo3NaturalPrompt(
            subject=subject,
            context=context,
            action=action,
            style=style,
            camera_motion=camera_motion,
            composition=composition,
            ambiance=ambiance,
            texture=texture,
            environment=environment_desc
        )
    
    def _build_subject(self, shot_data: Dict, characters: List, environment: Dict) -> str:
        """Build the subject description"""
        elements = []
        
        # Primary focus
        if characters:
            char_names = [c.get('name', 'Character') for c in characters[:2]]
            if len(char_names) == 1:
                elements.append(f"{char_names[0]}")
            else:
                elements.append(f"{' and '.join(char_names)}")
            
            # Add character states
            states = [c.get('emotional_state', '') for c in characters if c.get('emotional_state')]
            if states:
                elements.append(f"displaying {', '.join(states[:2])}")
        
        # Location
        location = environment.get('location', 'interior space')
        time_of_day = environment.get('time_of_day', 'day')
        
        if not characters:
            # Environment-focused shot
            elements.append(f"A {self._describe_mood(time_of_day)} {location}")
        else:
            elements.append(f"in a {location}")
        
        # Shot type context
        shot_type = shot_data.get('shot_type', 'medium shot')
        if 'ESTABLISHING' in shot_type.upper():
            elements.insert(0, "An establishing view of")
        elif 'CLOSE' in shot_type.upper():
            elements.insert(0, "An intimate close-up of")
        
        return ' '.join(elements) + '.'
    
    def _build_context(self, scene_data: Dict, environment: Dict, lighting: Dict) -> str:
        """Build the context description"""
        elements = []
        
        # Setting description
        location = environment.get('location', 'space')
        setting_desc = environment.get('setting_description', '')
        
        if setting_desc:
            elements.append(setting_desc)
        else:
            elements.append(f"The {location} is")
        
        # Architectural/spatial features
        if 'INT' in scene_data.get('heading', ''):
            elements.append("an interior space with")
            
            # Add room features based on location
            if 'OFFICE' in location.upper():
                elements.append("a desk, computer equipment, and professional furnishings")
            elif 'COFFEE' in location.upper() or 'CAFE' in location.upper():
                elements.append("tables, chairs, a counter, and the bustle of patrons")
            elif 'HOME' in location.upper() or 'APARTMENT' in location.upper():
                elements.append("personal furnishings and lived-in details")
            else:
                elements.append("appropriate furnishings and architectural details")
        else:
            elements.append("an exterior location featuring")
            elements.append(self._describe_exterior_features(location))
        
        # Lighting context
        light_sources = lighting.get('sources', [])
        if light_sources:
            if 'natural' in str(light_sources).lower():
                elements.append(". Natural light streams through windows")
            elif 'practical' in str(light_sources).lower():
                elements.append(". Practical lights provide warm illumination")
        
        # Time period/era if relevant
        if scene_data.get('scene_type') == 'FLASHBACK':
            elements.append(". The scene has a nostalgic, memory-like quality")
        
        # Environmental conditions
        conditions = environment.get('environmental_conditions', '')
        if conditions and conditions != 'normal':
            elements.append(f". {conditions.capitalize()} conditions affect the atmosphere")
        
        return ' '.join(elements) + '.'
    
    def _build_action(self, shot_data: Dict, characters: List, environment: Dict) -> str:
        """Build the action description"""
        elements = []
        
        # Primary action
        action = shot_data.get('action', '')
        dialogue = shot_data.get('dialogue', [])
        
        if action:
            elements.append(action[:200])  # Limit length
        
        # Character actions
        if characters:
            for char in characters[:2]:  # Focus on main characters
                movement = char.get('movement', '')
                if movement and movement != 'static':
                    char_name = char.get('name', 'The character')
                    elements.append(f"{char_name} {movement}")
        
        # Dialogue action
        if dialogue:
            if len(dialogue) == 1:
                elements.append("A character speaks")
            else:
                elements.append("Characters engage in conversation")
        
        # Environmental action
        env_movement = []
        
        time_of_day = environment.get('time_of_day', 'DAY')
        if 'DAWN' in time_of_day.upper() or 'MORNING' in time_of_day.upper():
            env_movement.append("Morning light gradually illuminates the space")
        elif 'DUSK' in time_of_day.upper() or 'SUNSET' in time_of_day.upper():
            env_movement.append("Golden hour light shifts across surfaces")
        elif 'NIGHT' in time_of_day.upper():
            env_movement.append("Artificial lights create pools of illumination")
        
        # Add subtle environmental movements
        if 'EXT' in shot_data.get('scene_heading', ''):
            env_movement.append("Gentle breeze moves through the scene")
        else:
            env_movement.append("Dust particles drift in the light")
        
        if env_movement:
            elements.extend(env_movement[:1])  # Add one environmental movement
        
        return '. '.join(elements) + '.' if elements else "The scene holds in quiet stillness."
    
    def _build_style(self, scene_data: Dict, lighting: Dict, camera: Dict) -> str:
        """Build the style description"""
        elements = []
        
        # Base aesthetic
        mood = lighting.get('mood', 'naturalistic')
        atmosphere = lighting.get('atmosphere', 'cinematic')
        
        # Genre-specific styling
        scene_type = scene_data.get('scene_type', 'PRESENT')
        
        if scene_type == 'FLASHBACK':
            elements.append("Nostalgic cinematography with slightly desaturated colors")
        elif scene_type == 'DREAM':
            elements.append("Dreamlike, ethereal quality with soft focus edges")
        elif scene_type == 'MONTAGE':
            elements.append("Dynamic, rhythmic editing style")
        else:
            # Present-day styling
            if 'dramatic' in mood.lower():
                elements.append("Dramatic cinematography with strong contrast")
            elif 'romantic' in mood.lower():
                elements.append("Soft, romantic visual treatment")
            elif 'tense' in mood.lower() or 'thriller' in mood.lower():
                elements.append("Thriller-style cinematography with sharp shadows")
            else:
                elements.append("Naturalistic cinematography with authentic lighting")
        
        # Color grading
        color_temp = lighting.get('color_temperature', '5000K')
        if '3' in color_temp[:1]:  # 3000K range
            elements.append("warm color grading")
        elif '6' in color_temp[:1]:  # 6000K+ range
            elements.append("cool color grading")
        else:
            elements.append("neutral color balance")
        
        # Film texture
        if scene_type == 'FLASHBACK':
            elements.append("subtle film grain")
        else:
            elements.append("clean digital aesthetic")
        
        # Overall feel
        elements.append(f"The overall style is {atmosphere}")
        
        return '. '.join(elements) + '.'
    
    def _build_camera_motion(self, camera: Dict, shot_data: Dict) -> str:
        """Build the camera motion description"""
        elements = []
        
        # Base movement
        movement = camera.get('camera_movement', 'static')
        shot_type = camera.get('shot_type', 'MEDIUM')
        
        # Opening movement
        if 'ESTABLISHING' in shot_type.upper():
            elements.append("A slow, majestic crane shot descends from above")
            elements.append("gradually revealing the full scope of the location")
        elif 'static' in movement.lower() or 'locked' in movement.lower():
            elements.append("The camera holds steady in a locked-off position")
            elements.append("allowing the action to unfold within the frame")
        elif 'dolly' in movement.lower():
            elements.append("A smooth dolly movement glides")
            if 'in' in movement.lower():
                elements.append("slowly toward the subject")
            elif 'out' in movement.lower():
                elements.append("gradually away from the subject")
            else:
                elements.append("laterally across the scene")
        elif 'handheld' in movement.lower():
            elements.append("Handheld camera work adds organic movement")
            elements.append("creating an intimate, documentary feel")
        elif 'steadicam' in movement.lower():
            elements.append("Steadicam movement flows smoothly through the space")
            elements.append("maintaining stability while following the action")
        elif 'pan' in movement.lower():
            elements.append("The camera pans smoothly")
            elements.append("surveying the scene from a fixed position")
        elif 'tilt' in movement.lower():
            elements.append("A gentle tilt reveals")
            elements.append("vertical elements of the composition")
        elif 'crane' in movement.lower():
            elements.append("A crane movement lifts the perspective")
            elements.append("providing a godlike view of the action")
        else:
            elements.append("The camera employs subtle movement")
            elements.append("maintaining visual interest without distraction")
        
        # Speed and rhythm
        if shot_data.get('duration', '').startswith('2-'):
            elements.append("The movement is brief and purposeful")
        elif shot_data.get('duration', '').startswith('5-') or shot_data.get('duration', '').startswith('8-'):
            elements.append("The movement unfolds leisurely, allowing viewers to absorb details")
        
        return '. '.join(elements) + '.'
    
    def _build_composition(self, camera: Dict, characters: List, environment: Dict) -> str:
        """Build the composition description"""
        elements = []
        
        # Framing
        framing = camera.get('framing', 'standard framing')
        composition_rule = camera.get('composition', 'balanced composition')
        
        # Main compositional element
        if 'rule of thirds' in composition_rule.lower():
            elements.append("The composition follows the rule of thirds")
        elif 'center' in composition_rule.lower():
            elements.append("The subject is center-framed")
        elif 'golden' in composition_rule.lower():
            elements.append("The composition uses golden ratio proportions")
        else:
            elements.append("The frame is thoughtfully composed")
        
        # Character placement
        if characters:
            if len(characters) == 1:
                elements.append(f"with {characters[0].get('name', 'the character')} positioned as the focal point")
            elif len(characters) == 2:
                elements.append("balancing both characters in the frame")
            else:
                elements.append("arranging multiple characters in dynamic groupings")
        
        # Environmental elements
        props = environment.get('props', [])
        if props:
            elements.append(f"Environmental elements like {', '.join(props[:2])} add visual layers")
        
        # Depth
        depth_of_field = camera.get('depth_of_field', 'medium depth')
        if 'shallow' in depth_of_field.lower():
            elements.append("Shallow depth of field isolates the subject from the background")
        elif 'deep' in depth_of_field.lower():
            elements.append("Deep focus keeps all planes sharp, revealing environmental detail")
        
        # Leading lines or shapes
        location = environment.get('location', '')
        if 'STREET' in location.upper() or 'ROAD' in location.upper():
            elements.append("Street lines create strong perspective")
        elif 'OFFICE' in location.upper():
            elements.append("Architectural lines frame the subjects")
        
        return '. '.join(elements) + '.'
    
    def _build_ambiance(self, lighting: Dict, sound: Dict, scene_data: Dict) -> str:
        """Build the ambiance description"""
        elements = []
        
        # Time and mood
        mood = lighting.get('mood', 'neutral')
        atmosphere = lighting.get('atmosphere', 'realistic')
        time_of_day = scene_data.get('time_of_day', 'day')
        
        # Primary atmosphere
        if 'NIGHT' in time_of_day.upper():
            elements.append("Nocturnal quietude pervades the scene")
        elif 'DAWN' in time_of_day.upper() or 'MORNING' in time_of_day.upper():
            elements.append("Early morning freshness fills the space")
        elif 'DUSK' in time_of_day.upper() or 'SUNSET' in time_of_day.upper():
            elements.append("Golden hour warmth bathes everything")
        else:
            elements.append("Daylight brings clarity and energy")
        
        # Emotional tone
        if 'tense' in mood.lower():
            elements.append("Tension hangs in the air")
        elif 'romantic' in mood.lower():
            elements.append("Romance softens every edge")
        elif 'mysterious' in mood.lower():
            elements.append("Mystery shrouds the atmosphere")
        elif 'melancholic' in mood.lower():
            elements.append("Melancholy permeates the moment")
        else:
            elements.append("The mood is contemplative and grounded")
        
        # Sound ambiance
        if sound:
            ambience = sound.get('ambience', [])
            if ambience:
                elements.append(f"The soundscape includes {', '.join(ambience[:2])}")
        
        # Overall feeling
        scene_type = scene_data.get('scene_type', 'PRESENT')
        if scene_type == 'FLASHBACK':
            elements.append("Everything feels distant yet vivid, like a memory")
        elif scene_type == 'DREAM':
            elements.append("Reality feels fluid and symbolic")
        else:
            elements.append("The space feels authentic and lived-in")
        
        return '. '.join(elements) + '.'
    
    def _build_texture(self, environment: Dict, lighting: Dict, characters: List) -> str:
        """Build the texture description"""
        elements = []
        
        # Surface qualities based on location
        location = environment.get('location', 'interior')
        
        # Architectural textures
        if 'INT' in location.upper() or 'INTERIOR' in location.upper():
            elements.extend([
                "Smooth painted walls",
                "polished wood surfaces",
                "soft fabric upholstery"
            ])
        else:
            elements.extend([
                "Weathered concrete",
                "rough stone",
                "natural foliage"
            ])
        
        # Lighting textures
        intensity = lighting.get('intensity', 'balanced')
        if 'soft' in intensity.lower():
            elements.append("diffused light creating gentle gradients")
        elif 'harsh' in intensity.lower():
            elements.append("hard light creating sharp shadow edges")
        else:
            elements.append("balanced light revealing surface details")
        
        # Character textures
        if characters:
            wardrobe_items = []
            for char in characters[:2]:
                wardrobe = char.get('wardrobe', '')
                if wardrobe:
                    wardrobe_items.append(wardrobe)
            
            if wardrobe_items:
                elements.append(f"clothing textures including {', '.join(wardrobe_items[:2])}")
        
        # Environmental textures
        props = environment.get('props', [])
        if props:
            if 'glass' in str(props).lower():
                elements.append("reflective glass surfaces")
            if 'metal' in str(props).lower():
                elements.append("brushed metal accents")
            if 'plant' in str(props).lower() or 'flower' in str(props).lower():
                elements.append("organic plant textures")
        
        # Atmospheric particles
        conditions = environment.get('environmental_conditions', '')
        if 'rain' in conditions.lower():
            elements.append("water droplets on surfaces")
        elif 'fog' in conditions.lower():
            elements.append("misty air softening edges")
        elif 'snow' in conditions.lower():
            elements.append("crystalline snow accumulation")
        else:
            elements.append("dust motes visible in light beams")
        
        return ', '.join(elements[:5]) + '.'  # Limit to 5 texture elements
    
    def _build_environment(self, environment: Dict, scene_data: Dict) -> str:
        """Build the environment summary"""
        elements = []
        
        # Primary description
        location = environment.get('location', 'location')
        time_of_day = environment.get('time_of_day', 'day')
        
        # Setting type
        if 'INT' in scene_data.get('heading', ''):
            elements.append(f"An interior {location.lower()}")
        else:
            elements.append(f"An exterior {location.lower()} setting")
        
        # Time context
        elements.append(f"during {time_of_day.lower()}")
        
        # Socioeconomic context (if relevant)
        if 'farmhouse' in location.lower() or 'rural' in location.lower():
            elements.append("in a rural, working-class setting")
        elif 'office' in location.lower() or 'corporate' in location.lower():
            elements.append("in a professional, urban environment")
        elif 'home' in location.lower() or 'apartment' in location.lower():
            elements.append("in a middle-class residential space")
        elif 'coffee' in location.lower() or 'cafe' in location.lower():
            elements.append("in a public social space")
        
        # Design philosophy
        elements.append("The space embodies")
        setting_desc = environment.get('setting_description', '')
        if setting_desc:
            if 'modern' in setting_desc.lower():
                elements.append("contemporary design sensibilities")
            elif 'vintage' in setting_desc.lower() or 'old' in setting_desc.lower():
                elements.append("timeworn character")
            else:
                elements.append("functional simplicity")
        else:
            elements.append("authentic environmental storytelling")
        
        # Purpose
        scene_type = scene_data.get('scene_type', 'PRESENT')
        if scene_type == 'FLASHBACK':
            elements.append("frozen in memory")
        else:
            elements.append("where life unfolds naturally")
        
        # Final atmospheric note
        elements.append("Every detail contributes to the narrative")
        
        return '. '.join(elements) + '.'
    
    def _describe_mood(self, time_of_day: str) -> str:
        """Get mood descriptor for time of day"""
        moods = {
            'DAWN': 'serene',
            'MORNING': 'fresh',
            'DAY': 'vibrant',
            'AFTERNOON': 'warm',
            'DUSK': 'golden',
            'SUNSET': 'romantic',
            'NIGHT': 'mysterious',
            'LATE NIGHT': 'intimate'
        }
        
        for key, mood in moods.items():
            if key in time_of_day.upper():
                return mood
        return 'atmospheric'
    
    def _describe_exterior_features(self, location: str) -> str:
        """Describe exterior location features"""
        location_upper = location.upper()
        
        if 'STREET' in location_upper:
            return "urban architecture, sidewalks, and city life"
        elif 'PARK' in location_upper:
            return "natural landscaping, paths, and open spaces"
        elif 'BEACH' in location_upper:
            return "sand, waves, and coastal elements"
        elif 'FOREST' in location_upper or 'WOODS' in location_upper:
            return "trees, undergrowth, and natural paths"
        elif 'FARM' in location_upper:
            return "fields, farm buildings, and rural landscape"
        else:
            return "natural and architectural elements"


class Veo3PromptProcessor:
    """Processes existing JSON outputs to create natural language prompts"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.synthesizer = Veo3PromptSynthesizer()
        
    def process_all_shots(self):
        """Process all shots and generate natural language prompts"""
        
        # Create output directory for natural prompts
        natural_prompts_dir = self.output_dir / "Veo3_Natural_Prompts"
        natural_prompts_dir.mkdir(exist_ok=True)
        
        # Find all Veo3 JSON files
        veo3_files = list((self.output_dir / "05_Veo3_Prompts").glob("*.json"))
        
        logger.info(f"Processing {len(veo3_files)} shots for natural language prompts")
        
        for json_file in veo3_files:
            try:
                # Load JSON data
                with open(json_file, 'r') as f:
                    data = json.load(f)
                
                # Create mock agent outputs from JSON
                agent_outputs = self._extract_agent_data(data)
                
                # Synthesize natural prompt
                natural_prompt = self.synthesizer.synthesize_prompt(
                    scene_data={'heading': data.get('metadata', {}).get('scene', ''),
                               'time_of_day': 'DAY',
                               'scene_type': 'PRESENT'},
                    shot_data=data,
                    agent_outputs=agent_outputs
                )
                
                # Save as text file
                output_file = natural_prompts_dir / f"{json_file.stem}_natural.txt"
                with open(output_file, 'w') as f:
                    f.write(natural_prompt.to_text())
                
                logger.info(f"Generated natural prompt: {output_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {json_file}: {e}")
        
        # Create master prompts file
        self._create_master_prompts_file(natural_prompts_dir)
    
    def _extract_agent_data(self, json_data: Dict) -> Dict:
        """Extract agent-like data from JSON"""
        # Parse the existing prompt to extract components
        prompt = json_data.get('veo3_prompt', '')
        
        agent_outputs = {
            'camera': {
                'shot_type': json_data.get('shot_type', 'MEDIUM'),
                'camera_movement': self._extract_movement(prompt),
                'framing': 'standard framing',
                'composition': 'balanced composition',
                'depth_of_field': 'medium depth'
            },
            'lighting': {
                'sources': ['natural light'],
                'mood': 'naturalistic',
                'atmosphere': 'cinematic',
                'color_temperature': '5000K',
                'intensity': 'balanced'
            },
            'environment': {
                'location': self._extract_location(prompt),
                'time_of_day': 'DAY',
                'props': [],
                'setting_description': '',
                'environmental_conditions': 'normal'
            },
            'characters': [],
            'sound': {
                'ambience': ['room tone', 'environmental sounds']
            }
        }
        
        return agent_outputs
    
    def _extract_movement(self, prompt: str) -> str:
        """Extract camera movement from prompt"""
        if 'static' in prompt.lower():
            return 'static'
        elif 'dolly' in prompt.lower():
            return 'dolly'
        elif 'pan' in prompt.lower():
            return 'pan'
        elif 'handheld' in prompt.lower():
            return 'handheld'
        elif 'crane' in prompt.lower():
            return 'crane'
        else:
            return 'subtle movement'
    
    def _extract_location(self, prompt: str) -> str:
        """Extract location from prompt"""
        # Look for location keywords
        locations = ['office', 'home', 'street', 'coffee shop', 'cafe', 
                    'apartment', 'hospital', 'farmhouse', 'park']
        
        prompt_lower = prompt.lower()
        for loc in locations:
            if loc in prompt_lower:
                return loc.title()
        
        return 'interior space'
    
    def _create_master_prompts_file(self, prompts_dir: Path):
        """Create a master file with all prompts"""
        all_prompts = []
        
        for txt_file in sorted(prompts_dir.glob("*.txt")):
            with open(txt_file, 'r') as f:
                content = f.read()
                all_prompts.append(f"=== {txt_file.stem} ===\n\n{content}\n")
        
        master_file = prompts_dir / "ALL_VEO3_PROMPTS.txt"
        with open(master_file, 'w') as f:
            separator = "\n" + "="*60 + "\n"
            f.write(separator.join(all_prompts))
        
        logger.info(f"Created master prompts file: {master_file}")


def main():
    """Test the natural language prompt generator"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Generate natural language Veo3 prompts from processed scripts"
    )
    parser.add_argument('--output-dir', type=str, 
                       help='Path to script output directory')
    parser.add_argument('--test', action='store_true',
                       help='Run test with sample data')
    
    args = parser.parse_args()
    
    if args.test:
        # Test with sample data
        synthesizer = Veo3PromptSynthesizer()
        
        test_scene = {
            'heading': 'INT. COFFEE SHOP - DAY',
            'time_of_day': 'MORNING',
            'scene_type': 'PRESENT'
        }
        
        test_shot = {
            'shot_type': 'WIDE ESTABLISHING',
            'shot_id': '1-001',
            'action': 'A busy coffee shop filled with morning patrons',
            'dialogue': [],
            'duration': '5-8 seconds'
        }
        
        test_agents = {
            'camera': {
                'shot_type': 'WIDE ESTABLISHING',
                'camera_movement': 'slow dolly in',
                'framing': 'wide framing',
                'composition': 'rule of thirds',
                'depth_of_field': 'deep focus'
            },
            'lighting': {
                'sources': ['natural sunlight', 'practical lights'],
                'mood': 'warm and inviting',
                'atmosphere': 'bustling morning energy',
                'color_temperature': '5600K',
                'intensity': 'bright and cheerful'
            },
            'environment': {
                'location': 'Coffee Shop',
                'time_of_day': 'MORNING',
                'props': ['tables', 'chairs', 'coffee machine', 'counter'],
                'setting_description': 'A modern coffee shop with large windows',
                'environmental_conditions': 'normal'
            },
            'characters': [
                {
                    'name': 'Sarah',
                    'emotional_state': 'anxious',
                    'wardrobe': 'casual business attire',
                    'movement': 'enters and scans the room'
                }
            ],
            'sound': {
                'ambience': ['coffee machine hiss', 'morning chatter', 'cups clinking']
            }
        }
        
        prompt = synthesizer.synthesize_prompt(test_scene, test_shot, test_agents)
        print("\n" + "="*60)
        print("NATURAL LANGUAGE VEO3 PROMPT TEST")
        print("="*60 + "\n")
        print(prompt.to_text())
        print("\n" + "="*60)
    
    elif args.output_dir:
        # Process actual output directory
        output_path = Path(args.output_dir)
        if output_path.exists():
            processor = Veo3PromptProcessor(output_path)
            processor.process_all_shots()
        else:
            print(f"Output directory not found: {output_path}")
    else:
        print("Please specify --output-dir or use --test for demo")


if __name__ == "__main__":
    main()