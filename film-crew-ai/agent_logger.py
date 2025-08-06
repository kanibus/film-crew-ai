#!/usr/bin/env python3
"""
Agent Execution Logger
Tracks and logs each AI agent's contribution to the film production process
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field

@dataclass
class AgentLog:
    """Represents a single agent's execution log"""
    agent_name: str
    agent_role: str
    timestamp: str
    scene_number: str
    shot_number: str
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    execution_time: float
    status: str = "success"
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class AgentExecutionLogger:
    """Logs and tracks AI agent execution throughout the pipeline"""
    
    # Define the 8 specialized agents
    AGENTS = {
        "script_breakdown": {
            "name": "Script Breakdown Agent",
            "role": "Analyzes script structure, identifies scenes, shots, and dramatic beats"
        },
        "character_analysis": {
            "name": "Character Analysis Agent", 
            "role": "Tracks character profiles, emotional arcs, and relationships"
        },
        "environment_props": {
            "name": "Environment & Props Agent",
            "role": "Identifies locations, set pieces, and required props"
        },
        "camera_director": {
            "name": "Camera Director Agent",
            "role": "Determines camera angles, movements, and shot compositions"
        },
        "lighting_designer": {
            "name": "Lighting Designer Agent",
            "role": "Plans lighting setups, mood, and visual atmosphere"
        },
        "sound_designer": {
            "name": "Sound Designer Agent",
            "role": "Designs soundscapes, effects, and ambient audio"
        },
        "music_director": {
            "name": "Music Director Agent",
            "role": "Selects musical themes, timing, and emotional scoring"
        },
        "prompt_synthesis": {
            "name": "Prompt Synthesis Agent",
            "role": "Combines all agent outputs into unified Veo3 prompts"
        }
    }
    
    def __init__(self, output_dir: Path):
        self.output_dir = output_dir
        self.logs_dir = output_dir / "Agent_Logs"
        self.logs_dir.mkdir(exist_ok=True)
        self.execution_logs: List[AgentLog] = []
        self.logger = logging.getLogger('AgentLogger')
        
    def log_agent_execution(self,
                           agent_key: str,
                           scene_number: str,
                           shot_number: str,
                           input_data: Dict,
                           output_data: Dict,
                           execution_time: float,
                           status: str = "success",
                           errors: List[str] = None) -> None:
        """Log a single agent's execution"""
        
        if agent_key not in self.AGENTS:
            self.logger.warning(f"Unknown agent key: {agent_key}")
            return
            
        agent_info = self.AGENTS[agent_key]
        
        log_entry = AgentLog(
            agent_name=agent_info["name"],
            agent_role=agent_info["role"],
            timestamp=datetime.now().isoformat(),
            scene_number=scene_number,
            shot_number=shot_number,
            input_data=input_data,
            output_data=output_data,
            execution_time=execution_time,
            status=status,
            errors=errors or []
        )
        
        self.execution_logs.append(log_entry)
        
        # Save individual agent log
        self._save_agent_log(agent_key, scene_number, shot_number, log_entry)
        
        # Log to console
        self.logger.info(f"✓ {agent_info['name']} - Scene {scene_number}, Shot {shot_number} ({execution_time:.2f}s)")
        
    def _save_agent_log(self, agent_key: str, scene_number: str, shot_number: str, log_entry: AgentLog):
        """Save individual agent log to file"""
        
        # Create agent-specific directory
        agent_dir = self.logs_dir / agent_key
        agent_dir.mkdir(exist_ok=True)
        
        # Save log file
        filename = f"scene{scene_number}_shot{shot_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        log_file = agent_dir / filename
        
        with open(log_file, 'w') as f:
            json.dump(log_entry.to_dict(), f, indent=2, default=str)
            
    def generate_execution_report(self) -> Dict:
        """Generate comprehensive execution report"""
        
        report = {
            "timestamp": datetime.now().isoformat(),
            "total_executions": len(self.execution_logs),
            "agents_summary": {},
            "scene_coverage": {},
            "performance_metrics": {},
            "errors": []
        }
        
        # Summarize by agent
        for agent_key, agent_info in self.AGENTS.items():
            agent_logs = [log for log in self.execution_logs if log.agent_name == agent_info["name"]]
            
            if agent_logs:
                report["agents_summary"][agent_key] = {
                    "name": agent_info["name"],
                    "role": agent_info["role"],
                    "executions": len(agent_logs),
                    "avg_execution_time": sum(log.execution_time for log in agent_logs) / len(agent_logs),
                    "success_rate": sum(1 for log in agent_logs if log.status == "success") / len(agent_logs) * 100
                }
        
        # Summarize by scene
        scenes = set(log.scene_number for log in self.execution_logs)
        for scene in sorted(scenes):
            scene_logs = [log for log in self.execution_logs if log.scene_number == scene]
            report["scene_coverage"][f"scene_{scene}"] = {
                "total_agent_executions": len(scene_logs),
                "agents_involved": list(set(log.agent_name for log in scene_logs)),
                "total_execution_time": sum(log.execution_time for log in scene_logs)
            }
        
        # Performance metrics
        if self.execution_logs:
            report["performance_metrics"] = {
                "total_execution_time": sum(log.execution_time for log in self.execution_logs),
                "average_execution_time": sum(log.execution_time for log in self.execution_logs) / len(self.execution_logs),
                "fastest_agent": min(self.execution_logs, key=lambda x: x.execution_time).agent_name,
                "slowest_agent": max(self.execution_logs, key=lambda x: x.execution_time).agent_name
            }
        
        # Collect errors
        report["errors"] = [
            {
                "agent": log.agent_name,
                "scene": log.scene_number,
                "shot": log.shot_number,
                "errors": log.errors
            }
            for log in self.execution_logs if log.errors
        ]
        
        # Save report
        report_file = self.logs_dir / f"execution_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
            
        return report
    
    def simulate_agent_execution(self, scene_number: str, shot_number: str) -> None:
        """Simulate execution of all 8 agents for a shot (for demonstration)"""
        import time
        import random
        
        for agent_key in self.AGENTS.keys():
            # Simulate processing time
            execution_time = random.uniform(0.1, 2.0)
            
            # Simulate input/output data
            input_data = {
                "scene_content": f"Scene {scene_number} content",
                "shot_description": f"Shot {shot_number} description"
            }
            
            output_data = {
                "analysis": f"{self.AGENTS[agent_key]['name']} analysis for scene {scene_number}, shot {shot_number}",
                "recommendations": [f"Recommendation {i+1}" for i in range(random.randint(1, 3))]
            }
            
            # Log the execution
            self.log_agent_execution(
                agent_key=agent_key,
                scene_number=scene_number,
                shot_number=shot_number,
                input_data=input_data,
                output_data=output_data,
                execution_time=execution_time
            )
            
            time.sleep(0.1)  # Small delay for realism


def integrate_with_pipeline(output_dir: Path, scenes: List, shots: List) -> AgentExecutionLogger:
    """Integrate agent logging with the main pipeline"""
    
    logger = AgentExecutionLogger(output_dir)
    
    # This would be called during actual processing
    # For now, we'll demonstrate with simulation
    for scene in scenes[:2]:  # Demo with first 2 scenes
        for shot in shots[:2]:  # Demo with first 2 shots per scene
            logger.simulate_agent_execution(
                scene_number=str(scene.get('scene_number', '1')),
                shot_number=str(shot.get('shot_number', '001'))
            )
    
    # Generate final report
    report = logger.generate_execution_report()
    
    print("\n" + "="*60)
    print("AGENT EXECUTION SUMMARY")
    print("="*60)
    for agent_key, summary in report["agents_summary"].items():
        print(f"✓ {summary['name']}: {summary['executions']} executions, {summary['avg_execution_time']:.2f}s avg")
    print("="*60)
    
    return logger


if __name__ == "__main__":
    # Test the logger
    test_output = Path("output/test_agent_logs")
    test_output.mkdir(parents=True, exist_ok=True)
    
    logger = AgentExecutionLogger(test_output)
    
    # Simulate some executions
    logger.simulate_agent_execution("1", "001")
    logger.simulate_agent_execution("1", "002")
    logger.simulate_agent_execution("2", "001")
    
    # Generate report
    report = logger.generate_execution_report()
    
    print("\nAgent Execution Report Generated!")
    print(f"Total Executions: {report['total_executions']}")
    print(f"Agents Involved: {len(report['agents_summary'])}")
    print(f"Scenes Processed: {len(report['scene_coverage'])}")