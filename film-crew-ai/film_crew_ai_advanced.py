#!/usr/bin/env python3
"""
Film Crew AI - Advanced Production System v5.0
Complete scene, shot, and voice-over detection with proper separation
"""

import os
import sys
import json
import re
import logging
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Set
import subprocess
from dataclasses import dataclass, asdict, field
import traceback
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FilmCrewAI-Advanced')


# ============================================================================
# ENHANCED DATA MODELS
# ============================================================================

@dataclass
class VoiceOver:
    """Represents a voice-over narration"""
    character: str
    text: str
    scene_context: str
    timing: str  # "during_scene" or "transitional"
    emotional_tone: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class Transition:
    """Represents scene transitions"""
    type: str  # CUT TO, FADE TO, DISSOLVE TO, etc.
    from_scene: str
    to_scene: str
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class VideoShot:
    """Enhanced shot with video-specific information"""
    shot_id: str
    scene_number: str
    shot_number: str
    shot_type: str  # WIDE, MEDIUM, CLOSE-UP, etc.
    description: str
    duration: str
    camera_movement: str
    characters_in_frame: List[str]
    dialogue: List[str]
    voice_overs: List[VoiceOver]
    is_flashback: bool = False
    is_montage: bool = False
    visual_effects: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "shot_id": self.shot_id,
            "scene_number": self.scene_number,
            "shot_number": self.shot_number,
            "shot_type": self.shot_type,
            "description": self.description,
            "duration": self.duration,
            "camera_movement": self.camera_movement,
            "characters_in_frame": self.characters_in_frame,
            "dialogue": self.dialogue,
            "voice_overs": [vo.to_dict() for vo in self.voice_overs],
            "is_flashback": self.is_flashback,
            "is_montage": self.is_montage,
            "visual_effects": self.visual_effects
        }


@dataclass
class EnhancedScene:
    """Scene with complete information"""
    scene_number: str
    heading: str
    location: str
    time_of_day: str
    scene_type: str  # PRESENT, FLASHBACK, DREAM, MONTAGE
    description: str
    action_blocks: List[str]
    dialogue_blocks: List[Dict]
    voice_overs: List[VoiceOver]
    shots: List[VideoShot]
    transitions_in: Optional[Transition] = None
    transitions_out: Optional[Transition] = None
    
    def to_dict(self) -> Dict:
        return {
            "scene_number": self.scene_number,
            "heading": self.heading,
            "location": self.location,
            "time_of_day": self.time_of_day,
            "scene_type": self.scene_type,
            "description": self.description,
            "action_blocks": self.action_blocks,
            "dialogue_blocks": self.dialogue_blocks,
            "voice_overs": [vo.to_dict() for vo in self.voice_overs],
            "shots": [shot.to_dict() for shot in self.shots],
            "transitions_in": self.transitions_in.to_dict() if self.transitions_in else None,
            "transitions_out": self.transitions_out.to_dict() if self.transitions_out else None
        }


# ============================================================================
# ADVANCED SCRIPT PARSER
# ============================================================================

class AdvancedScriptParser:
    """Advanced parser with complete scene, shot, and voice-over detection"""
    
    def __init__(self):
        # Scene patterns
        self.scene_pattern = re.compile(
            r'^(INT\.|EXT\.|INT/EXT\.|I/E\.)\s+(.+?)\s*[-–—]\s*(.+?)(?:\s*[-–—]\s*(.+))?$',
            re.MULTILINE | re.IGNORECASE
        )
        
        # Transition patterns
        self.transition_patterns = [
            re.compile(r'^(FADE IN:?|FADE OUT:?|FADE TO:?)$', re.MULTILINE | re.IGNORECASE),
            re.compile(r'^(CUT TO:?|DISSOLVE TO:?|MATCH CUT TO:?|SMASH CUT TO:?)$', re.MULTILINE | re.IGNORECASE),
            re.compile(r'^(INTERCUT WITH:?|BACK TO:?|ANGLE ON:?|CLOSE ON:?)$', re.MULTILINE | re.IGNORECASE)
        ]
        
        # Voice-over pattern
        self.vo_pattern = re.compile(r'^([A-Z][A-Z\s\.]+)\s*\(V\.O\.\)$', re.MULTILINE)
        self.os_pattern = re.compile(r'^([A-Z][A-Z\s\.]+)\s*\(O\.S\.\)$', re.MULTILINE)
        
        # Character and dialogue patterns
        self.character_pattern = re.compile(r'^([A-Z][A-Z\s\.]+)(?:\s*\([^)]+\))?$')
        self.parenthetical_pattern = re.compile(r'^\s*\([^)]+\)\s*$')
        
        # Shot type patterns
        self.shot_patterns = {
            'WIDE': re.compile(r'\b(WIDE|ESTABLISHING|EXTREME WIDE|FULL)\b', re.IGNORECASE),
            'MEDIUM': re.compile(r'\b(MEDIUM|MED|TWO-SHOT|THREE-SHOT)\b', re.IGNORECASE),
            'CLOSE-UP': re.compile(r'\b(CLOSE-UP|CLOSE UP|CU|TIGHT)\b', re.IGNORECASE),
            'EXTREME CLOSE-UP': re.compile(r'\b(EXTREME CLOSE-UP|ECU|MACRO)\b', re.IGNORECASE),
            'OVER-THE-SHOULDER': re.compile(r'\b(OVER THE SHOULDER|OTS|OVER SHOULDER)\b', re.IGNORECASE),
            'POV': re.compile(r'\b(POV|POINT OF VIEW|P\.O\.V\.)\b', re.IGNORECASE),
            'INSERT': re.compile(r'\b(INSERT|CUTAWAY)\b', re.IGNORECASE)
        }
        
        # Camera movement patterns
        self.movement_patterns = {
            'PAN': re.compile(r'\b(PAN|PANNING|PANS)\b', re.IGNORECASE),
            'TILT': re.compile(r'\b(TILT|TILTING|TILTS)\b', re.IGNORECASE),
            'DOLLY': re.compile(r'\b(DOLLY|DOLLYING|DOLLIES|TRACK|TRACKING)\b', re.IGNORECASE),
            'CRANE': re.compile(r'\b(CRANE|CRANING|BOOM)\b', re.IGNORECASE),
            'HANDHELD': re.compile(r'\b(HANDHELD|HAND-HELD|SHAKY)\b', re.IGNORECASE),
            'STEADICAM': re.compile(r'\b(STEADICAM|STEADY CAM|SMOOTH)\b', re.IGNORECASE),
            'ZOOM': re.compile(r'\b(ZOOM|ZOOMING|ZOOMS)\b', re.IGNORECASE),
            'STATIC': re.compile(r'\b(STATIC|LOCKED OFF|FIXED)\b', re.IGNORECASE)
        }
        
        # Special scene indicators
        self.flashback_pattern = re.compile(r'\b(FLASHBACK|FLASH BACK|YEARS? AGO|EARLIER)\b', re.IGNORECASE)
        self.montage_pattern = re.compile(r'\b(MONTAGE|SERIES OF SHOTS|SEQUENCE)\b', re.IGNORECASE)
        self.dream_pattern = re.compile(r'\b(DREAM|NIGHTMARE|FANTASY|IMAGINATION)\b', re.IGNORECASE)
        
    def parse(self, script_path: Path) -> Tuple[List[EnhancedScene], Dict]:
        """Parse script with complete analysis"""
        logger.info(f"Advanced parsing of script: {script_path}")
        
        # Read content with enhanced encoding detection
        try:
            from enhanced_document_reader import EnhancedDocumentReader
            content = EnhancedDocumentReader.read_file(script_path)
        except ImportError:
            # Fallback to original reader
            from film_crew_ai_enhanced import DocumentReader
            content = DocumentReader.read_file(script_path)
        
        # Parse all elements
        scenes = self._extract_scenes(content)
        transitions = self._extract_transitions(content)
        voice_overs = self._extract_voice_overs(content)
        
        # Process each scene
        processed_scenes = []
        for i, scene_data in enumerate(scenes):
            scene = self._process_scene(
                scene_data, i + 1, transitions, voice_overs, content
            )
            processed_scenes.append(scene)
        
        # Generate statistics
        stats = self._generate_statistics(processed_scenes)
        
        logger.info(f"Parsed {len(processed_scenes)} scenes with {stats['total_shots']} shots and {stats['total_voice_overs']} voice-overs")
        
        return processed_scenes, stats
    
    def _extract_scenes(self, content: str) -> List[Dict]:
        """Extract all scenes from script"""
        scenes = []
        scene_matches = list(self.scene_pattern.finditer(content))
        
        if not scene_matches:
            # Treat entire content as one scene if no headers found
            scenes.append({
                'start': 0,
                'end': len(content),
                'heading': 'INT. LOCATION - DAY',
                'text': content
            })
        else:
            for i, match in enumerate(scene_matches):
                scene_start = match.start()
                scene_end = scene_matches[i + 1].start() if i + 1 < len(scene_matches) else len(content)
                
                int_ext = match.group(1)
                location = match.group(2)
                time = match.group(3)
                extra = match.group(4) if match.lastindex >= 4 else ""
                
                # Handle flashback/special indicators
                scene_type = "PRESENT"
                if extra and self.flashback_pattern.search(extra):
                    scene_type = "FLASHBACK"
                
                heading = f"{int_ext} {location} - {time}"
                if extra:
                    heading += f" - {extra}"
                
                scenes.append({
                    'start': scene_start,
                    'end': scene_end,
                    'heading': heading,
                    'location': location,
                    'time': time,
                    'type': scene_type,
                    'text': content[scene_start:scene_end]
                })
        
        return scenes
    
    def _extract_transitions(self, content: str) -> List[Transition]:
        """Extract all transitions from script"""
        transitions = []
        
        for pattern in self.transition_patterns:
            for match in pattern.finditer(content):
                transition_text = match.group(1)
                position = match.start()
                
                # Determine which scenes this transition connects
                transitions.append(Transition(
                    type=transition_text.rstrip(':'),
                    from_scene="",  # Will be filled during scene processing
                    to_scene=""
                ))
        
        return transitions
    
    def _extract_voice_overs(self, content: str) -> List[Dict]:
        """Extract all voice-overs from script"""
        voice_overs = []
        
        # Find V.O. patterns
        for match in self.vo_pattern.finditer(content):
            character = match.group(1).strip()
            position = match.end()
            
            # Extract the voice-over text
            lines = []
            content_lines = content[position:].split('\n')
            
            for line in content_lines:
                line = line.strip()
                if not line:
                    break
                if self.character_pattern.match(line):
                    break
                if not self.parenthetical_pattern.match(line):
                    lines.append(line)
            
            if lines:
                voice_overs.append({
                    'character': character,
                    'text': ' '.join(lines),
                    'position': position,
                    'type': 'voice_over'
                })
        
        # Find O.S. (off-screen) patterns - also important for video
        for match in self.os_pattern.finditer(content):
            character = match.group(1).strip()
            position = match.end()
            
            lines = []
            content_lines = content[position:].split('\n')
            
            for line in content_lines:
                line = line.strip()
                if not line:
                    break
                if self.character_pattern.match(line):
                    break
                if not self.parenthetical_pattern.match(line):
                    lines.append(line)
            
            if lines:
                voice_overs.append({
                    'character': character,
                    'text': ' '.join(lines),
                    'position': position,
                    'type': 'off_screen'
                })
        
        return voice_overs
    
    def _process_scene(self, scene_data: Dict, scene_number: int,
                      transitions: List[Transition], 
                      voice_overs: List[Dict], 
                      full_content: str) -> EnhancedScene:
        """Process individual scene with complete analysis"""
        
        # Parse scene elements
        scene_text = scene_data['text']
        lines = scene_text.split('\n')
        
        # Extract action and dialogue
        action_blocks = []
        dialogue_blocks = []
        scene_voice_overs = []
        current_block = []
        current_character = None
        
        for line in lines[1:]:  # Skip heading
            line_stripped = line.strip()
            
            if not line_stripped:
                if current_block:
                    action_blocks.append(' '.join(current_block))
                    current_block = []
                current_character = None
                
            elif self.vo_pattern.match(line_stripped):
                # Voice-over
                char_match = self.vo_pattern.match(line_stripped)
                current_character = char_match.group(1).strip() + " (V.O.)"
                
            elif self.character_pattern.match(line_stripped) and line_stripped.isupper():
                # Regular character
                current_character = line_stripped
                dialogue_blocks.append({
                    'character': current_character,
                    'lines': []
                })
                
            elif current_character and not self.parenthetical_pattern.match(line_stripped):
                # Dialogue line
                if "(V.O.)" in current_character:
                    # Add to voice-overs
                    scene_voice_overs.append(VoiceOver(
                        character=current_character.replace(" (V.O.)", ""),
                        text=line_stripped,
                        scene_context=scene_data['heading'],
                        timing="during_scene"
                    ))
                elif dialogue_blocks:
                    dialogue_blocks[-1]['lines'].append(line_stripped)
                    
            else:
                # Action line
                current_block.append(line_stripped)
        
        if current_block:
            action_blocks.append(' '.join(current_block))
        
        # Detect scene type
        scene_type = self._detect_scene_type(scene_text, scene_data.get('type', 'PRESENT'))
        
        # Generate shots based on content
        shots = self._generate_video_shots(
            scene_number, scene_data, action_blocks, 
            dialogue_blocks, scene_voice_overs
        )
        
        # Determine transitions
        transition_in = None
        transition_out = None
        
        # Look for transitions before and after this scene
        scene_start = scene_data['start']
        scene_end = scene_data['end']
        
        before_text = full_content[max(0, scene_start - 100):scene_start]
        after_text = full_content[scene_end:min(len(full_content), scene_end + 100)]
        
        for pattern in self.transition_patterns:
            if pattern.search(before_text):
                match = pattern.search(before_text)
                transition_in = Transition(
                    type=match.group(1).rstrip(':'),
                    from_scene=str(scene_number - 1) if scene_number > 1 else "OPENING",
                    to_scene=str(scene_number)
                )
            
            if pattern.search(after_text):
                match = pattern.search(after_text)
                transition_out = Transition(
                    type=match.group(1).rstrip(':'),
                    from_scene=str(scene_number),
                    to_scene=str(scene_number + 1)
                )
        
        return EnhancedScene(
            scene_number=str(scene_number),
            heading=scene_data['heading'],
            location=scene_data['location'],
            time_of_day=scene_data['time'],
            scene_type=scene_type,
            description=' '.join(action_blocks[:1]) if action_blocks else "",
            action_blocks=action_blocks,
            dialogue_blocks=dialogue_blocks,
            voice_overs=scene_voice_overs,
            shots=shots,
            transitions_in=transition_in,
            transitions_out=transition_out
        )
    
    def _detect_scene_type(self, scene_text: str, default_type: str) -> str:
        """Detect the type of scene"""
        text_lower = scene_text.lower()
        
        if self.flashback_pattern.search(text_lower):
            return "FLASHBACK"
        elif self.dream_pattern.search(text_lower):
            return "DREAM"
        elif self.montage_pattern.search(text_lower):
            return "MONTAGE"
        else:
            return default_type
    
    def _generate_video_shots(self, scene_number: int, scene_data: Dict,
                             action_blocks: List[str], 
                             dialogue_blocks: List[Dict],
                             voice_overs: List[VoiceOver]) -> List[VideoShot]:
        """Generate video shots with proper detection"""
        shots = []
        shot_number = 1
        
        # Analyze the entire scene to determine shot breakdown
        scene_text = scene_data['text']
        
        # 1. Establishing shot (always first unless it's a continuation)
        if not any(trans in scene_text[:50] for trans in ['CONTINUED', 'CONT\'D', 'CONTINUOUS']):
            shots.append(self._create_establishing_shot(
                scene_number, shot_number, scene_data, action_blocks
            ))
            shot_number += 1
        
        # 2. Analyze action blocks for shot opportunities
        for action in action_blocks:
            shot_type = self._detect_shot_type(action)
            camera_movement = self._detect_camera_movement(action)
            
            # Check if this warrants a separate shot
            if shot_type or camera_movement or len(action) > 100:
                shots.append(VideoShot(
                    shot_id=f"{scene_number}-{shot_number:03d}",
                    scene_number=str(scene_number),
                    shot_number=f"{shot_number:03d}",
                    shot_type=shot_type or "MEDIUM",
                    description=action[:200],
                    duration=self._estimate_duration(action, shot_type),
                    camera_movement=camera_movement or "static",
                    characters_in_frame=self._extract_characters_from_action(action),
                    dialogue=[],
                    voice_overs=[vo for vo in voice_overs if vo.timing == "during_scene"],
                    is_flashback="FLASHBACK" in scene_data.get('type', ''),
                    is_montage="MONTAGE" in scene_data.get('type', '')
                ))
                shot_number += 1
        
        # 3. Dialogue shots
        current_dialogue_shot = None
        for dialogue in dialogue_blocks:
            character = dialogue['character']
            
            # Determine if we need a new shot or can continue
            if self._needs_new_shot(current_dialogue_shot, character):
                if current_dialogue_shot:
                    shots.append(current_dialogue_shot)
                
                current_dialogue_shot = VideoShot(
                    shot_id=f"{scene_number}-{shot_number:03d}",
                    scene_number=str(scene_number),
                    shot_number=f"{shot_number:03d}",
                    shot_type=self._determine_dialogue_shot_type(len(shots), character),
                    description=f"Dialogue: {character}",
                    duration="3-5 seconds",
                    camera_movement="subtle drift",
                    characters_in_frame=[character.split('(')[0].strip()],
                    dialogue=[' '.join(dialogue['lines'])],
                    voice_overs=[],
                    is_flashback="FLASHBACK" in scene_data.get('type', '')
                )
                shot_number += 1
            elif current_dialogue_shot:
                # Add to existing shot
                current_dialogue_shot.dialogue.append(' '.join(dialogue['lines']))
                if character.split('(')[0].strip() not in current_dialogue_shot.characters_in_frame:
                    current_dialogue_shot.characters_in_frame.append(character.split('(')[0].strip())
        
        if current_dialogue_shot:
            shots.append(current_dialogue_shot)
        
        # 4. Add voice-over shots if they're standalone
        for vo in voice_overs:
            if vo.timing == "transitional":
                shots.append(VideoShot(
                    shot_id=f"{scene_number}-{shot_number:03d}",
                    scene_number=str(scene_number),
                    shot_number=f"{shot_number:03d}",
                    shot_type="VARIOUS",
                    description=f"Voice-over montage: {vo.character}",
                    duration="5-10 seconds",
                    camera_movement="various",
                    characters_in_frame=[],
                    dialogue=[],
                    voice_overs=[vo],
                    is_flashback=False,
                    is_montage=True
                ))
                shot_number += 1
        
        # 5. Closing shot if scene is substantial
        if len(shots) > 3 and not any(trans in scene_text[-50:] for trans in ['CUT TO', 'FADE TO']):
            shots.append(self._create_closing_shot(
                scene_number, shot_number, scene_data
            ))
        
        return shots
    
    def _detect_shot_type(self, text: str) -> Optional[str]:
        """Detect shot type from text"""
        for shot_type, pattern in self.shot_patterns.items():
            if pattern.search(text):
                return shot_type
        return None
    
    def _detect_camera_movement(self, text: str) -> Optional[str]:
        """Detect camera movement from text"""
        movements = []
        for movement, pattern in self.movement_patterns.items():
            if pattern.search(text):
                movements.append(movement.lower())
        
        return ' '.join(movements) if movements else None
    
    def _estimate_duration(self, text: str, shot_type: str) -> str:
        """Estimate shot duration based on content"""
        word_count = len(text.split())
        
        if shot_type == "WIDE" or shot_type == "ESTABLISHING":
            return "5-8 seconds"
        elif word_count > 50:
            return "5-7 seconds"
        elif word_count > 20:
            return "3-5 seconds"
        else:
            return "2-3 seconds"
    
    def _extract_characters_from_action(self, action: str) -> List[str]:
        """Extract character names from action description"""
        characters = []
        # Look for capitalized names
        words = action.split()
        for word in words:
            if word.isupper() and len(word) > 2 and word.isalpha():
                if word not in ['THE', 'AND', 'BUT', 'FOR', 'WITH', 'INTO', 'OVER']:
                    characters.append(word)
        return list(set(characters))
    
    def _needs_new_shot(self, current_shot: Optional[VideoShot], 
                        new_character: str) -> bool:
        """Determine if we need a new shot"""
        if not current_shot:
            return True
        
        # New shot for different character (unless it's a two-shot)
        if len(current_shot.characters_in_frame) >= 2:
            return True
        
        # New shot after certain amount of dialogue
        if len(current_shot.dialogue) >= 3:
            return True
        
        return False
    
    def _determine_dialogue_shot_type(self, shot_count: int, character: str) -> str:
        """Determine appropriate shot type for dialogue"""
        if shot_count == 0:
            return "MEDIUM"
        elif shot_count % 3 == 0:
            return "CLOSE-UP"
        elif shot_count % 2 == 0:
            return "OVER-THE-SHOULDER"
        else:
            return "MEDIUM"
    
    def _create_establishing_shot(self, scene_number: int, shot_number: int,
                                 scene_data: Dict, action_blocks: List[str]) -> VideoShot:
        """Create establishing shot"""
        return VideoShot(
            shot_id=f"{scene_number}-{shot_number:03d}",
            scene_number=str(scene_number),
            shot_number=f"{shot_number:03d}",
            shot_type="WIDE ESTABLISHING",
            description=action_blocks[0][:200] if action_blocks else f"Establishing {scene_data['location']}",
            duration="5-8 seconds",
            camera_movement="slow push in or crane",
            characters_in_frame=[],
            dialogue=[],
            voice_overs=[],
            is_flashback="FLASHBACK" in scene_data.get('type', ''),
            visual_effects=""
        )
    
    def _create_closing_shot(self, scene_number: int, shot_number: int,
                            scene_data: Dict) -> VideoShot:
        """Create closing shot"""
        return VideoShot(
            shot_id=f"{scene_number}-{shot_number:03d}",
            scene_number=str(scene_number),
            shot_number=f"{shot_number:03d}",
            shot_type="WIDE",
            description=f"Scene closing - {scene_data['location']}",
            duration="3-5 seconds",
            camera_movement="pull back or static",
            characters_in_frame=[],
            dialogue=[],
            voice_overs=[],
            is_flashback=False,
            visual_effects=""
        )
    
    def _generate_statistics(self, scenes: List[EnhancedScene]) -> Dict:
        """Generate comprehensive statistics"""
        stats = {
            'total_scenes': len(scenes),
            'total_shots': sum(len(scene.shots) for scene in scenes),
            'total_voice_overs': sum(len(scene.voice_overs) for scene in scenes),
            'scene_types': defaultdict(int),
            'shot_types': defaultdict(int),
            'transitions': defaultdict(int),
            'flashback_scenes': 0,
            'montage_scenes': 0,
            'dialogue_shots': 0,
            'action_shots': 0
        }
        
        for scene in scenes:
            stats['scene_types'][scene.scene_type] += 1
            
            if scene.scene_type == "FLASHBACK":
                stats['flashback_scenes'] += 1
            elif scene.scene_type == "MONTAGE":
                stats['montage_scenes'] += 1
            
            for shot in scene.shots:
                stats['shot_types'][shot.shot_type] += 1
                
                if shot.dialogue:
                    stats['dialogue_shots'] += 1
                else:
                    stats['action_shots'] += 1
            
            if scene.transitions_in:
                stats['transitions'][scene.transitions_in.type] += 1
            if scene.transitions_out:
                stats['transitions'][scene.transitions_out.type] += 1
        
        return dict(stats)


# ============================================================================
# ADVANCED PROCESSOR
# ============================================================================

class AdvancedFilmCrewProcessor:
    """Advanced processor with complete scene/shot/VO separation"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.output_dir = project_dir / "output"
        self.scripts_dir = project_dir / "scripts"
        
        # Initialize parser
        self.parser = AdvancedScriptParser()
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
    
    def process_script(self, script_path: Path) -> Optional[Path]:
        """Process script with advanced analysis"""
        try:
            logger.info(f"Advanced processing of: {script_path.name}")
            
            # Parse script
            scenes, stats = self.parser.parse(script_path)
            
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{script_path.stem}_{timestamp}_advanced"
            script_output_dir = self.output_dir / output_name
            script_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create organized structure
            self._create_output_structure(script_output_dir, scenes, stats, script_path.stem)
            
            # Generate report
            self._generate_report(script_output_dir, scenes, stats)
            
            logger.info(f"✅ Advanced processing complete: {script_output_dir}")
            logger.info(f"📊 Statistics: {stats['total_scenes']} scenes, {stats['total_shots']} shots, {stats['total_voice_overs']} voice-overs")
            
            return script_output_dir
            
        except Exception as e:
            logger.error(f"Error in advanced processing: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _create_output_structure(self, output_dir: Path, 
                                scenes: List[EnhancedScene],
                                stats: Dict, script_name: str):
        """Create organized output structure"""
        
        # Main directories
        dirs = [
            "00_Statistics",
            "01_Scenes",
            "02_Shots",
            "03_VoiceOvers",
            "04_Transitions",
            "05_Veo3_Prompts"
        ]
        
        for dir_name in dirs:
            (output_dir / dir_name).mkdir(exist_ok=True)
        
        # Save statistics
        stats_file = output_dir / "00_Statistics" / "analysis.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
        
        # Process each scene
        all_shots = []
        all_voice_overs = []
        all_transitions = []
        
        for scene in scenes:
            # Scene directory
            scene_dir = output_dir / "01_Scenes" / f"Scene_{scene.scene_number}"
            scene_dir.mkdir(exist_ok=True)
            
            # Save scene data
            scene_file = scene_dir / f"scene_{scene.scene_number}_data.json"
            with open(scene_file, 'w') as f:
                json.dump(scene.to_dict(), f, indent=2)
            
            # Process shots
            for shot in scene.shots:
                all_shots.append(shot)
                
                # Individual shot file
                shot_file = (output_dir / "02_Shots" / 
                           f"{script_name}_scene{scene.scene_number}_shot{shot.shot_number}.json")
                with open(shot_file, 'w') as f:
                    json.dump(shot.to_dict(), f, indent=2)
                
                # Veo3 prompt
                veo3_file = (output_dir / "05_Veo3_Prompts" / 
                           f"{script_name}_scene{scene.scene_number}_shot{shot.shot_number}_veo3.json")
                with open(veo3_file, 'w') as f:
                    veo3_data = self._generate_veo3_prompt(shot, scene)
                    json.dump(veo3_data, f, indent=2)
            
            # Process voice-overs
            for vo in scene.voice_overs:
                all_voice_overs.append({
                    'scene': scene.scene_number,
                    **vo.to_dict()
                })
            
            # Process transitions
            if scene.transitions_in:
                all_transitions.append({
                    'scene': scene.scene_number,
                    'position': 'in',
                    **scene.transitions_in.to_dict()
                })
            if scene.transitions_out:
                all_transitions.append({
                    'scene': scene.scene_number,
                    'position': 'out',
                    **scene.transitions_out.to_dict()
                })
        
        # Save voice-overs
        if all_voice_overs:
            vo_file = output_dir / "03_VoiceOvers" / "all_voiceovers.json"
            with open(vo_file, 'w') as f:
                json.dump(all_voice_overs, f, indent=2)
        
        # Save transitions
        if all_transitions:
            trans_file = output_dir / "04_Transitions" / "all_transitions.json"
            with open(trans_file, 'w') as f:
                json.dump(all_transitions, f, indent=2)
        
        # Create master index
        self._create_master_index(output_dir, scenes, stats, script_name)
    
    def _generate_veo3_prompt(self, shot: VideoShot, scene: EnhancedScene) -> Dict:
        """Generate Veo3 prompt for shot"""
        prompt_parts = []
        
        # Camera
        prompt_parts.append(f"[CAMERA] {shot.shot_type}, {shot.camera_movement}")
        
        # Subject
        if shot.characters_in_frame:
            prompt_parts.append(f"[SUBJECT] {', '.join(shot.characters_in_frame)}")
        else:
            prompt_parts.append(f"[SUBJECT] {shot.description[:100]}")
        
        # Environment
        prompt_parts.append(f"[ENVIRONMENT] {scene.location}, {scene.time_of_day}")
        
        # Special effects
        if shot.is_flashback:
            prompt_parts.append("[EFFECT] Flashback treatment - desaturated, dreamy")
        if shot.is_montage:
            prompt_parts.append("[EFFECT] Montage sequence - quick cuts")
        
        # Voice-over
        if shot.voice_overs:
            prompt_parts.append(f"[AUDIO] Voice-over by {shot.voice_overs[0].character}")
        
        # Duration
        prompt_parts.append(f"[DURATION] {shot.duration}")
        
        return {
            "shot_id": shot.shot_id,
            "veo3_prompt": " | ".join(prompt_parts),
            "metadata": {
                "scene": scene.scene_number,
                "shot": shot.shot_number,
                "type": shot.shot_type
            }
        }
    
    def _create_master_index(self, output_dir: Path, 
                            scenes: List[EnhancedScene],
                            stats: Dict, script_name: str):
        """Create comprehensive master index"""
        index = {
            "project": script_name,
            "generated": datetime.now().isoformat(),
            "version": "5.0-ADVANCED",
            "statistics": stats,
            "structure": {
                "scenes": [
                    {
                        "number": scene.scene_number,
                        "heading": scene.heading,
                        "type": scene.scene_type,
                        "shots": len(scene.shots),
                        "voice_overs": len(scene.voice_overs),
                        "has_flashback": scene.scene_type == "FLASHBACK",
                        "transitions": {
                            "in": scene.transitions_in.type if scene.transitions_in else None,
                            "out": scene.transitions_out.type if scene.transitions_out else None
                        }
                    }
                    for scene in scenes
                ]
            },
            "summary": {
                "total_runtime_estimate": f"{stats['total_shots'] * 4} seconds (approx)",
                "narrative_elements": {
                    "present_scenes": stats['scene_types'].get('PRESENT', 0),
                    "flashback_scenes": stats['flashback_scenes'],
                    "montage_scenes": stats['montage_scenes'],
                    "voice_overs": stats['total_voice_overs']
                },
                "technical_breakdown": {
                    "wide_shots": stats['shot_types'].get('WIDE', 0) + stats['shot_types'].get('WIDE ESTABLISHING', 0),
                    "medium_shots": stats['shot_types'].get('MEDIUM', 0),
                    "close_ups": stats['shot_types'].get('CLOSE-UP', 0),
                    "dialogue_shots": stats['dialogue_shots'],
                    "action_shots": stats['action_shots']
                }
            }
        }
        
        index_file = output_dir / "MASTER_INDEX.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _generate_report(self, output_dir: Path, 
                        scenes: List[EnhancedScene], 
                        stats: Dict):
        """Generate human-readable report"""
        report_lines = [
            "FILM CREW AI - ADVANCED SCRIPT ANALYSIS REPORT",
            "=" * 50,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "OVERVIEW",
            "-" * 20,
            f"Total Scenes: {stats['total_scenes']}",
            f"Total Shots: {stats['total_shots']}",
            f"Total Voice-Overs: {stats['total_voice_overs']}",
            "",
            "SCENE BREAKDOWN",
            "-" * 20
        ]
        
        for scene in scenes:
            report_lines.extend([
                f"\nScene {scene.scene_number}: {scene.heading}",
                f"  Type: {scene.scene_type}",
                f"  Shots: {len(scene.shots)}",
                f"  Voice-Overs: {len(scene.voice_overs)}",
                f"  Location: {scene.location}",
                f"  Time: {scene.time_of_day}"
            ])
            
            if scene.transitions_in:
                report_lines.append(f"  Transition In: {scene.transitions_in.type}")
            if scene.transitions_out:
                report_lines.append(f"  Transition Out: {scene.transitions_out.type}")
        
        report_lines.extend([
            "",
            "SHOT TYPE DISTRIBUTION",
            "-" * 20
        ])
        
        for shot_type, count in stats['shot_types'].items():
            report_lines.append(f"  {shot_type}: {count}")
        
        report_lines.extend([
            "",
            "VOICE-OVER SUMMARY",
            "-" * 20
        ])
        
        vo_characters = set()
        for scene in scenes:
            for vo in scene.voice_overs:
                vo_characters.add(vo.character)
        
        for character in vo_characters:
            report_lines.append(f"  {character}: Voice-over narration")
        
        report_file = output_dir / "ANALYSIS_REPORT.txt"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for advanced system"""
    parser = argparse.ArgumentParser(
        description="Film Crew AI v5.0 - Advanced Scene/Shot/VO Detection"
    )
    parser.add_argument('--script', type=str, help='Path to script file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Create processor
    processor = AdvancedFilmCrewProcessor(project_dir)
    
    if args.script:
        script_path = Path(args.script)
        if script_path.exists():
            result = processor.process_script(script_path)
            if result:
                print(f"\nSuccess! Output saved to: {result}")
        else:
            print(f"Script not found: {script_path}")
    else:
        # Test with complex script
        test_script = project_dir / "scripts" / "complex_script.txt"
        if test_script.exists():
            processor.process_script(test_script)
        else:
            print("No script specified. Use --script parameter.")


if __name__ == "__main__":
    main()