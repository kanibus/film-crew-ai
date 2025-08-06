#!/usr/bin/env python3
"""
Film Crew AI - Vignette Script Parser v5.1
Specialized parser for vignette-style scripts with Video/VO format
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
from dataclasses import dataclass, asdict, field
import traceback
from collections import defaultdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('FilmCrewAI-Vignette')


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class VignetteSegment:
    """Represents a segment in a vignette script"""
    segment_id: str
    segment_number: int
    type: str  # "video", "vo", "transition", "text_overlay"
    content: str
    visual_notes: str = ""
    narration: str = ""
    on_screen_text: str = ""
    characters_mentioned: List[str] = field(default_factory=list)
    location: str = ""
    time_period: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class VignetteScene:
    """Represents a vignette scene with video and VO segments"""
    scene_number: int
    scene_title: str
    segments: List[VignetteSegment]
    total_video_segments: int
    total_vo_segments: int
    characters: List[str]
    locations: List[str]
    transitions: List[str]
    
    def to_dict(self) -> Dict:
        return {
            "scene_number": self.scene_number,
            "scene_title": self.scene_title,
            "segments": [seg.to_dict() for seg in self.segments],
            "total_video_segments": self.total_video_segments,
            "total_vo_segments": self.total_vo_segments,
            "characters": self.characters,
            "locations": self.locations,
            "transitions": self.transitions
        }


# ============================================================================
# VIGNETTE PARSER
# ============================================================================

class VignetteScriptParser:
    """Parser specifically for vignette-style scripts"""
    
    def __init__(self):
        # Patterns for vignette format
        self.video_pattern = re.compile(r'^Video:\s*(.*)$', re.MULTILINE | re.IGNORECASE)
        self.vo_pattern = re.compile(r'^VO:\s*(.*)$', re.MULTILINE | re.IGNORECASE)
        self.narration_pattern = re.compile(r'^NARRATION.*?:\s*(.*)$', re.MULTILINE | re.IGNORECASE)
        self.visual_notes_pattern = re.compile(r'^VISUAL NOTES\s*(.*)$', re.MULTILINE | re.IGNORECASE)
        
        # Text overlay patterns
        self.on_screen_pattern = re.compile(r'(?:On screen text:|Text on screen:|Text overlay:)\s*(.+)', re.IGNORECASE)
        self.text_on_pattern = re.compile(r'Text on (?:watch|screen|device):\s*["\']?(.+?)["\']?$', re.IGNORECASE)
        
        # Time/location patterns
        self.year_pattern = re.compile(r'Year:\s*(\d{4})', re.IGNORECASE)
        self.time_pattern = re.compile(r'Time:\s*(\d{1,2}:\d{2}\s*[ap]m)', re.IGNORECASE)
        
        # Character patterns
        self.character_names = ['Dr. Roy', 'Dr. Jalen Roy', 'Michael', 'Lanie', 'Priya']
        self.meet_pattern = re.compile(r'Meet\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', re.IGNORECASE)
        
        # Transition patterns
        self.transition_pattern = re.compile(r'TRANSITION TO|CUT TO|FADE TO|DISSOLVE TO', re.IGNORECASE)
        
        # Voice patterns
        self.digital_assistant_pattern = re.compile(r'Digital assistant voice:\s*(.+)', re.IGNORECASE)
        self.patient_voice_pattern = re.compile(r'Patient voice:\s*\(([^)]+)\)\s*(.+)', re.IGNORECASE)
        
    def parse(self, script_path: Path) -> Tuple[List[VignetteScene], Dict]:
        """Parse vignette script"""
        logger.info(f"Parsing vignette script: {script_path}")
        
        # Read content with proper encoding
        from enhanced_document_reader import EnhancedDocumentReader
        content = EnhancedDocumentReader.read_file(script_path)
        
        # Split into major sections
        scenes = self._extract_vignette_scenes(content)
        
        # Generate statistics
        stats = self._generate_statistics(scenes)
        
        logger.info(f"Parsed {len(scenes)} vignette scenes with {stats['total_segments']} segments")
        
        return scenes, stats
    
    def _extract_vignette_scenes(self, content: str) -> List[VignetteScene]:
        """Extract vignette scenes from content"""
        scenes = []
        
        # Split by "Vignette #" or major transitions
        vignette_splits = re.split(r'(?:Vignette #\d+|NARRATION \(Vignette #\d+\))', content)
        
        # Also check for TRANSITION TO markers
        if len(vignette_splits) <= 1:
            # Try splitting by major sections
            vignette_splits = re.split(r'TRANSITION TO[.\s]*', content)
        
        # Process each section
        scene_number = 1
        for section in vignette_splits:
            if len(section.strip()) > 50:  # Minimum content threshold
                scene = self._process_vignette_section(section, scene_number)
                if scene and scene.segments:  # Only add if has content
                    scenes.append(scene)
                    scene_number += 1
        
        # If no clear vignettes found, process as single scene
        if not scenes:
            scene = self._process_single_vignette(content)
            if scene:
                scenes.append(scene)
        
        return scenes
    
    def _process_vignette_section(self, section: str, scene_number: int) -> Optional[VignetteScene]:
        """Process a vignette section"""
        segments = []
        segment_number = 1
        
        # Extract title if present
        title_match = re.search(r'(?:Vignette #\d+[:\s]*)?([^\n]+)', section[:100])
        scene_title = f"Vignette {scene_number}"
        if title_match:
            potential_title = title_match.group(1).strip()
            if len(potential_title) > 5 and len(potential_title) < 100:
                scene_title = potential_title
        
        # Split into lines for processing
        lines = section.split('\n')
        current_segment = None
        current_type = None
        buffer = []
        
        for line in lines:
            line_stripped = line.strip()
            
            # Check for Video marker
            if self.video_pattern.match(line_stripped):
                # Save previous segment
                if current_segment and buffer:
                    current_segment.content = '\n'.join(buffer)
                    segments.append(current_segment)
                    buffer = []
                
                # Start new video segment
                current_segment = VignetteSegment(
                    segment_id=f"{scene_number}-{segment_number:03d}",
                    segment_number=segment_number,
                    type="video",
                    content=""
                )
                current_type = "video"
                segment_number += 1
                
                # Get initial content
                match = self.video_pattern.match(line_stripped)
                if match and match.group(1):
                    buffer.append(match.group(1))
            
            # Check for VO marker
            elif self.vo_pattern.match(line_stripped) or line_stripped.startswith('VO:'):
                # Save previous segment
                if current_segment and buffer:
                    current_segment.content = '\n'.join(buffer)
                    segments.append(current_segment)
                    buffer = []
                
                # Start new VO segment
                current_segment = VignetteSegment(
                    segment_id=f"{scene_number}-{segment_number:03d}",
                    segment_number=segment_number,
                    type="vo",
                    content="",
                    narration=""
                )
                current_type = "vo"
                segment_number += 1
                
                # Get initial content
                match = self.vo_pattern.match(line_stripped)
                if match and match.group(1):
                    buffer.append(match.group(1))
            
            # Check for on-screen text
            elif self.on_screen_pattern.search(line_stripped) or self.text_on_pattern.search(line_stripped):
                text_content = ""
                
                if self.on_screen_pattern.search(line_stripped):
                    match = self.on_screen_pattern.search(line_stripped)
                    text_content = match.group(1)
                elif self.text_on_pattern.search(line_stripped):
                    match = self.text_on_pattern.search(line_stripped)
                    text_content = match.group(1)
                
                if current_segment:
                    current_segment.on_screen_text = text_content
                else:
                    # Create text overlay segment
                    segments.append(VignetteSegment(
                        segment_id=f"{scene_number}-{segment_number:03d}",
                        segment_number=segment_number,
                        type="text_overlay",
                        content=text_content,
                        on_screen_text=text_content
                    ))
                    segment_number += 1
            
            # Check for digital assistant voice
            elif self.digital_assistant_pattern.match(line_stripped):
                match = self.digital_assistant_pattern.match(line_stripped)
                if current_segment:
                    current_segment.narration = f"Digital Assistant: {match.group(1)}"
                else:
                    segments.append(VignetteSegment(
                        segment_id=f"{scene_number}-{segment_number:03d}",
                        segment_number=segment_number,
                        type="vo",
                        content=match.group(1),
                        narration=f"Digital Assistant: {match.group(1)}"
                    ))
                    segment_number += 1
            
            # Check for patient voice
            elif self.patient_voice_pattern.match(line_stripped):
                match = self.patient_voice_pattern.match(line_stripped)
                character = match.group(1)
                dialogue = match.group(2)
                
                if current_segment:
                    current_segment.narration = f"{character}: {dialogue}"
                    current_segment.characters_mentioned.append(character)
                else:
                    segments.append(VignetteSegment(
                        segment_id=f"{scene_number}-{segment_number:03d}",
                        segment_number=segment_number,
                        type="vo",
                        content=dialogue,
                        narration=f"{character}: {dialogue}",
                        characters_mentioned=[character]
                    ))
                    segment_number += 1
            
            # Regular content line
            elif line_stripped and current_segment:
                buffer.append(line_stripped)
                
                # Extract characters mentioned
                for char_name in self.character_names:
                    if char_name in line_stripped:
                        if char_name not in current_segment.characters_mentioned:
                            current_segment.characters_mentioned.append(char_name)
                
                # Extract time/location info
                if self.year_pattern.search(line_stripped):
                    match = self.year_pattern.search(line_stripped)
                    current_segment.time_period = match.group(1)
                
                if self.time_pattern.search(line_stripped):
                    match = self.time_pattern.search(line_stripped)
                    if current_segment.time_period:
                        current_segment.time_period += f" {match.group(1)}"
                    else:
                        current_segment.time_period = match.group(1)
        
        # Save last segment
        if current_segment and buffer:
            current_segment.content = '\n'.join(buffer)
            segments.append(current_segment)
        
        # Extract scene metadata
        all_characters = []
        all_locations = []
        all_transitions = []
        video_count = 0
        vo_count = 0
        
        for seg in segments:
            all_characters.extend(seg.characters_mentioned)
            
            if seg.type == "video":
                video_count += 1
                # Extract locations from video descriptions
                if "farmhouse" in seg.content.lower():
                    all_locations.append("Farmhouse")
                if "home" in seg.content.lower():
                    all_locations.append("Home")
                if "office" in seg.content.lower():
                    all_locations.append("Office")
                if "hospital" in seg.content.lower():
                    all_locations.append("Hospital")
                    
            elif seg.type == "vo":
                vo_count += 1
            
            # Check for transitions
            if self.transition_pattern.search(seg.content):
                match = self.transition_pattern.search(seg.content)
                all_transitions.append(match.group(0))
        
        # Deduplicate
        all_characters = list(set(all_characters))
        all_locations = list(set(all_locations))
        
        return VignetteScene(
            scene_number=scene_number,
            scene_title=scene_title,
            segments=segments,
            total_video_segments=video_count,
            total_vo_segments=vo_count,
            characters=all_characters,
            locations=all_locations,
            transitions=all_transitions
        )
    
    def _process_single_vignette(self, content: str) -> Optional[VignetteScene]:
        """Process entire content as single vignette"""
        return self._process_vignette_section(content, 1)
    
    def _generate_statistics(self, scenes: List[VignetteScene]) -> Dict:
        """Generate statistics for vignette script"""
        stats = {
            'total_scenes': len(scenes),
            'total_segments': sum(len(scene.segments) for scene in scenes),
            'total_video_segments': sum(scene.total_video_segments for scene in scenes),
            'total_vo_segments': sum(scene.total_vo_segments for scene in scenes),
            'total_text_overlays': 0,
            'characters': set(),
            'locations': set(),
            'time_periods': set()
        }
        
        for scene in scenes:
            stats['characters'].update(scene.characters)
            stats['locations'].update(scene.locations)
            
            for segment in scene.segments:
                if segment.type == "text_overlay":
                    stats['total_text_overlays'] += 1
                if segment.time_period:
                    stats['time_periods'].add(segment.time_period)
        
        # Convert sets to lists for JSON serialization
        stats['characters'] = list(stats['characters'])
        stats['locations'] = list(stats['locations'])
        stats['time_periods'] = list(stats['time_periods'])
        
        return stats


# ============================================================================
# VIGNETTE PROCESSOR
# ============================================================================

class VignetteFilmCrewProcessor:
    """Processor for vignette-style scripts"""
    
    def __init__(self, project_dir: Path):
        self.project_dir = project_dir
        self.output_dir = project_dir / "output"
        self.scripts_dir = project_dir / "scripts"
        
        # Initialize parser
        self.parser = VignetteScriptParser()
        
        # Create directories
        self.output_dir.mkdir(exist_ok=True)
        self.scripts_dir.mkdir(exist_ok=True)
    
    def process_script(self, script_path: Path) -> Optional[Path]:
        """Process vignette script"""
        try:
            logger.info(f"Processing vignette script: {script_path.name}")
            
            # Parse script
            scenes, stats = self.parser.parse(script_path)
            
            if not scenes:
                logger.warning("No scenes detected in vignette script")
                return None
            
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_name = f"{script_path.stem}_{timestamp}_vignette"
            script_output_dir = self.output_dir / output_name
            script_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create organized structure
            self._create_output_structure(script_output_dir, scenes, stats, script_path.stem)
            
            # Generate report
            self._generate_report(script_output_dir, scenes, stats)
            
            logger.info(f"✅ Vignette processing complete: {script_output_dir}")
            logger.info(f"📊 Statistics: {stats['total_scenes']} scenes, {stats['total_segments']} segments")
            logger.info(f"   Video segments: {stats['total_video_segments']}")
            logger.info(f"   VO segments: {stats['total_vo_segments']}")
            logger.info(f"   Characters: {', '.join(stats['characters']) if stats['characters'] else 'None detected'}")
            
            return script_output_dir
            
        except Exception as e:
            logger.error(f"Error processing vignette script: {e}")
            logger.error(traceback.format_exc())
            return None
    
    def _create_output_structure(self, output_dir: Path, 
                                scenes: List[VignetteScene],
                                stats: Dict, script_name: str):
        """Create organized output structure for vignette"""
        
        # Main directories
        dirs = [
            "00_Statistics",
            "01_Vignettes",
            "02_Video_Segments",
            "03_VO_Segments",
            "04_Text_Overlays",
            "05_Characters",
            "06_Veo3_Prompts"
        ]
        
        for dir_name in dirs:
            (output_dir / dir_name).mkdir(exist_ok=True)
        
        # Save statistics
        stats_file = output_dir / "00_Statistics" / "vignette_analysis.json"
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
        
        # Process each vignette scene
        all_video_segments = []
        all_vo_segments = []
        all_text_overlays = []
        
        for scene in scenes:
            # Vignette directory
            vignette_dir = output_dir / "01_Vignettes" / f"Vignette_{scene.scene_number}"
            vignette_dir.mkdir(exist_ok=True)
            
            # Save vignette data
            vignette_file = vignette_dir / f"vignette_{scene.scene_number}_data.json"
            with open(vignette_file, 'w') as f:
                json.dump(scene.to_dict(), f, indent=2)
            
            # Process segments
            for segment in scene.segments:
                if segment.type == "video":
                    all_video_segments.append(segment)
                    
                    # Save video segment
                    video_file = (output_dir / "02_Video_Segments" / 
                                f"{script_name}_vignette{scene.scene_number}_video{segment.segment_number:03d}.json")
                    with open(video_file, 'w') as f:
                        json.dump(segment.to_dict(), f, indent=2)
                    
                    # Generate Veo3 prompt for video segment
                    veo3_prompt = self._generate_veo3_for_video(segment, scene)
                    veo3_file = (output_dir / "06_Veo3_Prompts" / 
                               f"{script_name}_vignette{scene.scene_number}_video{segment.segment_number:03d}_veo3.json")
                    with open(veo3_file, 'w') as f:
                        json.dump(veo3_prompt, f, indent=2)
                
                elif segment.type == "vo":
                    all_vo_segments.append(segment)
                    
                    # Save VO segment
                    vo_file = (output_dir / "03_VO_Segments" / 
                             f"{script_name}_vignette{scene.scene_number}_vo{segment.segment_number:03d}.json")
                    with open(vo_file, 'w') as f:
                        json.dump(segment.to_dict(), f, indent=2)
                
                elif segment.type == "text_overlay":
                    all_text_overlays.append(segment)
                    
                    # Save text overlay
                    text_file = (output_dir / "04_Text_Overlays" / 
                               f"{script_name}_vignette{scene.scene_number}_text{segment.segment_number:03d}.json")
                    with open(text_file, 'w') as f:
                        json.dump(segment.to_dict(), f, indent=2)
        
        # Save character information
        if stats['characters']:
            char_file = output_dir / "05_Characters" / "all_characters.json"
            with open(char_file, 'w') as f:
                json.dump({
                    "characters": stats['characters'],
                    "character_appearances": self._track_character_appearances(scenes)
                }, f, indent=2)
        
        # Create master index
        self._create_master_index(output_dir, scenes, stats, script_name)
    
    def _generate_veo3_for_video(self, segment: VignetteSegment, scene: VignetteScene) -> Dict:
        """Generate Veo3 prompt for video segment"""
        prompt_parts = []
        
        # Determine shot type from content
        content_lower = segment.content.lower()
        if "establishing" in content_lower or "wide" in content_lower:
            shot_type = "WIDE ESTABLISHING"
        elif "close" in content_lower:
            shot_type = "CLOSE-UP"
        else:
            shot_type = "MEDIUM"
        
        prompt_parts.append(f"[SHOT TYPE] {shot_type}")
        
        # Add visual description
        prompt_parts.append(f"[VISUAL] {segment.content[:200]}")
        
        # Add characters if present
        if segment.characters_mentioned:
            prompt_parts.append(f"[CHARACTERS] {', '.join(segment.characters_mentioned)}")
        
        # Add time period if present
        if segment.time_period:
            prompt_parts.append(f"[TIME] {segment.time_period}")
        
        # Add on-screen text if present
        if segment.on_screen_text:
            prompt_parts.append(f"[TEXT OVERLAY] {segment.on_screen_text}")
        
        # Add narration if present
        if segment.narration:
            prompt_parts.append(f"[AUDIO] {segment.narration[:100]}")
        
        return {
            "segment_id": segment.segment_id,
            "veo3_prompt": " | ".join(prompt_parts),
            "type": "video",
            "vignette": scene.scene_number
        }
    
    def _track_character_appearances(self, scenes: List[VignetteScene]) -> Dict:
        """Track where each character appears"""
        appearances = defaultdict(list)
        
        for scene in scenes:
            for segment in scene.segments:
                for character in segment.characters_mentioned:
                    appearances[character].append({
                        "vignette": scene.scene_number,
                        "segment": segment.segment_id,
                        "type": segment.type
                    })
        
        return dict(appearances)
    
    def _create_master_index(self, output_dir: Path, 
                            scenes: List[VignetteScene],
                            stats: Dict, script_name: str):
        """Create master index for vignette"""
        index = {
            "project": script_name,
            "type": "vignette_script",
            "generated": datetime.now().isoformat(),
            "version": "5.1-VIGNETTE",
            "statistics": stats,
            "structure": {
                "vignettes": [
                    {
                        "number": scene.scene_number,
                        "title": scene.scene_title,
                        "video_segments": scene.total_video_segments,
                        "vo_segments": scene.total_vo_segments,
                        "characters": scene.characters,
                        "locations": scene.locations
                    }
                    for scene in scenes
                ]
            },
            "summary": {
                "total_vignettes": len(scenes),
                "total_segments": stats['total_segments'],
                "video_segments": stats['total_video_segments'],
                "vo_segments": stats['total_vo_segments'],
                "text_overlays": stats['total_text_overlays'],
                "unique_characters": len(stats['characters']),
                "unique_locations": len(stats['locations']),
                "time_periods": stats['time_periods']
            }
        }
        
        index_file = output_dir / "MASTER_INDEX.json"
        with open(index_file, 'w') as f:
            json.dump(index, f, indent=2)
    
    def _generate_report(self, output_dir: Path, 
                        scenes: List[VignetteScene], 
                        stats: Dict):
        """Generate human-readable report for vignette"""
        report_lines = [
            "FILM CREW AI - VIGNETTE SCRIPT ANALYSIS REPORT",
            "=" * 50,
            "",
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "OVERVIEW",
            "-" * 20,
            f"Total Vignettes: {stats['total_scenes']}",
            f"Total Segments: {stats['total_segments']}",
            f"  - Video Segments: {stats['total_video_segments']}",
            f"  - VO Segments: {stats['total_vo_segments']}",
            f"  - Text Overlays: {stats['total_text_overlays']}",
            "",
            "CHARACTERS IDENTIFIED",
            "-" * 20
        ]
        
        if stats['characters']:
            for character in stats['characters']:
                report_lines.append(f"  • {character}")
        else:
            report_lines.append("  No specific characters identified")
        
        report_lines.extend([
            "",
            "LOCATIONS",
            "-" * 20
        ])
        
        if stats['locations']:
            for location in stats['locations']:
                report_lines.append(f"  • {location}")
        else:
            report_lines.append("  No specific locations identified")
        
        report_lines.extend([
            "",
            "TIME PERIODS",
            "-" * 20
        ])
        
        if stats['time_periods']:
            for period in stats['time_periods']:
                report_lines.append(f"  • {period}")
        else:
            report_lines.append("  No specific time periods identified")
        
        report_lines.extend([
            "",
            "VIGNETTE BREAKDOWN",
            "-" * 20
        ])
        
        for scene in scenes:
            report_lines.extend([
                f"\nVignette {scene.scene_number}: {scene.scene_title}",
                f"  Video Segments: {scene.total_video_segments}",
                f"  VO Segments: {scene.total_vo_segments}",
                f"  Total Segments: {len(scene.segments)}"
            ])
            
            if scene.characters:
                report_lines.append(f"  Characters: {', '.join(scene.characters)}")
            
            if scene.locations:
                report_lines.append(f"  Locations: {', '.join(scene.locations)}")
        
        report_file = output_dir / "VIGNETTE_ANALYSIS_REPORT.txt"
        with open(report_file, 'w') as f:
            f.write('\n'.join(report_lines))


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for vignette parser"""
    parser = argparse.ArgumentParser(
        description="Film Crew AI v5.1 - Vignette Script Parser"
    )
    parser.add_argument('--script', type=str, help='Path to vignette script file')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get project directory
    project_dir = Path(__file__).parent
    
    # Create processor
    processor = VignetteFilmCrewProcessor(project_dir)
    
    if args.script:
        script_path = Path(args.script)
        if script_path.exists():
            result = processor.process_script(script_path)
            if result:
                print(f"\nSuccess! Output saved to: {result}")
        else:
            print(f"Script not found: {script_path}")
    else:
        # Test with ES Health script
        test_script = project_dir / "scripts" / "DRAFT V3 - ES Health Vignettes (All in one).txt"
        if test_script.exists():
            processor.process_script(test_script)
        else:
            print("No script specified. Use --script parameter.")


if __name__ == "__main__":
    main()