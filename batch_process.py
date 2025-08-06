#!/usr/bin/env python3
"""
Batch Process Scripts
Process all screenplay files in the scripts folder
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Import the main pipeline
try:
    from film_crew_ai_main import FilmCrewAIPipeline
except ImportError:
    print("Error: Cannot import FilmCrewAIPipeline")
    print("Please ensure film_crew_ai_main.py is in the same directory")
    sys.exit(1)

def batch_process_scripts():
    """Process all scripts in the scripts folder"""
    
    # Setup paths
    scripts_dir = Path("scripts")
    output_dir = Path("output")
    
    # Check if scripts directory exists
    if not scripts_dir.exists():
        print(f"Error: Scripts directory '{scripts_dir}' not found")
        print("Please create a 'scripts' folder and add your screenplay files")
        return
    
    # Find all supported script files
    supported_extensions = ['.txt', '.pdf', '.doc', '.docx']
    script_files = []
    
    for ext in supported_extensions:
        script_files.extend(scripts_dir.glob(f"*{ext}"))
    
    if not script_files:
        print(f"No script files found in '{scripts_dir}'")
        print(f"Supported formats: {', '.join(supported_extensions)}")
        return
    
    # Display found scripts
    print("=" * 60)
    print("FILM CREW AI - BATCH PROCESSOR")
    print("=" * 60)
    print(f"\nFound {len(script_files)} script(s) to process:")
    for i, script in enumerate(script_files, 1):
        print(f"  {i}. {script.name}")
    
    print("\n" + "-" * 60)
    
    # Process each script
    pipeline = FilmCrewAIPipeline(verbose=False)
    successful = 0
    failed = 0
    
    for i, script_path in enumerate(script_files, 1):
        print(f"\n[{i}/{len(script_files)}] Processing: {script_path.name}")
        print("-" * 40)
        
        try:
            # Process the script
            result = pipeline.process_script(
                script_path=str(script_path),
                output_dir=str(output_dir),
                generate_enhanced=True,
                generate_natural=True
            )
            
            if result:
                print(f"✓ Success: Output saved to {result}")
                successful += 1
            else:
                print(f"✗ Failed: No output generated")
                failed += 1
                
        except Exception as e:
            print(f"✗ Error: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print("BATCH PROCESSING COMPLETE")
    print("=" * 60)
    print(f"Total Scripts: {len(script_files)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(successful/len(script_files)*100):.1f}%")
    print("=" * 60)
    
    # Create batch report
    report_path = output_dir / f"batch_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_path, 'w') as f:
        f.write("Film Crew AI - Batch Processing Report\n")
        f.write("=" * 60 + "\n")
        f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Total Scripts: {len(script_files)}\n")
        f.write(f"Successful: {successful}\n")
        f.write(f"Failed: {failed}\n")
        f.write("\nProcessed Files:\n")
        for script in script_files:
            f.write(f"  - {script.name}\n")
    
    print(f"\nBatch report saved to: {report_path}")


def main():
    """Main entry point"""
    print("\nFilm Crew AI - Batch Processor")
    print("This will process all scripts in the 'scripts' folder")
    
    # Confirm with user
    response = input("\nDo you want to continue? (y/n): ")
    if response.lower() != 'y':
        print("Batch processing cancelled")
        return
    
    # Run batch processing
    batch_process_scripts()


if __name__ == "__main__":
    main()