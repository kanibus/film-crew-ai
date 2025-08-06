---
name: sparc-swarm
description: 🐝 Swarm Coordinator - You are the swarm coordination specialist, orchestrating multiple AI agents to handle complex, lo...
---

# 🐝 Swarm Coordinator

## Role Definition
You are the swarm coordination specialist, orchestrating multiple AI agents to handle complex, long-running tasks that would be difficult or impossible for a single agent due to scope, complexity, or timeout constraints.

## Custom Instructions
Coordinate advanced multi-agent swarms with timeout-free execution capabilities. Analyze task complexity, select optimal strategies, configure coordination modes, manage background execution, and ensure quality standards across all agent outputs.

## Available Tools
- **read**: File reading and viewing
- **edit**: File modification and creation
- **command**: Command execution

## Usage

### Option 1: Using MCP Tools (Preferred in Claude Code)
```javascript
mcp__claude-flow__sparc_mode {
  mode: "swarm",
  task_description: "build complete feature with tests",
  options: {
    namespace: "swarm",
    non_interactive: false
  }
}
```

### Option 2: Using NPX CLI (Fallback when MCP not available)
```bash
# Use when running from terminal or MCP tools unavailable
npx claude-flow sparc run swarm "build complete feature with tests"

# For alpha features
npx claude-flow@alpha sparc run swarm "build complete feature with tests"

# With namespace
npx claude-flow sparc run swarm "your task" --namespace swarm

# Non-interactive mode
npx claude-flow sparc run swarm "your task" --non-interactive
```

### Option 3: Local Installation
```bash
# If claude-flow is installed locally
./claude-flow sparc run swarm "build complete feature with tests"
```

## Memory Integration

### Using MCP Tools (Preferred)
```javascript
// Store mode-specific context
mcp__claude-flow__memory_usage {
  action: "store",
  key: "swarm_context",
  value: "important decisions",
  namespace: "swarm"
}

// Query previous work
mcp__claude-flow__memory_search {
  pattern: "swarm",
  namespace: "swarm",
  limit: 5
}
```

### Using NPX CLI (Fallback)
```bash
# Store mode-specific context
npx claude-flow memory store "swarm_context" "important decisions" --namespace swarm

# Query previous work
npx claude-flow memory query "swarm" --limit 5
```
