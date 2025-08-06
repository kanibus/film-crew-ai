# Changelog

All notable changes to Film Crew AI will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [8.0.0] - 2025-01-06

### Added
- **8 Specialized AI Agents** working in coordination:
  - Script Breakdown Agent - Analyzes structure and dramatic beats
  - Character Analysis Agent - Tracks profiles and emotional arcs
  - Environment & Props Agent - Identifies locations and props
  - Camera Director Agent - Determines shots and compositions
  - Lighting Designer Agent - Plans mood and atmosphere
  - Sound Designer Agent - Creates soundscapes
  - Music Director Agent - Selects themes and scoring
  - Prompt Synthesis Agent - Combines all outputs
- **Multi-Platform Export Support**:
  - Google Veo3 (natural language)
  - Runway ML Gen-2 (structured)
  - Pika Labs (concise commands)
  - Stability AI Video (JSON format)
  - Haiper AI (natural style)
- **Scene Summary Generator**:
  - Individual scene summaries with key elements
  - Master script overview
  - Human-readable reports
- **Agent Execution Logger**:
  - Tracks all agent contributions
  - Performance metrics
  - Scene coverage analysis
- **Enhanced Document Reader**:
  - PDF support via PyPDF2
  - DOC/DOCX support via python-docx
  - Automatic encoding detection
- **Batch Processing**:
  - Process multiple scripts at once
  - Detailed batch reports
  - Progress tracking

### Changed
- Complete rewrite of core processing engine
- Improved scene/shot detection algorithms
- Enhanced voice-over extraction
- Better character consistency tracking
- Natural language prompt generation
- Organized output structure by scenes

### Fixed
- Scene separation now works correctly
- Voice-over detection improved
- Character tracking across scenes
- File naming includes script names
- Agent coordination issues resolved
- Support for multiple script formats

## [7.0.0] - 2025-01-05

### Added
- Advanced screenplay parser
- Character consistency tracking
- Voice-over integration in prompts

### Changed
- Improved prompt generation
- Better scene organization

## [6.0.0] - 2025-01-04

### Added
- Initial vignette format support
- Basic Veo3 prompt generation
- Simple script processing

## [5.0.0] - 2025-01-03

### Added
- Claude Flow integration attempts
- Swarm mode exploration

### Known Issues
- Claude Flow swarm mode not functional
- Limited screenplay format support

## [4.0.0] - 2025-01-02

### Added
- Basic screenplay parsing
- Initial project structure

## [3.0.0] - 2025-01-01

### Added
- Project inception
- Initial concept development

---

## Future Roadmap

### Version 9.0 (Planned)
- [ ] Web interface for easier access
- [ ] API endpoints for integration
- [ ] Real-time preview of generated prompts
- [ ] Custom agent configurations
- [ ] Advanced character emotion tracking

### Version 10.0 (Planned)
- [ ] AI-powered script analysis
- [ ] Automatic scene optimization
- [ ] Multi-language support
- [ ] Cloud processing options
- [ ] Collaborative features