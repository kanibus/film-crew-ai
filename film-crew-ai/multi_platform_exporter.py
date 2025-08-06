#!/usr/bin/env python3
"""
Multi-Platform Video Generator Exporter
Supports multiple AI video generation platforms beyond Veo3
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class VideoGeneratorConfig:
    """Configuration for different video generation platforms"""
    platform_name: str
    max_prompt_length: int
    supports_camera_motion: bool
    supports_voice_over: bool
    prompt_format: str  # 'natural', 'structured', 'json'
    special_requirements: Dict[str, Any]


class BasePlatformExporter(ABC):
    """Base class for platform-specific exporters"""
    
    def __init__(self, config: VideoGeneratorConfig):
        self.config = config
        
    @abstractmethod
    def format_prompt(self, shot_data: Dict) -> str:
        """Format prompt for specific platform"""
        pass
    
    @abstractmethod
    def export_shot(self, shot_data: Dict, output_path: Path) -> Path:
        """Export shot in platform-specific format"""
        pass


class Veo3Exporter(BasePlatformExporter):
    """Google Veo3 exporter (existing functionality)"""
    
    def __init__(self):
        config = VideoGeneratorConfig(
            platform_name="Google Veo3",
            max_prompt_length=500,
            supports_camera_motion=True,
            supports_voice_over=True,
            prompt_format="natural",
            special_requirements={"style": "cinematic", "duration": "3-5 seconds"}
        )
        super().__init__(config)
    
    def format_prompt(self, shot_data: Dict) -> str:
        """Format for Veo3 natural language style"""
        prompt_parts = []
        
        # Subject
        if shot_data.get('subject'):
            prompt_parts.append(f"Subject: {shot_data['subject']}")
        
        # Context
        if shot_data.get('context'):
            prompt_parts.append(f"Context: {shot_data['context']}")
        
        # Action
        if shot_data.get('action'):
            prompt_parts.append(f"Action: {shot_data['action']}")
        
        # Camera motion
        if shot_data.get('camera_motion'):
            prompt_parts.append(f"Camera Motion: {shot_data['camera_motion']}")
        
        # Style
        prompt_parts.append("Style: Cinematic, naturalistic cinematography")
        
        return "\n".join(prompt_parts)
    
    def export_shot(self, shot_data: Dict, output_path: Path) -> Path:
        """Export in Veo3 format"""
        prompt = self.format_prompt(shot_data)
        
        file_path = output_path / f"{shot_data.get('shot_id', 'shot')}_veo3.txt"
        with open(file_path, 'w') as f:
            f.write(prompt)
        
        return file_path


class RunwayMLExporter(BasePlatformExporter):
    """Runway ML Gen-2 exporter"""
    
    def __init__(self):
        config = VideoGeneratorConfig(
            platform_name="Runway ML Gen-2",
            max_prompt_length=320,
            supports_camera_motion=True,
            supports_voice_over=False,
            prompt_format="structured",
            special_requirements={"aspect_ratio": "16:9", "duration": "4 seconds"}
        )
        super().__init__(config)
    
    def format_prompt(self, shot_data: Dict) -> str:
        """Format for Runway ML structured style"""
        # Runway prefers concise, structured prompts
        elements = []
        
        # Main subject/action
        if shot_data.get('subject'):
            elements.append(shot_data['subject'])
        
        if shot_data.get('action'):
            elements.append(shot_data['action'])
        
        # Visual style
        elements.append("cinematic lighting")
        
        # Camera motion (Runway specific terms)
        camera_map = {
            "crane": "aerial view rising",
            "tracking": "smooth tracking shot",
            "static": "locked off shot",
            "handheld": "handheld camera movement"
        }
        
        if shot_data.get('camera_type'):
            camera = camera_map.get(shot_data['camera_type'], "steady cam")
            elements.append(camera)
        
        # Limit to max length
        prompt = ", ".join(elements)
        if len(prompt) > self.config.max_prompt_length:
            prompt = prompt[:self.config.max_prompt_length-3] + "..."
        
        return prompt
    
    def export_shot(self, shot_data: Dict, output_path: Path) -> Path:
        """Export in Runway ML format"""
        prompt = self.format_prompt(shot_data)
        
        export_data = {
            "prompt": prompt,
            "settings": {
                "duration": 4,
                "aspect_ratio": "16:9",
                "motion_amount": shot_data.get('motion_amount', 'auto')
            }
        }
        
        file_path = output_path / f"{shot_data.get('shot_id', 'shot')}_runway.json"
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return file_path


class PikaLabsExporter(BasePlatformExporter):
    """Pika Labs exporter"""
    
    def __init__(self):
        config = VideoGeneratorConfig(
            platform_name="Pika Labs",
            max_prompt_length=200,
            supports_camera_motion=True,
            supports_voice_over=False,
            prompt_format="natural",
            special_requirements={"duration": "3 seconds", "fps": 24}
        )
        super().__init__(config)
    
    def format_prompt(self, shot_data: Dict) -> str:
        """Format for Pika Labs concise style"""
        # Pika prefers very concise prompts
        elements = []
        
        # Core description
        if shot_data.get('subject'):
            elements.append(shot_data['subject'])
        
        # Simple camera motion
        camera_motions = {
            "crane": "camera zoom out",
            "tracking": "camera pan right",
            "zoom": "camera zoom in",
            "static": ""
        }
        
        if shot_data.get('camera_type'):
            motion = camera_motions.get(shot_data['camera_type'], "")
            if motion:
                elements.append(f"-camera {motion}")
        
        # Motion amount
        if shot_data.get('motion_amount'):
            elements.append(f"-motion {shot_data.get('motion_amount', '2')}")
        
        # Style modifier
        elements.append("-gs 16")  # Guidance scale
        
        return " ".join(elements)
    
    def export_shot(self, shot_data: Dict, output_path: Path) -> Path:
        """Export in Pika Labs format"""
        prompt = self.format_prompt(shot_data)
        
        file_path = output_path / f"{shot_data.get('shot_id', 'shot')}_pika.txt"
        with open(file_path, 'w') as f:
            f.write(f"/create {prompt}")
        
        return file_path


class StabilityAIExporter(BasePlatformExporter):
    """Stability AI Video exporter"""
    
    def __init__(self):
        config = VideoGeneratorConfig(
            platform_name="Stability AI Video",
            max_prompt_length=400,
            supports_camera_motion=False,
            supports_voice_over=False,
            prompt_format="structured",
            special_requirements={"style_strength": 0.8, "motion_bucket": 127}
        )
        super().__init__(config)
    
    def format_prompt(self, shot_data: Dict) -> str:
        """Format for Stability AI structured style"""
        prompt_dict = {
            "description": "",
            "style": "cinematic, professional color grading",
            "lighting": "natural lighting",
            "quality": "high detail, 4k"
        }
        
        # Build description
        desc_parts = []
        if shot_data.get('subject'):
            desc_parts.append(shot_data['subject'])
        if shot_data.get('location'):
            desc_parts.append(f"in {shot_data['location']}")
        if shot_data.get('action'):
            desc_parts.append(shot_data['action'])
        
        prompt_dict["description"] = ", ".join(desc_parts)
        
        # Add mood/atmosphere
        if shot_data.get('mood'):
            prompt_dict["atmosphere"] = shot_data['mood']
        
        return json.dumps(prompt_dict, indent=2)
    
    def export_shot(self, shot_data: Dict, output_path: Path) -> Path:
        """Export in Stability AI format"""
        prompt = self.format_prompt(shot_data)
        
        export_data = {
            "prompt": json.loads(prompt),
            "parameters": {
                "motion_bucket_id": 127,
                "fps": 24,
                "style_strength": 0.8
            }
        }
        
        file_path = output_path / f"{shot_data.get('shot_id', 'shot')}_stability.json"
        with open(file_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        return file_path


class HaiperAIExporter(BasePlatformExporter):
    """Haiper AI exporter"""
    
    def __init__(self):
        config = VideoGeneratorConfig(
            platform_name="Haiper AI",
            max_prompt_length=300,
            supports_camera_motion=True,
            supports_voice_over=False,
            prompt_format="natural",
            special_requirements={"duration": "2-4 seconds"}
        )
        super().__init__(config)
    
    def format_prompt(self, shot_data: Dict) -> str:
        """Format for Haiper AI natural style"""
        elements = []
        
        # Scene description
        if shot_data.get('subject'):
            elements.append(shot_data['subject'])
        
        if shot_data.get('location'):
            elements.append(f"Location: {shot_data['location']}")
        
        if shot_data.get('action'):
            elements.append(f"Action: {shot_data['action']}")
        
        # Visual style
        elements.append("Style: Cinematic, high quality")
        
        # Camera work
        if shot_data.get('camera_motion'):
            elements.append(f"Camera: {shot_data['camera_motion']}")
        
        return " | ".join(elements)
    
    def export_shot(self, shot_data: Dict, output_path: Path) -> Path:
        """Export in Haiper AI format"""
        prompt = self.format_prompt(shot_data)
        
        file_path = output_path / f"{shot_data.get('shot_id', 'shot')}_haiper.txt"
        with open(file_path, 'w') as f:
            f.write(prompt)
        
        return file_path


class MultiPlatformExporter:
    """Main exporter that handles multiple platforms"""
    
    AVAILABLE_PLATFORMS = {
        'veo3': Veo3Exporter,
        'runway': RunwayMLExporter,
        'pika': PikaLabsExporter,
        'stability': StabilityAIExporter,
        'haiper': HaiperAIExporter
    }
    
    def __init__(self, output_dir: Path, platforms: List[str] = None):
        self.output_dir = output_dir
        
        # Initialize requested platforms
        if platforms is None:
            platforms = ['veo3']  # Default to Veo3
        
        self.exporters = {}
        for platform in platforms:
            if platform.lower() in self.AVAILABLE_PLATFORMS:
                exporter_class = self.AVAILABLE_PLATFORMS[platform.lower()]
                self.exporters[platform] = exporter_class()
                
                # Create platform-specific output directory
                platform_dir = output_dir / f"{platform.upper()}_Exports"
                platform_dir.mkdir(exist_ok=True)
    
    def export_shot(self, shot_data: Dict) -> Dict[str, Path]:
        """Export shot to all configured platforms"""
        exported_files = {}
        
        for platform_name, exporter in self.exporters.items():
            platform_dir = self.output_dir / f"{platform_name.upper()}_Exports"
            
            try:
                file_path = exporter.export_shot(shot_data, platform_dir)
                exported_files[platform_name] = file_path
            except Exception as e:
                print(f"Error exporting to {platform_name}: {e}")
        
        return exported_files
    
    def export_all_shots(self, shots: List[Dict]) -> Dict[str, List[Path]]:
        """Export all shots to all platforms"""
        all_exports = {platform: [] for platform in self.exporters.keys()}
        
        for shot in shots:
            exports = self.export_shot(shot)
            for platform, path in exports.items():
                all_exports[platform].append(path)
        
        # Generate platform comparison report
        self._generate_comparison_report(all_exports)
        
        return all_exports
    
    def _generate_comparison_report(self, exports: Dict[str, List[Path]]):
        """Generate a report comparing outputs across platforms"""
        report_file = self.output_dir / "PLATFORM_COMPARISON.txt"
        
        with open(report_file, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("MULTI-PLATFORM EXPORT COMPARISON\n")
            f.write("=" * 60 + "\n\n")
            
            for platform, files in exports.items():
                exporter = self.exporters[platform]
                config = exporter.config
                
                f.write(f"\n{config.platform_name}:\n")
                f.write("-" * 40 + "\n")
                f.write(f"  Files Generated: {len(files)}\n")
                f.write(f"  Format: {config.prompt_format}\n")
                f.write(f"  Max Prompt Length: {config.max_prompt_length}\n")
                f.write(f"  Camera Motion: {'Yes' if config.supports_camera_motion else 'No'}\n")
                f.write(f"  Voice Over: {'Yes' if config.supports_voice_over else 'No'}\n")
                
                if config.special_requirements:
                    f.write("  Special Requirements:\n")
                    for key, value in config.special_requirements.items():
                        f.write(f"    - {key}: {value}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("Export Summary:\n")
            f.write(f"  Total Platforms: {len(exports)}\n")
            f.write(f"  Total Files: {sum(len(files) for files in exports.values())}\n")
            f.write("=" * 60 + "\n")
    
    @staticmethod
    def get_platform_info() -> Dict[str, Dict]:
        """Get information about all available platforms"""
        info = {}
        
        for name, exporter_class in MultiPlatformExporter.AVAILABLE_PLATFORMS.items():
            exporter = exporter_class()
            info[name] = {
                "name": exporter.config.platform_name,
                "max_prompt_length": exporter.config.max_prompt_length,
                "supports_camera_motion": exporter.config.supports_camera_motion,
                "supports_voice_over": exporter.config.supports_voice_over,
                "format": exporter.config.prompt_format
            }
        
        return info


def integrate_with_pipeline(output_dir: Path,
                           shots: List[Dict],
                           platforms: List[str] = None) -> MultiPlatformExporter:
    """Integrate multi-platform export with main pipeline"""
    
    if platforms is None:
        platforms = ['veo3', 'runway', 'pika']  # Default platforms
    
    exporter = MultiPlatformExporter(output_dir, platforms)
    exports = exporter.export_all_shots(shots)
    
    print(f"\n✓ Exported to {len(platforms)} platforms:")
    for platform, files in exports.items():
        print(f"  • {platform.upper()}: {len(files)} files")
    
    return exporter


if __name__ == "__main__":
    # Test the multi-platform exporter
    test_output = Path("output/test_multiplatform")
    test_output.mkdir(parents=True, exist_ok=True)
    
    # Sample shot data
    test_shot = {
        'shot_id': 'scene1_shot001',
        'subject': 'A woman walking through a bustling city street',
        'location': 'New York City',
        'action': 'walks purposefully while checking her phone',
        'camera_motion': 'Tracking shot following the subject',
        'camera_type': 'tracking',
        'mood': 'urban energy',
        'motion_amount': '3'
    }
    
    # Test export to all platforms
    exporter = MultiPlatformExporter(test_output, ['veo3', 'runway', 'pika', 'stability', 'haiper'])
    exports = exporter.export_shot(test_shot)
    
    print("Multi-platform export completed!")
    print("Exported files:")
    for platform, path in exports.items():
        print(f"  {platform}: {path}")
    
    # Show platform info
    print("\nAvailable Platforms:")
    for name, info in MultiPlatformExporter.get_platform_info().items():
        print(f"  {name}: {info['name']} (max {info['max_prompt_length']} chars)")