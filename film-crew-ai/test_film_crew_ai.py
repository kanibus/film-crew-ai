#!/usr/bin/env python3
"""
Unit Tests for Film Crew AI
Tests core functionality of the screenplay processing system
"""

import unittest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
from film_crew_ai_main import FilmCrewAIPipeline
from film_crew_ai_advanced import AdvancedScriptParser, EnhancedScene, VideoShot, VoiceOver
from enhanced_document_reader import EnhancedDocumentReader


class TestFilmCrewAIPipeline(unittest.TestCase):
    """Test main pipeline functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = FilmCrewAIPipeline(verbose=False)
        self.test_script = """FADE IN:

EXT. CITY STREET - DAY

A busy street. SARAH (30s) walks purposefully.

SARAH (V.O.)
Every morning starts the same way.

INT. COFFEE SHOP - DAY

Sarah enters, scanning the room.

SARAH
Is James here?

FADE OUT."""
    
    def test_validate_input_valid_file(self):
        """Test validation with valid file"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(self.test_script.encode())
            temp_path = Path(f.name)
        
        try:
            result = self.pipeline.validate_input(temp_path)
            self.assertTrue(result)
        finally:
            temp_path.unlink()
    
    def test_validate_input_missing_file(self):
        """Test validation with missing file"""
        missing_path = Path("nonexistent_script.txt")
        result = self.pipeline.validate_input(missing_path)
        self.assertFalse(result)
    
    def test_validate_input_unsupported_format(self):
        """Test validation with unsupported format"""
        with tempfile.NamedTemporaryFile(suffix='.xyz', delete=False) as f:
            temp_path = Path(f.name)
        
        try:
            result = self.pipeline.validate_input(temp_path)
            self.assertFalse(result)
        finally:
            temp_path.unlink()
    
    def test_detect_script_format_traditional(self):
        """Test format detection for traditional screenplay"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(self.test_script.encode())
            temp_path = Path(f.name)
        
        try:
            format_type = self.pipeline.detect_script_format(temp_path)
            self.assertEqual(format_type, 'traditional')
        finally:
            temp_path.unlink()
    
    def test_detect_script_format_vignette(self):
        """Test format detection for vignette format"""
        vignette_script = """Video: Wide shot of office
VO: The future of healthcare is here"""
        
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(vignette_script.encode())
            temp_path = Path(f.name)
        
        try:
            format_type = self.pipeline.detect_script_format(temp_path)
            self.assertEqual(format_type, 'vignette')
        finally:
            temp_path.unlink()
    
    def test_create_output_directory(self):
        """Test output directory creation"""
        with tempfile.NamedTemporaryFile(suffix='.txt') as f:
            script_path = Path(f.name)
            
            # Test with auto-generated directory
            output_path = self.pipeline.create_output_directory(script_path)
            self.assertTrue(output_path.exists())
            self.assertTrue(output_path.is_dir())
            
            # Clean up
            output_path.rmdir()
            
            # Test with custom directory
            custom_dir = "test_output"
            output_path = self.pipeline.create_output_directory(script_path, custom_dir)
            self.assertEqual(output_path, Path(custom_dir))
            self.assertTrue(output_path.exists())
            
            # Clean up
            output_path.rmdir()


class TestAdvancedScriptParser(unittest.TestCase):
    """Test advanced script parser functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.parser = AdvancedScriptParser()
        self.test_script = """FADE IN:

INT. OFFICE - DAY

JOHN (40s) sits at his desk.

JOHN
This is a test.

JOHN (V.O.)
Testing voice over.

CUT TO:

EXT. STREET - NIGHT

FADE OUT."""
    
    def test_parse_scenes(self):
        """Test scene parsing"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(self.test_script.encode())
            temp_path = Path(f.name)
        
        try:
            result = self.parser.parse(temp_path)
            # parse returns a tuple: (scenes, shots, voice_overs)
            scenes = result[0] if isinstance(result, tuple) else result
            self.assertEqual(len(scenes), 2)
            self.assertEqual(scenes[0].heading, "INT. OFFICE - DAY")
            self.assertEqual(scenes[1].heading, "EXT. STREET - NIGHT")
        finally:
            temp_path.unlink()
    
    def test_extract_voice_overs(self):
        """Test voice-over extraction"""
        text = """SARAH (V.O.)
This is a voice over.

SARAH (O.S.)
This is off-screen."""
        
        vos = self.parser._extract_voice_overs(text)
        self.assertEqual(len(vos), 2)
        self.assertEqual(vos[0].character, "SARAH")
        self.assertTrue("voice over" in vos[0].text)
    
    def test_extract_transitions(self):
        """Test transition extraction"""
        text = """FADE IN:

Some content.

CUT TO:

More content.

DISSOLVE TO:

Final content.

FADE OUT."""
        
        transitions = self.parser._extract_transitions(text)
        self.assertGreater(len(transitions), 0)
        transition_types = [t.transition_type for t in transitions]
        self.assertIn("FADE IN", transition_types)
        self.assertIn("CUT TO", transition_types)
        self.assertIn("FADE OUT", transition_types)


class TestEnhancedDocumentReader(unittest.TestCase):
    """Test document reader functionality"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.reader = EnhancedDocumentReader()
    
    def test_read_txt_file(self):
        """Test reading text file"""
        content = "Test content\nLine 2"
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(content.encode())
            temp_path = Path(f.name)
        
        try:
            result = self.reader.read_file(temp_path)
            self.assertEqual(result, content)
        finally:
            temp_path.unlink()
    
    def test_read_with_encoding(self):
        """Test reading file with different encoding"""
        # Test UTF-8
        content = "Test with unicode: © ™ €"
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(content.encode('utf-8'))
            temp_path = Path(f.name)
        
        try:
            result = self.reader.read_file(temp_path)
            self.assertIn("Test with unicode", result)
        finally:
            temp_path.unlink()


class TestDataClasses(unittest.TestCase):
    """Test data class functionality"""
    
    def test_voice_over_creation(self):
        """Test VoiceOver dataclass"""
        vo = VoiceOver(
            character="SARAH",
            text="This is a test",
            scene_context="INT. OFFICE - DAY",
            timing="beginning"
        )
        
        self.assertEqual(vo.character, "SARAH")
        self.assertEqual(vo.text, "This is a test")
        self.assertEqual(vo.timing, "beginning")
    
    def test_video_shot_creation(self):
        """Test VideoShot dataclass"""
        shot = VideoShot(
            shot_id="1-001",
            scene_number="1",
            shot_number="001",
            shot_type="WIDE",
            description="Test shot",
            duration="3-5 seconds",
            camera_movement="static",
            characters_in_frame=[],
            dialogue=[],
            voice_overs=[]
        )
        
        self.assertEqual(shot.shot_id, "1-001")
        self.assertEqual(shot.shot_type, "WIDE")
        self.assertEqual(shot.scene_number, "1")
        
        # Test conversion to dict
        shot_dict = shot.to_dict()
        self.assertIsInstance(shot_dict, dict)
        self.assertEqual(shot_dict['shot_id'], "1-001")
    
    def test_enhanced_scene_creation(self):
        """Test EnhancedScene dataclass"""
        scene = EnhancedScene(
            scene_number="1",
            heading="INT. OFFICE - DAY",
            location="OFFICE",
            time_of_day="DAY",
            scene_type="PRESENT",
            description="Scene in office",
            action_blocks=[],
            dialogue_blocks=[],
            voice_overs=[],
            shots=[]
        )
        
        self.assertEqual(scene.scene_number, "1")
        self.assertEqual(scene.heading, "INT. OFFICE - DAY")
        self.assertEqual(len(scene.shots), 0)  # Default empty list
        self.assertEqual(len(scene.voice_overs), 0)  # Default empty list


class TestIntegration(unittest.TestCase):
    """Integration tests for the full pipeline"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.pipeline = FilmCrewAIPipeline(verbose=False)
        self.test_script_content = """FADE IN:

EXT. FARMHOUSE - DAY

A rustic farmhouse. MICHAEL (62) works in the field.

MICHAEL (V.O.)
Life on the farm ain't easy.

INT. FARMHOUSE - KITCHEN - DAY

Michael enters, tired.

FADE OUT."""
    
    @patch('film_crew_ai_main.AdvancedFilmCrewProcessor')
    @patch('film_crew_ai_main.EnhancedVeo3Processor')
    def test_full_pipeline_traditional(self, mock_veo3, mock_processor):
        """Test full pipeline with traditional screenplay"""
        # Create temporary script file
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
            f.write(self.test_script_content.encode())
            temp_path = Path(f.name)
        
        try:
            # Mock the processors
            mock_processor_instance = MagicMock()
            mock_processor_instance.process_script.return_value = Path("test_output")
            mock_processor.return_value = mock_processor_instance
            
            mock_veo3_instance = MagicMock()
            mock_veo3.return_value = mock_veo3_instance
            
            # Run pipeline
            result = self.pipeline.process_script(str(temp_path))
            
            # Verify calls
            self.assertIsNotNone(result)
            mock_processor_instance.process_script.assert_called_once()
            
        finally:
            temp_path.unlink()


def run_tests():
    """Run all tests with verbose output"""
    unittest.main(argv=[''], verbosity=2, exit=False)


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("FILM CREW AI - Unit Test Suite")
    print("=" * 60 + "\n")
    
    run_tests()
    
    print("\n" + "=" * 60)
    print("Test suite complete!")
    print("=" * 60)