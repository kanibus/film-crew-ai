#!/usr/bin/env python3
"""
Film Crew AI - Unified Main Entry Point
Complete system for transforming screenplays into Veo3 prompts
Version 8.0 - Production Ready with Fixes
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List

# Constants
MAX_SCENE_LENGTH = 1000
DEFAULT_SHOT_DURATION = "3-5 seconds"
SUPPORTED_FORMATS = ['.txt', '.pdf', '.doc', '.docx']
DEFAULT_OUTPUT_DIR = "output"

# Import processors with proper error handling
try:
    from film_crew_ai_advanced import AdvancedFilmCrewProcessor
    from film_crew_ai_vignette import VignetteFilmCrewProcessor
    from veo3_enhanced_prompt_generator import EnhancedVeo3Processor
    from veo3_natural_prompt_generator import Veo3PromptProcessor
    from enhanced_document_reader import EnhancedDocumentReader
    from agent_logger import AgentExecutionLogger
    from scene_summary_generator import SceneSummaryGenerator
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please ensure all required modules are in the same directory.")
    sys.exit(1)

# Setup logging
def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup logging configuration"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    return logging.getLogger('FilmCrewAI')

class FilmCrewAIPipeline:
    """Main pipeline for processing screenplays to Veo3 prompts"""
    
    def __init__(self, verbose: bool = False):
        self.logger = setup_logging(verbose)
        self.supported_formats = SUPPORTED_FORMATS
        self.reader = EnhancedDocumentReader()
        
    def validate_input(self, script_path: Path) -> bool:
        """Validate input file"""
        if not script_path.exists():
            self.logger.error(f"Script not found: {script_path}")
            return False
            
        if script_path.suffix.lower() not in self.supported_formats:
            self.logger.error(f"Unsupported format: {script_path.suffix}")
            self.logger.info(f"Supported formats: {', '.join(self.supported_formats)}")
            return False
            
        return True
    
    def detect_script_format(self, script_path: Path) -> str:
        """Detect if script is traditional or vignette format"""
        try:
            # Read first 1000 characters to detect format
            content = self.reader.read_file(script_path)[:1000].lower()
            
            # Check for vignette markers
            if 'video:' in content or 'vo:' in content:
                return 'vignette'
            elif 'vignette' in script_path.name.lower():
                return 'vignette'
            else:
                return 'traditional'
        except Exception as e:
            self.logger.warning(f"Error detecting format: {e}, defaulting to traditional")
            return 'traditional'
    
    def create_output_directory(self, script_path: Path, output_dir: Optional[str] = None) -> Path:
        """Create and return output directory path"""
        if output_dir:
            output_path = Path(output_dir)
        else:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            script_name = script_path.stem.replace(' ', '_')
            output_path = Path(DEFAULT_OUTPUT_DIR) / f"{script_name}_{timestamp}"
        
        output_path.mkdir(parents=True, exist_ok=True)
        return output_path
    
    def process_script(self, 
                      script_path: str, 
                      output_dir: Optional[str] = None,
                      generate_enhanced: bool = True,
                      generate_natural: bool = True) -> Optional[Path]:
        """
        Process a screenplay through the complete pipeline
        
        Args:
            script_path: Path to the screenplay file
            output_dir: Optional output directory path
            generate_enhanced: Generate enhanced Veo3 prompts
            generate_natural: Generate natural language prompts
            
        Returns:
            Path to output directory or None if failed
        """
        script_path = Path(script_path)
        
        # Validate input
        if not self.validate_input(script_path):
            return None
        
        # Detect format
        format_type = self.detect_script_format(script_path)
        self.logger.info(f"Detected script format: {format_type}")
        
        # Create output directory
        output_path = self.create_output_directory(script_path, output_dir)
        
        try:
            # Process based on format
            self.logger.info("=" * 60)
            self.logger.info("PHASE 1: Script Analysis and Processing")
            self.logger.info("=" * 60)
            
            # Initialize processor with project directory (current directory)
            project_dir = Path.cwd()
            
            if format_type == 'vignette':
                processor = VignetteFilmCrewProcessor(project_dir)
            else:
                processor = AdvancedFilmCrewProcessor(project_dir)
            
            # Process the script
            result_dir = processor.process_script(script_path)
            
            if not result_dir:
                self.logger.error("Script processing failed")
                return None
            
            # Generate enhanced Veo3 prompts
            if generate_enhanced:
                self.logger.info("=" * 60)
                self.logger.info("PHASE 2: Enhanced Veo3 Prompt Generation")
                self.logger.info("=" * 60)
                
                try:
                    enhanced_processor = EnhancedVeo3Processor(result_dir)
                    enhanced_processor.process_with_enhancement()
                    self.logger.info("Enhanced prompts generated successfully")
                except Exception as e:
                    self.logger.error(f"Failed to generate enhanced prompts: {e}")
            
            # Generate natural language prompts
            if generate_natural:
                self.logger.info("=" * 60)
                self.logger.info("PHASE 3: Natural Language Prompt Generation")
                self.logger.info("=" * 60)
                
                try:
                    natural_processor = Veo3PromptProcessor(result_dir)
                    natural_processor.process_all_shots()
                    self.logger.info("Natural language prompts generated successfully")
                except Exception as e:
                    self.logger.error(f"Failed to generate natural prompts: {e}")
            
            self.logger.info("=" * 60)
            self.logger.info("PROCESSING COMPLETE!")
            self.logger.info("=" * 60)
            self.logger.info(f"Output directory: {result_dir}")
            
            return result_dir
            
        except Exception as e:
            self.logger.error(f"Processing failed: {e}")
            import traceback
            self.logger.debug(traceback.format_exc())
            return None
    
    def batch_process(self, scripts_dir: str = "scripts") -> Dict[str, Path]:
        """
        Process all scripts in a directory
        
        Args:
            scripts_dir: Directory containing scripts
            
        Returns:
            Dictionary of script names to output paths
        """
        scripts_path = Path(scripts_dir)
        results = {}
        
        if not scripts_path.exists():
            self.logger.error(f"Scripts directory not found: {scripts_path}")
            return results
        
        # Find all script files
        script_files = []
        for ext in self.supported_formats:
            script_files.extend(scripts_path.glob(f"*{ext}"))
        
        if not script_files:
            self.logger.warning(f"No scripts found in {scripts_path}")
            return results
        
        self.logger.info(f"Found {len(script_files)} scripts to process")
        
        for script_path in script_files:
            self.logger.info(f"Processing: {script_path.name}")
            result = self.process_script(str(script_path))
            if result:
                results[script_path.name] = result
                self.logger.info(f"Success: {script_path.name}")
            else:
                self.logger.error(f"Failed: {script_path.name}")
        
        return results


def main():
    """Main entry point with enhanced argument parsing"""
    parser = argparse.ArgumentParser(
        description="Film Crew AI - Transform screenplays into Veo3 prompts",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Process a single screenplay:
    %(prog)s script.txt
    %(prog)s screenplay.docx --output custom_output
  
  Batch process all scripts:
    %(prog)s --batch
    %(prog)s --batch --scripts-dir my_scripts
  
  Process with specific outputs:
    %(prog)s script.txt --enhanced-only
    %(prog)s script.txt --natural-only
  
  Debug mode:
    %(prog)s script.txt --verbose
        """
    )
    
    # Positional argument (optional when using --batch)
    parser.add_argument(
        'script',
        nargs='?',
        help='Path to screenplay file (.txt, .pdf, .doc, .docx)'
    )
    
    # Optional arguments
    parser.add_argument(
        '--output', '-o',
        help='Output directory (default: auto-generated with timestamp)'
    )
    
    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help='Process all scripts in scripts directory'
    )
    
    parser.add_argument(
        '--scripts-dir', '-d',
        default='scripts',
        help='Directory containing scripts for batch processing (default: scripts)'
    )
    
    parser.add_argument(
        '--enhanced-only',
        action='store_true',
        help='Generate only enhanced Veo3 prompts'
    )
    
    parser.add_argument(
        '--natural-only',
        action='store_true',
        help='Generate only natural language prompts'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='Film Crew AI v8.0'
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.batch and not args.script:
        parser.error("Either provide a script file or use --batch mode")
    
    # Print banner
    print("\n" + "=" * 60)
    print("FILM CREW AI - Screenplay to Veo3 Processor")
    print("=" * 60 + "\n")
    
    # Create pipeline
    pipeline = FilmCrewAIPipeline(verbose=args.verbose)
    
    # Determine what to generate
    generate_enhanced = not args.natural_only
    generate_natural = not args.enhanced_only
    
    # Process based on mode
    if args.batch:
        # Batch processing mode
        results = pipeline.batch_process(args.scripts_dir)
        
        print("\n" + "=" * 60)
        print("BATCH PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Processed: {len(results)} scripts")
        for script, output_path in results.items():
            print(f"  - {script}: {output_path}")
    else:
        # Single script mode
        result = pipeline.process_script(
            args.script,
            args.output,
            generate_enhanced,
            generate_natural
        )
        
        if result:
            print(f"\nSuccess! Output saved to: {result}")
            sys.exit(0)
        else:
            print("\nProcessing failed. Check the error messages above.")
            sys.exit(1)


if __name__ == "__main__":
    main()