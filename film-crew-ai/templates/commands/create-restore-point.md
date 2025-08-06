---
description: Create version snapshot before changes
argument-hint: <version-name> <description>
---

# Create Restore Point

Saves complete project state including all shots, memory, and outputs.

Process:
1. Generate timestamp version ID
2. Export all memory and swarm state
3. Copy current outputs
4. Create version metadata
5. Log in version history

Usage: /create-restore-point "pre-edit" "Before camera changes"