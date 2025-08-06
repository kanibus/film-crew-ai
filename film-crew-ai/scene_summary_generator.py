#!/usr/bin/env python3
"""
Scene Summary Generator
Creates concise summaries for each scene with quick overview of key elements
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class SceneSummary:
    """Represents a summary of a single scene"""
    scene_number: str
    location: str
    time_of_day: str
    characters: List[str]
    shot_count: int
    total_duration: str
    key_actions: List[str]
    voice_overs: List[str]
    emotional_tone: str
    narrative_purpose: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class SceneSummaryGenerator:
    """Generates comprehensive scene summaries for quick overview"""
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.summaries_dir = output_dir / "Scene_Summaries"
        self.summaries_dir.mkdir(exist_ok=True)
        
    def generate_scene_summary(self, 
                              scene_data: Dict,
                              shots: List[Dict],
                              voice_overs: List[str]) -> SceneSummary:
        """Generate summary for a single scene"""
        
        # Extract scene details
        scene_number = str(scene_data.get('scene_number', ''))
        location = scene_data.get('location', 'Unknown Location')
        time_of_day = scene_data.get('time_of_day', 'DAY')
        
        # Extract characters from scene
        characters = self._extract_characters(scene_data)
        
        # Calculate shot metrics
        shot_count = len(shots)
        total_duration = self._calculate_duration(shots)
        
        # Extract key actions
        key_actions = self._extract_key_actions(scene_data, shots)
        
        # Determine emotional tone
        emotional_tone = self._determine_emotional_tone(scene_data)
        
        # Determine narrative purpose
        narrative_purpose = self._determine_narrative_purpose(scene_data, scene_number)
        
        summary = SceneSummary(
            scene_number=scene_number,
            location=location,
            time_of_day=time_of_day,
            characters=characters,
            shot_count=shot_count,
            total_duration=total_duration,
            key_actions=key_actions,
            voice_overs=voice_overs[:3],  # First 3 VOs as preview
            emotional_tone=emotional_tone,
            narrative_purpose=narrative_purpose
        )
        
        return summary
    
    def _extract_characters(self, scene_data: Dict) -> List[str]:
        """Extract character names from scene"""
        characters = []
        
        # From dialogue
        if 'dialogue' in scene_data:
            for dialogue in scene_data['dialogue']:
                if 'character' in dialogue:
                    char = dialogue['character']
                    if char not in characters:
                        characters.append(char)
        
        # From action lines
        content = scene_data.get('content', '')
        # Simple extraction - look for capitalized names
        import re
        potential_names = re.findall(r'\b[A-Z][A-Z]+\b', content)
        for name in potential_names:
            if name not in characters and len(name) > 2:
                characters.append(name)
        
        return characters[:5]  # Limit to top 5 characters
    
    def _calculate_duration(self, shots: List[Dict]) -> str:
        """Calculate total duration based on shots"""
        if not shots:
            return "0 seconds"
            
        # Estimate 3-5 seconds per shot
        min_duration = len(shots) * 3
        max_duration = len(shots) * 5
        
        if min_duration < 60:
            return f"{min_duration}-{max_duration} seconds"
        else:
            min_minutes = min_duration // 60
            max_minutes = max_duration // 60
            return f"{min_minutes}-{max_minutes} minutes"
    
    def _extract_key_actions(self, scene_data: Dict, shots: List[Dict]) -> List[str]:
        """Extract key actions from scene"""
        actions = []
        
        # From scene content
        content = scene_data.get('content', '')
        lines = content.split('\n')
        
        # Look for action lines (not dialogue or sluglines)
        for line in lines:
            line = line.strip()
            if line and not line.startswith('INT.') and not line.startswith('EXT.'):
                if not any(line.startswith(c) for c in ['(', 'FADE', 'CUT']):
                    if len(line) > 20:  # Meaningful action lines
                        actions.append(line[:100])  # Truncate long lines
                        if len(actions) >= 3:
                            break
        
        return actions
    
    def _determine_emotional_tone(self, scene_data: Dict) -> str:
        """Determine the emotional tone of the scene"""
        content = scene_data.get('content', '').lower()
        
        # Simple keyword-based analysis
        tones = {
            'tense': ['nervous', 'worried', 'anxious', 'fear', 'threat'],
            'dramatic': ['shock', 'surprise', 'reveal', 'discover'],
            'romantic': ['love', 'kiss', 'embrace', 'tender', 'gentle'],
            'action': ['run', 'chase', 'fight', 'escape', 'rush'],
            'contemplative': ['think', 'consider', 'ponder', 'reflect'],
            'melancholic': ['sad', 'cry', 'tears', 'loss', 'goodbye'],
            'hopeful': ['hope', 'future', 'promise', 'new', 'begin']
        }
        
        for tone, keywords in tones.items():
            if any(keyword in content for keyword in keywords):
                return tone
        
        return "neutral"
    
    def _determine_narrative_purpose(self, scene_data: Dict, scene_number: str) -> str:
        """Determine the narrative purpose of the scene"""
        
        # Basic narrative structure
        scene_num = int(scene_number) if scene_number.isdigit() else 1
        
        if scene_num == 1:
            return "Opening - Establish world and characters"
        elif scene_num <= 3:
            return "Setup - Introduce conflict and stakes"
        elif 'reveal' in scene_data.get('content', '').lower():
            return "Revelation - Key information revealed"
        elif 'confrontation' in scene_data.get('content', '').lower():
            return "Confrontation - Characters clash"
        else:
            return "Development - Advance plot and character arcs"
    
    def save_scene_summary(self, summary: SceneSummary, script_name: str) -> Path:
        """Save scene summary to file"""
        
        # Create scene-specific file
        filename = f"{script_name}_scene{summary.scene_number}_summary.json"
        summary_file = self.summaries_dir / filename
        
        # Save as JSON
        with open(summary_file, 'w') as f:
            json.dump(summary.to_dict(), f, indent=2)
        
        return summary_file
    
    def generate_master_summary(self, 
                               all_summaries: List[SceneSummary],
                               script_name: str) -> Dict:
        """Generate master summary of entire script"""
        
        master = {
            "script_name": script_name,
            "generated_at": datetime.now().isoformat(),
            "total_scenes": len(all_summaries),
            "total_shots": sum(s.shot_count for s in all_summaries),
            "estimated_duration": self._calculate_total_duration(all_summaries),
            "main_characters": self._extract_main_characters(all_summaries),
            "locations": self._extract_unique_locations(all_summaries),
            "emotional_arc": self._determine_emotional_arc(all_summaries),
            "scene_breakdown": []
        }
        
        # Add scene breakdown
        for summary in all_summaries:
            scene_info = {
                "scene": summary.scene_number,
                "location": summary.location,
                "time": summary.time_of_day,
                "shots": summary.shot_count,
                "tone": summary.emotional_tone,
                "purpose": summary.narrative_purpose
            }
            master["scene_breakdown"].append(scene_info)
        
        # Save master summary
        master_file = self.summaries_dir / f"{script_name}_MASTER_SUMMARY.json"
        with open(master_file, 'w') as f:
            json.dump(master, f, indent=2)
        
        # Also create a quick text overview
        self._create_text_overview(master, script_name)
        
        return master
    
    def _calculate_total_duration(self, summaries: List[SceneSummary]) -> str:
        """Calculate total estimated duration"""
        total_shots = sum(s.shot_count for s in summaries)
        min_seconds = total_shots * 3
        max_seconds = total_shots * 5
        
        min_minutes = min_seconds // 60
        max_minutes = max_seconds // 60
        
        return f"{min_minutes}-{max_minutes} minutes"
    
    def _extract_main_characters(self, summaries: List[SceneSummary]) -> List[str]:
        """Extract main characters across all scenes"""
        character_count = {}
        
        for summary in summaries:
            for char in summary.characters:
                character_count[char] = character_count.get(char, 0) + 1
        
        # Sort by appearance count
        sorted_chars = sorted(character_count.items(), key=lambda x: x[1], reverse=True)
        return [char for char, _ in sorted_chars[:5]]
    
    def _extract_unique_locations(self, summaries: List[SceneSummary]) -> List[str]:
        """Extract unique locations"""
        locations = set()
        for summary in summaries:
            locations.add(f"{summary.location} - {summary.time_of_day}")
        return sorted(list(locations))
    
    def _determine_emotional_arc(self, summaries: List[SceneSummary]) -> str:
        """Determine overall emotional arc of the script"""
        if not summaries:
            return "Unknown"
        
        # Simple arc based on beginning and end tones
        start_tone = summaries[0].emotional_tone if summaries else "neutral"
        end_tone = summaries[-1].emotional_tone if summaries else "neutral"
        
        if start_tone == "neutral" and end_tone == "hopeful":
            return "Ascending - Moves toward hope"
        elif start_tone == "hopeful" and end_tone in ["melancholic", "tense"]:
            return "Descending - Moves toward conflict"
        elif "dramatic" in [s.emotional_tone for s in summaries]:
            return "Dramatic - Building tension and release"
        else:
            return "Steady - Consistent emotional tone"
    
    def _create_text_overview(self, master: Dict, script_name: str):
        """Create a human-readable text overview"""
        
        overview_file = self.summaries_dir / f"{script_name}_OVERVIEW.txt"
        
        with open(overview_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write(f"FILM PRODUCTION OVERVIEW: {script_name}\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"Total Scenes: {master['total_scenes']}\n")
            f.write(f"Total Shots: {master['total_shots']}\n")
            f.write(f"Estimated Duration: {master['estimated_duration']}\n\n")
            
            f.write("MAIN CHARACTERS:\n")
            for char in master['main_characters']:
                f.write(f"  • {char}\n")
            f.write("\n")
            
            f.write("LOCATIONS:\n")
            for loc in master['locations']:
                f.write(f"  • {loc}\n")
            f.write("\n")
            
            f.write(f"EMOTIONAL ARC: {master['emotional_arc']}\n\n")
            
            f.write("SCENE-BY-SCENE BREAKDOWN:\n")
            f.write("-" * 60 + "\n")
            
            for scene in master['scene_breakdown']:
                f.write(f"\nScene {scene['scene']}: {scene['location']} - {scene['time']}\n")
                f.write(f"  Shots: {scene['shots']} | Tone: {scene['tone']}\n")
                f.write(f"  Purpose: {scene['purpose']}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Generated by Film Crew AI\n")
            f.write(f"Timestamp: {master['generated_at']}\n")
            f.write("=" * 60 + "\n")


def integrate_with_pipeline(output_dir: Path, 
                           scenes: List[Dict],
                           script_name: str) -> SceneSummaryGenerator:
    """Integrate scene summaries with main pipeline"""
    
    generator = SceneSummaryGenerator(output_dir)
    all_summaries = []
    
    # Generate summary for each scene
    for scene in scenes:
        shots = scene.get('shots', [])
        voice_overs = scene.get('voice_overs', [])
        
        summary = generator.generate_scene_summary(scene, shots, voice_overs)
        generator.save_scene_summary(summary, script_name)
        all_summaries.append(summary)
    
    # Generate master summary
    generator.generate_master_summary(all_summaries, script_name)
    
    print(f"\n✓ Generated {len(all_summaries)} scene summaries")
    print(f"✓ Master summary created in {generator.summaries_dir}")
    
    return generator


if __name__ == "__main__":
    # Test the summary generator
    test_output = Path("output/test_summaries")
    test_output.mkdir(parents=True, exist_ok=True)
    
    # Sample scene data
    test_scene = {
        'scene_number': '1',
        'location': 'COFFEE SHOP',
        'time_of_day': 'DAY',
        'content': 'INT. COFFEE SHOP - DAY\n\nSARAH enters nervously.',
        'dialogue': [
            {'character': 'SARAH', 'text': 'Is anyone here?'}
        ]
    }
    
    test_shots = [
        {'shot_number': '001', 'type': 'WIDE'},
        {'shot_number': '002', 'type': 'CLOSE-UP'}
    ]
    
    test_vos = ["Some choices define us..."]
    
    generator = SceneSummaryGenerator(test_output)
    summary = generator.generate_scene_summary(test_scene, test_shots, test_vos)
    generator.save_scene_summary(summary, "test_script")
    
    print("Scene summary generated successfully!")
    print(f"Summary: {summary.to_dict()}")